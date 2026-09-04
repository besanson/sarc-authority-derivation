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
Proposition 0 (round-0 adjudicator review, finding F0; NOVELTY.md's
Amendment; appendix-a-proofs.md): measures, exhaustively over the full
declared grid (not a sample), whether remediation-reachability adds any
tuple beyond rank-0 in this artifact's current formal model.

This is a MEASUREMENT, not an enforced invariant: the checker reports
whatever the current model actually does, exit 1 only on an internal
inconsistency (the union not equal to rank-0 plus the reported new
tuples), not on redundancy itself -- v0.2 is explicitly scoped to change
this measurement, and this checker's job is to keep recording it
accurately across that change, not to gate on one particular answer.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from domain import (
    executable_reachable_tuples,
    load_pair_test_grid,
    property_domains,
    rank0_reachable_tuples,
    remediation_reachable_tuples,
)

OUTPUT_PATH = Path("out/checkers/reachability_check.json")


def run() -> Dict[str, Any]:
    grid = load_pair_test_grid()
    domains = property_domains(grid)
    rank0 = rank0_reachable_tuples(domains)
    remediated_new = remediation_reachable_tuples(rank0, domains["order_value"])
    combined = executable_reachable_tuples(domains)

    rank0_set = set(rank0)
    combined_set = set(combined)
    internally_consistent = combined_set == rank0_set | set(remediated_new)

    return {
        "rank0_size": len(rank0),
        "remediation_reachable_new_tuples": len(remediated_new),
        "executable_reachable_size": len(combined),
        "remediation_is_reachability_redundant": len(remediated_new) == 0,
        "internally_consistent": internally_consistent,
    }


def main() -> None:
    result = run()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["internally_consistent"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
