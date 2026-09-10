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
CH-C2 (`prereg/v8-large-realistic-domain.md`, tag `prereg-p5-v8`): does
a registered cost model select a contract with strictly lower cost than
at least one minimum-cardinality contract CH-C1's own blocking-clause
method found? Reads `out/checkers/ch_c1_check.json` for that set
(`checkers/ch_c1_check.py` must run first, wired immediately before this
checker in `make formal`) rather than recomputing it -- the SAME
multiplicity result both hypotheses are decided against, not two
independently-drawn ones.

SUPPORTED iff the minimum-cost contract is itself exactly sufficient AND
its cost is strictly lower than at least one of CH-C1's minimum-
cardinality contracts. NOT SUPPORTED, and registered as a fully valid,
fully retained result, iff either every minimum-cardinality contract
found has exactly equal cost, or only one was found at all."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from costs_v8 import observation_costs_v8
from domain_v8 import CANDIDATE_PROPERTIES_V8, executable_reachable_tuples_v8
from losses_v8 import load_loss_registry_v8
from reduct import sufficiency
from synthesis import find_minimum_cost_contract

OUTPUT_PATH = Path("out/checkers/ch_c2_check.json")
CH_C1_OUTPUT_PATH = Path("out/checkers/ch_c1_check.json")

COST_TIE_EPSILON = 1e-9


def run() -> Dict[str, Any]:
    ch_c1 = json.loads(CH_C1_OUTPUT_PATH.read_text())
    minimum_cardinality_contracts: List[List[str]] = ch_c1["minimum_cardinality_contracts_found"]

    reachable = executable_reachable_tuples_v8()
    registry = load_loss_registry_v8()
    costs = observation_costs_v8()

    missing = set(CANDIDATE_PROPERTIES_V8) - set(costs)
    if missing:
        raise ValueError(f"costs_v8 declares no cost for: {sorted(missing)}")

    min_cost_contract = find_minimum_cost_contract(CANDIDATE_PROPERTIES_V8, reachable, registry, costs)
    is_min_cost_sufficient, min_cost_cert = sufficiency(tuple(sorted(min_cost_contract)), reachable, registry)
    min_cost_total = sum(costs[p] for p in sorted(min_cost_contract))

    minimum_cardinality_costs: Dict[str, float] = {}
    for i, members in enumerate(minimum_cardinality_contracts, start=1):
        minimum_cardinality_costs[f"minimum_cardinality_contract_{i}"] = sum(costs[p] for p in sorted(members))

    strictly_cheaper_than = [
        key for key, c in minimum_cardinality_costs.items() if min_cost_total < c - COST_TIE_EPSILON
    ]
    supported = is_min_cost_sufficient and bool(strictly_cheaper_than)

    if len(minimum_cardinality_contracts) < 2:
        outcome_subcase = "negative_single_reduct"
    elif strictly_cheaper_than:
        outcome_subcase = "positive_strict_cost_separation"
    else:
        outcome_subcase = "negative_tie"

    result: Dict[str, Any] = {
        "reachable_tuples_swept": len(reachable),
        "candidate_properties": list(CANDIDATE_PROPERTIES_V8),
        "observation_costs": costs,
        "minimum_cardinality_contracts_from_ch_c1": minimum_cardinality_contracts,
        "minimum_cardinality_contracts_costs": minimum_cardinality_costs,
        "minimum_cost_contract": sorted(min_cost_contract),
        "minimum_cost_contract_total_cost": min_cost_total,
        "minimum_cost_contract_is_sufficient": is_min_cost_sufficient,
        "minimum_cost_contract_sufficiency_certificate": min_cost_cert if is_min_cost_sufficient else None,
        "minimum_cost_contract_counterexample": None if is_min_cost_sufficient else min_cost_cert,
        "minimum_cost_contract_is_one_of_ch_c1s_minimum_cardinality_contracts": sorted(min_cost_contract) in minimum_cardinality_contracts,
        "strictly_cheaper_than": strictly_cheaper_than,
        "outcome_subcase": outcome_subcase,
        "supported": supported,
    }
    return result


def main() -> None:
    result = run()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"\nCH-C2: {'SUPPORTED' if result['supported'] else 'NOT SUPPORTED'} ({result['outcome_subcase']})")


if __name__ == "__main__":
    main()
