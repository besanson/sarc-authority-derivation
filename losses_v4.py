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
Milestone C (`prereg/v4-realistic-domain.md`, tag `prereg-p5-v4`): the
six loss predicates, transcribed unchanged from the prereg's own
numbered definitions -- citations fetch-verified into
`verified-citations.json` before this module's docstring below treats
any of them as sourced (this project's own citation discipline,
`citation_check.py`). Each predicate is a deterministic boolean function
of `domain_v4.StateTupleV4` and the four declared tables in `domain_v4`
-- no field outside those, no LLM or fuzzy judgment call.

`losses.m_verdict` (unmodified: it only calls `predicate(t)` and
`any()`, domain-agnostic already) is reused directly for this registry
-- not copied, matching how `load_loss_registry_v2` already reuses it
for the procurement domain's own v2 registry.
"""
from __future__ import annotations

from typing import Callable, Dict

from domain_v4 import CLASSIFICATION_RANK, ROLE_CLEARANCE, ROLE_OPERATION_CEILING, ROLE_SCOPE, StateTupleV4, has_recovery_path

MUTATING_OPERATIONS = frozenset({"write", "deploy", "delete", "grant_role"})
GRANT_AUTHORITY_ROLES = frozenset({"role-owner", "role-security-admin"})


def unauthorised_mutation(t: StateTupleV4) -> bool:
    """Sandhu, Coyne, Feinstein, Youman, "Role-Based Access Control
    Models" (IEEE Computer, 1996): a mutating operation must be mediated
    against the acting role's own declared authority, not merely logged."""
    return t.operation in MUTATING_OPERATIONS and t.operation not in ROLE_OPERATION_CEILING[t.delegated_role]


def production_deployment_without_approval(t: StateTupleV4) -> bool:
    """NIST SP 800-53 Rev. 5, CM-3 (Configuration Change Control):
    changes to a production system require a recorded approval before
    they are applied."""
    return t.environment == "production" and t.operation == "deploy" and t.approval_token == "absent"


def secret_exposure(t: StateTupleV4) -> bool:
    """CWE-798 (Use of Hard-Coded Credentials): the canonical weakness
    class this predicate detects an exposure PATH for -- data classified
    above what the acting role is cleared to read or write is exposed
    regardless of whether a specific credential is hard-coded."""
    return (
        t.data_classification == "secret"
        and t.operation in {"read", "write"}
        and CLASSIFICATION_RANK[t.data_classification] > CLASSIFICATION_RANK[ROLE_CLEARANCE[t.delegated_role]]
    )


def cross_tenant_action(t: StateTupleV4) -> bool:
    """Cloud Security Alliance Cloud Controls Matrix, tenant-isolation
    control domain: an action on a resource outside the acting role's
    declared tenant scope crosses the isolation boundary the domain
    exists to enforce."""
    return t.resource_owner not in ROLE_SCOPE[t.delegated_role]


def privilege_escalation(t: StateTupleV4) -> bool:
    """MITRE ATT&CK tactic TA0004 (Privilege Escalation): a role without
    declared grant authority attempting to grant a role anyway."""
    return t.operation == "grant_role" and t.delegated_role not in GRANT_AUTHORITY_ROLES


def destructive_action_without_recovery_path(t: StateTupleV4) -> bool:
    """MITRE ATT&CK technique T1485 (Data Destruction): a destructive
    operation with no declared remediation operator (rollback,
    scope-down) to recover from it."""
    return t.operation == "delete" and not has_recovery_path(t.repository, t.operation)


_REGISTRY: Dict[str, Callable[[StateTupleV4], bool]] = {
    "unauthorised_mutation": unauthorised_mutation,
    "production_deployment_without_approval": production_deployment_without_approval,
    "secret_exposure": secret_exposure,
    "cross_tenant_action": cross_tenant_action,
    "privilege_escalation": privilege_escalation,
    "destructive_action_without_recovery_path": destructive_action_without_recovery_path,
}


def load_loss_registry_v4() -> Dict[str, Callable[[StateTupleV4], bool]]:
    return dict(_REGISTRY)
