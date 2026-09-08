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
Milestone D (`prereg/v5-synthesis.md`, tag `prereg-p5-v5`): the
discernibility-matrix IR (Skowron & Rauszer, 1992 --
`verified-citations.json`'s `skowron-rauszer-discernibility-1992`, the
source `prereg/v3-core-reduct-correction.md` already named as the
discernibility-matrix device `reduct.py`'s own algorithm would one day be
positioned against). `synthesis.py`'s SAT/MaxSAT backends encode this
IR directly as CNF; this module is domain-agnostic (only ever calls
`getattr(t, property)` and `losses.m_verdict`), the same style
`reduct.py`/`participation.py` already use.

**The claim this module exists to make machine-checkable (not asserted,
checked by `checkers/discernibility_check.py` against every subset of
several real and synthetic models):** Definition 4's sufficiency --
"every pair of reachable tuples agreeing on S has the same verdict" --
is logically equivalent to "S hits (has nonempty intersection with)
every discernibility set built from a cross-verdict-differing pair."
Contrapositive of Definition 4 itself: S is NOT sufficient iff some
cross-verdict pair agrees on all of S, iff S fails to hit that pair's
difference set. `verify_contract` below computes this the discernibility
way; `reduct.sufficiency` computes the identical fact the partition way;
`checkers/discernibility_check.py` confirms they always agree.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, FrozenSet, List, Optional, Tuple


def build_discernibility_family(
    candidate_properties: Tuple[str, ...],
    reachable: List[Any],
    registry: Dict[str, Callable[[Any], bool]],
) -> List[FrozenSet[str]]:
    """One set per DISTINCT pair of reachable tuples with differing
    M-verdicts -- the candidate properties they differ on. Only
    cross-verdict pairs are considered: a same-verdict pair imposes no
    hitting-set constraint under Definition 4 (agreeing OR disagreeing
    on any property set never has to change a verdict both tuples
    already share). Deduplicated: the returned family is a SET of
    difference sets, not one entry per pair -- many pairs produce the
    identical difference set, especially once candidate_properties is
    modest in size (at most 2^len(candidate_properties) distinct sets
    can ever occur, however many pairs generate them)."""
    from losses import m_verdict

    by_verdict: Dict[bool, List[Any]] = {True: [], False: []}
    for t in reachable:
        by_verdict[m_verdict(t, registry)].append(t)

    family: set = set()
    for t_a in by_verdict[True]:
        for t_b in by_verdict[False]:
            diff = frozenset(p for p in candidate_properties if getattr(t_a, p) != getattr(t_b, p))
            family.add(diff)
    return list(family)


def remove_redundant_supersets(family: List[FrozenSet[str]]) -> List[FrozenSet[str]]:
    """Standard discernibility-function simplification (absorption): a
    difference set that is a proper superset of another one already in
    the family adds no hitting-set constraint of its own -- any contract
    that hits the smaller set automatically hits every superset of it.
    Does not change which contracts are sufficient, only how many CNF
    clauses `synthesis.py` needs to encode that fact."""
    minimal: List[FrozenSet[str]] = []
    for candidate in sorted(family, key=len):
        if not any(existing <= candidate for existing in minimal):
            minimal.append(candidate)
    return minimal


def verify_contract(contract: FrozenSet[str], family: List[FrozenSet[str]]) -> Tuple[bool, Optional[FrozenSet[str]]]:
    """Is `contract` sufficient, checked the discernibility way: does it
    hit (intersect) every set in `family`? Returns (True, None) if so,
    or (False, the first difference set found unhit) otherwise -- the
    independent, family-based counterpart to `reduct.sufficiency`'s own
    partition-based check (module docstring)."""
    for diff in family:
        if contract.isdisjoint(diff):
            return False, diff
    return True, None


def counterexample_for(
    contract: FrozenSet[str],
    reachable: List[Any],
    registry: Dict[str, Callable[[Any], bool]],
) -> Optional[Dict[str, Any]]:
    """A concrete reachable pair witnessing that `contract` is NOT
    sufficient (two tuples agreeing on every property in `contract` with
    different verdicts), or None if `contract` is in fact sufficient.
    Reuses `reduct.sufficiency` directly (DRY -- the partition-based
    counterexample search is already written and already tested there;
    this is not a second implementation of it)."""
    from reduct import sufficiency

    is_sufficient, cert_or_counterexample = sufficiency(tuple(sorted(contract)), reachable, registry)
    return None if is_sufficient else cert_or_counterexample
