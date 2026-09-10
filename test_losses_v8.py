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
"""Tests for losses_v8.py -- one positive case and one negative
("near-miss": flip exactly one clause back to safe) case per declared
loss, mirroring test_losses_v4.py's own precision so a boundary
mutation (==/!=, and/or, in/not in) is caught, not just "fires
somewhere on the reachable set"."""
from __future__ import annotations

from domain_v8 import StateTupleV8
from losses_v8 import (
    automated_actor_manual_only_operation,
    cross_tenant_access,
    destructive_action_without_rollback,
    external_network_zone_for_sensitive_data,
    load_loss_registry_v8,
    privilege_escalation_via_grant,
    production_deployment_without_quorum,
    secret_exposure_beyond_clearance,
    stale_approval_carried_into_review,
    unauthorized_mutation,
)

BASE = StateTupleV8(
    actor_identity="oncall-engineer",
    delegated_role="role-owner",
    actor_authentication_strength="mfa",
    delegation_chain_depth="direct",
    session_assurance_level="medium",
    identity_provider_trust_tier="tier-1-internal",
    on_call_status="on-call",
    repository="repo-billing",
    resource_owner="tenant-a",
    resource_environment="staging",
    resource_criticality_tier="tier-0-critical",
    data_classification="public",
    data_residency_region="us",
    encryption_at_rest_status="unencrypted",
    operation="read",
    operation_criticality="low",
    batch_size="single-item",
    automation_level="manual",
    api_or_console_origin="console",
    rate_limit_bucket_state="normal",
    destination_endpoint_class="internal-only",
    workflow_stage="draft",
    change_ticket_linked="not-linked",
    approval_token="valid",
    approval_quorum_met="not-met",
    deployment_window="out_of_window",
    rollback_plan_declared="not-declared",
    sla_tier="gold",
    audit_logging_enabled="enabled",
    session_recording_enabled="disabled",
    previous_violation_flag="clean",
    anomaly_score_bucket="normal",
    evidence_retention_class="standard",
    network_zone="corp-trusted",
    device_posture="managed-compliant",
)


def _all_false(t: StateTupleV8, *exclude: str) -> None:
    for name, predicate in load_loss_registry_v8().items():
        if name in exclude:
            continue
        assert predicate(t) is False, f"{name} unexpectedly fired on {t}"


def test_base_tuple_is_clean():
    _all_false(BASE)


def test_unauthorized_mutation_positive_and_negatives():
    violating = BASE.with_property("delegated_role", "role-contractor-readonly").with_property("operation", "write")
    assert unauthorized_mutation(violating) is True
    assert unauthorized_mutation(violating.with_property("operation", "read")) is False
    assert unauthorized_mutation(violating.with_property("delegated_role", "role-owner")) is False


def test_production_deployment_without_quorum_positive_and_negatives():
    violating = BASE.with_property("resource_environment", "production").with_property(
        "network_zone", "corp-trusted"
    ).with_property("device_posture", "managed-compliant").with_property("operation", "deploy").with_property(
        "workflow_stage", "draft"
    ).with_property("approval_quorum_met", "not-met")
    assert production_deployment_without_quorum(violating) is True
    assert production_deployment_without_quorum(violating.with_property("resource_environment", "staging")) is False
    assert production_deployment_without_quorum(violating.with_property("operation", "read")) is False
    assert production_deployment_without_quorum(violating.with_property("approval_quorum_met", "met")) is False


def test_secret_exposure_beyond_clearance_positive_and_negatives():
    violating = BASE.with_property("delegated_role", "role-contractor-readonly").with_property(
        "data_classification", "secret"
    ).with_property("operation", "read")
    assert secret_exposure_beyond_clearance(violating) is True
    assert secret_exposure_beyond_clearance(violating.with_property("operation", "write")) is True
    assert secret_exposure_beyond_clearance(violating.with_property("data_classification", "public")) is False
    assert secret_exposure_beyond_clearance(violating.with_property("operation", "deploy")) is False
    assert secret_exposure_beyond_clearance(violating.with_property("delegated_role", "role-owner")) is False


def test_cross_tenant_access_positive_and_negative():
    violating = BASE.with_property("delegated_role", "role-deployer").with_property("resource_owner", "tenant-b")
    assert cross_tenant_access(violating) is True
    assert cross_tenant_access(violating.with_property("resource_owner", "tenant-a")) is False
    assert cross_tenant_access(violating.with_property("delegated_role", "role-owner")) is False


def test_privilege_escalation_via_grant_positive_and_negatives():
    violating = BASE.with_property("delegated_role", "role-deployer").with_property("operation", "grant_role")
    assert privilege_escalation_via_grant(violating) is True
    assert privilege_escalation_via_grant(violating.with_property("operation", "read")) is False
    assert privilege_escalation_via_grant(violating.with_property("delegated_role", "role-owner")) is False
    assert privilege_escalation_via_grant(violating.with_property("delegated_role", "role-security-admin")) is False


def test_destructive_action_without_rollback_positive_and_negatives():
    violating = BASE.with_property("repository", "repo-billing").with_property("operation", "delete").with_property(
        "rollback_plan_declared", "not-declared"
    )
    assert destructive_action_without_rollback(violating) is True
    assert destructive_action_without_rollback(violating.with_property("operation", "read")) is False
    assert destructive_action_without_rollback(violating.with_property("rollback_plan_declared", "declared")) is False


def test_external_network_zone_for_sensitive_data_positive_and_negatives():
    violating = BASE.with_property("network_zone", "public-internet").with_property("data_classification", "secret")
    assert external_network_zone_for_sensitive_data(violating) is True
    assert external_network_zone_for_sensitive_data(violating.with_property("data_classification", "confidential")) is True
    assert external_network_zone_for_sensitive_data(violating.with_property("data_classification", "public")) is False
    assert external_network_zone_for_sensitive_data(violating.with_property("network_zone", "corp-trusted")) is False


def test_automated_actor_manual_only_operation_positive_and_negatives():
    violating = BASE.with_property("automation_level", "fully-automated").with_property("operation", "grant_role")
    assert automated_actor_manual_only_operation(violating) is True
    assert automated_actor_manual_only_operation(violating.with_property("operation", "read")) is False
    assert automated_actor_manual_only_operation(violating.with_property("automation_level", "manual")) is False


def test_stale_approval_carried_into_review_positive_and_negatives():
    violating = BASE.with_property("approval_token", "expired").with_property("workflow_stage", "review").with_property(
        "operation", "deploy"
    )
    assert stale_approval_carried_into_review(violating) is True
    # every member of the declared high-risk operation set triggers it independently.
    assert stale_approval_carried_into_review(violating.with_property("operation", "delete")) is True
    assert stale_approval_carried_into_review(violating.with_property("operation", "grant_role")) is True
    assert stale_approval_carried_into_review(violating.with_property("operation", "read")) is False
    assert stale_approval_carried_into_review(violating.with_property("operation", "write")) is False
    assert stale_approval_carried_into_review(violating.with_property("workflow_stage", "draft")) is False
    assert stale_approval_carried_into_review(violating.with_property("approval_token", "valid")) is False


def test_registry_has_all_nine_declared_losses():
    assert set(load_loss_registry_v8()) == {
        "unauthorized_mutation",
        "production_deployment_without_quorum",
        "secret_exposure_beyond_clearance",
        "cross_tenant_access",
        "privilege_escalation_via_grant",
        "destructive_action_without_rollback",
        "external_network_zone_for_sensitive_data",
        "automated_actor_manual_only_operation",
        "stale_approval_carried_into_review",
    }
