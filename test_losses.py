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
"""Tests for losses.py -- one positive and one negative case per
declared loss, plus the registry cross-check."""
from __future__ import annotations

import pytest

from domain import StateTuple, load_loss_model
from losses import evaluate_losses, load_loss_registry, m_verdict

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


@pytest.fixture(scope="module")
def registry():
    return load_loss_registry(load_loss_model())


def test_registry_has_all_six_declared_losses(registry):
    assert set(registry) == {
        "order_value_beyond_entitlement",
        "procurement_outside_temporal_window",
        "resource_class_not_entitled",
        "replayed_consumed_grant",
        "spend_against_depleted_delegated_budget",
        "action_on_frozen_control_state",
    }


def test_registry_rejects_undeclared_predicate():
    with pytest.raises(ValueError, match="no registered implementation"):
        load_loss_registry({"losses": [{"id": "x", "predicate": "not_a_real_predicate"}]})


def test_base_tuple_is_clean(registry):
    assert m_verdict(BASE, registry) is False
    assert all(v is False for v in evaluate_losses(BASE, registry).values())


def test_order_value_beyond_entitlement(registry):
    assert registry["order_value_beyond_entitlement"](BASE.with_property("order_value", 2500.0)) is True
    assert registry["order_value_beyond_entitlement"](BASE.with_property("order_value", 1200.0)) is False
    delegate = BASE.with_property("actor_role", "agent-delegate")
    assert registry["order_value_beyond_entitlement"](delegate.with_property("order_value", 1200.0)) is True


def test_procurement_outside_temporal_window(registry):
    delegate = BASE.with_property("actor_role", "agent-delegate").with_property("day", 140)
    assert registry["procurement_outside_temporal_window"](delegate) is False
    assert registry["procurement_outside_temporal_window"](delegate.with_property("day", 50)) is True
    unauthorized = BASE.with_property("actor_role", "agent-unauthorized")
    assert registry["procurement_outside_temporal_window"](unauthorized) is True


def test_resource_class_not_entitled(registry):
    delegate = BASE.with_property("actor_role", "agent-delegate")
    assert registry["resource_class_not_entitled"](delegate.with_property("resource_class", "consumables")) is False
    assert registry["resource_class_not_entitled"](delegate.with_property("resource_class", "capital-equipment")) is True


def test_replayed_consumed_grant(registry):
    fresh = BASE.with_property("grant_id", "g1")
    assert registry["replayed_consumed_grant"](fresh) is False
    replayed = fresh.with_property("consumed_grant_ids", frozenset({"g1"}))
    assert registry["replayed_consumed_grant"](replayed) is True
    no_grant = BASE.with_property("consumed_grant_ids", frozenset({"g1"}))
    assert registry["replayed_consumed_grant"](no_grant) is False


def test_spend_against_depleted_delegated_budget(registry):
    assert registry["spend_against_depleted_delegated_budget"](BASE.with_property("budget_remaining", 500.0)) is True
    assert registry["spend_against_depleted_delegated_budget"](BASE.with_property("budget_remaining", 1000.0)) is False


def test_action_on_frozen_control_state(registry):
    assert registry["action_on_frozen_control_state"](BASE.with_property("frozen", True)) is True
    assert registry["action_on_frozen_control_state"](BASE) is False


def test_m_verdict_is_any_loss_firing(registry):
    two_losses = BASE.with_property("order_value", 2500.0).with_property("frozen", True)
    fired = evaluate_losses(two_losses, registry)
    assert fired["order_value_beyond_entitlement"] is True
    assert fired["action_on_frozen_control_state"] is True
    assert m_verdict(two_losses, registry) is True
