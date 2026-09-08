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
Milestone C (`prereg/v4-realistic-domain.md`, tag `prereg-p5-v4`): a
software-and-cloud execution-agent domain, independent of the retail-
procurement domain `domain.py`/`losses.py` implement -- built to test
whether the core-versus-reduct distinction (Definitions 4-6) shows up on
a domain this project did not build around that distinction, not to
reuse or extend the procurement domain's own structure. `reduct.py` is
applied to this domain unmodified (CH-B1, `checkers/ch_b1_check.py`).

Every declared value below (candidate domains, the four background-
configuration tables, both reachability constraints) is transcribed
unchanged from the prereg's own tables -- this module does not re-decide
anything the prereg already fixed (its own "Registration discipline"
section)."""
from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Dict, List, Tuple

CANDIDATE_PROPERTIES_V4: Tuple[str, ...] = (
    "actor_identity",
    "delegated_role",
    "repository",
    "branch",
    "environment",
    "resource_owner",
    "operation",
    "approval_token",
    "deployment_window",
    "data_classification",
)


@dataclass(frozen=True)
class StateTupleV4:
    actor_identity: str
    delegated_role: str
    repository: str
    branch: str
    environment: str
    resource_owner: str
    operation: str
    approval_token: str
    deployment_window: str
    data_classification: str

    def with_property(self, name: str, value: object) -> "StateTupleV4":
        from dataclasses import replace
        return replace(self, **{name: value})


PROPERTY_DOMAINS_V4: Dict[str, List[str]] = {
    "actor_identity": ["agent-ci-bot", "agent-oncall-engineer", "agent-contractor", "agent-automated-pipeline"],
    "delegated_role": ["role-owner", "role-deployer", "role-contractor-readonly", "role-security-admin"],
    "repository": ["repo-billing", "repo-public-website", "repo-internal-tools"],
    "branch": ["main", "staging", "feature"],
    "environment": ["production", "staging", "development"],
    "resource_owner": ["tenant-a", "tenant-b"],
    "operation": ["read", "write", "deploy", "delete", "grant_role"],
    "approval_token": ["valid", "absent"],
    "deployment_window": ["in_window", "out_of_window"],
    "data_classification": ["public", "internal", "secret"],
}

# -- Declared background configuration (prereg's own four tables; policy
# the gate is built with, not itself a candidate observation -- ADR-002's
# non-candidacy argument for v1/v2's own per-role tables, unchanged). ---

ROLE_SCOPE: Dict[str, frozenset] = {
    "role-owner": frozenset({"tenant-a", "tenant-b"}),
    "role-security-admin": frozenset({"tenant-a", "tenant-b"}),
    "role-deployer": frozenset({"tenant-a"}),
    "role-contractor-readonly": frozenset({"tenant-a"}),
}

ROLE_OPERATION_CEILING: Dict[str, frozenset] = {
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

CLASSIFICATION_RANK: Dict[str, int] = {"public": 0, "internal": 1, "secret": 2}

# recovery-path declaration: (repository, operation) -> has a declared
# remediation operator. `deploy` on any repository has `rollback`
# declared; `delete` on `repo-internal-tools` has `scope-down` declared;
# `delete` on the other two repositories has none declared.
BRANCH_ENVIRONMENT_PAIRING: Dict[str, str] = {"main": "production", "staging": "staging", "feature": "development"}


def has_recovery_path(repository: str, operation: str) -> bool:
    if operation == "deploy":
        return True
    if operation == "delete" and repository == "repo-internal-tools":
        return True
    return False


def rank0_reachable_tuples_v4() -> List[StateTupleV4]:
    """The declared-constraint-filtered product of the ten domains
    above, under both of the prereg's own reachability rules: (1)
    branch/environment is a one-to-one pairing (BRANCH_ENVIRONMENT_
    PAIRING), not a free product of the two domains; (2) `role-
    contractor-readonly` never reaches `resource_owner == tenant-b`
    (real provisioning -- contractors are never onboarded into
    tenant-b's systems) -- `role-deployer` is deliberately NOT
    constrained by this second rule (prereg's own "narrowly, a real
    provisioning fact" note: a rule that excluded every out-of-scope
    tuple for every scoped role would make `cross_tenant_action`
    unsatisfiable by construction)."""
    domains = PROPERTY_DOMAINS_V4
    out: List[StateTupleV4] = []
    for branch in domains["branch"]:
        environment = BRANCH_ENVIRONMENT_PAIRING[branch]
        for delegated_role in domains["delegated_role"]:
            allowed_owners = (
                ["tenant-a"] if delegated_role == "role-contractor-readonly" else domains["resource_owner"]
            )
            for combo in itertools.product(
                domains["actor_identity"],
                domains["repository"],
                allowed_owners,
                domains["operation"],
                domains["approval_token"],
                domains["deployment_window"],
                domains["data_classification"],
            ):
                actor_identity, repository, resource_owner, operation, approval_token, deployment_window, data_classification = combo
                out.append(StateTupleV4(
                    actor_identity=actor_identity,
                    delegated_role=delegated_role,
                    repository=repository,
                    branch=branch,
                    environment=environment,
                    resource_owner=resource_owner,
                    operation=operation,
                    approval_token=approval_token,
                    deployment_window=deployment_window,
                    data_classification=data_classification,
                ))
    return out


def executable_reachable_tuples_v4() -> List[StateTupleV4]:
    """Whether remediation operators (`rollback`, `scope-down`) add any
    tuple beyond rank-0 is a checked fact, not assumed (Proposition 0's
    own precedent for v1, `appendix-a-proofs.md`): unlike v1's evidence
    substitution or v2's downroute/retry-delay, neither `rollback` nor
    `scope-down` transforms a field's VALUE into a new domain point --
    `has_recovery_path` only reads the declared (repository, operation)
    table, it does not produce a tuple rank0_reachable_tuples_v4()
    would not already enumerate. executable == rank0 exactly for this
    domain; recomputed and compared directly by
    `checkers/ch_b1_check.py`, not asserted here."""
    return rank0_reachable_tuples_v4()
