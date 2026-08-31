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
Phase 2: exhaustive verification of the grant mechanism's single-use
invariant (grant.py) -- at most one 'consumed' (admitted) event per
grant_id, ever, and only for the sealed action it was issued against.

Enumerated domain: two grant_ids (g1, g2), each issued for a distinct
sealed action (h1, h2); every sequence of length 0-3 of consume attempts
drawn from the 4 (grant_id, presented_action) combinations {g1,g2} x
{h1,h2} -- 1 + 4 + 16 + 64 = 85 sequences, the entire relevant finite
state space for this invariant (a longer sequence cannot exercise a new
case: once a grant_id has produced one 'consumed' event, every
subsequent attempt for it is symmetric to the cases already covered).
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from grant import GrantLedger

OUTPUT_PATH = Path("out/checkers/grant_check.json")

GRANT_IDS = ("g1", "g2")
ACTIONS = {"h1": {"content": "action-1"}, "h2": {"content": "action-2"}}
COMBINATIONS: List[Tuple[str, str]] = [(g, a) for g in GRANT_IDS for a in ACTIONS]
MAX_SEQUENCE_LENGTH = 3


def run_sequence(seq: Tuple[Tuple[str, str], ...]) -> Dict[str, int]:
    ledger = GrantLedger()
    ledger.issue("g1", ACTIONS["h1"], decision_id=0, day=0)
    ledger.issue("g2", ACTIONS["h2"], decision_id=0, day=0)
    admits_by_grant: Dict[str, int] = {g: 0 for g in GRANT_IDS}
    for step, (grant_id, action_key) in enumerate(seq, start=1):
        admitted = ledger.consume(grant_id, ACTIONS[action_key], decision_id=step, day=step)
        if admitted:
            admits_by_grant[grant_id] += 1
            # binding: an admitted consumption must have presented the
            # exact action the grant was issued for.
            assert (grant_id == "g1" and action_key == "h1") or (grant_id == "g2" and action_key == "h2"), (
                f"grant {grant_id} admitted a mismatched action {action_key}"
            )
    return admits_by_grant


def run() -> Dict[str, Any]:
    violations = []
    sequences_checked = 0
    for length in range(0, MAX_SEQUENCE_LENGTH + 1):
        for seq in itertools.product(COMBINATIONS, repeat=length):
            sequences_checked += 1
            admits = run_sequence(seq)
            for grant_id, count in admits.items():
                if count > 1:
                    violations.append({"sequence": seq, "grant_id": grant_id, "admit_count": count})
    return {
        "sequences_checked": sequences_checked,
        "max_sequence_length": MAX_SEQUENCE_LENGTH,
        "violations": violations,
        "single_use_holds_exhaustively": violations == [],
    }


def main() -> None:
    result = run()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True, default=str))
    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    if not result["single_use_holds_exhaustively"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
