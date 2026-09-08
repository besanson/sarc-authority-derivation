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
"""Tests for losses_v4.py -- one positive case and one negative
("near-miss": flip exactly one clause back to safe) case per declared
loss, mirroring test_losses.py's own precision (a BASE safe tuple,
`.with_property()` overrides) so a boundary mutation (==/!=, and/or,
in/not in) is caught, not just "fires somewhere on the reachable set"."""
from __future__ import annotations

from domain_v4 import StateTupleV4
from losses_v4 import (
    cross_tenant_action,
    destructive_action_without_recovery_path,
    load_loss_registry_v4,
    privilege_escalation,
    production_deployment_without_approval,
    secret_exposure,
    unauthorised_mutation,
)

BASE = StateTupleV4(
    actor_identity="agent-ci-bot",
    delegated_role="role-owner",
    repository="repo-billing",
    branch="staging",
    environment="staging",
    resource_owner="tenant-a",
    operation="read",
    approval_token="valid",
    deployment_window="in_window",
    data_classification="public",
)


def _all_false(t: StateTupleV4, *exclude: str) -> None:
    for name, predicate in load_loss_registry_v4().items():
        if name in exclude:
            continue
        assert predicate(t) is False, f"{name} unexpectedly fired on {t}"


def test_base_tuple_is_clean():
    _all_false(BASE)


def test_unauthorised_mutation_positive_and_negatives():
    # role-contractor-readonly's ceiling is {read} -- write is mutating and outside it.
    violating = BASE.with_property("delegated_role", "role-contractor-readonly").with_property("operation", "write")
    assert unauthorised_mutation(violating) is True
    # near-miss 1: same role, but a non-mutating operation (read) -- first clause fails.
    assert unauthorised_mutation(violating.with_property("operation", "read")) is False
    # near-miss 2: same mutating operation, but role-owner's ceiling includes it -- second clause fails.
    assert unauthorised_mutation(violating.with_property("delegated_role", "role-owner")) is False


def test_production_deployment_without_approval_positive_and_negatives():
    violating = BASE.with_property("branch", "main").with_property("environment", "production").with_property(
        "operation", "deploy"
    ).with_property("approval_token", "absent")
    assert production_deployment_without_approval(violating) is True
    assert production_deployment_without_approval(violating.with_property("environment", "staging")) is False
    assert production_deployment_without_approval(violating.with_property("operation", "read")) is False
    assert production_deployment_without_approval(violating.with_property("approval_token", "valid")) is False


def test_secret_exposure_positive_and_negatives():
    violating = BASE.with_property("delegated_role", "role-contractor-readonly").with_property(
        "data_classification", "secret"
    ).with_property("operation", "read")
    assert secret_exposure(violating) is True
    # both members of {read, write} must independently trigger it.
    assert secret_exposure(violating.with_property("operation", "write")) is True
    assert secret_exposure(violating.with_property("data_classification", "public")) is False
    assert secret_exposure(violating.with_property("operation", "deploy")) is False
    # role-owner is cleared for secret -- third clause (exceeds clearance) fails.
    assert secret_exposure(violating.with_property("delegated_role", "role-owner")) is False


def test_cross_tenant_action_positive_and_negative():
    # role-deployer's declared scope is tenant-a only; tenant-b is reachable for it
    # (the reachability fix found and fixed while drafting the prereg) but outside scope.
    violating = BASE.with_property("delegated_role", "role-deployer").with_property("resource_owner", "tenant-b")
    assert cross_tenant_action(violating) is True
    assert cross_tenant_action(violating.with_property("resource_owner", "tenant-a")) is False
    # role-owner is unscoped -- same resource_owner, no longer outside scope.
    assert cross_tenant_action(violating.with_property("delegated_role", "role-owner")) is False


def test_privilege_escalation_positive_and_negatives():
    violating = BASE.with_property("delegated_role", "role-deployer").with_property("operation", "grant_role")
    assert privilege_escalation(violating) is True
    assert privilege_escalation(violating.with_property("operation", "read")) is False
    assert privilege_escalation(violating.with_property("delegated_role", "role-owner")) is False
    assert privilege_escalation(violating.with_property("delegated_role", "role-security-admin")) is False


def test_destructive_action_without_recovery_path_positive_and_negatives():
    violating = BASE.with_property("repository", "repo-billing").with_property("operation", "delete")
    assert destructive_action_without_recovery_path(violating) is True
    assert destructive_action_without_recovery_path(violating.with_property("operation", "read")) is False
    # repo-internal-tools' delete HAS a declared recovery path (scope-down).
    assert destructive_action_without_recovery_path(violating.with_property("repository", "repo-internal-tools")) is False


def test_registry_has_all_six_declared_losses():
    assert set(load_loss_registry_v4()) == {
        "unauthorised_mutation",
        "production_deployment_without_approval",
        "secret_exposure",
        "cross_tenant_action",
        "privilege_escalation",
        "destructive_action_without_recovery_path",
    }
