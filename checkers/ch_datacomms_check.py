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
CH-DC1 (`prereg/v6.1-authoritybench-amendment.md`, tag `prereg-p5-v6.1`):
core-versus-reduct on the data-and-communications domain, independently
built for this milestone. `reduct.py`'s own machinery
(`verify_core_identity`, `sufficiency`), unmodified -- this milestone
applies it to a new domain, it does not extend or change it. No outcome
was asserted in the registration (`prereg/v6.1-authoritybench-
amendment.md`'s own "no core/reduct outcome is asserted in advance");
this checker reports whatever the model actually produces.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from domain_datacomms import CANDIDATE_PROPERTIES_DATACOMMS, executable_reachable_tuples_datacomms
from losses_datacomms import load_loss_registry_datacomms
from reduct import sufficiency, verify_core_identity

OUTPUT_PATH = Path("out/checkers/ch_datacomms_check.json")


def run() -> Dict[str, Any]:
    reachable = executable_reachable_tuples_datacomms()
    registry = load_loss_registry_datacomms()

    identity = verify_core_identity(reachable, registry, CANDIDATE_PROPERTIES_DATACOMMS)
    core_attributes = identity["core_via_definition_1"]
    core_is_sufficient, core_certificate_or_counterexample = sufficiency(tuple(sorted(core_attributes)), reachable, registry)

    cardinalities = [len(r) for r in identity["reducts"]]
    minimum_reduct_cardinality = min(cardinalities) if cardinalities else 0
    minimum_reducts = [r for r in identity["reducts"] if len(r) == minimum_reduct_cardinality]
    core_is_unique_reduct = len(identity["reducts"]) == 1 and identity["reducts"][0] == core_attributes
    redundant_attributes = sorted(set(CANDIDATE_PROPERTIES_DATACOMMS) - set(core_attributes))

    return {
        "candidate_properties": list(CANDIDATE_PROPERTIES_DATACOMMS),
        "reachable_tuples_swept": len(reachable),
        "subsets_considered": identity["subsets_considered"],
        "core_attributes": core_attributes,
        "core_is_sufficient": core_is_sufficient,
        "core_sufficiency_certificate_or_counterexample": core_certificate_or_counterexample,
        "reducts": identity["reducts"],
        "minimum_reducts": minimum_reducts,
        "minimum_reduct_cardinality": minimum_reduct_cardinality,
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
    print(f"\nCH-DC1: core_is_sufficient={result['core_is_sufficient']}, "
          f"{len(result['reducts'])} reduct(s), minimum cardinality {result['minimum_reduct_cardinality']}, "
          f"core is unique reduct: {result['core_is_unique_reduct']}")


if __name__ == "__main__":
    main()
