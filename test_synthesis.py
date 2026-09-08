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
from synthesis import (
    contract_change_delta,
    find_any_sufficient_contract,
    find_minimum_cardinality_contract,
    find_minimum_cost_contract,
)


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


# -- contract_change_delta: same x/y/z fixture as the backend-agreement test above --

_DELTA_RECHABLE = [Toy(x=1, y=1, z="a"), Toy(x=9, y=1, z="a"), Toy(x=1, y=2, z="b")]
_DELTA_REGISTRY = {"x_ge_5": lambda t: t.x >= 5}
_DELTA_CANDIDATES = ("x", "y", "z")
_HARMLESS_NEW_TUPLE = Toy(x=2, y=9, z="q")  # x_ge_5 False, collides with no differently-verdicted x group


def test_contract_change_delta_reports_no_change_when_still_sufficient():
    """A new tuple that does not collide with any existing (x-group,
    verdict) pairing leaves {x} sufficient -- no resynthesis needed,
    and the reported contract is the untouched base_contract."""
    base_contract = frozenset({"x"})
    delta = contract_change_delta(
        base_contract, _DELTA_CANDIDATES, _DELTA_RECHABLE, [_HARMLESS_NEW_TUPLE], _DELTA_REGISTRY
    )
    assert delta["was_still_sufficient"] is True
    assert delta["updated_contract"] == ["x"]
    assert delta["incremental_is_sufficient"] is True
    assert delta["full_recomputation_cardinality_gap"] == 0


def test_contract_change_delta_extends_a_broken_contract_and_keeps_the_pinned_property():
    """The new tuple shares x=1, y=1 with an existing tuple but a NEW
    predicate (z_is_dangerous) distinguishes them on z -- {x} alone can
    no longer separate the two, breaking sufficiency; the incremental
    update must keep x (pinned, never dropped) and add exactly z."""
    base_contract = frozenset({"x"})
    new_tuples = [Toy(x=1, y=1, z="c")]
    combined_registry = {**_DELTA_REGISTRY, "z_is_dangerous": lambda t: t.z == "c"}

    delta = contract_change_delta(base_contract, _DELTA_CANDIDATES, _DELTA_RECHABLE, new_tuples, combined_registry)
    assert delta["was_still_sufficient"] is False
    assert delta["updated_contract"] == ["x", "z"]
    assert delta["incremental_is_sufficient"] is True
    assert delta["full_recomputation_contract"] == ["x", "z"]
    assert delta["full_recomputation_cardinality_gap"] == 0


def test_contract_change_delta_pins_a_non_minimal_base_contract_and_reports_a_nonzero_gap():
    """base_contract need only be KNOWN sufficient, not itself minimum
    cardinality -- {x, y} is sufficient on the old reachable set (a
    strict superset of the already-sufficient {x}). The harmless new
    tuple keeps it sufficient, so updated_contract is base_contract
    verbatim (y kept despite being redundant), while independent full
    recomputation on the combined set finds the true minimum {x} alone
    -- the honest, nonzero price of incrementality this function
    registers as `full_recomputation_cardinality_gap`."""
    base_contract = frozenset({"x", "y"})
    delta = contract_change_delta(
        base_contract, _DELTA_CANDIDATES, _DELTA_RECHABLE, [_HARMLESS_NEW_TUPLE], _DELTA_REGISTRY
    )
    assert delta["was_still_sufficient"] is True
    assert delta["updated_contract"] == ["x", "y"]
    assert delta["full_recomputation_contract"] == ["x"]
    assert delta["full_recomputation_cardinality_gap"] == 1


def test_contract_change_delta_reports_every_declared_field():
    """The other tests above each exercise was_still_sufficient/
    updated_contract/incremental_is_sufficient/full_recomputation_
    contract/full_recomputation_cardinality_gap; base_contract,
    new_tuple_count, updated_contract_cardinality, and full_
    recomputation_cardinality have no assertion anywhere else -- checked
    directly here, once, rather than left as unread fields of the
    returned dict."""
    base_contract = frozenset({"x"})
    new_tuples = [Toy(x=1, y=1, z="c")]
    combined_registry = {**_DELTA_REGISTRY, "z_is_dangerous": lambda t: t.z == "c"}

    delta = contract_change_delta(base_contract, _DELTA_CANDIDATES, _DELTA_RECHABLE, new_tuples, combined_registry)
    assert delta["base_contract"] == ["x"]
    assert delta["new_tuple_count"] == 1
    assert delta["updated_contract_cardinality"] == len(delta["updated_contract"]) == 2
    assert delta["full_recomputation_cardinality"] == len(delta["full_recomputation_contract"]) == 2


def test_contract_change_delta_picks_a_minimum_cardinality_extension_on_a_genuine_two_way_tie():
    """A discernibility clause offering an unabsorbed choice between two
    DIFFERENT non-base properties (a colliding pair differing in BOTH y
    and z, with no other clause a subset of {y, z} -- so `discernibility.
    remove_redundant_supersets` cannot collapse this one down to a
    single-property clause the way the fixtures above's {x}-vs-{x,z}
    shape does): it is specifically the soft "prefer excluded" clause on
    EVERY non-base property that makes RC2 resolve this tie at minimum
    cost rather than arbitrarily. Verified directly (not assumed) that
    this installed PySAT/RC2 deterministically resolves this exact tie
    to {x, z}, repeatably, through `contract_change_delta` itself."""
    reachable = [Toy(x=1, y=1, z="p"), Toy(x=9, y=1, z="p")]
    new_tuples = [Toy(x=1, y=2, z="q")]  # collides with the first tuple on x; differs in BOTH y and z
    registry = {"x_ge_5": lambda t: t.x >= 5, "yz_marker": lambda t: (t.y, t.z) == (1, "p")}
    base_contract = frozenset({"x"})

    delta = contract_change_delta(base_contract, _DELTA_CANDIDATES, reachable, new_tuples, registry)
    assert delta["updated_contract"] == ["x", "z"]
