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
"""Tests for costs_v7.py -- every expected cost below is hardcoded from
`prereg/v7-cost-sensitive-contracts.md`'s own "Predicted outcome" table
(hand-computed there before this module existed), not re-derived from
the formula under test, so a mutation to a weight, a component value,
or the formula's shape (e.g. `+` -> `-`, a dropped term) is caught
against the registered numbers themselves, not merely against a second
copy of the same code."""
from __future__ import annotations

import pytest

from costs_v7 import ALPHA, BETA, GAMMA, DELTA, LATENCY_NORMALIZATION_MS, cost, normalized_latency, observation_costs_v7
from domain_v4 import CANDIDATE_PROPERTIES_V4

EXPECTED_COST_BY_PROPERTY = {
    "branch": 0.225,
    "repository": 0.225,
    "actor_identity": 0.325,
    "delegated_role": 0.325,
    "operation": 0.044,
    "environment": 1.455,
    "deployment_window": 1.430,
    "approval_token": 2.225,
    "resource_owner": 1.740,
    "data_classification": 1.340,
}


def test_registered_weights_match_prereg():
    assert (ALPHA, BETA, GAMMA, DELTA) == (1.0, 2.0, 1.5, 3.0)
    assert LATENCY_NORMALIZATION_MS == 250.0


def test_normalized_latency_below_at_and_above_the_cap():
    assert normalized_latency(0) == 0.0
    assert normalized_latency(5) == pytest.approx(0.02)
    assert normalized_latency(125) == pytest.approx(0.5)
    assert normalized_latency(250) == pytest.approx(1.0)
    # above the 250ms normalization point: clamped at 1.0, not left > 1.0.
    assert normalized_latency(500) == pytest.approx(1.0)


@pytest.mark.parametrize("property_name,expected", sorted(EXPECTED_COST_BY_PROPERTY.items()))
def test_cost_matches_prereg_hand_computation(property_name, expected):
    assert cost(property_name) == pytest.approx(expected, abs=1e-9)


def test_observation_costs_v7_covers_exactly_the_v4_candidate_properties():
    costs = observation_costs_v7()
    assert set(costs) == set(CANDIDATE_PROPERTIES_V4)


def test_every_registered_cost_is_strictly_positive():
    # find_minimum_cost_contract (synthesis.py) requires this to make its
    # own result a reduct, not merely sufficient -- checked here at the
    # source, not only where synthesis.py itself raises on a violation.
    for name, value in observation_costs_v7().items():
        assert value > 0, f"{name} has non-positive cost {value}"


def test_core_and_reduct_costs_match_prereg_predicted_outcome():
    costs = observation_costs_v7()
    core = ["approval_token", "data_classification", "delegated_role", "operation", "repository", "resource_owner"]
    core_cost = sum(costs[p] for p in core)
    assert core_cost == pytest.approx(5.899, abs=1e-9)
    assert core_cost + costs["branch"] == pytest.approx(6.124, abs=1e-9)
    assert core_cost + costs["environment"] == pytest.approx(7.354, abs=1e-9)
