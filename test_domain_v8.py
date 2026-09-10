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
"""Tests for domain_v8.py (prereg/v8-large-realistic-domain.md, tag
prereg-p5-v8): the six reachability drivers and the 29 deterministic
derivation rules, checked directly against the real 27,000-tuple
reachable set."""
from __future__ import annotations

from dataclasses import fields

from domain_v8 import (
    ACTOR_ROLE_PAIRS,
    CANDIDATE_PROPERTIES_V8,
    ENV_ZONE_POSTURE_TRIPLES,
    REPO_TENANT_PAIRS,
    WORKFLOW_APPROVAL_PAIRS,
    StateTupleV8,
    rank0_reachable_tuples_v8,
)


def test_driver_table_sizes_match_prereg():
    assert len(ACTOR_ROLE_PAIRS) == 5
    assert len(REPO_TENANT_PAIRS) == 5
    assert len(WORKFLOW_APPROVAL_PAIRS) == 9
    assert len(ENV_ZONE_POSTURE_TRIPLES) == 6


def test_rank0_reachable_exact_size_matches_prereg():
    """5 x 5 x 9 x 6 x 4 (data_classification) x 5 (operation) = 27,000
    -- hand-derived independently of the implementation in the prereg
    itself, not copied from this module's own output."""
    reachable = rank0_reachable_tuples_v8()
    assert len(reachable) == 27_000


def test_candidate_properties_match_state_tuple_fields():
    reachable = rank0_reachable_tuples_v8()
    field_names = {f.name for f in fields(reachable[0])}
    assert set(CANDIDATE_PROPERTIES_V8) == field_names
    assert len(CANDIDATE_PROPERTIES_V8) == 35


def test_every_declared_value_occurs_on_some_reachable_tuple():
    """Registered domain design goal (prereg's own claim): no candidate
    property carries a structurally-unreachable declared value."""
    reachable = rank0_reachable_tuples_v8()
    declared = {
        "actor_identity": {"ci-bot", "oncall-engineer", "contractor", "automated-pipeline"},
        "delegated_role": {"role-owner", "role-deployer", "role-contractor-readonly", "role-security-admin"},
        "repository": {"repo-billing", "repo-public-website", "repo-internal-tools", "repo-ml-pipeline"},
        "resource_owner": {"tenant-a", "tenant-b", "tenant-c"},
        "resource_environment": {"production", "staging", "development"},
        "data_classification": {"public", "internal", "confidential", "secret"},
        "operation": {"read", "write", "deploy", "delete", "grant_role"},
        "workflow_stage": {"draft", "review", "approved", "executing", "completed"},
        "approval_token": {"valid", "absent", "expired"},
        "network_zone": {"corp-trusted", "vpn", "public-internet"},
        "device_posture": {"managed-compliant", "managed-noncompliant", "unmanaged"},
    }
    for field, expected_values in declared.items():
        seen = {getattr(t, field) for t in reachable}
        assert seen == expected_values, field


def test_workflow_approval_joint_constraint():
    reachable = rank0_reachable_tuples_v8()
    for t in reachable:
        if t.workflow_stage in ("approved", "executing", "completed"):
            assert t.approval_token == "valid", t
        else:
            assert t.workflow_stage in ("draft", "review")


def test_environment_zone_posture_joint_constraint():
    reachable = rank0_reachable_tuples_v8()
    valid_triples = set(ENV_ZONE_POSTURE_TRIPLES)
    for t in reachable:
        assert (t.resource_environment, t.network_zone, t.device_posture) in valid_triples


def test_production_never_pairs_with_public_internet_or_noncompliant_device():
    reachable = rank0_reachable_tuples_v8()
    for t in reachable:
        if t.resource_environment == "production":
            assert t.network_zone == "corp-trusted"
            assert t.device_posture == "managed-compliant"


def test_delegated_role_never_reaches_a_disallowed_actor_identity():
    reachable = rank0_reachable_tuples_v8()
    valid_pairs = set(ACTOR_ROLE_PAIRS)
    for t in reachable:
        assert (t.actor_identity, t.delegated_role) in valid_pairs


