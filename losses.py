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
The six loss predicates declared in prereg/loss-model.yaml, registered by
id. Each predicate is a pure function of one domain.StateTuple to a bool
(True = hazard/loss-violation fires).

Three predicates (order_value_beyond_entitlement,
procurement_outside_temporal_window, resource_class_not_entitled) read
per-role policy (domain.role_policy()) via actor_role -- policy is
declared BACKGROUND CONFIGURATION (see domain.py's CANDIDATE_PROPERTIES
docstring for why it is not a separate observable field), so these three
are PREDICATE FACTORIES: make_*(policy) -> the actual bound predicate.
The other three are plain functions of a tuple alone. load_loss_registry()
builds the fully-bound registry from a loaded loss_model.

Registration mirrors sarc_governance's own predicate-registry pattern
(composition.py's register_sg_predicate) -- names here must match
loss-model.yaml's `predicate:` fields exactly, checked by
load_loss_registry().
"""
from __future__ import annotations

from typing import Callable, Dict

from domain import StateTuple, StateTupleV2, role_policy


def make_order_value_beyond_entitlement(policy: Dict[str, Dict[str, object]]) -> Callable[[StateTuple], bool]:
    def predicate(t: StateTuple) -> bool:
        return t.order_value > policy[t.actor_role]["role_entitlement_ceiling"]
    return predicate


def make_procurement_outside_temporal_window(policy: Dict[str, Dict[str, object]]) -> Callable[[StateTuple], bool]:
    def predicate(t: StateTuple) -> bool:
        window = policy[t.actor_role]["role_window"]
        if window is None:
            return True
        start, end = window
        return not (start <= t.day <= end)
    return predicate


def make_resource_class_not_entitled(policy: Dict[str, Dict[str, object]]) -> Callable[[StateTuple], bool]:
    def predicate(t: StateTuple) -> bool:
        return t.resource_class not in policy[t.actor_role]["role_allowed_classes"]
    return predicate


def replayed_consumed_grant(t: StateTuple) -> bool:
    return t.grant_id is not None and t.grant_id in t.consumed_grant_ids


def spend_against_depleted_delegated_budget(t: StateTuple) -> bool:
    return t.order_value > t.budget_remaining


def action_on_frozen_control_state(t: StateTuple) -> bool:
    return t.frozen


_FACTORY_REGISTRY: Dict[str, Callable[[Dict[str, Dict[str, object]]], Callable[[StateTuple], bool]]] = {
    "order_value_beyond_entitlement": make_order_value_beyond_entitlement,
    "procurement_outside_temporal_window": make_procurement_outside_temporal_window,
    "resource_class_not_entitled": make_resource_class_not_entitled,
}

_PLAIN_REGISTRY: Dict[str, Callable[[StateTuple], bool]] = {
    "replayed_consumed_grant": replayed_consumed_grant,
    "spend_against_depleted_delegated_budget": spend_against_depleted_delegated_budget,
    "action_on_frozen_control_state": action_on_frozen_control_state,
}


def load_loss_registry(loss_model: dict) -> Dict[str, Callable[[StateTuple], bool]]:
    """Bind loss-model.yaml's declared predicate names to the registered
    implementations (building the three policy-dependent ones via their
    factory and domain.role_policy()), failing loudly if a declared
    predicate has no registered implementation (or vice versa) -- the
    same declared-vs-registered cross-check specs/authority.yaml's
    predicate names get from composition.py."""
    declared = {loss["id"]: loss["predicate"] for loss in loss_model["losses"]}
    known = set(_FACTORY_REGISTRY) | set(_PLAIN_REGISTRY)
    missing_impl = [pid for pid, pred in declared.items() if pred not in known]
    if missing_impl:
        raise ValueError(f"declared predicates with no registered implementation: {missing_impl}")
    unclaimed = [pred for pred in known if pred not in declared.values()]
    if unclaimed:
        raise ValueError(f"registered predicates not declared in loss-model.yaml: {unclaimed}")

    policy = role_policy(loss_model)
    registry: Dict[str, Callable[[StateTuple], bool]] = {}
    for pid, pred_name in declared.items():
        if pred_name in _FACTORY_REGISTRY:
            registry[pid] = _FACTORY_REGISTRY[pred_name](policy)
        else:
            registry[pid] = _PLAIN_REGISTRY[pred_name]
    return registry


def evaluate_losses(t: StateTuple, registry: Dict[str, Callable[[StateTuple], bool]]) -> Dict[str, bool]:
    return {loss_id: predicate(t) for loss_id, predicate in registry.items()}


def m_verdict(t: StateTuple, registry: Dict[str, Callable[[StateTuple], bool]]) -> bool:
    """The loss model's overall verdict for one tuple: hazardous if ANY
    registered loss predicate fires. Domain-agnostic in practice (only
    calls predicate(t) and any()), so load_loss_registry_v2's registry
    below is evaluated through this same function, not a v2 copy of it."""
    return any(predicate(t) for predicate in registry.values())


# -- v2 (prereg/v2-reachability-redesign.md, tag prereg-p5-v2) --------------
#
# Additive only: load_loss_registry() and the six v1 predicates above are
# unedited. downrouted_quantity_below_supplier_minimum is the seventh loss
# (prereg/loss-model.yaml's v2_losses key); load_loss_registry_v2() binds
# it alongside v1's six into one registry over StateTupleV2. m_verdict()
# above is reused unmodified -- it only ever calls predicate(t) and any(),
# so it works identically over a StateTupleV2 registry.

def downrouted_quantity_below_supplier_minimum(t: StateTupleV2) -> bool:
    return t.order_value < t.min_order_quantity


_PLAIN_REGISTRY_V2_EXTRA: Dict[str, Callable[[StateTupleV2], bool]] = {
    "downrouted_quantity_below_supplier_minimum": downrouted_quantity_below_supplier_minimum,
}


def load_loss_registry_v2(loss_model: dict) -> Dict[str, Callable[[StateTupleV2], bool]]:
    """v1's six losses (loss_model['losses']) plus the seventh
    (loss_model['v2_losses']) bound into one registry over StateTupleV2.
    Reuses domain.role_policy() unmodified (it only ever reads
    loss_model['losses'], so the v2_losses key is invisible to it, exactly
    as intended). Mirrors load_loss_registry()'s declared-vs-registered
    cross-check, extended to the seven-loss union so v2's registration is
    checked exactly as strictly as v1's -- load_loss_registry() itself is
    not called and not modified."""
    all_declared = list(loss_model["losses"]) + list(loss_model["v2_losses"])
    declared = {loss["id"]: loss["predicate"] for loss in all_declared}
    known = set(_FACTORY_REGISTRY) | set(_PLAIN_REGISTRY) | set(_PLAIN_REGISTRY_V2_EXTRA)
    missing_impl = [pid for pid, pred in declared.items() if pred not in known]
    if missing_impl:
        raise ValueError(f"declared predicates with no registered implementation: {missing_impl}")
    unclaimed = [pred for pred in known if pred not in declared.values()]
    if unclaimed:
        raise ValueError(f"registered predicates not declared in loss-model.yaml (v1+v2): {unclaimed}")

    policy = role_policy(loss_model)
    registry: Dict[str, Callable[[StateTupleV2], bool]] = {}
    for pid, pred_name in declared.items():
        if pred_name in _FACTORY_REGISTRY:
            registry[pid] = _FACTORY_REGISTRY[pred_name](policy)
        elif pred_name in _PLAIN_REGISTRY:
            registry[pid] = _PLAIN_REGISTRY[pred_name]
        else:
            registry[pid] = _PLAIN_REGISTRY_V2_EXTRA[pred_name]
    return registry
