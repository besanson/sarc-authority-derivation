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
Milestone E4 (`prereg/v6-authority-bench.md`, tag `prereg-p5-v6`): the
scoped reimplementation of Xu and Stoller's seed-and-generalize-and-
select mining core, registered precisely (seed order, generalization
order, simplify rule, comparison metric) before this file was written.
Every numbered step below implements the identically-numbered step in
the prereg's own "The algorithm" section -- this module does not
introduce, drop, or reorder any of them.

`mine_policy`'s only registered discretion is IMPLEMENTATION speed (the
prereg's own "Tractability contingency": denied tuples are pre-filtered
once per domain and `_matches`' `all()` short-circuits, rather than a
literal nested loop over the full reachable set at every step -- an
engineering choice with no effect on which rules get accepted, not a
change to step 3's OBSERVABLE per-drop decision, which still checks
"does the generalized rule match a denied tuple" over exactly the same
`denied_tuples` set a naive scan would)."""
from __future__ import annotations

import time
from typing import Any, Callable, Dict, FrozenSet, List, Tuple

from losses import m_verdict


def _matches(t: Any, rule: Dict[str, Any]) -> bool:
    """Does reachable tuple `t` satisfy every pinned constraint in
    `rule`? An empty rule (nothing pinned) matches everything -- the
    fully-wildcarded case `all()` already handles correctly (vacuously
    True over zero conjuncts)."""
    return all(getattr(t, prop) == value for prop, value in rule.items())


def _simplify_rules(rules: List[Dict[str, Any]], reachable: List[Any]) -> List[Dict[str, Any]]:
    """Step 5: drop a rule iff its entire matched-tuple set is already a
    subset of the union of the OTHER rules' matched sets -- checked once,
    in `rules`' own order, against whichever rules are still alive at
    that point (so a removal decision reflects every earlier removal in
    the same pass, and is never itself undone by a later one)."""
    match_sets = [frozenset(idx for idx, t in enumerate(reachable) if _matches(t, r)) for r in rules]
    alive = [True] * len(rules)
    for idx in range(len(rules)):
        others_union: set = set()
        for other_idx in range(len(rules)):
            if other_idx != idx and alive[other_idx]:
                others_union |= match_sets[other_idx]
        if match_sets[idx] <= others_union:
            alive[idx] = False
    return [rules[idx] for idx in range(len(rules)) if alive[idx]]


def mine_policy(
    candidate_properties: Tuple[str, ...],
    reachable: List[Any],
    registry: Dict[str, Callable[[Any], bool]],
    *,
    time_budget_seconds: float = 1200.0,
) -> Dict[str, Any]:
    """Steps 1-6 of `prereg/v6-authority-bench.md`'s registered
    algorithm. `granted(t) = not m_verdict(t, registry)` (the prereg's
    own "ground-truth grant relation" section) -- fixed here, not a
    parameter, since the prereg registers this one specific translation,
    not a family of possible ones.

    Returns a dict: `rules` (the surviving policy, each a dict of pinned
    property -> value), `mined_attributes` (the union of pinned
    properties across every surviving rule -- the prereg's own
    registered comparison metric, step 6), `rule_count_before_simplify`/
    `rule_count_after_simplify`, `tractable` (False iff the 20-minute
    default budget -- prereg's own "Tractability contingency" -- was
    exceeded before every granted tuple was covered, in which case
    `rules` holds whatever had already been accepted), and
    `elapsed_seconds`."""
    start = time.perf_counter()
    granted_flags = [not m_verdict(t, registry) for t in reachable]
    denied_tuples = [t for t, g in zip(reachable, granted_flags) if not g]

    covered = [False] * len(reachable)
    rules: List[Dict[str, Any]] = []
    tractable = True

    for i, seed in enumerate(reachable):
        if time.perf_counter() - start > time_budget_seconds:
            tractable = False
            break
        if covered[i] or not granted_flags[i]:
            continue

        # Step 2: most specific starting rule.
        rule: Dict[str, Any] = {p: getattr(seed, p) for p in candidate_properties}

        # Step 3: generalize by dropping conjuncts, one pass, fixed order.
        for p in candidate_properties:
            trial = {k: v for k, v in rule.items() if k != p}
            if not any(_matches(d, trial) for d in denied_tuples):
                rule = trial

        rules.append(rule)

        # Step 1's own "skip already-covered" bookkeeping: mark every
        # reachable tuple this newly-accepted rule matches.
        for j, other in enumerate(reachable):
            if not covered[j] and _matches(other, rule):
                covered[j] = True

    rule_count_before_simplify = len(rules)
    final_rules = _simplify_rules(rules, reachable)

    # Step 6: the comparison attribute set -- the union across every
    # SURVIVING rule, not any single rule's own pinned set.
    mined_attributes: FrozenSet[str] = frozenset().union(*(set(r.keys()) for r in final_rules)) if final_rules else frozenset()

    return {
        "rules": final_rules,
        "mined_attributes": mined_attributes,
        "rule_count_before_simplify": rule_count_before_simplify,
        "rule_count_after_simplify": len(final_rules),
        "tractable": tractable,
        "elapsed_seconds": time.perf_counter() - start,
    }


def verify_soundness(
    candidate_properties: Tuple[str, ...],
    reachable: List[Any],
    registry: Dict[str, Callable[[Any], bool]],
    rules: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """The prereg's own registered soundness cross-check: for every
    reachable tuple, is "granted by the true labels" identical to
    "granted by the mined rule set (matches at least one surviving
    rule)"? Checked directly, once, over the FULL policy -- not inferred
    from step 3's own per-rule construction invariant (which guarantees
    each rule individually never matches a denied tuple, but does not,
    by itself, prove the union of rules never OMITS a granted tuple --
    that omission is exactly what step 1's own "repeat until every
    granted tuple is covered" loop is supposed to prevent, checked here
    rather than assumed)."""
    mismatches = []
    for t in reachable:
        true_granted = not m_verdict(t, registry)
        mined_granted = any(_matches(t, r) for r in rules)
        if true_granted != mined_granted:
            mismatches.append({
                "tuple": {p: getattr(t, p) for p in candidate_properties},
                "true_granted": true_granted,
                "mined_granted": mined_granted,
            })
    return {"sound": not mismatches, "mismatch_count": len(mismatches), "mismatches": mismatches[:10]}
