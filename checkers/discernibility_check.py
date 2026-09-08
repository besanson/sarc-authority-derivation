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
Milestone D (`prereg/v5-synthesis.md`, tag `prereg-p5-v5`): machine-checks
`discernibility.py`'s own docstring claim -- that `verify_contract`
(the discernibility/hitting-set way of deciding sufficiency) agrees with
`reduct.sufficiency` (the partition way) on EVERY subset of candidate
properties, not sampled -- against all three of this artifact's real
enumerated models (v1, v2, v4). Exhaustive because each model's
candidate count (9 or 10) keeps 2^n subsets cheap once the (more
expensive, built once per model) discernibility family itself is
constructed."""
from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from discernibility import build_discernibility_family, remove_redundant_supersets, verify_contract
from reduct import sufficiency

OUTPUT_PATH = Path("out/checkers/discernibility_check.json")


def _check_model(name: str, candidate_properties: Tuple[str, ...], reachable: List[Any], registry) -> Dict[str, Any]:
    family = build_discernibility_family(candidate_properties, reachable, registry)
    reduced_family = remove_redundant_supersets(family)

    mismatches = []
    subsets_checked = 0
    n = len(candidate_properties)
    for size in range(n + 1):
        for combo in itertools.combinations(candidate_properties, size):
            s = frozenset(combo)
            subsets_checked += 1
            is_suff_partition, _ = sufficiency(tuple(sorted(s)), reachable, registry)
            is_suff_discernibility, _ = verify_contract(s, family)
            is_suff_discernibility_reduced, _ = verify_contract(s, reduced_family)
            if is_suff_partition != is_suff_discernibility or is_suff_partition != is_suff_discernibility_reduced:
                mismatches.append({
                    "subset": sorted(s),
                    "partition_says_sufficient": is_suff_partition,
                    "discernibility_says_sufficient": is_suff_discernibility,
                    "discernibility_reduced_says_sufficient": is_suff_discernibility_reduced,
                })

    return {
        "model": name,
        "reachable_tuples_swept": len(reachable),
        "candidate_property_count": n,
        "family_size": len(family),
        "reduced_family_size": len(reduced_family),
        "subsets_checked": subsets_checked,
        "power_set_size": 2 ** n,
        "mismatches": mismatches,
        "all_agree": not mismatches,
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
    return {"models": results, "all_models_agree": all(r["all_agree"] for r in results)}


def main() -> None:
    result = run()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["all_models_agree"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