def test_repository_tenant_pairing_matches_declared_table():
    reachable = rank0_reachable_tuples_v8()
    valid_pairs = set(REPO_TENANT_PAIRS)
    for t in reachable:
        assert (t.repository, t.resource_owner) in valid_pairs


def test_encryption_at_rest_forced_by_data_classification():
    reachable = rank0_reachable_tuples_v8()
    for t in reachable:
        if t.data_classification == "public":
            assert t.encryption_at_rest_status == "unencrypted"
        else:
            assert t.encryption_at_rest_status == "encrypted"


def test_approval_quorum_met_tracks_workflow_stage_exactly():
    """Registered as a real, if redundant, derived property (prereg's
    own note): given reachability rule 3, quorum-met is fully
    determined by workflow_stage alone in this domain."""
    reachable = rank0_reachable_tuples_v8()
    for t in reachable:
        expected = "met" if t.workflow_stage in ("approved", "executing", "completed") else "not-met"
        assert t.approval_quorum_met == expected


def test_with_property_overrides_a_single_field():
    reachable = rank0_reachable_tuples_v8()
    t = reachable[0]
    changed = t.with_property("operation", "read")
    assert changed.operation == "read"
    for f in fields(t):
        if f.name != "operation":
            assert getattr(changed, f.name) == getattr(t, f.name)


# -- Exhaustive derivation consistency, checked against every one of the
# 27,000 real reachable tuples, not a hand-picked sample: each of these
# recomputes one declared derivation independently (a literal transcript
# of domain_v8.py's own derivation tables) and compares it against the
# tuple's own stored field. A mutation to the derivation function itself,
# OR to which argument rank0_reachable_tuples_v8() passes it (a wrong
# variable, a None substitution), makes at least one of the 27,000 real
# tuples violate its own declared relationship -- unlike a single
# hand-picked positive/negative case, this can't be satisfied by
# accident for a specific narrow input. --------------------------------

def test_actor_authentication_strength_derivation_holds_on_every_tuple():
    expected = {"ci-bot": "hardware-key", "automated-pipeline": "hardware-key", "oncall-engineer": "mfa", "contractor": "mfa"}
    for t in rank0_reachable_tuples_v8():
        assert t.actor_authentication_strength == expected[t.actor_identity]


def test_delegation_chain_depth_derivation_holds_on_every_tuple():
    for t in rank0_reachable_tuples_v8():
        expected = "one-hop-delegated" if t.delegated_role == "role-contractor-readonly" else "direct"
        assert t.delegation_chain_depth == expected


def test_session_assurance_level_derivation_holds_on_every_tuple():
    expected = {"hardware-key": "high", "mfa": "medium"}
    for t in rank0_reachable_tuples_v8():
        assert t.session_assurance_level == expected[t.actor_authentication_strength]


def test_identity_provider_trust_tier_derivation_holds_on_every_tuple():
    for t in rank0_reachable_tuples_v8():
        expected = "tier-3-external" if t.actor_identity == "contractor" else "tier-1-internal"
        assert t.identity_provider_trust_tier == expected


def test_on_call_status_derivation_holds_on_every_tuple():
    for t in rank0_reachable_tuples_v8():
        expected = "on-call" if t.actor_identity == "oncall-engineer" else "not-on-call"
        assert t.on_call_status == expected


def test_resource_criticality_tier_derivation_holds_on_every_tuple():
    expected_map = {
        "repo-billing": "tier-0-critical",
        "repo-public-website": "tier-1-important",
        "repo-ml-pipeline": "tier-1-important",
        "repo-internal-tools": "tier-2-standard",
    }
    for t in rank0_reachable_tuples_v8():
        assert t.resource_criticality_tier == expected_map[t.repository]


def test_data_residency_region_derivation_holds_on_every_tuple():
    expected = {"tenant-a": "us", "tenant-b": "eu", "tenant-c": "apac"}
    for t in rank0_reachable_tuples_v8():
        assert t.data_residency_region == expected[t.resource_owner]


