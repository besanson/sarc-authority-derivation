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
Package D (`prereg/v8-large-realistic-domain.md`, tag `prereg-p5-v8`): a
large (35-candidate-property), independently-structured enterprise
code/cloud action domain -- built to test whether core-versus-reduct and
cost-sensitive differentiation (CH-B1/CH-B2's own questions on v4's
10-property domain) survive at a scale close to a real enterprise
attribute surface, where exhaustive reduct enumeration is no longer an
option at all.

Every declared value below (property domains, the six reachability
drivers and their valid-combination tables, the 29 deterministic
derivation rules, the three declared role tables) is transcribed
unchanged from the prereg's own tables -- this module does not re-decide
anything the prereg already fixed (its own "Registration discipline"
section)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Tuple

CANDIDATE_PROPERTIES_V8: Tuple[str, ...] = (
    "actor_identity",
    "delegated_role",
    "actor_authentication_strength",
    "delegation_chain_depth",
    "session_assurance_level",
    "identity_provider_trust_tier",
    "on_call_status",
    "repository",
    "resource_owner",
    "resource_environment",
    "resource_criticality_tier",
    "data_classification",
    "data_residency_region",
    "encryption_at_rest_status",
    "operation",
    "operation_criticality",
    "batch_size",
    "automation_level",
    "api_or_console_origin",
    "rate_limit_bucket_state",
    "destination_endpoint_class",
    "workflow_stage",
    "change_ticket_linked",
    "approval_token",
    "approval_quorum_met",
    "deployment_window",
    "rollback_plan_declared",
    "sla_tier",
    "audit_logging_enabled",
    "session_recording_enabled",
    "previous_violation_flag",
    "anomaly_score_bucket",
    "evidence_retention_class",
    "network_zone",
    "device_posture",
)

assert len(CANDIDATE_PROPERTIES_V8) == 35


@dataclass(frozen=True)
class StateTupleV8:
    actor_identity: str
    delegated_role: str
    actor_authentication_strength: str
    delegation_chain_depth: str
    session_assurance_level: str
    identity_provider_trust_tier: str
    on_call_status: str
    repository: str
    resource_owner: str
    resource_environment: str
    resource_criticality_tier: str
    data_classification: str
    data_residency_region: str
    encryption_at_rest_status: str
    operation: str
    operation_criticality: str
    batch_size: str
    automation_level: str
    api_or_console_origin: str
    rate_limit_bucket_state: str
    destination_endpoint_class: str
    workflow_stage: str
    change_ticket_linked: str
    approval_token: str
    approval_quorum_met: str
    deployment_window: str
    rollback_plan_declared: str
    sla_tier: str
    audit_logging_enabled: str
    session_recording_enabled: str
    previous_violation_flag: str
    anomaly_score_bucket: str
    evidence_retention_class: str
    network_zone: str
    device_posture: str

    def with_property(self, name: str, value: object) -> "StateTupleV8":
        from dataclasses import replace
        return replace(self, **{name: value})


# -- Six reachability drivers (prereg's own "Reachability" section,
# categories 1-6) -- every other property below is a deterministic
# function of these. --------------------------------------------------

ACTOR_ROLE_PAIRS: List[Tuple[str, str]] = [
    ("ci-bot", "role-deployer"),
    ("oncall-engineer", "role-owner"),
    ("oncall-engineer", "role-deployer"),
    ("contractor", "role-contractor-readonly"),
    ("automated-pipeline", "role-security-admin"),
]

REPO_TENANT_PAIRS: List[Tuple[str, str]] = [
    ("repo-billing", "tenant-a"),
    ("repo-public-website", "tenant-a"),
    ("repo-public-website", "tenant-b"),
    ("repo-internal-tools", "tenant-b"),
    ("repo-ml-pipeline", "tenant-c"),
]

WORKFLOW_APPROVAL_PAIRS: List[Tuple[str, str]] = (
    [(ws, tok) for ws in ("draft", "review") for tok in ("valid", "absent", "expired")]
    + [(ws, "valid") for ws in ("approved", "executing", "completed")]
)

ENV_ZONE_POSTURE_TRIPLES: List[Tuple[str, str, str]] = [
    ("production", "corp-trusted", "managed-compliant"),
    ("staging", "corp-trusted", "managed-compliant"),
    ("staging", "vpn", "managed-compliant"),
    ("staging", "vpn", "managed-noncompliant"),
    ("development", "corp-trusted", "managed-compliant"),
    ("development", "public-internet", "unmanaged"),
]

