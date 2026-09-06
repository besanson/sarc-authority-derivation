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
Negative Proposition N and CH-A9 (prereg/v3-core-reduct-correction.md,
tag prereg-p5-v3): runs the same generic core/reduct machinery
(reduct.py) reduct_check.py uses against two registered cases, so a
negative finding is exactly as replayable and independently checked as
CH-A8/CH-A10's positive ones.

Case 1, negative_proposition_n: loads
prereg/fixtures/negative-proposition-n-counterexample.json (the abstract
two-state counterexample, re-derived from first principles) and confirms
the fixture's own `expected` block -- registered before this checker
existed, not fitted to whatever this checker happens to compute.

Case 2, ch_a9_constrained_procurement_variant: does a real, declared
co-variation between actor_role and resource_class (pair-test-grid.yaml's
v3 section) break core sufficiency in a constrained variant of this
artifact's own v2 procurement model? Two-sided: SUPPORTED iff the core is
insufficient AND the minimum reduct cardinality strictly exceeds the
core's cardinality; NOT SUPPORTED (itself a checkable finding) otherwise.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Dict

from domain import (
    ch_a9_role_resource_class_pairing,
    load_loss_model,
    load_pair_test_grid,
    property_domains_v2,
    rank0_reachable_tuples_v3_constrained_ch_a9,
)
from losses import load_loss_registry_v2, m_verdict
from reduct import exact_reducts, sufficiency

FIXTURE_PATH = Path("prereg/fixtures/negative-proposition-n-counterexample.json")
OUTPUT_PATH = Path("out/checkers/core_insufficiency_counterexample.json")


@dataclass(frozen=True)
class _FixtureTuple:
    x: int
    y: int

    def with_property(self, name: str, value: Any) -> "_FixtureTuple":
        return replace(self, **{name: value})


def _run_negative_proposition_n() -> Dict[str, Any]:
    fixture = json.loads(FIXTURE_PATH.read_text())
    candidates = tuple(fixture["candidate_properties"])
    reachable = [_FixtureTuple(**t) for t in fixture["reachable_tuples"]]
    verdict_field = fixture["verdict_field"]
    registry = {"fixture_verdict": lambda t: bool(getattr(t, verdict_field))}

    reducts, subsets_considered = exact_reducts(candidates, reachable, registry)
    core = sorted(set(candidates).intersection(*reducts)) if reducts else sorted(candidates)
    is_sufficient, cert_or_counter = sufficiency(tuple(core), reachable, registry)
    cardinalities = [len(r) for r in reducts]
    min_cardinality = min(cardinalities) if cardinalities else 0

    case: Dict[str, Any] = {
        "name": "negative_proposition_n",
        "candidate_properties": list(candidates),
        "reachable_tuples_swept": len(reachable),
        "core_attributes": core,
        "is_core_sufficient": is_sufficient,
        "minimum_reduct_cardinality": min_cardinality,
        "supported": (not is_sufficient) and min_cardinality > len(core),
    }
    if not is_sufficient:
        case["counterexample"] = cert_or_counter

    expected = fixture["expected"]
    matches_registered_expectation = (
        core == expected["core_attributes"]
        and is_sufficient == expected["is_core_sufficient"]
        and sorted([sorted(r) for r in reducts]) == sorted(expected["reducts"])
        and min_cardinality == expected["minimum_reduct_cardinality"]
    )
    case["matches_registered_fixture_expectation"] = matches_registered_expectation
    return case


def _run_ch_a9_constrained_variant() -> Dict[str, Any]:
    loss_model = load_loss_model()
    grid = load_pair_test_grid()
    registry = load_loss_registry_v2(loss_model)
    domains = property_domains_v2(grid)
    pairing = ch_a9_role_resource_class_pairing(grid)
    candidates = ("actor_role", "resource_class", "order_value", "min_order_quantity",
                  "day", "workflow", "grant_id", "consumed_grant_ids", "budget_remaining", "frozen")

    reachable = rank0_reachable_tuples_v3_constrained_ch_a9(domains, pairing)

    reducts, _subsets_considered = exact_reducts(candidates, reachable, registry)
    core = sorted(set(candidates).intersection(*reducts)) if reducts else sorted(candidates)
    is_sufficient, cert_or_counter = sufficiency(tuple(core), reachable, registry)
    cardinalities = [len(r) for r in reducts]
    min_cardinality = min(cardinalities) if cardinalities else 0

    case: Dict[str, Any] = {
        "name": "ch_a9_constrained_procurement_variant",
        "candidate_properties": list(candidates),
        "reachable_tuples_swept": len(reachable),
        "core_attributes": core,
        "is_core_sufficient": is_sufficient,
        "minimum_reduct_cardinality": min_cardinality,
        "supported": (not is_sufficient) and min_cardinality > len(core),
    }
    if not is_sufficient:
        case["counterexample"] = cert_or_counter
    return case


def run() -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "cases": [_run_negative_proposition_n(), _run_ch_a9_constrained_variant()],
    }


def main() -> None:
    result = run()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))
    for case in result["cases"]:
        print(f"\n{case['name']}: {'SUPPORTED' if case['supported'] else 'NOT SUPPORTED'}")


if __name__ == "__main__":
    main()
