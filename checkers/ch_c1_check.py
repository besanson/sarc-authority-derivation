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
CH-C1 (`prereg/v8-large-realistic-domain.md`, tag `prereg-p5-v8`): does
the large (35-candidate-property), non-planted domain's core fail to be
sufficient? `reduct.compute_core`/`sufficiency` (Definition 1's own
`O(n)` witness search, unmodified) decide this directly -- no exhaustive
reduct enumeration is needed or attempted here.

Also implements the prereg's own registered "Multiplicity, without
exhaustive enumeration" method: `synthesis.find_up_to_k_minimum_
cardinality_contracts` (capped at 5, registered before this checker was
written) reports a genuine LOWER BOUND on how many minimum-cardinality
reducts exist, never an exhaustive count.

SUPPORTED iff the core is not sufficient (a concrete counterexample pair
is reported). NOT SUPPORTED iff the core is sufficient -- registered as
a fully valid outcome, not a failed exercise (prereg's own decision
rule)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from domain_v8 import CANDIDATE_PROPERTIES_V8, executable_reachable_tuples_v8, rank0_reachable_tuples_v8
from losses_v8 import load_loss_registry_v8
from reduct import compute_core, sufficiency
from synthesis import find_up_to_k_minimum_cardinality_contracts

OUTPUT_PATH = Path("out/checkers/ch_c1_check.json")
MULTIPLICITY_CAP = 5


def run() -> Dict[str, Any]:
    rank0 = rank0_reachable_tuples_v8()
    reachable = executable_reachable_tuples_v8()
    executable_equals_rank0 = reachable == rank0
    registry = load_loss_registry_v8()

    core, redundant, _witnesses = compute_core(reachable, registry, CANDIDATE_PROPERTIES_V8)
    is_core_sufficient, cert_or_counterexample = sufficiency(tuple(sorted(core)), reachable, registry)
    supported = not is_core_sufficient

    minimum_cardinality_contracts = find_up_to_k_minimum_cardinality_contracts(
        CANDIDATE_PROPERTIES_V8, reachable, registry, k=MULTIPLICITY_CAP
    )
    minimum_cardinality = len(minimum_cardinality_contracts[0]) if minimum_cardinality_contracts else None
    multiplicity_certificates = []
    for contract in minimum_cardinality_contracts:
        is_suff, cert = sufficiency(tuple(sorted(contract)), reachable, registry)
        multiplicity_certificates.append({
            "members": sorted(contract),
            "is_sufficient": is_suff,
            "sufficiency_certificate": cert if is_suff else None,
            "counterexample": None if is_suff else cert,
        })

    result: Dict[str, Any] = {
        "reachable_tuples_swept": len(reachable),
        "executable_equals_rank0": executable_equals_rank0,
        "candidate_properties": list(CANDIDATE_PROPERTIES_V8),
        "core_attributes": sorted(core),
        "core_cardinality": len(core),
        "is_core_sufficient": is_core_sufficient,
        "redundant_attributes": sorted(redundant),
        "supported": supported,
        "minimum_cardinality": minimum_cardinality,
        "minimum_cardinality_contracts_found": [sorted(c) for c in minimum_cardinality_contracts],
        "minimum_cardinality_contracts_found_count": len(minimum_cardinality_contracts),
        "multiplicity_cap": MULTIPLICITY_CAP,
        "multiplicity_is_a_lower_bound_not_exhaustive": True,
        "multiplicity_certificates": multiplicity_certificates,
    }
    if is_core_sufficient:
        result["sufficiency_certificate"] = cert_or_counterexample
        result["counterexample"] = None
    else:
        result["sufficiency_certificate"] = None
        result["counterexample"] = cert_or_counterexample
    return result


def main() -> None:
    result = run()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"\nCH-C1: {'SUPPORTED' if result['supported'] else 'NOT SUPPORTED'}")
    print(
        f"Multiplicity: found {result['minimum_cardinality_contracts_found_count']} of at most "
        f"{MULTIPLICITY_CAP} minimum-cardinality contracts (a lower bound, not exhaustive)."
    )


if __name__ == "__main__":
    main()
