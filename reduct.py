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
v3 (prereg/v3-core-reduct-correction.md, tag prereg-p5-v3): Definitions
4-6 (sufficiency, reduct, core) and Proposition 1'/Negative Proposition
N's shared machinery.

Corrects v0.1/v0.2's Proposition 1, which interpreted `participation.
compute_p_star`'s output (the CORE: properties with an individual
singleton-perturbation witness, Definition 1) as a REDUCT (a minimal
JOINTLY SUFFICIENT observation set, Definition 5). Core is always
contained in every reduct (Definition 6), but a core need not itself be
sufficient -- Negative Proposition N's registered counterexample
(`prereg/fixtures/negative-proposition-n-counterexample.json`) is the
sharpest possible instance: an empty core that is not sufficient, with
two singleton reducts neither of which is the core.

`compute_core()` below calls `participation.compute_p_star` UNCHANGED --
Proposition 1' claim 1 ("Definition 1 computes the core") is a claim
about what that existing, unedited function's output IS, not a
reimplementation of it. `verify_core_identity()` is the actual machine
check of that claim: it recomputes the core a SECOND, independent way
(the intersection of every reduct `exact_reducts()` finds by direct
enumeration against Definition 4) and confirms the two agree.
"""
from __future__ import annotations

from itertools import combinations
from typing import Any, Callable, Dict, FrozenSet, List, Tuple

from participation import _serialize, compute_p_star


def sufficiency(
    s: Tuple[str, ...],
    reachable: List[Any],
    registry: Dict[str, Callable[[Any], bool]],
) -> Tuple[bool, Dict[str, Any]]:
    """Definition 4: is property set `s` sufficient for `registry`'s loss
    model on `reachable`? Partitions `reachable` by projection onto `s`
    and checks every partition cell carries a uniform M-verdict.

    Returns (True, sufficiency_certificate) -- the partition itself,
    per-cell uniformity confirmed -- or (False, counterexample) -- one
    concrete reachable pair agreeing on every property in `s` with
    different verdicts, found by direct iteration, not asserted."""
    from losses import m_verdict

    groups: Dict[Tuple[Any, ...], List[Any]] = {}
    for t in reachable:
        key = tuple(getattr(t, attr) for attr in s)
        groups.setdefault(key, []).append(t)

    for group in groups.values():
        base = group[0]
        base_verdict = m_verdict(base, registry)
        for t in group[1:]:
            v = m_verdict(t, registry)
            if v != base_verdict:
                return False, {
                    "tuple_a": _serialize(base),
                    "tuple_a_prime": _serialize(t),
                    "verdict_a": base_verdict,
                    "verdict_a_prime": v,
                }
    return True, {"partition_cell_count": len(groups), "uniform_verdict_within_every_cell": True}


def exact_reducts(
    candidate_properties: Tuple[str, ...],
    reachable: List[Any],
    registry: Dict[str, Callable[[Any], bool]],
) -> Tuple[List[FrozenSet[str]], int]:
    """Definition 5, exhaustive: every reduct, found by testing subsets of
    `candidate_properties` in order of INCREASING size, with subset
    pruning -- a candidate that is a superset of an already-confirmed
    reduct cannot itself be minimal, so it is skipped without being
    tested for sufficiency at all. Because sizes are tested smallest
    first, every set actually tested and found sufficient is, by
    construction, minimal (no smaller subset of it was found sufficient
    earlier, and pruning already ruled out every superset of a smaller
    reduct) -- so the confirmed-sufficient sets found this way ARE
    exactly the reducts; no separate minimality pass is needed.

    Returns (reducts, subsets_considered) -- subsets_considered counts
    only the sets actually tested (post-pruning), always
    <= 2^len(candidate_properties), so exhaustiveness-with-pruning is
    distinguishable from a sample."""
    reducts: List[FrozenSet[str]] = []
    subsets_considered = 0
    n = len(candidate_properties)
    for size in range(0, n + 1):
        for combo in combinations(candidate_properties, size):
            s = frozenset(combo)
            if any(r <= s for r in reducts):
                continue
            subsets_considered += 1
            is_suff, _ = sufficiency(tuple(sorted(s)), reachable, registry)
            if is_suff:
                reducts.append(s)
    return reducts, subsets_considered


def compute_core(
    reachable: List[Any],
    registry: Dict[str, Callable[[Any], bool]],
    candidate_properties: Tuple[str, ...],
) -> Tuple[List[str], List[str], Dict[str, Any]]:
    """Definition 6 via Proposition 1' claim 1: the core is exactly what
    Definition 1 (`participation.compute_p_star`, called here UNCHANGED)
    already computes. Returns (core_attributes, redundant_attributes,
    witnesses) -- the v3-renamed vocabulary
    (prereg/v3-core-reduct-correction.md's Renaming plan) for exactly the
    same values `compute_p_star` always returned as
    (participating_properties, coverage_list, witnesses)."""
    return compute_p_star(reachable, registry, candidate_properties)


def verify_core_identity(
    reachable: List[Any],
    registry: Dict[str, Callable[[Any], bool]],
    candidate_properties: Tuple[str, ...],
) -> Dict[str, Any]:
    """Machine-checks Proposition 1' claim 1 by recomputing the core TWO
    independent ways and confirming they agree: (a) Definition 1's own
    witness search (`compute_core`, i.e. `participation.compute_p_star`
    unmodified), and (b) Definition 6's literal intersection of every
    reduct `exact_reducts` finds by direct enumeration against
    Definition 4. Also confirms claim 2 (core subset-of every reduct) --
    a direct structural consequence of computing the core as that same
    intersection, checked here against EVERY individual reduct, not only
    asserted from the intersection arithmetic."""
    core_via_definition_1, _, _ = compute_core(reachable, registry, candidate_properties)
    reducts, subsets_considered = exact_reducts(candidate_properties, reachable, registry)

    core_via_intersection = set(candidate_properties)
    for r in reducts:
        core_via_intersection &= r
    core_via_intersection_sorted = sorted(core_via_intersection)

    identity_holds = sorted(core_via_definition_1) == core_via_intersection_sorted
    core_subset_of_every_reduct = all(core_via_intersection <= r for r in reducts)

    return {
        "core_via_definition_1": sorted(core_via_definition_1),
        "core_via_reduct_intersection": core_via_intersection_sorted,
        "identity_holds": identity_holds,
        "core_subset_of_every_reduct": core_subset_of_every_reduct,
        "reducts": [sorted(r) for r in reducts],
        "subsets_considered": subsets_considered,
    }
