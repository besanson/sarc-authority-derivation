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
Phase 2: the consumable execution-grant mechanism. A grant is a token
bound to the content hash of one sealed (post-remediation) final action,
single-use: issuing it records "issued"; the first matching consumption
records "consumed" and admits; any later consumption attempt for the
same grant_id -- or one whose presented action hash does not match what
the grant was sealed for -- is rejected and recorded, never silently
dropped, so loss-model.yaml's replayed_consumed_grant and CH-A3's
replay-admission count are both auditable from the ledger alone.

State is an append-only list of records (schemas/grant_state.schema.json)
mirroring the imported baseline's governed-buffer write-history design
(composition.py's Evidence Set / buffer write history): every issuance
and every consumption attempt is a new appended entry, never an in-place
mutation of a single mutable "consumed" flag -- replay detection is
verifiable by scanning the ledger, not by trusting one bit.

The grant predicate (grant_admits_or_none) is registered into the
authority gate's own predicate registry the same way loss-model.yaml's
other predicates are (losses.py) -- see participation.py's CANDIDATE_
PROPERTIES: grant_id and consumed_grant_ids are already two of the nine,
so the grant mechanism's own state is exactly what Definition 1 already
derives as authority-bearing (replayed_consumed_grant), not a bolt-on
outside the derivation.

SEED = 26313 (inherited; grant_id generation in Phase 3 experiments uses
the seeded RNG, not this module, which is deterministic given its inputs)
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


def sealed_action_content_hash(sealed_action: Dict[str, Any]) -> str:
    """sha256 over the canonical (sorted-key) JSON encoding of the sealed
    final action -- the single-use binding target. Canonical encoding
    means two calls on equal dicts always hash identically regardless of
    key insertion order, the same property checkers/_provenance.py's
    inputs_hash() relies on for its own byte-for-byte determinism."""
    canonical = json.dumps(sealed_action, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class GrantLedgerEntry:
    schema_version: int
    grant_id: str
    sealed_action_content_hash: str
    event: str  # "issued" | "consumed" | "consumption_rejected_replay"
    decision_id: int
    day: int


class GrantLedger:
    """Append-only. No entry is ever mutated or removed once written."""

    def __init__(self) -> None:
        self._entries: List[GrantLedgerEntry] = []

    def entries(self) -> List[GrantLedgerEntry]:
        return list(self._entries)

    def consumed_grant_ids(self) -> frozenset:
        """The set loss-model.yaml's replayed_consumed_grant and
        domain.StateTuple.consumed_grant_ids both mean: every grant_id
        with at least one 'consumed' entry."""
        return frozenset(e.grant_id for e in self._entries if e.event == "consumed")

    def _issued_hash(self, grant_id: str) -> Optional[str]:
        for e in self._entries:
            if e.grant_id == grant_id and e.event == "issued":
                return e.sealed_action_content_hash
        return None

    def issue(self, grant_id: str, sealed_action: Dict[str, Any], decision_id: int, day: int) -> GrantLedgerEntry:
        if self._issued_hash(grant_id) is not None:
            raise ValueError(f"grant_id {grant_id!r} already issued -- grant ids must be fresh")
        entry = GrantLedgerEntry(
            schema_version=1,
            grant_id=grant_id,
            sealed_action_content_hash=sealed_action_content_hash(sealed_action),
            event="issued",
            decision_id=decision_id,
            day=day,
        )
        self._entries.append(entry)
        return entry

    def consume(
        self, grant_id: Optional[str], presented_sealed_action: Dict[str, Any], decision_id: int, day: int
    ) -> bool:
        """Returns True (admitted) iff grant_id was issued, has not
        already been consumed, and presented_sealed_action's content hash
        matches exactly what it was issued for. Every attempt -- admitted
        or not -- appends a ledger entry; nothing is silently dropped."""
        if grant_id is None:
            return False
        issued_hash = self._issued_hash(grant_id)
        already_consumed = grant_id in self.consumed_grant_ids()
        presented_hash = sealed_action_content_hash(presented_sealed_action)
        admits = issued_hash is not None and not already_consumed and presented_hash == issued_hash
        entry = GrantLedgerEntry(
            schema_version=1,
            grant_id=grant_id,
            sealed_action_content_hash=presented_hash,
            event="consumed" if admits else "consumption_rejected_replay",
            decision_id=decision_id,
            day=day,
        )
        self._entries.append(entry)
        return admits

    def to_json(self) -> List[Dict[str, Any]]:
        return [asdict(e) for e in self._entries]
