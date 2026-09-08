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
"""Tests for src/authority_compiler (Milestone E1) -- confirms the
packaged entry point returns exactly what its three wrapped functions
(reduct.compute_core, reduct.sufficiency, synthesis.
find_minimum_cardinality_contract) return when called directly with the
same arguments, on small synthetic fixtures shared with test_reduct.py
for direct comparability -- deliberately no real-domain integration test
here: this file feeds mutation testing (pyproject.toml), and a real
domain's discernibility-family build (tens of seconds, benchmarks.py's
own Makefile comment) run per mutant would make `make mutate` prohibitive,
the same reason test_reduct.py/test_synthesis.py stay synthetic-only and
real-domain checks live separately in checkers/*.py instead."""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from reduct import compute_core, sufficiency
from synthesis import find_minimum_cardinality_contract

from authority_compiler import AuthorityContract, derive_authority_contract


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


def test_derive_authority_contract_matches_the_three_wrapped_functions_directly():
    """x alone determines the verdict (test_reduct.py's own unique-reduct
    fixture): core == {x}, sufficient, minimum-cardinality contract ==
    {x} too -- and every field matches calling the three wrapped
    functions directly with the same arguments, not just a plausible-
    looking value."""
    reachable = [Toy(x=1, y=1, z="a"), Toy(x=9, y=1, z="a"), Toy(x=1, y=2, z="b")]
    registry = {"x_ge_5": lambda t: t.x >= 5}
    candidate_properties = ("x", "y", "z")

    result = derive_authority_contract(candidate_properties, reachable, registry)
    assert isinstance(result, AuthorityContract)

    expected_core, expected_coverage, _ = compute_core(reachable, registry, candidate_properties)
    expected_sufficient, _ = sufficiency(tuple(sorted(expected_core)), reachable, registry)
    expected_min_card = find_minimum_cardinality_contract(candidate_properties, reachable, registry)

    assert result.core == frozenset(expected_core) == frozenset({"x"})
    assert result.coverage_list == frozenset(expected_coverage) == frozenset({"y", "z"})
    assert result.core_is_sufficient == expected_sufficient is True
    assert result.minimum_cardinality_contract == expected_min_card == frozenset({"x"})
    assert result.candidate_property_count == 3
    assert result.reachable_tuple_count == 3


def test_derive_authority_contract_reports_an_insufficient_empty_core_honestly():
    """Negative Proposition N's own registered counterexample
    (test_reduct.py's TWO_STATE): the core is EMPTY and NOT sufficient --
    `derive_authority_contract` must report core_is_sufficient=False, not
    silently treat the empty core as though it were a valid answer, and
    minimum_cardinality_contract must still be a genuine, nonempty,
    sufficient reduct (the packaged entry point's own honest fallback
    when the core alone does not suffice)."""
    registry = two_state_registry()
    candidate_properties = ("x", "y")

    result = derive_authority_contract(candidate_properties, TWO_STATE, registry)

    assert result.core == frozenset()
    assert result.coverage_list == frozenset({"x", "y"})
    assert result.core_is_sufficient is False
    assert result.minimum_cardinality_contract in (frozenset({"x"}), frozenset({"y"}))
    is_suff, _ = sufficiency(tuple(sorted(result.minimum_cardinality_contract)), TWO_STATE, registry)
    assert is_suff is True