def test_operation_criticality_derivation_holds_on_every_tuple():
    expected = {"read": "low", "write": "medium", "deploy": "high", "delete": "high", "grant_role": "high"}
    for t in rank0_reachable_tuples_v8():
        assert t.operation_criticality == expected[t.operation]


def test_batch_size_derivation_holds_on_every_tuple():
    for t in rank0_reachable_tuples_v8():
        expected = "bulk" if t.operation == "delete" else "single-item"
        assert t.batch_size == expected


def test_automation_level_derivation_holds_on_every_tuple():
    for t in rank0_reachable_tuples_v8():
        expected = "fully-automated" if t.actor_identity in ("ci-bot", "automated-pipeline") else "manual"
        assert t.automation_level == expected


def test_api_or_console_origin_derivation_holds_on_every_tuple():
    for t in rank0_reachable_tuples_v8():
        expected = "api" if t.automation_level == "fully-automated" else "console"
        assert t.api_or_console_origin == expected


def test_rate_limit_bucket_state_derivation_holds_on_every_tuple():
    for t in rank0_reachable_tuples_v8():
        expected = "throttled" if t.automation_level == "fully-automated" else "normal"
        assert t.rate_limit_bucket_state == expected


def test_destination_endpoint_class_derivation_holds_on_every_tuple():
    for t in rank0_reachable_tuples_v8():
        expected = "external-facing" if t.repository == "repo-public-website" else "internal-only"
        assert t.destination_endpoint_class == expected


def test_change_ticket_linked_derivation_holds_on_every_tuple():
    for t in rank0_reachable_tuples_v8():
        expected = "linked" if (t.resource_criticality_tier != "tier-2-standard" and t.operation_criticality == "high") else "not-linked"
        assert t.change_ticket_linked == expected


def test_deployment_window_derivation_holds_on_every_tuple():
    for t in rank0_reachable_tuples_v8():
        expected = "in_window" if t.workflow_stage in ("approved", "executing", "completed") else "out_of_window"
        assert t.deployment_window == expected


def test_rollback_plan_declared_derivation_holds_on_every_tuple():
    for t in rank0_reachable_tuples_v8():
        expected = "declared" if (t.operation == "deploy" or (t.operation == "delete" and t.repository == "repo-internal-tools")) else "not-declared"
        assert t.rollback_plan_declared == expected


def test_sla_tier_derivation_holds_on_every_tuple():
    expected = {"tier-0-critical": "gold", "tier-1-important": "silver", "tier-2-standard": "bronze"}
    for t in rank0_reachable_tuples_v8():
        assert t.sla_tier == expected[t.resource_criticality_tier]


def test_audit_logging_enabled_derivation_holds_on_every_tuple():
    for t in rank0_reachable_tuples_v8():
        expected = "disabled" if t.resource_criticality_tier == "tier-2-standard" else "enabled"
        assert t.audit_logging_enabled == expected


def test_session_recording_enabled_derivation_holds_on_every_tuple():
    for t in rank0_reachable_tuples_v8():
        expected = "enabled" if t.delegated_role == "role-contractor-readonly" else "disabled"
        assert t.session_recording_enabled == expected


def test_previous_violation_flag_derivation_holds_on_every_tuple():
    for t in rank0_reachable_tuples_v8():
        expected = "flagged" if t.actor_identity == "contractor" else "clean"
        assert t.previous_violation_flag == expected


def test_anomaly_score_bucket_derivation_holds_on_every_tuple():
    for t in rank0_reachable_tuples_v8():
        expected = "elevated" if t.previous_violation_flag == "flagged" else "normal"
        assert t.anomaly_score_bucket == expected


def test_evidence_retention_class_derivation_holds_on_every_tuple():
    expected_map = {"public": "standard", "internal": "standard", "confidential": "extended", "secret": "legal-hold"}
    for t in rank0_reachable_tuples_v8():
        assert t.evidence_retention_class == expected_map[t.data_classification]
