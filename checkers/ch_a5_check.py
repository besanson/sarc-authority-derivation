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
CH-A5 (prereg/v2-reachability-redesign.md, tag prereg-p5-v2): does the v2
reachability redesign make remediation reachability-relevant, in general?

Decision rule (registered two-sided -- either outcome is a result):
compute P*, the coverage list, and the witness set under
domain.executable_reachable_tuples_v2() (rank-0 union downroute-reachable
union retry-delay-reachable), using the seven losses (six from v1,
unchanged, plus the new loss) over ten candidate properties (nine from
v1 plus min_order_quantity). Compare against v1's own committed P*/
coverage list (out/checkers/derivation_output.json, read only, never
written by this module). Two possible outcomes, decided here by the
computation, not assumed: if the nine original properties' own
participation/coverage split changed, or min_order_quantity itself
participates, the fence's original claim ("remediation changes the
reachable set") is demonstrated for the redesigned model
(ch_a5_outcome: "reachability_relevant"); if the nine original
properties are unchanged AND min_order_quantity does not participate,
reported as "reachability_robust" -- a real finding either way.

This module also reports the v2 reachability measurement CH-A5's
decision rule depends on (rank0_v2/downroute/retry-delay sizes, and an
internal-consistency check mirroring checkers/reachability_check.py's
own bug-detection gate, which is the only thing this module exits
nonzero on -- never on which of the two registered outcomes obtained).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from domain import (
    CANDIDATE_PROPERTIES,
    CANDIDATE_PROPERTIES_V2,
    downroute_reachable_tuples_v2,
    executable_reachable_tuples_v2,
    load_loss_model,
    load_pair_test_grid,
    property_domains_v2,
    rank0_reachable_tuples_v2,
    retry_delay_reachable_tuples_v2,
)
from losses import load_loss_registry_v2
from participation import compute_p_star

V1_DERIVATION_OUTPUT_PATH = Path("out/checkers/derivation_output.json")
OUTPUT_PATH = Path("out/checkers/ch_a5_check.json")


def run() -> Dict[str, Any]:
    loss_model = load_loss_model()
    grid = load_pair_test_grid()
    registry = load_loss_registry_v2(loss_model)
    domains = property_domains_v2(grid)

    rank0 = rank0_reachable_tuples_v2(domains)
    downroute_new = downroute_reachable_tuples_v2(rank0, domains["order_value"])
    retry_new = retry_delay_reachable_tuples_v2(rank0)
    reachable = executable_reachable_tuples_v2(domains)

    internally_consistent = set(reachable) == set(rank0) | set(downroute_new) | set(retry_new)

    v2_p_star, v2_coverage, v2_witnesses = compute_p_star(reachable, registry, CANDIDATE_PROPERTIES_V2)

    v1_derived = json.loads(V1_DERIVATION_OUTPUT_PATH.read_text())
    v1_p_star = sorted(v1_derived["participating_properties"])
    v1_coverage = sorted(v1_derived["coverage_list"])

    # Like-for-like comparison against v1: restrict v2's result to the nine
    # v1 properties. min_order_quantity has no v1 analogue; its own
    # membership is reported separately below, not folded into "changed
    # from v1" (a property that did not exist in v1 cannot have "changed").
    v2_p_star_v1_props = sorted(set(v2_p_star) & set(CANDIDATE_PROPERTIES))
    v2_coverage_v1_props = sorted(set(v2_coverage) & set(CANDIDATE_PROPERTIES))
    nine_original_properties_unchanged = (
        v2_p_star_v1_props == v1_p_star and v2_coverage_v1_props == v1_coverage
    )
    min_order_quantity_participates = "min_order_quantity" in v2_p_star

    reachability_relevant = min_order_quantity_participates or not nine_original_properties_unchanged

    return {
        "rank0_v2_size": len(rank0),
        "downroute_reachable_new_tuples": len(downroute_new),
        "retry_delay_reachable_new_tuples": len(retry_new),
        "executable_reachable_v2_size": len(reachable),
        "internally_consistent": internally_consistent,
        "v2_participating_properties": v2_p_star,
        "v2_coverage_list": v2_coverage,
        "v1_participating_properties": v1_p_star,
        "v1_coverage_list": v1_coverage,
        "nine_original_properties_unchanged_from_v1": nine_original_properties_unchanged,
        "min_order_quantity_participates": min_order_quantity_participates,
        "ch_a5_outcome": "reachability_relevant" if reachability_relevant else "reachability_robust",
        "witnesses": v2_witnesses,
    }


def main() -> None:
    result = run()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"\nCH-A5: {result['ch_a5_outcome']}")
    if not result["internally_consistent"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
