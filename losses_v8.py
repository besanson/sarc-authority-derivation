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
the nine loss predicates, transcribed unchanged from the prereg's own
numbered definitions -- citations fetch-verified into
`verified-citations.json` before this module's docstring below treats
any of them as sourced (this project's own citation discipline,
`citation_check.py`). Each predicate is a deterministic boolean function
of `domain_v8.StateTupleV8` and the three declared role tables in
`domain_v8` -- no field outside those, no LLM or fuzzy judgment call.

`losses.m_verdict` (unmodified, domain-agnostic already) is reused
directly for this registry, matching v4's own precedent."""
from __future__ import annotations

from typing import Callable, Dict

from domain_v8 import (
    CLASSIFICATION_RANK,
    ROLE_CLEARANCE,
    ROLE_OPERATION_CEILING,
    ROLE_SCOPE,
    StateTupleV8,
)

MUTATING_OPERATIONS = frozenset({"write", "deploy", "delete", "grant_role"})
GRANT_AUTHORITY_ROLES = frozenset({"role-owner", "role-security-admin"})


def unauthorized_mutation(t: StateTupleV8) -> bool:
    """Sandhu, Coyne, Feinstein, Youman, "Role-Based Access Control
    Models" (IEEE Computer, 1996) / NIST SP 800-53 Rev. 5, AC-3 (Access
    Enforcement): a mutating operation must be mediated against the
    acting role's own declared authority, not merely logged."""
    return t.operation in MUTATING_OPERATIONS and t.operation not in ROLE_OPERATION_CEILING[t.delegated_role]


def production_deployment_without_quorum(t: StateTupleV8) -> bool:
    """NIST SP 800-53 Rev. 5, CM-3 (Configuration Change Control):
    changes to a production system require a recorded, quorum-met
    approval before they are applied -- not merely a present token."""
    return t.resource_environment == "production" and t.operation == "deploy" and t.approval_quorum_met == "not-met"


def secret_exposure_beyond_clearance(t: StateTupleV8) -> bool:
    """OWASP Secrets Management Cheat Sheet / CWE-798 (Use of
    Hard-Coded Credentials): data classified above what the acting role
    is cleared to read or write is exposed regardless of whether a
    specific credential is hard-coded."""
    return (
        t.data_classification == "secret"
        and t.operation in {"read", "write"}
        and CLASSIFICATION_RANK[t.data_classification] > CLASSIFICATION_RANK[ROLE_CLEARANCE[t.delegated_role]]
    )


def cross_tenant_access(t: StateTupleV8) -> bool:
    """Cloud Security Alliance Cloud Controls Matrix, tenant-isolation
    control domain: an action on a resource outside the acting role's
    declared tenant scope crosses the isolation boundary the domain
    exists to enforce."""
    return t.resource_owner not in ROLE_SCOPE[t.delegated_role]


def privilege_escalation_via_grant(t: StateTupleV8) -> bool:
    """MITRE ATT&CK tactic TA0004 (Privilege Escalation): a role without
    declared grant authority attempting to grant a role anyway."""
    return t.operation == "grant_role" and t.delegated_role not in GRANT_AUTHORITY_ROLES


def destructive_action_without_rollback(t: StateTupleV8) -> bool:
    """NIST SP 800-34 (Contingency Planning Guide) / MITRE ATT&CK
    technique T1485 (Data Destruction): a destructive operation with no
    declared rollback plan to recover from it."""
    return t.operation == "delete" and t.rollback_plan_declared == "not-declared"


def external_network_zone_for_sensitive_data(t: StateTupleV8) -> bool:
    """NIST SP 800-207 (Zero Trust Architecture): network location is
    never itself a trust signal -- confidential or secret data reached
    over the public internet is exposed regardless of any other
    property's value."""
    return t.network_zone == "public-internet" and t.data_classification in {"confidential", "secret"}


def automated_actor_manual_only_operation(t: StateTupleV8) -> bool:
    """NIST SP 800-53 Rev. 5, AC-6 (Least Privilege): a fully-automated
    principal performing a role-grant is exactly the kind of action
    least-privilege review expects a human attestation step for, the
    per-role operation ceiling notwithstanding."""
    return t.automation_level == "fully-automated" and t.operation == "grant_role"


def stale_approval_carried_into_review(t: StateTupleV8) -> bool:
    """NIST SP 800-53 Rev. 5, CM-3 (Configuration Change Control): a
    distinct clause of the same control -- stale authorization evidence
    (an expired token) accompanying a still-open, high-risk change."""
    return t.approval_token == "expired" and t.workflow_stage == "review" and t.operation in {"deploy", "delete", "grant_role"}


_REGISTRY: Dict[str, Callable[[StateTupleV8], bool]] = {
    "unauthorized_mutation": unauthorized_mutation,
    "production_deployment_without_quorum": production_deployment_without_quorum,
    "secret_exposure_beyond_clearance": secret_exposure_beyond_clearance,
    "cross_tenant_access": cross_tenant_access,
    "privilege_escalation_via_grant": privilege_escalation_via_grant,
    "destructive_action_without_rollback": destructive_action_without_rollback,
    "external_network_zone_for_sensitive_data": external_network_zone_for_sensitive_data,
    "automated_actor_manual_only_operation": automated_actor_manual_only_operation,
    "stale_approval_carried_into_review": stale_approval_carried_into_review,
}


def load_loss_registry_v8() -> Dict[str, Callable[[StateTupleV8], bool]]:
    return dict(_REGISTRY)
