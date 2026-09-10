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
"""Tests for costs_v8.py -- every expected cost below is hardcoded from
`prereg/v8-large-realistic-domain.md`'s own seven-tier cost table
(computed independently by direct application of the same formula
`costs_v7.py`'s own tests already exercise), not re-derived from the
module under test."""
from __future__ import annotations

import pytest

from costs_v8 import ALPHA, BETA, GAMMA, DELTA, LATENCY_NORMALIZATION_MS, cost, normalized_latency, observation_costs_v8
from domain_v8 import CANDIDATE_PROPERTIES_V8

# cost(local-identity) = 1*0.02 + 2*0.05 + 1.5*0.05 + 3*0.01 = 0.02+0.10+0.075+0.03 = 0.225
# cost(local-request) = 1*0.004 + 2*0.02 + 1.5*0.00 + 3*0.00 = 0.004+0.04 = 0.044
# cost(local-resource-metadata) = same components as local-identity = 0.225
# cost(remote-governance-lookup) = 1*1.0 + 2*0.20 + 1.5*0.15 + 3*0.20 = 1.0+0.40+0.225+0.60 = 2.225
# cost(remote-iam-cmdb-lookup) = 1*0.6 + 2*0.30 + 1.5*0.20 + 3*0.08 = 0.6+0.60+0.30+0.24 = 1.74
# cost(remote-deployment-control-lookup) = 1*0.48 + 2*0.15 + 1.5*0.35 + 3*0.05 = 0.48+0.30+0.525+0.15 = 1.455
# cost(remote-security-telemetry-lookup) = 1*0.8 + 2*0.25 + 1.5*0.30 + 3*0.10 = 0.8+0.50+0.45+0.30 = 2.05
EXPECTED_TIER_COST = {
    "local-identity": 0.225,
    "local-request": 0.044,
    "local-resource-metadata": 0.225,
    "remote-governance-lookup": 2.225,
    "remote-iam-cmdb-lookup": 1.74,
    "remote-deployment-control-lookup": 1.455,
    "remote-security-telemetry-lookup": 2.05,
}

EXPECTED_PROPERTY_TIER = {
    "actor_identity": "local-identity",
    "operation": "local-request",
    "repository": "local-resource-metadata",
    "approval_token": "remote-governance-lookup",
    "resource_owner": "remote-iam-cmdb-lookup",
    "resource_environment": "remote-deployment-control-lookup",
    "audit_logging_enabled": "remote-security-telemetry-lookup",
}


def test_registered_weights_match_prereg():
    assert (ALPHA, BETA, GAMMA, DELTA) == (1.0, 2.0, 1.5, 3.0)
    assert LATENCY_NORMALIZATION_MS == 250.0


def test_normalized_latency_below_at_and_above_the_cap():
    # No registered v8 tier's own raw latency exceeds 250ms, so this
    # boundary must be checked directly, not only via cost()/the tiers.
    assert normalized_latency(0) == 0.0
    assert normalized_latency(125) == pytest.approx(0.5)
    assert normalized_latency(250) == pytest.approx(1.0)
    assert normalized_latency(500) == pytest.approx(1.0)


@pytest.mark.parametrize("property_name,tier", sorted(EXPECTED_PROPERTY_TIER.items()))
def test_representative_property_cost_matches_its_tier(property_name, tier):
    assert cost(property_name) == pytest.approx(EXPECTED_TIER_COST[tier], abs=1e-9)


def test_observation_costs_v8_covers_exactly_the_v8_candidate_properties():
    costs = observation_costs_v8()
    assert set(costs) == set(CANDIDATE_PROPERTIES_V8)


def test_every_registered_cost_is_strictly_positive():
    for name, value in observation_costs_v8().items():
        assert value > 0, f"{name} has non-positive cost {value}"


def test_every_property_in_exactly_one_tier_and_every_tier_used():
    from costs_v8 import COST_TIERS_V8, PROPERTY_TIER_V8
    used_tiers = set(PROPERTY_TIER_V8.values())
    assert used_tiers == set(COST_TIERS_V8)
