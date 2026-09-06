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
Mutation testing hard gate (v0.3, B4: `make mutate` no longer swallows a
failing score with `|| true`). Reads `mutants/mutmut-cicd-stats.json`
(written by `mutmut export-cicd-stats`, run immediately before this by
`make mutate`) and fails if the kill score -- killed / (killed +
survived), the same formula ADR-003-mutation-testing.md's own baseline
uses -- is below 0.85 on participation.py, derive.py, and reduct.py
(pyproject.toml's `[tool.mutmut]` target set), or if any mutant recorded
`no_tests` (a real coverage gap, not a hard-to-kill survivor -- ADR-003's
own first pass treated a nonzero no_tests count as a bug to fix, not an
acceptable score component, and this gate holds that line going forward).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

THRESHOLD = 0.85
STATS_PATH = Path("mutants/mutmut-cicd-stats.json")


def run(stats_path: Path = STATS_PATH) -> Dict[str, Any]:
    stats = json.loads(stats_path.read_text())
    killed = stats["killed"]
    survived = stats["survived"]
    no_tests = stats["no_tests"]
    denominator = killed + survived
    kill_score = (killed / denominator) if denominator else 0.0

    return {
        "killed": killed,
        "survived": survived,
        "no_tests": no_tests,
        "total": stats["total"],
        "kill_score": kill_score,
        "threshold": THRESHOLD,
        "meets_threshold": kill_score >= THRESHOLD,
        "no_coverage_gaps": no_tests == 0,
        "passes": kill_score >= THRESHOLD and no_tests == 0,
    }


def main() -> None:
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    print(
        f"\nMutation kill score: {result['kill_score']:.4f} "
        f"({result['killed']}/{result['killed'] + result['survived']}), "
        f"threshold {result['threshold']}, no_tests={result['no_tests']}"
    )
    if not result["passes"]:
        if not result["meets_threshold"]:
            print(f"FAIL: kill score {result['kill_score']:.4f} is below the {THRESHOLD} threshold.")
        if not result["no_coverage_gaps"]:
            print(f"FAIL: {result['no_tests']} mutant(s) had no covering test at all (a coverage gap).")
        raise SystemExit(1)
    print("PASS")


if __name__ == "__main__":
    main()
