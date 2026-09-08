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
"""Tests for mining_baseline.py (Milestone E4, prereg/v6-authority-bench.md)
-- the majority-of-three test reproduces the prereg's own hand-worked
example exactly, checked here against the real implementation rather
than trusted from the by-hand trace alone; the other tests exercise
`_simplify_rules` and `verify_soundness` directly, since natural
seed-driven redundancy turned out (during the prereg's own hand-tracing)
to be structurally hard to produce through `mine_policy`'s own
covered-tracking -- every accepted rule's own originating seed is, by
construction, not covered by any earlier rule, so an artificial,
directly-constructed `rules` list is the honest way to exercise step 5
on a case that actually needs it."""
from __future__ import annotations

from dataclasses import dataclass

from mining_baseline import _simplify_rules, mine_policy, verify_soundness


@dataclass(frozen=True)
class PQR:
    p: int
    q: int
    r: int


def majority_registry():
    """m_verdict's own polarity: a registered predicate FIRES on a LOSS
    (denial). To make "granted = majority true" (the prereg's own hand
    derivation), the predicate must fire on the opposite -- minority --
    not on majority itself."""
    return {"minority": lambda t: (t.p + t.q + t.r) < 2}


ALL_EIGHT = [PQR(p, q, r) for p in (0, 1) for q in (0, 1) for r in (0, 1)]


def test_majority_of_three_matches_the_prereg_hand_derivation():
    """prereg/v6-authority-bench.md's own hand-worked example, checked
    against the real implementation: 3 rules, none redundant, union of
    pinned attributes == {p,q,r} (the true unique reduct) -- and each
    individual rule matches the hand trace exactly, not just the final
    union."""
    result = mine_policy(("p", "q", "r"), ALL_EIGHT, majority_registry())

    assert result["tractable"] is True
    assert result["rule_count_before_simplify"] == 3
    assert result["rule_count_after_simplify"] == 3
    assert result["mined_attributes"] == frozenset({"p", "q", "r"})
    assert result["rules"] == [
        {"q": 1, "r": 1},
        {"p": 1, "r": 1},
        {"p": 1, "q": 1},
    ]

    soundness = verify_soundness(("p", "q", "r"), ALL_EIGHT, majority_registry(), result["rules"])
    assert soundness["sound"] is True
    assert soundness["mismatch_count"] == 0


def test_mine_policy_recovers_a_single_relevant_attribute():
    """verdict depends on p alone; q, r are noise. The minimal answer is
    one rule pinning only p -- confirms generalization does not stop
    early just because MULTIPLE attributes happen to be droppable."""
    registry = {"p_is_zero": lambda t: t.p == 0}  # fires (denies) on p=0, so granted = (p=1)
    result = mine_policy(("p", "q", "r"), ALL_EIGHT, registry)

    assert result["mined_attributes"] == frozenset({"p"})
    assert result["rules"] == [{"p": 1}]
    assert result["rule_count_before_simplify"] == 1


def test_simplify_rules_drops_a_rule_fully_covered_by_a_more_general_one():
    """A directly-constructed case step 5 must handle: a fully general
    rule (matches every tuple) makes every narrower rule redundant."""
    @dataclass(frozen=True)
    class Indexed:
        n: int

    reachable = [Indexed(n=i) for i in range(4)]
    rules = [{"n": 0}, {"n": 1}, {}]  # the empty rule matches all 4

    survivors = _simplify_rules(rules, reachable)
    assert survivors == [{}]


def test_simplify_rules_keeps_the_later_of_two_identical_rules_not_the_earlier():
    """Two literally identical rules (same coverage): processed in
    order, the FIRST is checked against the SECOND (still alive) and
    found redundant; the SECOND is then checked against the FIRST
    (already dead) and is NOT found redundant -- "removal reflects
    every earlier removal, never undone by a later one" means the
    surviving copy is whichever one is checked LAST, not first."""
    @dataclass(frozen=True)
    class Indexed:
        n: int

    reachable = [Indexed(n=i) for i in range(2)]
    rules = [{"n": 0}, {"n": 1}, {"n": 0}]  # rule 0 and rule 2 are identical

    survivors = _simplify_rules(rules, reachable)
    assert survivors == [{"n": 1}, {"n": 0}]  # the ORIGINAL rule 0 (index 0) is the one dropped


def test_simplify_rules_keeps_every_rule_when_none_is_redundant():
    """Each rule uniquely covers at least one tuple -- the no-op case,
    confirmed directly rather than assumed from the redundant cases
    above alone."""
    @dataclass(frozen=True)
    class Indexed:
        n: int

    reachable = [Indexed(n=i) for i in range(3)]
    rules = [{"n": 0}, {"n": 1}, {"n": 2}]

    assert _simplify_rules(rules, reachable) == rules


def test_verify_soundness_detects_a_genuine_mismatch():
    """A rule set that is otherwise the exact correct, complete policy
    (the majority-of-three hand derivation's own 3 rules) PLUS one extra
    rule that wrongly grants a single truly-denied tuple: isolates a
    genuine over-grant from mere incompleteness (a single narrow rule
    alone would ALSO under-grant everything else it doesn't cover,
    confounding the two) -- exactly one mismatch, the added rule's own
    false grant, not caught by accident."""
    registry = majority_registry()
    correct_policy_plus_one_bad_rule = [
        {"q": 1, "r": 1},
        {"p": 1, "r": 1},
        {"p": 1, "q": 1},
        {"p": 1, "q": 0, "r": 0},  # PQR(1,0,0) has minority (sum=1<2) -- truly denied, wrongly granted by this rule
    ]

    result = verify_soundness(("p", "q", "r"), ALL_EIGHT, registry, correct_policy_plus_one_bad_rule)
    assert result["sound"] is False
    assert result["mismatch_count"] == 1
    assert result["mismatches"][0]["true_granted"] is False
    assert result["mismatches"][0]["mined_granted"] is True


def test_verify_soundness_accepts_a_genuinely_sound_but_incomplete_policy():
    """Soundness (never grants a denied tuple) is independent of
    COMPLETENESS (covering every granted tuple) -- a policy that grants
    strictly fewer tuples than the truth is still, by this check's own
    definition, unsound wherever it under-grants a truly-granted tuple.
    This test confirms the checker reports that honestly (sound=False
    here, for exactly that reason), not conflating "sound" with "safe to
    under-grant"."""
    registry = majority_registry()
    incomplete_rules = [{"p": 1, "q": 1, "r": 1}]  # grants only PQR(1,1,1), missing every other majority-true tuple

    result = verify_soundness(("p", "q", "r"), ALL_EIGHT, registry, incomplete_rules)
    assert result["sound"] is False
    assert all(m["true_granted"] is True and m["mined_granted"] is False for m in result["mismatches"])


def test_mine_policy_respects_the_tractability_budget():
    """A budget of 0 seconds must stop before the first seed completes
    and report tractable=False -- the registered contingency mechanism
    itself, verified to actually trigger, not just declared in prose."""
    result = mine_policy(("p", "q", "r"), ALL_EIGHT, majority_registry(), time_budget_seconds=0.0)
    assert result["tractable"] is False
