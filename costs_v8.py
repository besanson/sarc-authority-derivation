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
Package D (`prereg/v8-large-realistic-domain.md`, tag `prereg-p5-v8`):
the registered per-property observation-cost model for `domain_v8.py`'s
35 candidate properties -- the same formula and weights as
`costs_v7.py` (methodology is domain-independent), a freshly declared
seven-tier per-property source-class assignment for this domain's own
35 candidates, transcribed unchanged from the prereg's own table."""
from __future__ import annotations

from typing import Dict, NamedTuple

from domain_v8 import CANDIDATE_PROPERTIES_V8

ALPHA = 1.0   # normalized_latency weight
BETA = 2.0    # privacy_exposure weight
GAMMA = 1.5   # staleness_risk weight
DELTA = 3.0   # lookup_failure_probability weight

LATENCY_NORMALIZATION_MS = 250.0


class CostTierV8(NamedTuple):
    raw_latency_ms: float
    privacy_exposure: float
    staleness_risk: float
    lookup_failure_probability: float
    source_class: str


COST_TIERS_V8: Dict[str, CostTierV8] = {
    "local-identity": CostTierV8(5, 0.05, 0.05, 0.01, "already-known request/session context"),
    "local-request": CostTierV8(1, 0.02, 0.00, 0.00, "the request's own parameters"),
    "local-resource-metadata": CostTierV8(5, 0.05, 0.05, 0.01, "cached/replicated resource config"),
    "remote-governance-lookup": CostTierV8(250, 0.20, 0.15, 0.20, "a synchronous change/approval service"),
    "remote-iam-cmdb-lookup": CostTierV8(150, 0.30, 0.20, 0.08, "IAM / CMDB / ownership lookup"),
    "remote-deployment-control-lookup": CostTierV8(120, 0.15, 0.35, 0.05, "deployment/environment control plane"),
    "remote-security-telemetry-lookup": CostTierV8(200, 0.25, 0.30, 0.10, "SIEM / anomaly / audit telemetry"),
}

# Every one of the 35 candidates, assigned to exactly one tier above --
# transcribed unchanged from the prereg's own cost-model table.
PROPERTY_TIER_V8: Dict[str, str] = {
    "actor_identity": "local-identity",
    "delegated_role": "local-identity",
    "actor_authentication_strength": "local-identity",
    "delegation_chain_depth": "local-identity",
    "session_assurance_level": "local-identity",
    "identity_provider_trust_tier": "local-identity",
    "on_call_status": "local-identity",
    "automation_level": "local-identity",
    "api_or_console_origin": "local-identity",
    "operation": "local-request",
    "operation_criticality": "local-request",
    "batch_size": "local-request",
    "rate_limit_bucket_state": "local-request",
    "workflow_stage": "local-request",
    "deployment_window": "local-request",
    "repository": "local-resource-metadata",
    "resource_criticality_tier": "local-resource-metadata",
    "destination_endpoint_class": "local-resource-metadata",
    "rollback_plan_declared": "local-resource-metadata",
    "sla_tier": "local-resource-metadata",
    "approval_token": "remote-governance-lookup",
    "approval_quorum_met": "remote-governance-lookup",
    "change_ticket_linked": "remote-governance-lookup",
    "resource_owner": "remote-iam-cmdb-lookup",
    "data_residency_region": "remote-iam-cmdb-lookup",
    "data_classification": "remote-iam-cmdb-lookup",
    "encryption_at_rest_status": "remote-iam-cmdb-lookup",
    "evidence_retention_class": "remote-iam-cmdb-lookup",
    "resource_environment": "remote-deployment-control-lookup",
    "network_zone": "remote-deployment-control-lookup",
    "device_posture": "remote-deployment-control-lookup",
    "audit_logging_enabled": "remote-security-telemetry-lookup",
    "session_recording_enabled": "remote-security-telemetry-lookup",
    "anomaly_score_bucket": "remote-security-telemetry-lookup",
    "previous_violation_flag": "remote-security-telemetry-lookup",
}

assert set(PROPERTY_TIER_V8) == set(CANDIDATE_PROPERTIES_V8)


def normalized_latency(raw_latency_ms: float) -> float:
    return min(raw_latency_ms / LATENCY_NORMALIZATION_MS, 1.0)


def cost(property_name: str) -> float:
    tier = COST_TIERS_V8[PROPERTY_TIER_V8[property_name]]
    return (
        ALPHA * normalized_latency(tier.raw_latency_ms)
        + BETA * tier.privacy_exposure
        + GAMMA * tier.staleness_risk
        + DELTA * tier.lookup_failure_probability
    )


def observation_costs_v8() -> Dict[str, float]:
    return {name: cost(name) for name in CANDIDATE_PROPERTIES_V8}
