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
"""Tests for synthesis.py (PySAT SAT/MaxSAT backends) -- small synthetic
models, independent of the real models checkers/synthesis_exactness_
check.py exhaustively cross-checks."""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

import pytest

from reduct import sufficiency
from synthesis import find_any_sufficient_contract, find_minimum_cardinality_contract, find_minimum_cost_contract


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


def test_find_any_sufficient_contract_is_actually_sufficient():
    contract = find_any_sufficient_contract(("x", "y"), TWO_STATE, two_state_registry())
    is_suff, _ = sufficiency(tuple(sorted(contract)), TWO_STATE, two_state_registry())
    assert is_suff is True


def test_find_minimum_cardinality_contract_is_a_singleton_reduct():
    contract = find_minimum_cardinality_contract(("x", "y"), TWO_STATE, two_state_registry())
    assert len(contract) == 1
    assert contract in ({"x"}, {"y"})
    is_suff, _ = sufficiency(tuple(sorted(contract)), TWO_STATE, two_state_registry())
    assert is_suff is True


def test_find_minimum_cost_contract_picks_the_cheaper_reduct():
    cheap_y = find_minimum_cost_contract(("x", "y"), TWO_STATE, two_state_registry(), {"x": 5.0, "y": 1.0})
    assert cheap_y == frozenset({"y"})
    cheap_x = find_minimum_cost_contract(("x", "y"), TWO_STATE, two_state_registry(), {"x": 1.0, "y": 5.0})
    assert cheap_x == frozenset({"x"})


def test_find_minimum_cost_contract_rejects_non_positive_costs():
    with pytest.raises(ValueError, match="strictly positive"):
        find_minimum_cost_contract(("x", "y"), TWO_STATE, two_state_registry(), {"x": 0.0, "y": 1.0})
    with pytest.raises(ValueError, match="strictly positive"):
        find_minimum_cost_contract(("x", "y"), TWO_STATE, two_state_registry(), {"x": -1.0, "y": 1.0})


def test_find_minimum_cost_contract_requires_every_candidate_costed():
    with pytest.raises(ValueError, match="no declared cost"):
        find_minimum_cost_contract(("x", "y"), TWO_STATE, two_state_registry(), {"x": 1.0})


def test_backends_agree_on_a_three_property_model_with_one_reduct():
    """x alone determines the verdict (x_ge_5); y, z are both redundant
    -- every backend must return exactly {x}, the unique reduct."""
    reachable = [Toy(x=1, y=1, z="a"), Toy(x=9, y=1, z="a"), Toy(x=1, y=2, z="b")]
    registry = {"x_ge_5": lambda t: t.x >= 5}
    candidate_properties = ("x", "y", "z")

    any_contract = find_any_sufficient_contract(candidate_properties, reachable, registry)
    is_suff, _ = sufficiency(tuple(sorted(any_contract)), reachable, registry)
    assert is_suff is True

    min_card = find_minimum_cardinality_contract(candidate_properties, reachable, registry)
    assert min_card == frozenset({"x"})

    min_cost = find_minimum_cost_contract(candidate_properties, reachable, registry, {"x": 1.0, "y": 1.0, "z": 1.0})
    assert min_cost == frozenset({"x"})
