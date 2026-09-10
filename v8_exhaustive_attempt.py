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
Package D (`prereg/v8-large-realistic-domain.md`, tag `prereg-p5-v8`):
the registered 300-second exhaustive `reduct.exact_reducts()` attempt on
the real 35-property, 27,000-tuple domain -- a pure complexity-scaling
data point, NOT a prerequisite for CH-C1 or CH-C2 (both decided by
`checkers/ch_c1_check.py`/`checkers/ch_c2_check.py` via `compute_core`'s
`O(n)` witness search and solver optimality, neither of which needs
this). Reuses `discernibility_scaling_benchmark.py`'s own generic
`exhaustive_with_budget` (a separate-process timeout wrapper around
`exact_reducts()`, already exercised at up to 100 synthetic properties
in `prereg/v5.3-combinatorial-hardness-scaling.md`) unmodified.

Deliberately NOT wired into `make formal`/`make release-check`: those
already run this file's own two checkers, which together take several
minutes (the discernibility-family construction's own `O(reachable^2)`
cost, `discernibility.py`'s docstring); adding a further registered
300-second budget to EVERY future release-check run for a data point
neither decision rule depends on would be pure overhead, not a gate --
`make v8-exhaustive-attempt` runs this on demand instead, mirroring how
`discernibility-scaling`/`discernibility-hardness-scaling` are already
their own separate Makefile targets, not part of `formal`."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from discernibility_scaling_benchmark import EXHAUSTIVE_BUDGET_SECONDS, exhaustive_with_budget
from domain_v8 import CANDIDATE_PROPERTIES_V8, executable_reachable_tuples_v8
from losses_v8 import load_loss_registry_v8

OUTPUT_PATH = Path("out/results/v8_exhaustive_attempt.json")


def run() -> Dict[str, Any]:
    reachable = executable_reachable_tuples_v8()
    registry = load_loss_registry_v8()
    result = exhaustive_with_budget(CANDIDATE_PROPERTIES_V8, reachable, registry, EXHAUSTIVE_BUDGET_SECONDS)
    return {
        "domain": "v8-large-realistic-domain",
        "candidate_property_count": len(CANDIDATE_PROPERTIES_V8),
        "reachable_tuples_swept": len(reachable),
        "budget_seconds": EXHAUSTIVE_BUDGET_SECONDS,
        "size_7_subset_count_for_reference": 6_724_520,  # C(35, 7), registered in the prereg
        **result,
    }


def main() -> None:
    result = run()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"\nExhaustive reduct enumeration feasible within {EXHAUSTIVE_BUDGET_SECONDS}s: {result['feasible']}")


if __name__ == "__main__":
    main()
