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
"""Tests for benchmarks.py (Milestone D5, prereg/v5-synthesis.md) --
the two registered constructions' own hand-derived, brute-force-verified
answers (module docstrings there and in the prereg), checked directly
against the actual functions, not just re-run and eyeballed."""
from __future__ import annotations

from reduct import exact_reducts
from synthesis import find_minimum_cardinality_contract, find_minimum_cost_contract

from benchmarks import (
    contract_change_delta,
    declared_cost,
    make_planted_family,
    make_xor_bijection_domain,
    planted_verdict_registry,
    run_contract_change_demo,
)


def test_planted_family_produces_exactly_the_signal_set_reduct_at_n_10():
    names, tuples = make_planted_family(10)
    registry = planted_verdict_registry()
    reducts, _ = exact_reducts(names, tuples, registry)
    assert len(reducts) == 1
    assert set(reducts[0]) == {"p_1", "p_2", "p_3", "p_4", "p_5"}


def test_planted_family_reachable_size_is_independent_of_n():
    for n in (10, 30, 100):
        _, tuples = make_planted_family(n)
        assert len(tuples) == 6  # k + 1 = 5 + 1, regardless of n


def test_planted_family_min_cardinality_backend_matches_construction_at_large_n():
    """n=100 is not exhaustible (2^100), so this checks the SAT backend
    against the construction's OWN known answer, not against
    reduct.exact_reducts() -- exactly what the prereg itself registers
    as the only available cross-check past n=10."""
    names, tuples = make_planted_family(100)
    registry = planted_verdict_registry()
    contract = find_minimum_cardinality_contract(names, tuples, registry)
    assert set(contract) == {"p_1", "p_2", "p_3", "p_4", "p_5"}


def test_xor_bijection_domain_has_the_two_registered_reducts():
    props, tuples, registry, costs = make_xor_bijection_domain()
    reducts, _ = exact_reducts(props, tuples, registry)
    assert sorted(sorted(r) for r in reducts) == [["a"], ["b1", "b2"]]
    assert costs["a"] > costs["b1"] + costs["b2"]


def test_xor_bijection_min_cardinality_and_min_cost_disagree():
    props, tuples, registry, costs = make_xor_bijection_domain()
    min_card = find_minimum_cardinality_contract(props, tuples, registry)
    min_cost = find_minimum_cost_contract(props, tuples, registry, costs)
    assert min_card == frozenset({"a"})
    assert min_cost == frozenset({"b1", "b2"})


def test_declared_cost_sums_the_four_sub_factors():
    assert declared_cost({"latency": 0.1, "privacy": 0.2, "staleness": 0.3, "failure_probability": 0.4}) == 1.0


def test_declared_cost_floors_a_zero_total():
    assert declared_cost({"latency": 0, "privacy": 0, "staleness": 0, "failure_probability": 0}) > 0


def test_contract_change_demo_shows_a_genuine_break_and_a_matching_extension():
    delta = run_contract_change_demo()
    assert delta["was_still_sufficient"] is False
    assert delta["updated_contract"] == ["x", "z"]
    assert delta["incremental_is_sufficient"] is True
    assert delta["full_recomputation_cardinality_gap"] == 0
