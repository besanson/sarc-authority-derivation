# Copyright 2026 SARC Suite Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Domain model: the (action, context, evidence, control_state) four-tuple
Definition 1 (participation.py) sweeps, and the finite-model enumeration
(rank-0 reachable, remediation-reachable, executable-reachable) declared
in prereg/pair-test-grid.yaml.

Twelve fields, flattened into one frozen, hashable StateTuple for ease of
"differs in exactly one field" comparisons (dataclasses.replace). Each
field's namespace (action/context/evidence/control_state) is documented
per-field; the flattening does not erase which namespace a field belongs
to, it is a representational convenience.

SEED = 26313 (inherited baseline seed; used only where this module reads
real one-pass data, e.g. sku_resource_class())
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass, fields, replace
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Optional, Tuple

import yaml

LOSS_MODEL_PATH = "prereg/loss-model.yaml"
PAIR_TEST_GRID_PATH = "prereg/pair-test-grid.yaml"

# Ordered exactly as pair-test-grid.yaml's nine rows; participation.py's
# candidate_properties always equals this list.
#
# Per-role policy (entitlement ceiling, temporal window, allowed resource
# classes) is declared BACKGROUND CONFIGURATION the gate is built with
# (role_policy() below), read by the loss predicates via actor_role --
# deliberately NOT exposed as separate tuple fields. An earlier version of
# this module did expose them as separate "already resolved" context
# fields; running derive.py against it surfaced a real problem, recorded
# here rather than silently fixed: because each field was a pure,
# deterministic function of actor_role (a 1:1 per-role lookup), Definition
# 1's single-field perturbation test could never vary any one of {actor_
# role, role_entitlement_ceiling, role_window, role_allowed_classes} while
# holding the other three fixed -- they are structurally coupled, so ALL
# FOUR were derived as non-participating, which is mathematically correct
# under that tuple design but practically useless: a gate observing
# neither actor_role nor the resolved ceiling cannot evaluate the
# entitlement check at all. The fix is this module's actual design:
# per-role policy is CONFIGURATION (analogous to sarc-governance's own
# role_unauthorised/order_value_over_cap, which read declared per-scenario
# allowed_roles/order_value_cap as config the predicate is evaluated
# against -- one-pass's own model has no PER-ROLE table, only a single
# flat scenario-wide cap, so it never hits this coupling at all), not a
# per-decision observable input, so it is out of Definition 1's candidacy
# the same way SEED or a fixed predicate threshold would be. See
# ADR-002-participation-tuple-design.md.
CANDIDATE_PROPERTIES: Tuple[str, ...] = (
    "actor_role",
    "resource_class",
    "order_value",
    "day",
    "workflow",
    "grant_id",
    "consumed_grant_ids",
    "budget_remaining",
    "frozen",
)


@dataclass(frozen=True)
class StateTuple:
    # action
    actor_role: str
    resource_class: str
    order_value: float
    day: int
    workflow: str
    # evidence
    grant_id: Optional[str]
    # control_state
    consumed_grant_ids: FrozenSet[str]
    budget_remaining: float
    frozen: bool

    def with_property(self, name: str, value: Any) -> "StateTuple":
        return replace(self, **{name: value})


def field_names() -> Tuple[str, ...]:
    return tuple(f.name for f in fields(StateTuple))


# -- loss-model.yaml: declared per-role policy parameters -------------------

def load_loss_model(path: str = LOSS_MODEL_PATH) -> Dict[str, Any]:
    return yaml.safe_load(Path(path).read_text())


