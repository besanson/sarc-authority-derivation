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
Milestone E1, full signature (task brief; prereg/v6.1-authoritybench-
amendment.md's own "authority_compiler's fuller API" section, which
this file implements verbatim): packages this artifact's own
already-verified derivation machinery (participation.py's Definition
1/2, reduct.py's Definitions 4-6, synthesis.py's SAT/MaxSAT backend and
contract_change_delta) behind one call, `derive_authority_contract
(loss_model, reachable_semantics, candidate_context, observation_costs)`,
returning the nine fields the task brief's own E1 item names. No new
derivation semantics anywhere in this file: every field is computed by
calling straight through to an existing, already-tested function of the
same name; this module's own new behavior is the packaging (one
dataclass, one dispatch function, the `reachability_dependencies` field,
which IS new logic -- documented at its own definition below, not
borrowed from an existing function).

**Parameter naming, fixed by the task brief's own E1 item, not this
module's choice:** `reachable_semantics` is the MATERIALIZED executable-
reachable tuple list (`List[Any]`) -- every other function in this
codebase (`reduct.sufficiency`, `reduct.exact_reducts`, `participation.
compute_p_star`, `synthesis.find_minimum_cardinality_contract`) already
takes a materialized list, not a callable that produces one, and this
module keeps that same convention rather than introducing a second one;
"semantics" names WHAT it is (the domain's reachability semantics,
already executed), not its Python type. `candidate_context` is
`Dict[str, List[Any]]` -- property name to its declared domain values
(`domain.property_domains`/`domain_v4.PROPERTY_DOMAINS_V4`'s own
existing shape, reused directly) -- candidate_properties themselves are
`tuple(candidate_context.keys())`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, FrozenSet, List, Optional, Tuple

from reduct import compute_core, exact_reducts, sufficiency
from synthesis import contract_change_delta as _contract_change_delta
from synthesis import find_minimum_cardinality_contract, find_minimum_cost_contract

EXHAUSTIVE_REDUCT_SUBSET_LIMIT = 20  # 2**20 = 1,048,576 subsets -- affordable; matches this project's own "where exhaustion is feasible" scoping (synthesis.py's module docstring), a documented threshold rather than an unstated one


@dataclass(frozen=True)
class AuthorityContract:
    """The packaged result of one `derive_authority_contract` call --
    the nine fields task brief E1 names, in its own order.

    `core_attributes`: Definition 2's P* (`reduct.compute_core`,
    `participation.compute_p_star` unmodified).
    `minimal_reducts`: Definition 5, every reduct (`reduct.exact_reducts`)
    when `len(candidate_context) <= EXHAUSTIVE_REDUCT_SUBSET_LIMIT`;
    otherwise `None`, with `minimal_reducts_note` stating why -- never
    silently truncated or sampled.
    `minimum_cardinality_reduct`: Definition 5, one reduct of minimum
    cardinality (`synthesis.find_minimum_cardinality_contract`).
    `minimum_cost_reduct`: the same, minimum COST instead of cardinality
    (`synthesis.find_minimum_cost_contract`) -- `None` when
    `observation_costs` is not supplied (never a fabricated cost).
    `redundant_attributes`: Definition 3, `candidate_properties -
    core_attributes`.
    `sufficiency_certificate`: `reduct.sufficiency`'s own full
    certificate dict for `core_attributes` (not merely a boolean).
    `counterexamples`: the certificate's own counterexample pair when
    `core_attributes` is not sufficient; `None` when it is.
    `reachability_dependencies`: properties whose OBSERVED value set in
    `reachable_semantics` is a strict subset of their DECLARED domain in
    `candidate_context` -- i.e., properties some reachability
    constraint actually restricts, detected directly by comparing the
    two, not asserted from a separately-declared rule list (this
    module's own new logic, `_reachability_dependencies` below).
    `contract_change_delta`: a bound callable, `new_tuples -> dict`,
    closing over this call's own `minimum_cardinality_reduct`,
    `candidate_properties`, `reachable_semantics`, and `loss_model` --
    `synthesis.contract_change_delta` wired through, not reimplemented.
    """

    core_attributes: FrozenSet[str]
    minimal_reducts: Optional[List[FrozenSet[str]]]
    minimal_reducts_note: Optional[str]
    minimum_cardinality_reduct: FrozenSet[str]
    minimum_cost_reduct: Optional[FrozenSet[str]]
    redundant_attributes: FrozenSet[str]
    sufficiency_certificate: Dict[str, Any]
    counterexamples: Optional[Dict[str, Any]]
    reachability_dependencies: FrozenSet[str]
    contract_change_delta: Callable[[List[Any]], Dict[str, Any]]
    candidate_property_count: int
    reachable_tuple_count: int


