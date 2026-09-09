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
"""Tests for discernibility_scaling_benchmark.py (prereg/v5.1-
discernibility-scaling.md) -- confirms the hand-derivation registered
there (two singleton reducts, empty core, discernibility family size 1
after superset removal) directly, on a small q before trusting the same
construction at the registered q=3/4/5 sizes, the same discipline
Experiment 1's own test suite already used for its n=10 cross-check."""
from __future__ import annotations

from discernibility import build_discernibility_family, remove_redundant_supersets
from reduct import compute_core, exact_reducts, sufficiency
from discernibility_scaling_benchmark import (
    make_multi_reduct_family,
    multi_reduct_costs,
    multi_reduct_registry,
    run_family,
)


def test_family_size_matches_1_plus_r_to_the_q():
    for q in (1, 2, 3):
        _, tuples = make_multi_reduct_family(q, r=10)
        assert len(tuples) == 1 + 10 ** q


def test_both_twins_are_independently_sufficient_and_the_empty_set_is_not():
    names, tuples = make_multi_reduct_family(1)
    registry = multi_reduct_registry()

    empty_sufficient, _ = sufficiency((), tuples, registry)
    assert empty_sufficient is False

    a_sufficient, _ = sufficiency(("twin_a",), tuples, registry)
    assert a_sufficient is True

    b_sufficient, _ = sufficiency(("twin_b",), tuples, registry)
    assert b_sufficient is True


def test_core_is_empty_and_there_are_exactly_two_singleton_reducts():
    names, tuples = make_multi_reduct_family(1)
    registry = multi_reduct_registry()

    core, redundant, _witnesses = compute_core(tuples, registry, names)
    assert core == []

    reducts, _subsets_considered = exact_reducts(names, tuples, registry)
    assert sorted(sorted(r) for r in reducts) == [["twin_a"], ["twin_b"]]


def test_discernibility_family_size_after_superset_removal_is_exactly_one():
    for q in (1, 2, 3):
        names, tuples = make_multi_reduct_family(q)
        registry = multi_reduct_registry()
        family = remove_redundant_supersets(build_discernibility_family(names, tuples, registry))
        assert family == [frozenset({"twin_a", "twin_b"})]


def test_run_family_reports_the_predicted_exact_answers_on_a_small_q():
    names, tuples = make_multi_reduct_family(2)
    registry = multi_reduct_registry()
    costs = multi_reduct_costs(names)

    result = run_family("multi_reduct_q2_test", names, tuples, registry, costs)

    assert result["reachable_tuple_count"] == 1 + 10 ** 2
    assert result["discernibility_family_size_after_superset_removal"] == 1
    assert sorted(sorted(r) for r in result["exhaustive_cross_check"]["reducts"]) == [["twin_a"], ["twin_b"]]
    assert result["exhaustive_cross_check"]["minimum_cardinality"] == 1
    assert result["exhaustive_cross_check"]["minimum_cost"] == 1.0  # cost(twin_a) = 1.0, the cheaper singleton

    assert result["backends"]["sat_any_sufficient"]["is_sufficient"] is True
    assert result["backends"]["sat_any_sufficient"]["matches_a_known_minimal_reduct"] is True

    assert result["backends"]["cardinality_maxsat"]["exact"] is True
    assert len(result["backends"]["cardinality_maxsat"]["contract"]) == 1

    assert result["backends"]["weighted_maxsat_cost"]["exact"] is True
    assert result["backends"]["weighted_maxsat_cost"]["contract"] == ["twin_a"]
    assert result["backends"]["weighted_maxsat_cost"]["contract_cost"] == 1.0


def test_multi_reduct_costs_prices_twin_a_cheaper_than_twin_b():
    names, _ = make_multi_reduct_family(2)
    costs = multi_reduct_costs(names)
    assert costs["twin_a"] < costs["twin_b"]
    assert all(costs[p] > 0 for p in names)
