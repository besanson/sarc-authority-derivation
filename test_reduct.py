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
"""Tests for reduct.py (Definitions 4-6, Proposition 1'/Negative
Proposition N's shared machinery) using small synthetic models --
independent of the real v2 model, so these catch bugs in the
core/reduct MACHINERY itself, not just reproduce checkers/reduct_check.py's
own output (already exercised against the real model there)."""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from reduct import compute_core, exact_reducts, sufficiency, verify_core_identity


@dataclass(frozen=True)
class Toy:
    x: int
    y: int
    z: str

    def with_property(self, name: str, value: Any) -> "Toy":
        return replace(self, **{name: value})


def toy_registry():
    return {"x_ge_2": lambda t: t.x >= 2}


TWO_STATE = [Toy(x=0, y=0, z="a"), Toy(x=1, y=1, z="a")]


def two_state_registry():
    return {"is_one": lambda t: bool(t.x)}


def test_sufficiency_holds_for_the_full_candidate_set():
    reachable = [Toy(x=1, y=1, z="a"), Toy(x=3, y=1, z="a"), Toy(x=1, y=2, z="b")]
    is_suff, cert = sufficiency(("x", "y", "z"), reachable, toy_registry())
    assert is_suff is True
    assert cert["partition_cell_count"] == 3
    assert cert["uniform_verdict_within_every_cell"] is True


def test_sufficiency_fails_for_an_uninformative_set_with_counterexample():
    reachable = [Toy(x=1, y=1, z="a"), Toy(x=3, y=9, z="a")]
    is_suff, cert = sufficiency(("z",), reachable, toy_registry())
    assert is_suff is False
    assert cert["verdict_a"] != cert["verdict_a_prime"]
    assert {cert["tuple_a"]["x"], cert["tuple_a_prime"]["x"]} == {1, 3}


def test_sufficiency_empty_set_on_verdict_uniform_reachable_set():
    reachable = [Toy(x=1, y=1, z="a"), Toy(x=1, y=2, z="a")]
    is_suff, cert = sufficiency((), reachable, toy_registry())
    assert is_suff is True
    assert cert["partition_cell_count"] == 1


def test_negative_proposition_n_two_state_counterexample():
    """The registered counterexample (prereg/fixtures/negative-proposition-
    n-counterexample.json), reproduced directly against reduct.py's own
    functions: empty core, not sufficient, two singleton reducts."""
    reducts, subsets_considered = exact_reducts(("x", "y"), TWO_STATE, two_state_registry())
    assert sorted(sorted(r) for r in reducts) == [["x"], ["y"]]
    assert subsets_considered == 3  # {}, {x}, {y} tested; {x,y} pruned as a superset of both

    core, _redundant, _witnesses = compute_core(TWO_STATE, two_state_registry(), ("x", "y"))
    assert core == []
    is_suff, counterexample = sufficiency(tuple(core), TWO_STATE, two_state_registry())
    assert is_suff is False
    assert counterexample["verdict_a"] != counterexample["verdict_a_prime"]


def test_exact_reducts_prunes_supersets_of_a_found_reduct():
    """A model where {x} alone is already sufficient: {x,y}, {x,z}, and
    {x,y,z} must never be tested (each a superset of the {x} reduct found
    at the smaller size) -- {y,z} is NOT a superset of {x} so it is still
    tested (and found insufficient), so subsets_considered is 5, not the
    full 2^3 = 8."""
    reachable = [Toy(x=1, y=1, z="a"), Toy(x=1, y=2, z="b"), Toy(x=9, y=1, z="a")]
    registry = {"x_ge_5": lambda t: t.x >= 5}
    reducts, subsets_considered = exact_reducts(("x", "y", "z"), reachable, registry)
    assert reducts == [frozenset({"x"})]
    # tested: {}, {x} (sufficient -> reduct), {y}, {z}, {y,z} -- {x,y}/{x,z}/{x,y,z} pruned
    assert subsets_considered == 5


def test_verify_core_identity_holds_on_two_state_counterexample():
    result = verify_core_identity(TWO_STATE, two_state_registry(), ("x", "y"))
    assert result["identity_holds"] is True
    assert result["core_via_definition_1"] == []
    assert result["core_subset_of_every_reduct"] is True
    assert sorted(sorted(r) for r in result["reducts"]) == [["x"], ["y"]]


def test_verify_core_identity_holds_when_core_is_the_unique_reduct():
    """x alone determines the verdict; the only reachable pair differing
    in exactly y, or exactly z, also happens to share a verdict, so
    neither participates -- core == the single reduct {x} exactly (not a
    proper subset of it), the boundary case a `<=` vs `<` mutant in the
    core-subset-of-every-reduct check would otherwise not be caught by
    (every other test here has a core that is a PROPER subset of its
    reduct(s), where `<=` and `<` happen to agree)."""
    reachable = [Toy(x=1, y=1, z="a"), Toy(x=9, y=1, z="a"), Toy(x=1, y=2, z="b")]
    registry = {"x_ge_5": lambda t: t.x >= 5}
    result = verify_core_identity(reachable, registry, ("x", "y", "z"))
    assert result["core_via_definition_1"] == ["x"]
    assert result["core_via_reduct_intersection"] == ["x"]
    assert result["identity_holds"] is True
    assert result["core_subset_of_every_reduct"] is True
    assert result["reducts"] == [["x"]]
    # tested: {}, {x} (reduct), {y}, {z}, {y,z} (not a superset of {x}, so not pruned) -- {x,y}/{x,z}/{x,y,z} pruned
    assert result["subsets_considered"] == 5
