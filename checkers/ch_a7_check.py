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
CH-A7 (prereg/v2-reachability-redesign.md, tag prereg-p5-v2): new,
targeted, sharp, machine-checked ablation on the remediation-induced
property.

Decision rule: compute P* twice over the same seven-loss, ten-property
model -- (a) rank-0 union downroute-reachable union retry-delay-
reachable (domain.executable_reachable_tuples_v2(), the full v2 set) and
(b) rank-0 union retry-delay-reachable only, downroute excluded. CH-A7
is SUPPORTED iff min_order_quantity is an element of P*(a) but not of
P*(b) -- downroute demonstrated derivation-relevant for this specific
property, machine-checked, not asserted. If membership is unchanged
between (a) and (b), CH-A7 is NOT SUPPORTED, printed as such (this
project's own discipline for a registered hypothesis that does not
hold), not smoothed over -- exit status is never used to force one
outcome; a two-sided registered hypothesis exits 0 either way.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from domain import (
    CANDIDATE_PROPERTIES_V2,
    executable_reachable_tuples_v2,
    load_loss_model,
    load_pair_test_grid,
    property_domains_v2,
    rank0_reachable_tuples_v2,
    retry_delay_reachable_tuples_v2,
)
from losses import load_loss_registry_v2
from participation import compute_p_star

OUTPUT_PATH = Path("out/checkers/ch_a7_check.json")

TARGET_PROPERTY = "min_order_quantity"


def run() -> Dict[str, Any]:
    loss_model = load_loss_model()
    grid = load_pair_test_grid()
    registry = load_loss_registry_v2(loss_model)
    domains = property_domains_v2(grid)

    # (a) full v2 reachable set: rank-0 union downroute union retry-delay.
    reachable_a = executable_reachable_tuples_v2(domains)
    p_star_a, coverage_a, _ = compute_p_star(reachable_a, registry, CANDIDATE_PROPERTIES_V2)

    # (b) downroute excluded: rank-0 union retry-delay only.
    rank0 = rank0_reachable_tuples_v2(domains)
    retry_new = retry_delay_reachable_tuples_v2(rank0)
    reachable_b = list(dict.fromkeys(rank0 + retry_new))
    p_star_b, coverage_b, _ = compute_p_star(reachable_b, registry, CANDIDATE_PROPERTIES_V2)

    in_a = TARGET_PROPERTY in p_star_a
    in_b = TARGET_PROPERTY in p_star_b
    supported = in_a and not in_b

    return {
        "target_property": TARGET_PROPERTY,
        "reachable_size_a_full_v2": len(reachable_a),
        "reachable_size_b_downroute_excluded": len(reachable_b),
        "p_star_a_full_v2": p_star_a,
        "p_star_b_downroute_excluded": p_star_b,
        "coverage_a_full_v2": coverage_a,
        "coverage_b_downroute_excluded": coverage_b,
        "target_in_p_star_a": in_a,
        "target_in_p_star_b": in_b,
        "ch_a7_supported": supported,
    }


def main() -> None:
    result = run()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"\nCH-A7: {'SUPPORTED' if result['ch_a7_supported'] else 'NOT SUPPORTED'}")


if __name__ == "__main__":
    main()
