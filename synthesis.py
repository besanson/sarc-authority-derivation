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
Milestone D (`prereg/v5-synthesis.md`, tag `prereg-p5-v5`): SAT/MaxSAT
backends over `discernibility.py`'s own IR, via PySAT (`python-sat`,
added `bootstrap.sh`/CI this milestone -- `reproducibility_report.py`'s
`DEPENDENCY_NAMES`). `exact_reducts()` (`reduct.py`) stays the
authoritative, from-first-principles method this repo's own paper
results are built on; these backends exist to SCALE beyond
`exact_reducts()`'s 2^n subset enumeration, not to replace it where
enumeration is already feasible -- `checkers/synthesis_exactness_check.py`
holds them to the exhaustive answer everywhere exhaustion is affordable
(this artifact's own v1/v2/v4 models), so a real regression is caught by
comparison, not assumed away by trusting a solver.

Each candidate property maps to one boolean SAT variable (`var(p)`, 1
per `candidate_properties`, 1-indexed for PySAT); `var(p) = True` means
`p` is included in the synthesized contract. `discernibility.py`'s own
reduced family becomes the CNF's hard clauses directly (one clause per
difference set: at least one of its properties must be included) -- a
satisfying assignment is a sufficient contract, by
`discernibility.verify_contract`'s own equivalence to `reduct.
sufficiency` (Definition 4), machine-checked by
`checkers/discernibility_check.py`, not merely assumed here.

**Why minimum-cardinality and minimum-cost solutions are each,
themselves, reducts (Definition 5), not merely sufficient:** if a proper
subset of a minimum-cardinality sufficient contract were also
sufficient, it would have strictly smaller cardinality, contradicting
minimality -- so the minimum-cardinality solution cannot properly
contain a smaller sufficient set, which is exactly Definition 5's own
minimality clause. The same argument holds for minimum-cost under any
STRICTLY POSITIVE cost assignment (a proper sufficient subset would have
strictly lower total cost) -- `find_minimum_cost_contract` asserts every
declared cost is positive for exactly this reason, not merely as an
input-validation nicety.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, FrozenSet, List, Optional, Tuple

from pysat.examples.rc2 import RC2
from pysat.formula import CNF, WCNF
from pysat.solvers import Glucose3

from discernibility import build_discernibility_family, remove_redundant_supersets
from reduct import sufficiency


def _property_variables(candidate_properties: Tuple[str, ...]) -> Dict[str, int]:
    """1-indexed SAT variable per candidate property, in declared order
    -- deterministic given the same `candidate_properties` tuple, so two
    calls (e.g. encoding then decoding a model) always agree."""
    return {p: i + 1 for i, p in enumerate(candidate_properties)}


def _included_from_model(model: List[int], var: Dict[str, int]) -> FrozenSet[str]:
    """Decode a PySAT model into the set of included properties by SET
    membership of each property's positive literal, not positional
    indexing (`model[var[p] - 1]`) -- a property that never appears in
    any clause (every discernibility set it could hit was already
    subsumed by `remove_redundant_supersets`) is a genuine "don't care"
    the solver may omit from the returned model entirely, making the
    model list shorter than the declared variable count; membership
    correctly (and safely) treats an omitted variable as not included,
    which is also the right answer -- a variable no clause needs is not
    part of a minimal sufficient contract."""
    model_set = set(model)
    return frozenset(p for p, v in var.items() if v in model_set)


def _hard_clauses(
    candidate_properties: Tuple[str, ...],
    reachable: List[Any],
    registry: Dict[str, Callable[[Any], bool]],
) -> Tuple[List[List[int]], Dict[str, int]]:
    var = _property_variables(candidate_properties)
    family = remove_redundant_supersets(build_discernibility_family(candidate_properties, reachable, registry))
    clauses = [[var[p] for p in diff] for diff in family]
    return clauses, var


def find_any_sufficient_contract(
    candidate_properties: Tuple[str, ...],
    reachable: List[Any],
    registry: Dict[str, Callable[[Any], bool]],
) -> Optional[FrozenSet[str]]:
    """SAT: does ANY sufficient contract exist at all, and if so, name
    one -- not necessarily minimal in cardinality or cost.
    `candidate_properties` itself is always sufficient (Definition 5's
    own remark: two tuples agreeing on every candidate property are the
    same tuple), so this can only return None if `reachable` is
    malformed (not actually iterable tuples of `candidate_properties`),
    never because no sufficient set exists."""
    clauses, var = _hard_clauses(candidate_properties, reachable, registry)
    cnf = CNF(from_clauses=clauses) if clauses else CNF()
    with Glucose3(bootstrap_with=cnf) as solver:
        if not solver.solve():
            return None
        model = solver.get_model()
    return _included_from_model(model, var)


def find_minimum_cardinality_contract(
    candidate_properties: Tuple[str, ...],
    reachable: List[Any],
    registry: Dict[str, Callable[[Any], bool]],
) -> FrozenSet[str]:
    """Cardinality MaxSAT (RC2): the hard clauses are the same
    discernibility constraints `find_any_sufficient_contract` uses; a
    unit soft clause `[-var(p)]`, weight 1, per candidate property
    prefers each property EXCLUDED, so RC2's minimum-cost solution is
    exactly the sufficient contract with the fewest included
    properties -- a minimum-cardinality reduct (module docstring)."""
    clauses, var = _hard_clauses(candidate_properties, reachable, registry)
    wcnf = WCNF()
    for clause in clauses:
        wcnf.append(clause)
    for p in candidate_properties:
        wcnf.append([-var[p]], weight=1)
    with RC2(wcnf) as rc2:
        model = rc2.compute()
    return _included_from_model(model, var)


def find_minimum_cost_contract(
    candidate_properties: Tuple[str, ...],
    reachable: List[Any],
    registry: Dict[str, Callable[[Any], bool]],
    costs: Dict[str, float],
) -> FrozenSet[str]:
    """Weighted MaxSAT (RC2): identical construction to
    `find_minimum_cardinality_contract`, except each property's soft
    clause weight is its declared observation cost (`costs[p]`), not a
    uniform 1 -- RC2 then minimizes total OBSERVATION COST among
    sufficient contracts, not count. Every declared cost must be
    strictly positive (module docstring: this is what makes the result a
    reduct, not merely sufficient). PySAT's WCNF/RC2 accept float
    weights directly (verified against this installed version, not
    assumed from the API docs) -- costs are passed through unscaled."""
    missing = set(candidate_properties) - set(costs)
    if missing:
        raise ValueError(f"no declared cost for: {sorted(missing)}")
    non_positive = {p: c for p, c in costs.items() if p in candidate_properties and c <= 0}
    if non_positive:
        raise ValueError(f"costs must be strictly positive (else the result need not be minimal): {non_positive}")

    clauses, var = _hard_clauses(candidate_properties, reachable, registry)
    wcnf = WCNF()
    for clause in clauses:
        wcnf.append(clause)
    for p in candidate_properties:
        wcnf.append([-var[p]], weight=costs[p])
    with RC2(wcnf) as rc2:
        model = rc2.compute()
    return _included_from_model(model, var)


def contract_change_delta(
    base_contract: FrozenSet[str],
    candidate_properties: Tuple[str, ...],
    old_reachable: List[Any],
    new_tuples: List[Any],
    registry: Dict[str, Callable[[Any], bool]],
) -> Dict[str, Any]:
    """Milestone D5: `base_contract` is already known sufficient on
    `old_reachable` (a prior synthesis result); `new_tuples` are what a
    new transition or a new remediation operator makes newly reachable
    (this whole SARC series' own convention: an operator's effect IS
    additional reachable tuples, `domain.py`'s
    `downroute_reachable_tuples_v2`/`retry_delay_reachable_tuples_v2`,
    not a change to any existing tuple). Reports the DELTA, not just a
    fresh answer:

    1. `was_still_sufficient` -- checked directly (`reduct.sufficiency`,
       a single pass over the COMBINED reachable set, not a full
       discernibility-family rebuild) -- often the change adds nothing
       that `base_contract` didn't already cover, and this is the cheap
       way to know that without resynthesizing anything.
    2. If not: `updated_contract` keeps every property `base_contract`
       already has (pinned as hard unit clauses) and asks RC2 for the
       minimum ADDITIONAL properties needed to restore sufficiency on
       the combined set -- stable (never silently drops an
       already-relied-on observation), not necessarily cardinality-
       optimal in the batch sense (module docstring's own "incremental
       vs. batch" trade-off; measured below, not assumed away).
    3. `full_recomputation_contract`: `find_minimum_cardinality_contract`
       run from scratch on the combined set, completely independently
       of `base_contract` -- the correctness check D5 registers.
       `updated_contract` is independently confirmed sufficient
       (`incremental_is_sufficient`); `full_recomputation_cardinality_
       gap` reports how much larger (if at all) keeping `base_contract`
       pinned made the result, compared to the free-choice optimum --
       the honest price of incrementality, not hidden."""
    combined = list(old_reachable) + list(new_tuples)
    was_still_sufficient, _ = sufficiency(tuple(sorted(base_contract)), combined, registry)

    if was_still_sufficient:
        updated_contract = base_contract
    else:
        clauses, var = _hard_clauses(candidate_properties, combined, registry)
        wcnf = WCNF()
        for clause in clauses:
            wcnf.append(clause)
        for p in base_contract:
            wcnf.append([var[p]])  # hard: stay included, never dropped by an incremental update
        for p in candidate_properties:
            if p not in base_contract:
                wcnf.append([-var[p]], weight=1)
        with RC2(wcnf) as rc2:
            model = rc2.compute()
        updated_contract = _included_from_model(model, var)

    incremental_is_sufficient, _ = sufficiency(tuple(sorted(updated_contract)), combined, registry)
    full_recomputation_contract = find_minimum_cardinality_contract(candidate_properties, combined, registry)

    return {
        "base_contract": sorted(base_contract),
        "new_tuple_count": len(new_tuples),
        "was_still_sufficient": was_still_sufficient,
        "updated_contract": sorted(updated_contract),
        "updated_contract_cardinality": len(updated_contract),
        "incremental_is_sufficient": incremental_is_sufficient,
        "full_recomputation_contract": sorted(full_recomputation_contract),
        "full_recomputation_cardinality": len(full_recomputation_contract),
        "full_recomputation_cardinality_gap": len(updated_contract) - len(full_recomputation_contract),
    }
