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
Milestone E1 (`prereg/v6.1-authoritybench-amendment.md`, "the paper
pipeline becomes a consumer"): calls `src.authority_compiler.
derive_authority_contract` on the v2 model and cross-checks its own
`core_attributes`/`minimum_cardinality_reduct` DIRECTLY against
`checkers/reduct_check.py`'s already-committed, already machine-checked
CH-A10 result (`out/checkers/reduct_check.json`) -- confirming the
packaged entry point agrees with the underlying, separately-verified
machinery it wraps, not assuming agreement from `derive_authority_
contract`'s own docstring claim alone. `checkers/reduct_check.py` itself
is unmodified -- CH-A10's own more rigorous verification
(`reduct.verify_core_identity`'s two-independent-methods cross-check)
stays exactly as committed; this is an ADDITIONAL, separate checker, not
a replacement, so CH-A10's own proof status is never put at risk by
this milestone's own packaging work.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from authority_compiler import derive_authority_contract  # noqa: E402
from domain import CANDIDATE_PROPERTIES_V2, executable_reachable_tuples_v2, load_loss_model, load_pair_test_grid, property_domains_v2  # noqa: E402
from losses import load_loss_registry_v2  # noqa: E402

OUTPUT_PATH = Path("out/checkers/authority_compiler_check.json")
REDUCT_CHECK_PATH = Path("out/checkers/reduct_check.json")


def run() -> Dict[str, Any]:
    loss_model = load_loss_model()
    grid = load_pair_test_grid()
    registry = load_loss_registry_v2(loss_model)
    domains = property_domains_v2(grid)
    reachable = executable_reachable_tuples_v2(domains)
    candidate_context = {p: domains[p] for p in CANDIDATE_PROPERTIES_V2}

    contract = derive_authority_contract(registry, reachable, candidate_context)

    reduct_check = json.loads(REDUCT_CHECK_PATH.read_text())
    already_committed_core = sorted(reduct_check["core_attributes"])
    already_committed_minimum_reducts = [sorted(r) for r in reduct_check["minimum_reducts"]]

    packaged_core = sorted(contract.core_attributes)
    packaged_minimum_cardinality_reduct = sorted(contract.minimum_cardinality_reduct)
    packaged_minimal_reducts = [sorted(r) for r in contract.minimal_reducts] if contract.minimal_reducts is not None else None

    core_agrees = packaged_core == already_committed_core
    minimum_cardinality_reduct_is_one_of_the_already_committed_minimum_reducts = (
        packaged_minimum_cardinality_reduct in already_committed_minimum_reducts
    )
    minimal_reducts_agree = (
        packaged_minimal_reducts is not None
        and sorted(packaged_minimal_reducts) == sorted(already_committed_minimum_reducts)
    )

    return {
        "model": "v2",
        "already_committed_core": already_committed_core,
        "already_committed_minimum_reducts": already_committed_minimum_reducts,
        "packaged_core_attributes": packaged_core,
        "packaged_minimum_cardinality_reduct": packaged_minimum_cardinality_reduct,
        "packaged_minimal_reducts": packaged_minimal_reducts,
        "core_agrees": core_agrees,
        "minimum_cardinality_reduct_is_one_of_the_already_committed_minimum_reducts": minimum_cardinality_reduct_is_one_of_the_already_committed_minimum_reducts,
        "minimal_reducts_agree": minimal_reducts_agree,
        "packaged_core_is_sufficient": contract.counterexamples is None,
        "reduct_check_core_is_unique_reduct": reduct_check["core_is_unique_reduct"],
        "clean": core_agrees and minimum_cardinality_reduct_is_one_of_the_already_committed_minimum_reducts and minimal_reducts_agree,
    }


def main() -> None:
    result = run()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["clean"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
