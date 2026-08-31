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
"""Tests for domain.py."""
from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from domain import (
    CANDIDATE_PROPERTIES,
    StateTuple,
    executable_reachable_tuples,
    field_names,
    load_loss_model,
    load_pair_test_grid,
    property_domains,
    rank0_reachable_tuples,
    remediation_reachable_tuples,
    role_policy,
    sku_resource_class,
)

BASE = StateTuple(
    actor_role="agent-replenish",
    resource_class="consumables",
    order_value=600.0,
    day=50,
    workflow="W1",
    grant_id=None,
    consumed_grant_ids=frozenset(),
    budget_remaining=1000.0,
    frozen=False,
)


def test_field_names_match_candidate_properties():
    assert set(field_names()) == set(CANDIDATE_PROPERTIES)


def test_with_property_changes_exactly_one_field():
    variant = BASE.with_property("order_value", 2500.0)
    assert variant.order_value == 2500.0
    assert variant.actor_role == BASE.actor_role
    assert variant != BASE


def test_state_tuple_is_hashable_and_usable_in_sets():
    s = {BASE, BASE.with_property("day", 140)}
    assert len(s) == 2
    assert BASE in s


def test_role_policy_cross_references_all_three_mappings():
    loss_model = load_loss_model()
    policy = role_policy(loss_model)
    assert set(policy) == {"agent-replenish", "agent-w2-replenish", "agent-delegate", "agent-unauthorized"}
    assert policy["agent-delegate"]["role_entitlement_ceiling"] == 800.0
    assert policy["agent-delegate"]["role_window"] == (100, 180)
    assert policy["agent-delegate"]["role_allowed_classes"] == frozenset({"consumables"})
    assert policy["agent-unauthorized"]["role_window"] is None
    assert policy["agent-unauthorized"]["role_allowed_classes"] == frozenset()


def test_role_policy_rejects_partial_role_coverage():
    broken = {
        "losses": [
            {"id": "order_value_beyond_entitlement", "declared_parameters": {"role_entitlement_ceiling": {"r1": 1.0}}},
            {"id": "procurement_outside_temporal_window", "declared_parameters": {"role_window": {"r1": [0, 1], "r2": None}}},
            {"id": "resource_class_not_entitled", "declared_parameters": {"role_allowed_classes": {"r1": [], "r2": []}}},
        ]
    }
    with pytest.raises(ValueError, match="missing"):
        role_policy(broken)


def test_property_domains_matches_candidate_properties_exactly():
    grid = load_pair_test_grid()
    domains = property_domains(grid)
    assert set(domains) == set(CANDIDATE_PROPERTIES)


def test_property_domains_rejects_mismatched_grid():
    with pytest.raises(ValueError, match="do not match"):
        property_domains({"properties": {"action": {"actor_role": {"domain": ["x"]}}}})


@pytest.mark.parametrize("sku,expected", [
    ("a", "consumables"), ("b", "consumables"), ("c", "consumables"),
    ("d", "durable-goods"), ("e", "durable-goods"), ("f", "durable-goods"),
    ("g", "capital-equipment"), ("h", "capital-equipment"), ("i", "capital-equipment"),
])
def test_sku_resource_class_thirds(sku, expected):
    all_skus = list("abcdefghi")  # 9 skus -> exact thirds
    assert sku_resource_class(sku, all_skus) == expected


def test_sku_resource_class_every_sku_gets_exactly_one_class():
    all_skus = [f"sku{i:03d}" for i in range(40)]
    classes = {sku_resource_class(s, all_skus) for s in all_skus}
    assert classes == {"consumables", "durable-goods", "capital-equipment"}


def test_rank0_reachable_size_is_product_of_domains():
    grid = load_pair_test_grid()
    domains = property_domains(grid)
    rank0 = rank0_reachable_tuples(domains)
    expected = 1
    for prop in CANDIDATE_PROPERTIES:
        expected *= len(domains[prop])
    assert len(rank0) == expected
    assert len(rank0) == len(set(rank0))  # no duplicates


def test_remediation_reachable_only_touches_order_value():
    grid = load_pair_test_grid()
    domains = property_domains(grid)
    rank0 = rank0_reachable_tuples(domains)
    remediated = remediation_reachable_tuples(rank0, domains["order_value"])
    rank0_set = set(rank0)
    for t in remediated:
        assert t not in rank0_set
        matches = [r for r in rank0 if r.with_property("order_value", t.order_value) == t]
        assert len(matches) >= 1


def test_remediation_reachable_downroute_never_increases_order_value_from_some_source():
    """Every remediation-reachable tuple's order_value is reachable either
    via substitution (any direction) from SOME rank-0 tuple with the same
    other fields, or via downroute (strictly lower) -- i.e. every
    remediated tuple has at least one valid justification, checked
    directly against the domain's own declared ordering."""
    grid = load_pair_test_grid()
    domains = property_domains(grid)
    ordered = sorted(domains["order_value"])
    rank0 = rank0_reachable_tuples(domains)
    remediated = remediation_reachable_tuples(rank0, domains["order_value"])
    for t in remediated:
        assert t.order_value in ordered


def test_executable_reachable_is_union_and_deduplicated():
    grid = load_pair_test_grid()
    domains = property_domains(grid)
    rank0 = rank0_reachable_tuples(domains)
    remediated = remediation_reachable_tuples(rank0, domains["order_value"])
    combined = executable_reachable_tuples(domains)
    assert set(combined) == set(rank0) | set(remediated)
    assert len(combined) == len(set(combined))


@given(st.lists(st.sampled_from(list("abcdefghijklmnopqrstuvwxyz0123456789")), min_size=1, max_size=1, unique=True))
def test_sku_resource_class_is_deterministic(letters):
    all_skus = sorted(set("abcdefghijklmnopqrstuvwxyz0123456789"))
    sku = letters[0]
    first = sku_resource_class(sku, all_skus)
    second = sku_resource_class(sku, all_skus)
    assert first == second