def _reachability_dependencies(candidate_context: Dict[str, List[Any]], reachable_semantics: List[Any]) -> FrozenSet[str]:
    """Which candidate properties does SOME reachability constraint
    actually restrict, observed directly (not asserted from a
    separately-declared rule list this function does not receive): a
    property is reported iff the SET of values it actually takes across
    `reachable_semantics` is a strict subset of the FULL declared domain
    `candidate_context` names for it -- e.g. v2's own `min_order_
    quantity` cross-field filter, or this milestone's new domain's
    `recipient_type == internal_only` -> `destination_region == eea`
    rule, both narrow the AFFECTED property's own observed value set
    below its full declared domain, detectably, without re-parsing
    either rule's own prose."""
    dependent = set()
    for prop, declared_domain in candidate_context.items():
        observed = {getattr(t, prop) for t in reachable_semantics}
        if len(observed) < len(set(declared_domain)):
            dependent.add(prop)
    return frozenset(dependent)


def derive_authority_contract(
    loss_model: Dict[str, Callable[[Any], bool]],
    reachable_semantics: List[Any],
    candidate_context: Dict[str, List[Any]],
    observation_costs: Optional[Dict[str, float]] = None,
) -> AuthorityContract:
    """The packaged entry point, task brief E1's own four parameters in
    its own order. Every field is computed by an existing, already-
    tested function (`reachability_dependencies` excepted, documented at
    its own definition); nothing here recomputes anything from first
    principles."""
    candidate_properties: Tuple[str, ...] = tuple(candidate_context.keys())

    core, coverage, _witnesses = compute_core(reachable_semantics, loss_model, candidate_properties)
    core = frozenset(core)
    coverage = frozenset(coverage)
    certificate_holds, certificate = sufficiency(tuple(sorted(core)), reachable_semantics, loss_model)
    counterexamples = None if certificate_holds else certificate

    if len(candidate_properties) <= EXHAUSTIVE_REDUCT_SUBSET_LIMIT:
        reducts, _subsets_considered = exact_reducts(candidate_properties, reachable_semantics, loss_model)
        minimal_reducts: Optional[List[FrozenSet[str]]] = reducts
        minimal_reducts_note = None
    else:
        minimal_reducts = None
        minimal_reducts_note = (
            f"{len(candidate_properties)} candidate properties exceeds EXHAUSTIVE_REDUCT_SUBSET_LIMIT "
            f"({EXHAUSTIVE_REDUCT_SUBSET_LIMIT}); exhaustive enumeration (2**n subsets) not attempted."
        )

    min_card = find_minimum_cardinality_contract(candidate_properties, reachable_semantics, loss_model)
    min_cost = (
        find_minimum_cost_contract(candidate_properties, reachable_semantics, loss_model, observation_costs)
        if observation_costs is not None
        else None
    )

    def _bound_contract_change_delta(new_tuples: List[Any]) -> Dict[str, Any]:
        return _contract_change_delta(min_card, candidate_properties, reachable_semantics, new_tuples, loss_model)

    return AuthorityContract(
        core_attributes=core,
        minimal_reducts=minimal_reducts,
        minimal_reducts_note=minimal_reducts_note,
        minimum_cardinality_reduct=min_card,
        minimum_cost_reduct=min_cost,
        redundant_attributes=coverage,
        sufficiency_certificate=certificate,
        counterexamples=counterexamples,
        reachability_dependencies=_reachability_dependencies(candidate_context, reachable_semantics),
        contract_change_delta=_bound_contract_change_delta,
        candidate_property_count=len(candidate_properties),
        reachable_tuple_count=len(reachable_semantics),
    )
