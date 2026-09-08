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
CH-B1 (`prereg/v4-realistic-domain.md`, tag `prereg-p5-v4`): does the
independently-built software-and-cloud domain's core fail to be
sufficient, or does more than one reduct exist? `reduct.py`'s own
machinery (`verify_core_identity`, `sufficiency`), unmodified -- this
milestone applies it to a new domain, it does not extend or change it.

SUPPORTED iff the core is not sufficient (a concrete counterexample pair
is reported) OR more than one reduct is found. NOT SUPPORTED iff the
core is sufficient AND is the unique reduct -- registered as a fully
valid outcome, not a failed exercise (prereg's own decision rule)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from domain_v4 import CANDIDATE_PROPERTIES_V4, executable_reachable_tuples_v4
from losses_v4 import load_loss_registry_v4
from reduct import sufficiency, verify_core_identity

OUTPUT_PATH = Path("out/checkers/ch_b1_check.json")


def run() -> Dict[str, Any]:
    reachable = executable_reachable_tuples_v4()
    registry = load_loss_registry_v4()

    identity = verify_core_identity(reachable, registry, CANDIDATE_PROPERTIES_V4)
    core = identity["core_via_definition_1"]
    is_sufficient, cert_or_counterexample = sufficiency(tuple(core), reachable, registry)

    reducts = identity["reducts"]
    minimum_cardinality = min((len(r) for r in reducts), default=0)
    minimum_reducts = [r for r in reducts if len(r) == minimum_cardinality]
    core_is_unique_reduct = is_sufficient and len(reducts) == 1 and set(reducts[0]) == set(core)

    supported = (not is_sufficient) or (len(reducts) > 1)

    result: Dict[str, Any] = {
        "reachable_tuples_swept": len(reachable),
        "candidate_properties": list(CANDIDATE_PROPERTIES_V4),
        "core_attributes": sorted(core),
        "core_cardinality": len(core),
        "is_core_sufficient": is_sufficient,
        "reducts": [sorted(r) for r in reducts],
        "num_reducts": len(reducts),
        "minimum_reduct_cardinality": minimum_cardinality,
        "minimum_reducts": [sorted(r) for r in minimum_reducts],
        "core_is_unique_reduct": core_is_unique_reduct,
        "redundant_attributes": sorted(set(CANDIDATE_PROPERTIES_V4) - set(core)),
        "subsets_considered": identity["subsets_considered"],
        "power_set_size": 2 ** len(CANDIDATE_PROPERTIES_V4),
        "supported": supported,
    }
    if is_sufficient:
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
    print(f"\nCH-B1: {'SUPPORTED' if result['supported'] else 'NOT SUPPORTED'}")


if __name__ == "__main__":
    main()