DATA_CLASSIFICATION_VALUES: List[str] = ["public", "internal", "confidential", "secret"]
OPERATION_VALUES: List[str] = ["read", "write", "deploy", "delete", "grant_role"]

assert len(ACTOR_ROLE_PAIRS) == 5
assert len(REPO_TENANT_PAIRS) == 5
assert len(WORKFLOW_APPROVAL_PAIRS) == 9
assert len(ENV_ZONE_POSTURE_TRIPLES) == 6

# -- Declared role tables used only by losses_v8.py's predicates
# (background configuration, not candidate observations -- ADR-002's
# non-candidacy argument, unchanged). ----------------------------------

ROLE_OPERATION_CEILING: Dict[str, FrozenSet[str]] = {
    "role-owner": frozenset({"read", "write", "deploy", "delete", "grant_role"}),
    "role-deployer": frozenset({"read", "write", "deploy"}),
    "role-contractor-readonly": frozenset({"read"}),
    "role-security-admin": frozenset({"read", "grant_role"}),
}

ROLE_CLEARANCE: Dict[str, str] = {
    "role-owner": "secret",
    "role-security-admin": "secret",
    "role-deployer": "internal",
    "role-contractor-readonly": "public",
}

CLASSIFICATION_RANK: Dict[str, int] = {"public": 0, "internal": 1, "confidential": 2, "secret": 3}

ROLE_SCOPE: Dict[str, FrozenSet[str]] = {
    "role-owner": frozenset({"tenant-a", "tenant-b", "tenant-c"}),
    "role-security-admin": frozenset({"tenant-a", "tenant-b", "tenant-c"}),
    "role-deployer": frozenset({"tenant-a"}),
    "role-contractor-readonly": frozenset({"tenant-a"}),
}


# -- 29 deterministic derivation rules (prereg's own "Deterministic
# derivation tables" section, transcribed unchanged). -------------------

def _actor_authentication_strength(actor_identity: str) -> str:
    return "hardware-key" if actor_identity in ("ci-bot", "automated-pipeline") else "mfa"


def _delegation_chain_depth(delegated_role: str) -> str:
    return "one-hop-delegated" if delegated_role == "role-contractor-readonly" else "direct"


def _session_assurance_level(actor_authentication_strength: str) -> str:
    return "high" if actor_authentication_strength == "hardware-key" else "medium"


def _identity_provider_trust_tier(actor_identity: str) -> str:
    return "tier-3-external" if actor_identity == "contractor" else "tier-1-internal"


def _on_call_status(actor_identity: str) -> str:
    return "on-call" if actor_identity == "oncall-engineer" else "not-on-call"


def _resource_criticality_tier(repository: str) -> str:
    if repository == "repo-billing":
        return "tier-0-critical"
    if repository in ("repo-public-website", "repo-ml-pipeline"):
        return "tier-1-important"
    return "tier-2-standard"


def _data_residency_region(resource_owner: str) -> str:
    return {"tenant-a": "us", "tenant-b": "eu", "tenant-c": "apac"}[resource_owner]


def _encryption_at_rest_status(data_classification: str) -> str:
    return "unencrypted" if data_classification == "public" else "encrypted"


def _operation_criticality(operation: str) -> str:
    if operation == "read":
        return "low"
    if operation == "write":
        return "medium"
    return "high"


def _batch_size(operation: str) -> str:
    return "bulk" if operation == "delete" else "single-item"


def _automation_level(actor_identity: str) -> str:
    return "fully-automated" if actor_identity in ("ci-bot", "automated-pipeline") else "manual"


def _api_or_console_origin(automation_level: str) -> str:
    return "api" if automation_level == "fully-automated" else "console"


def _rate_limit_bucket_state(automation_level: str) -> str:
    return "throttled" if automation_level == "fully-automated" else "normal"


def _destination_endpoint_class(repository: str) -> str:
    return "external-facing" if repository == "repo-public-website" else "internal-only"


def _change_ticket_linked(resource_criticality_tier: str, operation_criticality: str) -> str:
    if resource_criticality_tier != "tier-2-standard" and operation_criticality == "high":
        return "linked"
    return "not-linked"


def _approval_quorum_met(workflow_stage: str) -> str:
    return "met" if workflow_stage in ("approved", "executing", "completed") else "not-met"


def _deployment_window(workflow_stage: str) -> str:
    return "out_of_window" if workflow_stage in ("draft", "review") else "in_window"


def _rollback_plan_declared(repository: str, operation: str) -> str:
    if operation == "deploy":
        return "declared"
    if operation == "delete" and repository == "repo-internal-tools":
        return "declared"
    return "not-declared"


