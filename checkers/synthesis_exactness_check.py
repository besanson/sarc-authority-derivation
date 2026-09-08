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
Milestone D (`prereg/v5-synthesis.md`, tag `prereg-p5-v5`): the
exactness gate D2 registers -- "on every model where exhaustion is
feasible, backends must return exactly the exhaustive reducts; fail
otherwise." Run against all three of this artifact's real enumerated
models (v1, v2, v4; all 2^9 or 2^10 subsets, cheap to exhaust) --
`synthesis.py`'s SAT/MaxSAT results are checked against `reduct.
exact_reducts()`'s own from-first-principles answer, not trusted on
the solver's say-so."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

from reduct import exact_reducts, sufficiency
from synthesis import find_any_sufficient_contract, find_minimum_cardinality_contract, find_minimum_cost_contract

OUTPUT_PATH = Path("out/checkers/synthesis_exactness_check.json")


def _check_model(
    name: str,
    candidate_properties: Tuple[str, ...],
    reachable: List[Any],
    registry: Dict[str, Callable[[Any], bool]],
) -> Dict[str, Any]:
    exhaustive_reducts, subsets_considered = exact_reducts(candidate_properties, reachable, registry)
    exhaustive_reduct_sets = {frozenset(r) for r in exhaustive_reducts}
    exhaustive_min_cardinality = min((len(r) for r in exhaustive_reducts), default=0)

    any_contract = find_any_sufficient_contract(candidate_properties, reachable, registry)
    any_is_sufficient, _ = sufficiency(tuple(sorted(any_contract)), reachable, registry) if any_contract is not None else (False, None)

    min_card_contract = find_minimum_cardinality_contract(candidate_properties, reachable, registry)
    min_card_matches_exhaustive = (
        len(min_card_contract) == exhaustive_min_cardinality and min_card_contract in exhaustive_reduct_sets
    )

    uniform_costs = {p: 1.0 for p in candidate_properties}
    min_cost_uniform_contract = find_minimum_cost_contract(candidate_properties, reachable, registry, uniform_costs)
    uniform_cost_matches_cardinality_backend = (
        len(min_cost_uniform_contract) == len(min_card_contract) and min_cost_uniform_contract in exhaustive_reduct_sets
    )

    return {
        "model": name,
        "reachable_tuples_swept": len(reachable),
        "exhaustive_reducts": [sorted(r) for r in exhaustive_reducts],
        "exhaustive_num_reducts": len(exhaustive_reducts),
        "exhaustive_min_cardinality": exhaustive_min_cardinality,
        "exhaustive_subsets_considered": subsets_considered,
        "sat_any_contract": sorted(any_contract) if any_contract is not None else None,
        "sat_any_contract_is_sufficient": any_is_sufficient,
        "maxsat_min_cardinality_contract": sorted(min_card_contract),
        "maxsat_min_cardinality_matches_exhaustive_reduct": min_card_matches_exhaustive,
        "maxsat_min_cost_uniform_contract": sorted(min_cost_uniform_contract),
        "maxsat_min_cost_uniform_matches_cardinality_backend": uniform_cost_matches_cardinality_backend,
        "exact": bool(any_is_sufficient and min_card_matches_exhaustive and uniform_cost_matches_cardinality_backend),
    }


def run() -> Dict[str, Any]:
    from domain import (
        CANDIDATE_PROPERTIES,
        CANDIDATE_PROPERTIES_V2,
        executable_reachable_tuples,
        executable_reachable_tuples_v2,
        load_loss_model,
        load_pair_test_grid,
        property_domains,
        property_domains_v2,
    )
    from domain_v4 import CANDIDATE_PROPERTIES_V4, executable_reachable_tuples_v4
    from losses import load_loss_registry, load_loss_registry_v2
    from losses_v4 import load_loss_registry_v4

    grid = load_pair_test_grid()
    loss_model = load_loss_model()

    results = [
        _check_model(
            "v1", CANDIDATE_PROPERTIES,
            executable_reachable_tuples(property_domains(grid)),
            load_loss_registry(loss_model),
        ),
        _check_model(
            "v2", CANDIDATE_PROPERTIES_V2,
            executable_reachable_tuples_v2(property_domains_v2(grid)),
            load_loss_registry_v2(loss_model),
        ),
        _check_model(
            "v4", CANDIDATE_PROPERTIES_V4,
            executable_reachable_tuples_v4(),
            load_loss_registry_v4(),
        ),
    ]
    return {"models": results, "exact_on_every_feasible_model": all(r["exact"] for r in results)}


def main() -> None:
    result = run()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["exact_on_every_feasible_model"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
