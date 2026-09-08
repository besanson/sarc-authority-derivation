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
"""Tests for domain_v4.py/losses_v4.py (prereg/v4-realistic-domain.md,
tag prereg-p5-v4): the reachability rules and each loss predicate's own
satisfiability, checked directly against the real domain -- small enough
(51,840 rank-0 tuples) not to need a synthetic stand-in."""
from __future__ import annotations

from domain_v4 import CANDIDATE_PROPERTIES_V4, PROPERTY_DOMAINS_V4, has_recovery_path, rank0_reachable_tuples_v4
from losses_v4 import load_loss_registry_v4
from losses import m_verdict


def test_has_recovery_path_exact_boundary():
    # deploy always has rollback declared, on every repository.
    for repo in PROPERTY_DOMAINS_V4["repository"]:
        assert has_recovery_path(repo, "deploy") is True
    # delete has scope-down declared ONLY on repo-internal-tools.
    assert has_recovery_path("repo-internal-tools", "delete") is True
    assert has_recovery_path("repo-billing", "delete") is False
    assert has_recovery_path("repo-public-website", "delete") is False
    # no other operation has any declared recovery path, on any repository.
    for repo in PROPERTY_DOMAINS_V4["repository"]:
        for op in ("read", "write", "grant_role"):
            assert has_recovery_path(repo, op) is False


def test_rank0_size_matches_declared_domain_product_before_constraints():
    raw_product = 1
    for values in PROPERTY_DOMAINS_V4.values():
        raw_product *= len(values)
    assert raw_product == 51_840


def test_branch_environment_pairing_is_one_to_one():
    reachable = rank0_reachable_tuples_v4()
    pairing = {t.branch: t.environment for t in reachable}
    assert pairing == {"main": "production", "staging": "staging", "feature": "development"}
    for t in reachable:
        assert (t.branch, t.environment) in [("main", "production"), ("staging", "staging"), ("feature", "development")]


def test_contractor_readonly_never_reaches_tenant_b():
    reachable = rank0_reachable_tuples_v4()
    assert not any(t.delegated_role == "role-contractor-readonly" and t.resource_owner == "tenant-b" for t in reachable)


def test_rank0_reachable_every_field_takes_every_declared_value():
    """Every field a StateTupleV4 is built from must actually carry its
    OWN loop variable's value, not a placeholder -- catches a
    tuple-construction bug (a field silently pinned to one value or
    None) that no per-predicate test would notice for a field none of
    the six losses reads directly (`actor_identity`, `deployment_window`)."""
    reachable = rank0_reachable_tuples_v4()
    for field, declared_values in PROPERTY_DOMAINS_V4.items():
        seen = {getattr(t, field) for t in reachable}
        assert seen == set(declared_values), field


def test_rank0_reachable_exact_size_after_constraints():
    """3 branch/environment pairings (not 9) x [3 roles x 2 tenants + 1
    role (contractor-readonly) x 1 tenant = 7] x 720 (the other seven
    fields' free product: 4x3x5x2x2x3) = 15,120 -- hand-derived
    independently of the implementation, not copied from its own output."""
    reachable = rank0_reachable_tuples_v4()
    assert len(reachable) == 15_120


def test_rank0_reachable_per_role_tenant_count():
    reachable = rank0_reachable_tuples_v4()
    for role in ["role-owner", "role-deployer", "role-security-admin"]:
        role_tuples = [t for t in reachable if t.delegated_role == role]
        assert len(role_tuples) == 3 * 2 * 720, role
        assert {t.resource_owner for t in role_tuples} == {"tenant-a", "tenant-b"}
    contractor_tuples = [t for t in reachable if t.delegated_role == "role-contractor-readonly"]
    assert len(contractor_tuples) == 3 * 1 * 720
    assert {t.resource_owner for t in contractor_tuples} == {"tenant-a"}


def test_deployer_does_reach_tenant_b_despite_narrower_declared_scope():
    """The reachability fix (prereg's own note): role-deployer must
    remain reachable against tenant-b so cross_tenant_action has a live
    case to catch -- this is the regression test for the exact bug found
    and fixed while drafting the prereg."""
    reachable = rank0_reachable_tuples_v4()
    assert any(t.delegated_role == "role-deployer" and t.resource_owner == "tenant-b" for t in reachable)


def test_every_loss_predicate_is_satisfiable_on_the_reachable_set():
    """Registered domain design goal: none of the six predicates is
    vacuous -- each must fire for at least one reachable tuple, or the
    predicate's own registration was broken (as `cross_tenant_action`'s
    first draft was, caught here before commit)."""
    reachable = rank0_reachable_tuples_v4()
    registry = load_loss_registry_v4()
    for name, predicate in registry.items():
        assert any(predicate(t) for t in reachable), f"{name} never fires on any reachable tuple"


def test_m_verdict_is_domain_agnostic_over_state_tuple_v4():
    reachable = rank0_reachable_tuples_v4()
    registry = load_loss_registry_v4()
    some_violation = next(t for t in reachable if any(p(t) for p in registry.values()))
    assert m_verdict(some_violation, registry) is True
    some_safe = next(t for t in reachable if not any(p(t) for p in registry.values()))
    assert m_verdict(some_safe, registry) is False


def test_candidate_properties_match_state_tuple_fields():
    from dataclasses import fields
    reachable = rank0_reachable_tuples_v4()
    field_names = {f.name for f in fields(reachable[0])}
    assert set(CANDIDATE_PROPERTIES_V4) == field_names
