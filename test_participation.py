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
"""Tests for participation.py (Definitions 1-3) using small synthetic
loss models -- independent of loss-model.yaml's actual six losses, so
these tests catch bugs in the participation MACHINERY itself, not just
reproduce derive.py's own output (which checkers/participation_check.py
already verifies against the real declared model)."""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, FrozenSet, Optional

from participation import compute_p_star, find_witness


@dataclass(frozen=True)
class Toy:
    x: int
    y: int
    z: str

    def with_property(self, name: str, value: Any) -> "Toy":
        return replace(self, **{name: value})


def toy_verdict(t: Toy) -> bool:
    return t.x > 5  # only x ever matters


def toy_registry():
    return {"only_loss": toy_verdict}


def toy_m_verdict(t, registry):
    return any(p(t) for p in registry.values())


def test_find_witness_detects_the_only_relevant_property(monkeypatch):
    import participation as p
    monkeypatch.setattr(p, "m_verdict", toy_m_verdict)
    reachable = [Toy(x=3, y=1, z="a"), Toy(x=8, y=1, z="a")]
    witness = find_witness("x", reachable, toy_registry())
    assert witness is not None
    assert witness["loss_id"] == "only_loss"


def test_find_witness_returns_none_for_irrelevant_property(monkeypatch):
    import participation as p
    monkeypatch.setattr(p, "m_verdict", toy_m_verdict)
    reachable = [Toy(x=3, y=1, z="a"), Toy(x=3, y=99, z="a")]
    assert find_witness("y", reachable, toy_registry()) is None


def test_find_witness_ignores_pairs_that_also_differ_elsewhere(monkeypatch):
    """A pair differing in BOTH y and z (not just y) must not count as a
    witness for y, even if their verdicts differ for some other reason --
    the fingerprint grouping must hold every other field fixed."""
    import participation as p
    monkeypatch.setattr(p, "m_verdict", toy_m_verdict)
    reachable = [Toy(x=3, y=1, z="a"), Toy(x=8, y=2, z="b")]
    assert find_witness("y", reachable, toy_registry()) is None
    assert find_witness("z", reachable, toy_registry()) is None


def test_compute_p_star_partitions_candidates_exactly(monkeypatch):
    import participation as p
    monkeypatch.setattr(p, "m_verdict", toy_m_verdict)
    reachable = [
        Toy(x=3, y=1, z="a"),
        Toy(x=8, y=1, z="a"),
        Toy(x=3, y=2, z="a"),
        Toy(x=3, y=1, z="b"),
    ]
    p_star, coverage, witnesses = compute_p_star(reachable, toy_registry(), ("x", "y", "z"))
    assert p_star == ["x"]
    assert coverage == ["y", "z"]
    assert set(p_star) | set(coverage) == {"x", "y", "z"}
    assert set(p_star) & set(coverage) == set()
    assert "x" in witnesses and len(witnesses["x"]) == 1


def test_compute_p_star_empty_reachable_set_is_all_coverage(monkeypatch):
    import participation as p
    monkeypatch.setattr(p, "m_verdict", toy_m_verdict)
    p_star, coverage, witnesses = compute_p_star([], toy_registry(), ("x", "y"))
    assert p_star == []
    assert coverage == ["x", "y"]
    assert witnesses == {}


def test_find_witness_does_not_stop_at_an_earlier_singleton_group(monkeypatch):
    """A fingerprint group of size 1 (no possible pair) must be skipped,
    not treated as a signal to stop searching entirely -- regression
    test for a continue-vs-break distinction: with a singleton group
    ordered before the real witness-bearing group, a `break` in place of
    `continue` would incorrectly return None."""
    import participation as p
    monkeypatch.setattr(p, "m_verdict", toy_m_verdict)
    reachable = [
        Toy(x=1, y=100, z="unique"),  # singleton fingerprint group when testing "x"
        Toy(x=3, y=1, z="a"),
        Toy(x=8, y=1, z="a"),
    ]
    witness = find_witness("x", reachable, toy_registry())
    assert witness is not None
    assert witness["verdict_a"] != witness["verdict_a_prime"]


def test_serialize_frozenset_field_becomes_a_sorted_list():
    from domain import StateTuple
    from participation import _serialize

    t = StateTuple(
        actor_role="agent-replenish", resource_class="consumables", order_value=1.0,
        day=1, workflow="W1", grant_id=None,
        consumed_grant_ids=frozenset({"g2", "g1", "g3"}), budget_remaining=1.0, frozen=False,
    )
    d = _serialize(t)
    assert d["consumed_grant_ids"] == ["g1", "g2", "g3"]
    assert isinstance(d["consumed_grant_ids"], list)


def test_serialize_empty_frozenset_becomes_empty_list():
    from domain import StateTuple
    from participation import _serialize

    t = StateTuple(
        actor_role="agent-replenish", resource_class="consumables", order_value=1.0,
        day=1, workflow="W1", grant_id=None,
        consumed_grant_ids=frozenset(), budget_remaining=1.0, frozen=False,
    )
    assert _serialize(t)["consumed_grant_ids"] == []