def _sla_tier(resource_criticality_tier: str) -> str:
    return {"tier-0-critical": "gold", "tier-1-important": "silver", "tier-2-standard": "bronze"}[resource_criticality_tier]


def _audit_logging_enabled(resource_criticality_tier: str) -> str:
    return "disabled" if resource_criticality_tier == "tier-2-standard" else "enabled"


def _session_recording_enabled(delegated_role: str) -> str:
    return "enabled" if delegated_role == "role-contractor-readonly" else "disabled"


def _previous_violation_flag(actor_identity: str) -> str:
    return "flagged" if actor_identity == "contractor" else "clean"


def _anomaly_score_bucket(previous_violation_flag: str) -> str:
    return "elevated" if previous_violation_flag == "flagged" else "normal"


def _evidence_retention_class(data_classification: str) -> str:
    if data_classification in ("public", "internal"):
        return "standard"
    if data_classification == "confidential":
        return "extended"
    return "legal-hold"


def rank0_reachable_tuples_v8() -> List[StateTupleV8]:
    """The declared-constraint-filtered product of the six drivers
    above (prereg's own "Rank-0 reachable-tuple count": `5 x 5 x 9 x 6
    x 4 x 5 = 27,000`); every other property is then computed by direct
    application of the deterministic derivation functions above, not
    re-decided here."""
    out: List[StateTupleV8] = []
    for actor_identity, delegated_role in ACTOR_ROLE_PAIRS:
        actor_authentication_strength = _actor_authentication_strength(actor_identity)
        for repository, resource_owner in REPO_TENANT_PAIRS:
            resource_criticality_tier = _resource_criticality_tier(repository)
            for workflow_stage, approval_token in WORKFLOW_APPROVAL_PAIRS:
                for resource_environment, network_zone, device_posture in ENV_ZONE_POSTURE_TRIPLES:
                    for data_classification in DATA_CLASSIFICATION_VALUES:
                        for operation in OPERATION_VALUES:
                            operation_criticality = _operation_criticality(operation)
                            out.append(StateTupleV8(
                                actor_identity=actor_identity,
                                delegated_role=delegated_role,
                                actor_authentication_strength=actor_authentication_strength,
                                delegation_chain_depth=_delegation_chain_depth(delegated_role),
                                session_assurance_level=_session_assurance_level(actor_authentication_strength),
                                identity_provider_trust_tier=_identity_provider_trust_tier(actor_identity),
                                on_call_status=_on_call_status(actor_identity),
                                repository=repository,
                                resource_owner=resource_owner,
                                resource_environment=resource_environment,
                                resource_criticality_tier=resource_criticality_tier,
                                data_classification=data_classification,
                                data_residency_region=_data_residency_region(resource_owner),
                                encryption_at_rest_status=_encryption_at_rest_status(data_classification),
                                operation=operation,
                                operation_criticality=operation_criticality,
                                batch_size=_batch_size(operation),
                                automation_level=_automation_level(actor_identity),
                                api_or_console_origin=_api_or_console_origin(_automation_level(actor_identity)),
                                rate_limit_bucket_state=_rate_limit_bucket_state(_automation_level(actor_identity)),
                                destination_endpoint_class=_destination_endpoint_class(repository),
                                workflow_stage=workflow_stage,
                                change_ticket_linked=_change_ticket_linked(resource_criticality_tier, operation_criticality),
                                approval_token=approval_token,
                                approval_quorum_met=_approval_quorum_met(workflow_stage),
                                deployment_window=_deployment_window(workflow_stage),
                                rollback_plan_declared=_rollback_plan_declared(repository, operation),
                                sla_tier=_sla_tier(resource_criticality_tier),
                                audit_logging_enabled=_audit_logging_enabled(resource_criticality_tier),
                                session_recording_enabled=_session_recording_enabled(delegated_role),
                                previous_violation_flag=_previous_violation_flag(actor_identity),
                                anomaly_score_bucket=_anomaly_score_bucket(_previous_violation_flag(actor_identity)),
                                evidence_retention_class=_evidence_retention_class(data_classification),
                                network_zone=network_zone,
                                device_posture=device_posture,
                            ))
    return out


def executable_reachable_tuples_v8() -> List[StateTupleV8]:
    """No remediation operator transforms a field's value into a new
    domain point for this domain (mirroring v4's own `executable ==
    rank0` finding, `checkers/ch_b1_check.py`'s precedent) -- checked
    directly by `checkers/ch_c1_check.py` (byte-for-byte length/content
    comparison against `rank0_reachable_tuples_v8()`), not assumed
    here."""
    return rank0_reachable_tuples_v8()
