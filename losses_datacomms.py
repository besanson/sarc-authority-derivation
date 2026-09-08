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
Milestone E, Step 2 (`prereg/v6.1-authoritybench-amendment.md`, tag
`prereg-p5-v6.1`): six loss predicates for the data-and-communications
domain, transcribed from the GDPR (Regulation (EU) 2016/679,
`gdpr-2016-679` in `verified-citations.json`) and the ePrivacy Directive
(2002/58/EC, `eprivacy-directive-2002-58`), both fetch-verified. Each
predicate is a deterministic boolean function of `StateTupleDataComms`'s
own eight fields -- no LLM, no fuzzy judgement, matching this project's
own standing "no LLM inside the derivation" rule and `losses_v4.py`'s
own precedent."""
from __future__ import annotations

from typing import Callable, Dict

from domain_datacomms import StateTupleDataComms


def unlawful_processing(t: StateTupleDataComms) -> bool:
    """GDPR Art. 6(1): processing is lawful only if at least one of the
    enumerated bases applies; declaring none is the violation."""
    return t.legal_basis == "none_declared"


def special_category_without_basis(t: StateTupleDataComms) -> bool:
    """GDPR Art. 9(1)/9(2): special-category data requires one of ten
    enumerated exceptions; legitimate interest (the Art. 6(1)(f) basis)
    is confirmed NOT among them (fetch-verified, gdpr-info.eu/art-9-gdpr/,
    2026-09-08) -- a basis that would suffice for ordinary data under
    Art. 6 does not suffice here."""
    return t.data_category == "special_category" and t.legal_basis in ("none_declared", "legitimate_interest")


def unsafeguarded_transfer(t: StateTupleDataComms) -> bool:
    """GDPR Art. 44 (Chapter V's general principle for transfers): a
    transfer "shall take place only if the conditions laid down in this
    Chapter are complied with"; `third_country_no_safeguards` names
    that failure directly."""
    return t.destination_region == "third_country_no_safeguards" and t.data_category != "public"


def retention_violation(t: StateTupleDataComms) -> bool:
    """GDPR Art. 5(1)(e), the storage-limitation principle."""
    return t.retention_status == "beyond_declared_period" and t.data_category != "public"


def unconfidential_channel(t: StateTupleDataComms) -> bool:
    """Directive 2002/58/EC (ePrivacy) Art. 5(1): confidentiality of
    communications, prohibiting interception or storage of
    communications content without consent."""
    return t.channel_encryption == "unencrypted" and t.data_category in ("personal", "special_category")


def unfulfilled_erasure(t: StateTupleDataComms) -> bool:
    """GDPR Art. 17, the right to erasure."""
    return t.erasure_request_state == "pending_unhandled" and t.data_category != "public"


def load_loss_registry_datacomms() -> Dict[str, Callable[[StateTupleDataComms], bool]]:
    return {
        "unlawful_processing": unlawful_processing,
        "special_category_without_basis": special_category_without_basis,
        "unsafeguarded_transfer": unsafeguarded_transfer,
        "retention_violation": retention_violation,
        "unconfidential_channel": unconfidential_channel,
        "unfulfilled_erasure": unfulfilled_erasure,
    }