def role_policy(loss_model: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Cross-reference the three declared_parameters mappings (entitlement
    ceiling, window, allowed classes) by role, so a role's full policy
    tuple can be looked up in one call. Every role appearing in any one
    mapping must appear in all three -- asserted here rather than left to
    silently produce a partial policy."""
    losses_by_id = {loss["id"]: loss for loss in loss_model["losses"]}
    ceilings = losses_by_id["order_value_beyond_entitlement"]["declared_parameters"]["role_entitlement_ceiling"]
    windows = losses_by_id["procurement_outside_temporal_window"]["declared_parameters"]["role_window"]
    classes = losses_by_id["resource_class_not_entitled"]["declared_parameters"]["role_allowed_classes"]
    roles = set(ceilings) | set(windows) | set(classes)
    missing = [r for r in roles if r not in ceilings or r not in windows or r not in classes]
    if missing:
        raise ValueError(f"roles missing from one or more declared_parameters mappings: {missing}")
    policy = {}
    for role in roles:
        window = windows[role]
        policy[role] = {
            "role_entitlement_ceiling": float(ceilings[role]),
            "role_window": tuple(window) if window is not None else None,
            "role_allowed_classes": frozenset(classes[role]),
        }
    return policy


# -- pair-test-grid.yaml: per-field finite domains ---------------------------

def load_pair_test_grid(path: str = PAIR_TEST_GRID_PATH) -> Dict[str, Any]:
    return yaml.safe_load(Path(path).read_text())


def property_domains(grid: Dict[str, Any]) -> Dict[str, List[Any]]:
    """Flatten the grid's action/evidence/control_state groups into one
    {property_name: [domain values]} dict, normalizing consumed_grant_ids
    to the same frozenset representation StateTuple uses."""
    domains: Dict[str, List[Any]] = {}
    for group in grid["properties"].values():
        for prop_name, spec in group.items():
            values = spec["domain"]
            if prop_name == "consumed_grant_ids":
                values = [frozenset(v) for v in values]
            domains[prop_name] = values
    missing = set(CANDIDATE_PROPERTIES) - set(domains)
    extra = set(domains) - set(CANDIDATE_PROPERTIES)
    if missing or extra:
        raise ValueError(f"pair-test-grid.yaml domains do not match CANDIDATE_PROPERTIES: missing={missing} extra={extra}")
    return domains


# -- resource class assignment (declared synthetic metadata layer) ----------

def sku_resource_class(sku: str, all_skus: List[str]) -> str:
    """Deterministic rule (prereg/loss-model.yaml): sort all SKU codes,
    split into three equal contiguous thirds. First third
    'consumables', second 'durable-goods', last 'capital-equipment'.
    all_skus must be the full sorted-once list this SKU is drawn from,
    passed explicitly so this function has no hidden I/O and is trivially
    testable."""
    ordered = sorted(all_skus)
    n = len(ordered)
    idx = ordered.index(sku)
    third = n / 3.0
    if idx < third:
        return "consumables"
    elif idx < 2 * third:
        return "durable-goods"
    else:
        return "capital-equipment"


def load_all_skus(data_path: str) -> List[str]:
    skus = set()
    with open(data_path, newline="") as f:
        for row in csv.DictReader(f):
            skus.add(row["sku"])
    return sorted(skus)


# -- reachability -------------------------------------------------------

def rank0_reachable_tuples(domains: Dict[str, List[Any]]) -> List[StateTuple]:
    """Every combination of the nine candidate properties' declared
    domains. No cross-field consistency filter is needed: per-role
    policy is background configuration the predicates consult via
    actor_role (losses.py), not a separate tuple field, so every
    combination here is a legitimate independent per-decision input."""
    out: List[StateTuple] = []
    for role in domains["actor_role"]:
        for resource_class in domains["resource_class"]:
            for order_value in domains["order_value"]:
                for day in domains["day"]:
                    for workflow in domains["workflow"]:
                        for grant_id in domains["grant_id"]:
                            for consumed in domains["consumed_grant_ids"]:
                                for budget in domains["budget_remaining"]:
                                    for frz in domains["frozen"]:
                                        out.append(StateTuple(
                                            actor_role=role,
                                            resource_class=resource_class,
                                            order_value=order_value,
                                            day=day,
                                            workflow=workflow,
                                            grant_id=grant_id,
                                            consumed_grant_ids=consumed,
                                            budget_remaining=budget,
                                            frozen=frz,
                                        ))
    return out


# The two remediation operators (composition.py, sarc-suite-one-pass,
# imported not copied): evidence substitution can move order_value to ANY
# other domain value; resource downroute (W2 only) can only move it to a
# STRICTLY LOWER value in the domain's own declared ordering. Both are
# read-only characterisations of the imported baseline's own remediators,
# not new remediation logic -- Phase 3 exercises the real operators
# directly; this finite abstraction is only for the exhaustive checkers.
def remediation_reachable_tuples(rank0: List[StateTuple], order_value_domain: List[float]) -> List[StateTuple]:
    ordered_values = sorted(order_value_domain)
    out: List[StateTuple] = []
    seen = set(rank0)
    for t in rank0:
        current_idx = ordered_values.index(t.order_value)
        # evidence substitution: any other domain value
        for v in ordered_values:
            if v == t.order_value:
                continue
            candidate = t.with_property("order_value", v)
            if candidate not in seen:
                seen.add(candidate)
                out.append(candidate)
        # resource downroute: any strictly lower value (subset of the
        # substitution case above, kept as an explicit branch so the two
        # operators stay independently auditable per ADR-001-foundation.md)
        for v in ordered_values[:current_idx]:
            candidate = t.with_property("order_value", v)
            if candidate not in seen:
                seen.add(candidate)
                out.append(candidate)
    return out


def executable_reachable_tuples(domains: Dict[str, List[Any]]) -> List[StateTuple]:
    """Definition 1's reachable set: rank-0 union remediation-reachable
    (prereg/pair-test-grid.yaml's reachability section)."""
    rank0 = rank0_reachable_tuples(domains)
    remediated = remediation_reachable_tuples(rank0, domains["order_value"])
    combined = list(dict.fromkeys(rank0 + remediated))  # de-duplicated, order-stable
    return combined


# -- v2 (prereg/v2-reachability-redesign.md, tag prereg-p5-v2) --------------
#
# Additive only: every name above this point is v1, unedited, and every v1
# result file (out/checkers/derivation_output.json, reachability_check.json
# etc.) is generated exclusively by the v1 names above. Nothing below is
# imported or called by them. StateTupleV2 adds one field, min_order_
# quantity, to StateTuple's nine; CANDIDATE_PROPERTIES_V2 correspondingly
# extends CANDIDATE_PROPERTIES by exactly that one name.

CANDIDATE_PROPERTIES_V2: Tuple[str, ...] = CANDIDATE_PROPERTIES + ("min_order_quantity",)


@dataclass(frozen=True)
class StateTupleV2:
    # action
    actor_role: str
    resource_class: str
    order_value: float
    min_order_quantity: float
    day: int
    workflow: str
    # evidence
    grant_id: Optional[str]
    # control_state
    consumed_grant_ids: FrozenSet[str]
    budget_remaining: float
    frozen: bool

    def with_property(self, name: str, value: Any) -> "StateTupleV2":
        return replace(self, **{name: value})


def field_names_v2() -> Tuple[str, ...]:
    return tuple(f.name for f in fields(StateTupleV2))


def property_domains_v2(grid: Dict[str, Any]) -> Dict[str, List[Any]]:
    """v1's nine domains (property_domains(), called unmodified) plus the
    tenth (min_order_quantity), read from the grid's sibling `v2` key
    (prereg/pair-test-grid.yaml) that property_domains() itself never
    looks at."""
    domains: Dict[str, List[Any]] = dict(property_domains(grid))
    domains["min_order_quantity"] = list(grid["v2"]["properties"]["action"]["min_order_quantity"]["domain"])
    missing = set(CANDIDATE_PROPERTIES_V2) - set(domains)
    extra = set(domains) - set(CANDIDATE_PROPERTIES_V2)
    if missing or extra:
        raise ValueError(f"v2 domains do not match CANDIDATE_PROPERTIES_V2: missing={missing} extra={extra}")
    return domains


def rank0_reachable_tuples_v2(domains: Dict[str, List[Any]]) -> List[StateTupleV2]:
    """v2's rank-0 (prereg/v2-reachability-redesign.md's rank0_constraint_v2):
    the unconstrained product over all ten domains, FILTERED by one
    declared cross-field constraint -- order_value >= min_order_quantity
    always holds at rank-0 -- that v1's rank0_reachable_tuples() has no
    equivalent of (ADR-002 removed v1's one filter, per-role policy
    consistency, when policy stopped being a separate field; v2
    reintroduces a filter for an unrelated reason, a declared modeling
    assumption about well-formed initial proposals, not a coupling bug)."""
    out: List[StateTupleV2] = []
    for role in domains["actor_role"]:
        for resource_class in domains["resource_class"]:
            for order_value in domains["order_value"]:
                for min_oq in domains["min_order_quantity"]:
                    if order_value < min_oq:
                        continue
                    for day in domains["day"]:
                        for workflow in domains["workflow"]:
                            for grant_id in domains["grant_id"]:
                                for consumed in domains["consumed_grant_ids"]:
                                    for budget in domains["budget_remaining"]:
                                        for frz in domains["frozen"]:
                                            out.append(StateTupleV2(
                                                actor_role=role,
                                                resource_class=resource_class,
                                                order_value=order_value,
                                                min_order_quantity=min_oq,
                                                day=day,
                                                workflow=workflow,
                                                grant_id=grant_id,
                                                consumed_grant_ids=consumed,
                                                budget_remaining=budget,
                                                frozen=frz,
                                            ))
    return out


def downroute_reachable_tuples_v2(
    rank0_v2: List[StateTupleV2], order_value_domain: List[float]
) -> List[StateTupleV2]:
    """Primary v2 mechanism (prereg/v2-reachability-redesign.md), grounded
    directly in composition._maybe_downroute (sarc-suite-one-pass, pinned):
    feasible_qty = max(0, min(proposed_qty, max_qty_by_cost,
    max_qty_by_carbon)), W2 only, strictly decreasing when it fires, with
    no minimum-order-quantity term anywhere in it. Characterized here as:
    from any rank-0 tuple with workflow == "W2" (rank0_constraint_v2
    guarantees order_value >= min_order_quantity for every such tuple),
    the tuple with order_value moved to any strictly lower point in its
    declared domain is downroute-only reachable -- including points that
    now violate order_value >= min_order_quantity, since the real
    mechanism this characterizes has no MOQ term to respect that
    boundary. Returns only the tuples NEW beyond rank0_v2 (mirrors v1's
    remediation_reachable_tuples's own new-tuples-only contract): a
    downroute candidate that still satisfies order_value >=
    min_order_quantity is already independently rank0_v2-reachable and is
    not re-added here."""
    ordered_values = sorted(order_value_domain)
    out: List[StateTupleV2] = []
    seen = set(rank0_v2)
    for t in rank0_v2:
        if t.workflow != "W2":
            continue
        current_idx = ordered_values.index(t.order_value)
        for v in ordered_values[:current_idx]:
            candidate = t.with_property("order_value", v)
            if candidate not in seen:
                seen.add(candidate)
                out.append(candidate)
    return out


RETRY_DELAY_DAY = 200


def retry_delay_reachable_tuples_v2(rank0_v2: List[StateTupleV2]) -> List[StateTupleV2]:
    """Secondary v2 mechanism (prereg/v2-reachability-redesign.md). day=200
    is declared rank-0-unreachable -- rank0_reachable_tuples_v2's own day
    domain is v1's unchanged three points {50, 140, 300}, read from
    pair-test-grid.yaml's v1 `properties` section; this function is the
    only source of day=200 tuples. Every rank-0 tuple can be resubmitted
    once at day=200 with every other field unchanged, characterizing a
    decision whose evidence was rejected at its originally-proposed day
    and resubmitted."""
    out: List[StateTupleV2] = []
    seen = set(rank0_v2)
    for t in rank0_v2:
        candidate = t.with_property("day", RETRY_DELAY_DAY)
        if candidate not in seen:
            seen.add(candidate)
            out.append(candidate)
    return out


def executable_reachable_tuples_v2(domains: Dict[str, List[Any]]) -> List[StateTupleV2]:
    """CH-A5's decision rule (prereg/v2-reachability-redesign.md):
    rank-0 union downroute-reachable union retry-delay-reachable.
    Evidence substitution is deliberately NOT a term here (unlike v1's
    executable_reachable_tuples()) -- see appendix-a-proofs.md's
    Proposition 0-general, Corollary 1's scope note, for why porting it
    over unexamined would be unsound once rank0_constraint_v2 is in
    force, and it is not needed since this function's registered
    reachable set already includes both of v2's actual mechanisms."""
    rank0 = rank0_reachable_tuples_v2(domains)
    downroute_new = downroute_reachable_tuples_v2(rank0, domains["order_value"])
    retry_new = retry_delay_reachable_tuples_v2(rank0)
    combined = list(dict.fromkeys(rank0 + downroute_new + retry_new))
    return combined
