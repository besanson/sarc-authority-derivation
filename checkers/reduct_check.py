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
CH-A10 (prereg/v3-core-reduct-correction.md, tag prereg-p5-v3): exact
reduct enumeration on the v2 model. Not a two-sided hypothesis -- a full
enumeration whose reported numbers are the result.

Also machine-checks Proposition 1' claim 1 (Definition 1 computes the
core) by recomputing the core two independent ways -- reduct.
verify_core_identity() -- and claim 3 (core sufficient => unique reduct)
directly from this run's own reducts/core_attributes.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from domain import CANDIDATE_PROPERTIES_V2, executable_reachable_tuples_v2, load_loss_model, load_pair_test_grid, property_domains_v2
from losses import load_loss_registry_v2
from reduct import verify_core_identity

OUTPUT_PATH = Path("out/checkers/reduct_check.json")


def run() -> Dict[str, Any]:
    loss_model = load_loss_model()
    grid = load_pair_test_grid()
    registry = load_loss_registry_v2(loss_model)
    domains = property_domains_v2(grid)
    reachable = executable_reachable_tuples_v2(domains)

    identity = verify_core_identity(reachable, registry, CANDIDATE_PROPERTIES_V2)
    reducts = identity["reducts"]
    core_attributes = identity["core_via_definition_1"]

    cardinalities = [len(r) for r in reducts]
    minimum_reduct_cardinality = min(cardinalities) if cardinalities else 0
    minimum_reducts = [r for r in reducts if len(r) == minimum_reduct_cardinality]
    core_is_unique_reduct = len(reducts) == 1 and reducts[0] == core_attributes
    redundant_attributes = sorted(set(CANDIDATE_PROPERTIES_V2) - set(core_attributes))

    return {
        "schema_version": 1,
        "model": "v2",
        "candidate_properties": list(CANDIDATE_PROPERTIES_V2),
        "reachable_tuples_swept": len(reachable),
        "subsets_considered": identity["subsets_considered"],
        "reducts": reducts,
        "minimum_reducts": minimum_reducts,
        "minimum_reduct_cardinality": minimum_reduct_cardinality,
        "core_attributes": core_attributes,
        "core_is_unique_reduct": core_is_unique_reduct,
        "redundant_attributes": redundant_attributes,
        "proposition_1_prime_claim_1_identity_holds": identity["identity_holds"],
        "proposition_1_prime_claim_2_core_subset_of_every_reduct": identity["core_subset_of_every_reduct"],
    }


def main() -> None:
    result = run()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"\nCH-A10: {len(result['reducts'])} reduct(s), minimum cardinality {result['minimum_reduct_cardinality']}, "
          f"core is unique reduct: {result['core_is_unique_reduct']}")


if __name__ == "__main__":
    main()
