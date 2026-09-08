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
`prereg-p5-v6.1`): the data-and-communications agent domain -- the third
of AuthorityBench's three registered domains, independently built for
this milestone (procurement and software-and-cloud are v2 and v4,
reused unmodified). Eight candidate observations, one declared
reachability rule, transcribed exactly as registered -- this file does
not adjust the registration to change any outcome.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import product
from typing import Any, Dict, List, Tuple

CANDIDATE_PROPERTIES_DATACOMMS: Tuple[str, ...] = (
    "data_category",
    "legal_basis",
    "recipient_type",
    "destination_region",
    "retention_status",
    "channel_encryption",
    "erasure_request_state",
    "actor_role",
)


@dataclass(frozen=True)
class StateTupleDataComms:
    data_category: str
    legal_basis: str
    recipient_type: str
    destination_region: str
    retention_status: str
    channel_encryption: str
    erasure_request_state: str
    actor_role: str

    def with_property(self, name: str, value: Any) -> "StateTupleDataComms":
        return replace(self, **{name: value})


PROPERTY_DOMAINS_DATACOMMS: Dict[str, List[str]] = {
    "data_category": ["public", "internal", "personal", "special_category"],
    "legal_basis": ["consent", "contract", "legitimate_interest", "legal_obligation", "none_declared"],
    "recipient_type": ["internal_only", "processor_under_contract", "third_party_controller"],
    "destination_region": ["eea", "adequacy_country", "third_country_with_safeguards", "third_country_no_safeguards"],
    "retention_status": ["within_declared_period", "beyond_declared_period"],
    "channel_encryption": ["encrypted", "unencrypted"],
    "erasure_request_state": ["none", "honored", "pending_unhandled"],
    "actor_role": ["agent-support-bot", "agent-analytics-pipeline", "agent-marketing-automation", "agent-admin"],
}

assert set(PROPERTY_DOMAINS_DATACOMMS.keys()) == set(CANDIDATE_PROPERTIES_DATACOMMS)


def _internal_only_stays_in_eea(recipient_type: str, destination_region: str) -> bool:
    """The one declared reachability rule (`prereg/v6.1-authoritybench-
    amendment.md`): data that never leaves the organisation cannot, by
    construction, be a cross-border transfer. Narrows the `recipient_
    type` x `destination_region` product from 12 pairs to 9 (internal_
    only pairs only with eea; the other two recipient types pair with
    all four regions)."""
    if recipient_type == "internal_only":
        return destination_region == "eea"
    return True


def rank0_reachable_tuples_datacomms() -> List[StateTupleDataComms]:
    """The full declared product of all eight fields' domains, filtered
    by the one declared reachability rule -- 4x5x9x2x2x3x4 = 8,640
    tuples (registered, not sampled)."""
    fields = CANDIDATE_PROPERTIES_DATACOMMS
    domains = [PROPERTY_DOMAINS_DATACOMMS[f] for f in fields]
    tuples = []
    for combo in product(*domains):
        values = dict(zip(fields, combo))
        if _internal_only_stays_in_eea(values["recipient_type"], values["destination_region"]):
            tuples.append(StateTupleDataComms(**values))
    return tuples


def executable_reachable_tuples_datacomms() -> List[StateTupleDataComms]:
    """No remediation operator is declared for this domain (unlike v2's
    downroute/retry-delay) -- the executable-reachable set equals
    rank-0 exactly, the same choice v4's own domain already made for
    the identical reason (`prereg/v4-realistic-domain.md`: "no
    remediation-reachable transformation for this domain")."""
    return rank0_reachable_tuples_datacomms()
