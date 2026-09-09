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


# -- v5.3: combinatorial-hardness scaling (prereg/v5.3-combinatorial-hardness-scaling.md) --
# Toy-scale (small k, d_flags, padding_depth) so exhaustive cross-check
# genuinely completes in well under a second -- confirms the same
# hand-derivation registered there (S and F the only two reducts, S the
# unique minimum, family size 200*k before / 25*k after pruning at the
# REGISTERED d_flags=25/padding_depth=8) directly, before trusting the
# same construction at the registered (k, n) sizes, the same discipline
# `make_multi_reduct_family`'s own tests above already use.
from discernibility_scaling_benchmark import (
    combinatorial_hardness_costs,
    combinatorial_hardness_registry,
    exhaustive_with_budget,
    make_combinatorial_hardness_family,
    run_hardness_family,
)


def test_combinatorial_hardness_family_size_matches_1_plus_k_times_d_times_j():
    for k, d, j in ((2, 4, 3), (3, 5, 2), (1, 3, 4)):
        _, reachable, _, _ = make_combinatorial_hardness_family(k, k + d, d_flags=d, padding_depth=j)
        assert len(reachable) == 1 + k * d * j


def test_combinatorial_hardness_signal_set_is_sufficient_and_minimal():
    names, reachable, signal_names, _flag_names = make_combinatorial_hardness_family(3, 8, d_flags=5, padding_depth=2)
    registry = combinatorial_hardness_registry(signal_names)

    s_sufficient, _ = sufficiency(tuple(signal_names), reachable, registry)
    assert s_sufficient is True

    for i in range(len(signal_names)):
        proper_subset = tuple(p for idx, p in enumerate(signal_names) if idx != i)
        subset_sufficient, _ = sufficiency(proper_subset, reachable, registry)
        assert subset_sufficient is False


def test_combinatorial_hardness_exactly_two_reducts_S_and_F():
    k, d, j = 2, 4, 3
    n = k + d
    names, reachable, signal_names, flag_names = make_combinatorial_hardness_family(k, n, d_flags=d, padding_depth=j)
    registry = combinatorial_hardness_registry(signal_names)

    reducts, _subsets_considered = exact_reducts(names, reachable, registry)
    reducts_sorted = sorted(sorted(r) for r in reducts)
    assert reducts_sorted == sorted([sorted(signal_names), sorted(flag_names)])


def test_combinatorial_hardness_family_size_before_and_after_pruning():
    k, d, j = 3, 5, 2
    n = k + d
    names, reachable, signal_names, _flag_names = make_combinatorial_hardness_family(k, n, d_flags=d, padding_depth=j)
    registry = combinatorial_hardness_registry(signal_names)

    family_before = build_discernibility_family(names, reachable, registry)
    family_after = remove_redundant_supersets(family_before)
    assert len(family_before) == k * d * j
    assert len(family_after) == k * d


def test_combinatorial_hardness_costs_signal_cheaper_than_everything_else():
    k, d, j = 2, 4, 2
    n = k + d
    names, _reachable, signal_names, flag_names = make_combinatorial_hardness_family(k, n, d_flags=d, padding_depth=j)
    costs = combinatorial_hardness_costs(names, signal_names)
    assert all(costs[p] == 1.0 for p in signal_names)
    assert all(costs[p] == 100.0 for p in flag_names)


def test_exhaustive_with_budget_reports_feasible_on_a_tiny_family():
    k, d, j = 1, 3, 2
    n = k + d
    names, reachable, signal_names, _flag_names = make_combinatorial_hardness_family(k, n, d_flags=d, padding_depth=j)
    registry = combinatorial_hardness_registry(signal_names)

    result = exhaustive_with_budget(names, reachable, registry, budget_seconds=30)
    assert result["feasible"] is True
    assert sorted(sorted(r) for r in result["reducts"]) == [["f_1", "f_2", "f_3"], ["p_1"]]


def test_exhaustive_with_budget_reports_infeasible_when_the_budget_is_too_small():
    # A deliberately tiny budget (a fraction of a second) on a family
    # sized to take meaningfully longer than that to exhaust -- proves
    # the timeout path itself actually fires and reports honestly,
    # not just the feasible path.
    k, d, j = 3, 8, 3
    n = k + d
    names, reachable, signal_names, _flag_names = make_combinatorial_hardness_family(k, n, d_flags=d, padding_depth=j)
    registry = combinatorial_hardness_registry(signal_names)

    result = exhaustive_with_budget(names, reachable, registry, budget_seconds=0)
    assert result["feasible"] is False
    assert result["budget_seconds"] == 0


def test_run_hardness_family_reports_the_predicted_exact_answers_on_a_toy_scale():
    result = run_hardness_family("toy_test", k=2, n=6, d_flags=4, padding_depth=2, budget_seconds=10)

    assert result["reachable_tuple_count"] == 1 + 2 * 4 * 2
    assert result["discernibility_family_size_before_superset_removal"] == 2 * 4 * 2
    assert result["discernibility_family_size_after_superset_removal"] == 2 * 4
    assert result["exhaustive_cross_check"]["feasible"] is True
    assert result["number_of_reducts"] == {"source": "exhaustive", "count": 2}
    assert result["exhaustive_cross_check"]["agrees_with_hand_proof"] is True

    assert result["backends"]["cardinality_maxsat"]["exact"] is True
    assert result["backends"]["cardinality_maxsat"]["contract"] == ["p_1", "p_2"]
    assert result["backends"]["cardinality_maxsat"]["exhaustive_cross_check_agrees"] is True

    assert result["backends"]["weighted_maxsat_cost"]["exact"] is True
    assert result["backends"]["weighted_maxsat_cost"]["contract"] == ["p_1", "p_2"]
    assert result["backends"]["weighted_maxsat_cost"]["exhaustive_cross_check_agrees"] is True

    assert result["backends"]["sat_any_sufficient"]["is_sufficient"] is True
    assert result["backends"]["sat_any_sufficient"]["matches"] in ("S", "F", "neither")

    assert result["maxsat_advantage"]["cardinality_advantage"] >= 0
