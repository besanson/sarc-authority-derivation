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
"""Tests for losses_datacomms.py -- one positive case and one or more
negative ("near-miss": flip exactly one clause back to safe) cases per
declared loss, mirroring test_losses_v4.py's own precision so a
boundary mutation (==/!=, and/or, in/not in) is caught, not just "fires
somewhere on the reachable set"."""
from __future__ import annotations

from domain_datacomms import StateTupleDataComms
from losses_datacomms import (
    load_loss_registry_datacomms,
    retention_violation,
    special_category_without_basis,
    unconfidential_channel,
    unfulfilled_erasure,
    unlawful_processing,
    unsafeguarded_transfer,
)

BASE = StateTupleDataComms(
    data_category="personal",
    legal_basis="consent",
    recipient_type="internal_only",
    destination_region="eea",
    retention_status="within_declared_period",
    channel_encryption="encrypted",
    erasure_request_state="none",
    actor_role="agent-support-bot",
)


def _all_false(t: StateTupleDataComms, *exclude: str) -> None:
    for name, predicate in load_loss_registry_datacomms().items():
        if name in exclude:
            continue
        assert predicate(t) is False, f"{name} unexpectedly fired on {t}"


def test_base_tuple_is_clean():
    _all_false(BASE)


def test_unlawful_processing_positive_and_negative():
    violating = BASE.with_property("legal_basis", "none_declared")
    assert unlawful_processing(violating) is True
    _all_false(violating, "unlawful_processing")

    safe = BASE.with_property("legal_basis", "legitimate_interest")
    assert unlawful_processing(safe) is False


def test_special_category_without_basis_positive_and_negatives():
    violating = BASE.with_property("data_category", "special_category").with_property("legal_basis", "legitimate_interest")
    assert special_category_without_basis(violating) is True
    _all_false(violating, "special_category_without_basis")

    # legitimate_interest alone (ordinary personal data) does not violate Art. 9 (only Art. 6, already covered).
    assert special_category_without_basis(BASE.with_property("legal_basis", "legitimate_interest")) is False
    # special_category with a valid basis (consent) is safe.
    assert special_category_without_basis(BASE.with_property("data_category", "special_category")) is False


def test_unsafeguarded_transfer_positive_and_negatives():
    violating = (
        BASE.with_property("recipient_type", "third_party_controller")
        .with_property("destination_region", "third_country_no_safeguards")
    )
    assert unsafeguarded_transfer(violating) is True
    _all_false(violating, "unsafeguarded_transfer")

    public_exempt = violating.with_property("data_category", "public")
    assert unsafeguarded_transfer(public_exempt) is False

    safeguarded = (
        BASE.with_property("recipient_type", "third_party_controller")
        .with_property("destination_region", "third_country_with_safeguards")
    )
    assert unsafeguarded_transfer(safeguarded) is False


def test_retention_violation_positive_and_negatives():
    violating = BASE.with_property("retention_status", "beyond_declared_period")
    assert retention_violation(violating) is True
    _all_false(violating, "retention_violation")

    public_exempt = violating.with_property("data_category", "public")
    assert retention_violation(public_exempt) is False


def test_unconfidential_channel_positive_and_negatives():
    violating = BASE.with_property("channel_encryption", "unencrypted")
    assert unconfidential_channel(violating) is True
    _all_false(violating, "unconfidential_channel")

    public_exempt = violating.with_property("data_category", "public")
    assert unconfidential_channel(public_exempt) is False

    internal_exempt = violating.with_property("data_category", "internal")
    assert unconfidential_channel(internal_exempt) is False

    special_category_also_fires = violating.with_property("data_category", "special_category")
    assert unconfidential_channel(special_category_also_fires) is True


def test_unfulfilled_erasure_positive_and_negatives():
    violating = BASE.with_property("erasure_request_state", "pending_unhandled")
    assert unfulfilled_erasure(violating) is True
    _all_false(violating, "unfulfilled_erasure")

    public_exempt = violating.with_property("data_category", "public")
    assert unfulfilled_erasure(public_exempt) is False

    honored = BASE.with_property("erasure_request_state", "honored")
    assert unfulfilled_erasure(honored) is False


def test_registry_has_all_six_declared_losses():
    assert set(load_loss_registry_datacomms().keys()) == {
        "unlawful_processing",
        "special_category_without_basis",
        "unsafeguarded_transfer",
        "retention_violation",
        "unconfidential_channel",
        "unfulfilled_erasure",
    }
