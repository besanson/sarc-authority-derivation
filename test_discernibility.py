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
"""Tests for discernibility.py -- small synthetic models (mirroring
test_reduct.py's own Toy/TWO_STATE fixtures), independent of the real
models `checkers/discernibility_check.py` exhaustively cross-checks."""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from discernibility import build_discernibility_family, counterexample_for, remove_redundant_supersets, verify_contract


@dataclass(frozen=True)
class Toy:
    x: int
    y: int
    z: str

    def with_property(self, name: str, value: Any) -> "Toy":
        return replace(self, **{name: value})


TWO_STATE = [Toy(x=0, y=0, z="a"), Toy(x=1, y=1, z="a")]


def two_state_registry():
    return {"is_one": lambda t: bool(t.x)}


def test_build_discernibility_family_two_state_counterexample():
    """Registered counterexample (Negative Proposition N's own fixture):
    the only cross-verdict pair differs in BOTH x and y, so the family
    is exactly one set, {x, y} -- neither {x} nor {y} alone hits it,
    matching the empty core."""
    family = build_discernibility_family(("x", "y"), TWO_STATE, two_state_registry())
    assert family == [frozenset({"x", "y"})]

    is_suff_empty, unhit = verify_contract(frozenset(), family)
    assert is_suff_empty is False
    assert unhit == frozenset({"x", "y"})

    is_suff_x, _ = verify_contract(frozenset({"x"}), family)
    assert is_suff_x is True
    is_suff_y, _ = verify_contract(frozenset({"y"}), family)
    assert is_suff_y is True


def test_remove_redundant_supersets_drops_supersets_of_a_smaller_set():
    family = [frozenset({"x"}), frozenset({"x", "y"}), frozenset({"y", "z"}), frozenset({"x", "y", "z"})]
    reduced = remove_redundant_supersets(family)
    # {x} subsumes {x,y} and {x,y,z}; {y,z} is not a superset of {x}, so it survives.
    assert sorted(reduced, key=sorted) == sorted([frozenset({"x"}), frozenset({"y", "z"})], key=sorted)


def test_remove_redundant_supersets_keeps_incomparable_sets():
    family = [frozenset({"x"}), frozenset({"y"})]
    assert sorted(remove_redundant_supersets(family), key=sorted) == sorted(family, key=sorted)


def test_remove_redundant_supersets_requires_size_order_not_input_or_default_order():
    """A superset given BEFORE its own subset in the input list must
    still be recognized as redundant: {a,b} appears first here, but
    {a} (given third) subsumes it. Python's own default frozenset sort
    (subset comparison, not size) does NOT reliably order this family
    the same way size-sort does -- verified directly, not assumed --
    so this input distinguishes a `sorted(family, key=len)` -> `sorted
    (family)` mutation, which a same-order or already-size-ordered
    input would not."""
    family = [frozenset({"a", "b"}), frozenset({"c"}), frozenset({"a"})]
    assert sorted(remove_redundant_supersets(family), key=sorted) == sorted(
        [frozenset({"c"}), frozenset({"a"})], key=sorted
    )


def test_remove_redundant_supersets_drops_an_exact_duplicate():
    """Two identical sets in the family: the second is redundant (a set
    is trivially a subset of an equal one) and must not survive as a
    separate entry -- distinguishes `existing <= candidate` (correct)
    from a `existing < candidate` mutant, which only differ when the two
    sides are equal."""
    family = [frozenset({"x"}), frozenset({"x"})]
    assert remove_redundant_supersets(family) == [frozenset({"x"})]


def test_verify_contract_hits_every_set_returns_true():
    family = [frozenset({"x"}), frozenset({"y", "z"})]
    is_suff, unhit = verify_contract(frozenset({"x", "y"}), family)
    assert is_suff is True
    assert unhit is None


def test_verify_contract_misses_one_set_returns_it():
    family = [frozenset({"x"}), frozenset({"y", "z"})]
    is_suff, unhit = verify_contract(frozenset({"x"}), family)
    assert is_suff is False
    assert unhit == frozenset({"y", "z"})


def test_counterexample_for_matches_sufficiency_directly():
    ce = counterexample_for(frozenset(), TWO_STATE, two_state_registry())
    assert ce is not None
    assert ce["verdict_a"] != ce["verdict_a_prime"]

    assert counterexample_for(frozenset({"x"}), TWO_STATE, two_state_registry()) is None
