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
CH-A8 (prereg/v3-core-reduct-correction.md, tag prereg-p5-v3): is the v2
core sufficient (Definition 4) on the v2 executable-reachable set?

Decision rule: run reduct.sufficiency() against
domain.executable_reachable_tuples_v2() and the committed v2 loss
registry, testing v2's own already-derived core
(out/checkers/derivation_output_v2.json's participating_properties, read
and reported under its v3-renamed key -- not recomputed differently, and
not the adjudicator's own prior recomputation copied forward). SUPPORTED
iff the sufficiency certificate holds for every pair of v2-reachable
tuples; NOT SUPPORTED iff a concrete counterexample pair is found.
Either outcome is reported.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from domain import executable_reachable_tuples_v2, load_loss_model, load_pair_test_grid, property_domains_v2
from losses import load_loss_registry_v2
from reduct import sufficiency

DERIVATION_OUTPUT_V2_PATH = Path("out/checkers/derivation_output_v2.json")
OUTPUT_PATH = Path("out/checkers/sufficiency_check.json")


def run() -> Dict[str, Any]:
    loss_model = load_loss_model()
    grid = load_pair_test_grid()
    registry = load_loss_registry_v2(loss_model)
    domains = property_domains_v2(grid)
    reachable = executable_reachable_tuples_v2(domains)

    derived_v2 = json.loads(DERIVATION_OUTPUT_V2_PATH.read_text())
    core_attributes = tuple(sorted(derived_v2["participating_properties"]))

    is_sufficient, cert_or_counter = sufficiency(core_attributes, reachable, registry)

    result: Dict[str, Any] = {
        "schema_version": 1,
        "model": "v2",
        "candidate_properties": sorted(derived_v2["candidate_properties"]),
        "tested_set": list(core_attributes),
        "is_sufficient": is_sufficient,
        "reachable_tuples_swept": len(reachable),
    }
    if is_sufficient:
        result["sufficiency_certificate"] = cert_or_counter
    else:
        result["counterexample"] = cert_or_counter
    return result


def main() -> None:
    result = run()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"\nCH-A8: {'SUPPORTED' if result['is_sufficient'] else 'NOT SUPPORTED'}")


if __name__ == "__main__":
    main()
