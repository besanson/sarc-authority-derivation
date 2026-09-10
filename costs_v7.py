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

"""
Package C (`prereg/v7-cost-sensitive-contracts.md`, tag `prereg-p5-v7`):
the registered per-property observation-cost model for `domain_v4.py`'s
ten candidate properties. Every raw component value, the four weights,
and the formula below are transcribed unchanged from the prereg's own
tables -- this module does not re-decide anything the prereg already
fixed (its own "Registration discipline" section), and no value here may
be adjusted after `checkers/ch_b2_check.py` has been run once."""
from __future__ import annotations

from typing import Dict, NamedTuple

ALPHA = 1.0   # normalized_latency weight
BETA = 2.0    # privacy_exposure weight
GAMMA = 1.5   # staleness_risk weight
DELTA = 3.0   # lookup_failure_probability weight

LATENCY_NORMALIZATION_MS = 250.0


class CostComponentsV7(NamedTuple):
    raw_latency_ms: float
    privacy_exposure: float
    staleness_risk: float
    lookup_failure_probability: float
    source_class: str


# Registered per-property values (prereg's own table, transcribed
# unchanged): (latency_ms, privacy_exposure, staleness_risk,
# lookup_failure_probability, source_class).
COST_COMPONENTS_V7: Dict[str, CostComponentsV7] = {
    "branch": CostComponentsV7(5, 0.05, 0.05, 0.01, "local repository metadata"),
    "repository": CostComponentsV7(5, 0.05, 0.05, 0.01, "local repository metadata"),
    "actor_identity": CostComponentsV7(5, 0.10, 0.05, 0.01, "local identity context"),
    "delegated_role": CostComponentsV7(5, 0.10, 0.05, 0.01, "local identity context"),
    "operation": CostComponentsV7(1, 0.02, 0.00, 0.00, "local request metadata (the action itself)"),
    "environment": CostComponentsV7(120, 0.15, 0.35, 0.05, "remote deployment-control lookup"),
    "deployment_window": CostComponentsV7(120, 0.10, 0.40, 0.05, "remote deployment-control lookup"),
    "approval_token": CostComponentsV7(250, 0.20, 0.15, 0.20, "remote approval service"),
    "resource_owner": CostComponentsV7(150, 0.30, 0.20, 0.08, "IAM/CMDB lookup"),
    "data_classification": CostComponentsV7(100, 0.35, 0.10, 0.03, "policy metadata lookup"),
}


def normalized_latency(raw_latency_ms: float) -> float:
    """Prereg formula: `min(raw_latency_ms / 250, 1.0)` -- bounds the
    latency component to `[0, 1]`, the same range every other component
    is declared in, so no component dominates purely from unit choice."""
    return min(raw_latency_ms / LATENCY_NORMALIZATION_MS, 1.0)


def cost(property_name: str) -> float:
    """Prereg formula: `alpha*normalized_latency + beta*privacy_exposure
    + gamma*staleness_risk + delta*lookup_failure_probability`."""
    c = COST_COMPONENTS_V7[property_name]
    return (
        ALPHA * normalized_latency(c.raw_latency_ms)
        + BETA * c.privacy_exposure
        + GAMMA * c.staleness_risk
        + DELTA * c.lookup_failure_probability
    )


def observation_costs_v7() -> Dict[str, float]:
    """Every candidate property's registered cost, computed fresh from
    the declared components above -- never a hand-typed literal, so a
    future edit to a component value cannot silently drift out of sync
    with the cost RC2 actually optimizes against."""
    return {name: cost(name) for name in COST_COMPONENTS_V7}
