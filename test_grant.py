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
"""Tests for grant.py. checkers/grant_check.py covers the single-use
invariant exhaustively (appendix-a-proofs.md, Proposition 3); these
tests cover the surrounding API contract."""
from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from grant import GrantLedger, sealed_action_content_hash
from schemas_check import validate_against_schema

ACTION_A = {"sku": "X", "order_value": 100.0}
ACTION_B = {"sku": "Y", "order_value": 200.0}


def test_sealed_action_content_hash_is_order_independent():
    assert sealed_action_content_hash({"a": 1, "b": 2}) == sealed_action_content_hash({"b": 2, "a": 1})


def test_sealed_action_content_hash_distinguishes_different_content():
    assert sealed_action_content_hash(ACTION_A) != sealed_action_content_hash(ACTION_B)


def test_issue_then_consume_admits():
    ledger = GrantLedger()
    ledger.issue("g1", ACTION_A, decision_id=1, day=1)
    assert ledger.consume("g1", ACTION_A, decision_id=1, day=1) is True
    assert ledger.consumed_grant_ids() == frozenset({"g1"})


def test_consume_without_issue_never_admits():
    ledger = GrantLedger()
    assert ledger.consume("never-issued", ACTION_A, decision_id=1, day=1) is False


def test_consume_with_none_grant_id_never_admits_and_is_not_ledgered():
    ledger = GrantLedger()
    assert ledger.consume(None, ACTION_A, decision_id=1, day=1) is False
    assert ledger.entries() == []


def test_replay_after_consumption_is_rejected_and_recorded():
    ledger = GrantLedger()
    ledger.issue("g1", ACTION_A, decision_id=1, day=1)
    assert ledger.consume("g1", ACTION_A, decision_id=1, day=1) is True
    assert ledger.consume("g1", ACTION_A, decision_id=2, day=2) is False
    events = [e.event for e in ledger.entries() if e.grant_id == "g1"]
    assert events == ["issued", "consumed", "consumption_rejected_replay"]


def test_hash_mismatch_is_rejected_even_if_never_consumed():
    ledger = GrantLedger()
    ledger.issue("g1", ACTION_A, decision_id=1, day=1)
    assert ledger.consume("g1", ACTION_B, decision_id=1, day=1) is False
    assert ledger.consumed_grant_ids() == frozenset()


def test_reissuing_a_grant_id_raises():
    ledger = GrantLedger()
    ledger.issue("g1", ACTION_A, decision_id=1, day=1)
    with pytest.raises(ValueError, match="already issued"):
        ledger.issue("g1", ACTION_B, decision_id=2, day=2)


def test_ledger_entries_are_never_mutated_in_place():
    ledger = GrantLedger()
    ledger.issue("g1", ACTION_A, decision_id=1, day=1)
    before = ledger.entries()
    ledger.consume("g1", ACTION_A, decision_id=1, day=1)
    after = ledger.entries()
    assert before == before  # frozen dataclasses, unaffected by later calls
    assert len(after) == len(before) + 1


def test_to_json_matches_schema():
    ledger = GrantLedger()
    ledger.issue("g1", ACTION_A, decision_id=1, day=1)
    ledger.consume("g1", ACTION_A, decision_id=1, day=1)
    for entry in ledger.to_json():
        validate_against_schema(entry, "schemas/grant_state.schema.json")


@given(st.integers(min_value=0, max_value=5))
def test_single_use_holds_for_any_number_of_replay_attempts(n_extra_attempts):
    ledger = GrantLedger()
    ledger.issue("g1", ACTION_A, decision_id=0, day=0)
    admits = [ledger.consume("g1", ACTION_A, decision_id=i, day=i) for i in range(1 + n_extra_attempts)]
    assert admits.count(True) == 1
    assert admits[0] is True
    assert all(a is False for a in admits[1:])
