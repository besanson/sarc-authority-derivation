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
CH-B2 (`prereg/v7-cost-sensitive-contracts.md`, tag `prereg-p5-v7`): does
a registered, source-grounded observation-cost model select a contract
with strictly lower cost than at least one minimum-cardinality reduct,
on `domain_v4`'s own code/cloud domain (CH-B1, unmodified)? Reuses
`synthesis.find_minimum_cost_contract`/`find_minimum_cardinality_contract`
(Milestone D, already exactness-tested) and
`reduct.exact_reducts`/`sufficiency` (Milestone B), unmodified -- this
checker applies existing machinery to a new registered cost model
(`costs_v7.py`), it does not add a new derivation mechanism.

SUPPORTED iff the minimum-cost contract found is itself exactly
sufficient AND its registered total cost is strictly lower than at
least one minimum-cardinality reduct's cost. NOT SUPPORTED iff either
every minimum-cardinality reduct has exactly equal registered cost (a
genuine tie) or only one minimum-cardinality reduct exists -- both
registered as fully valid, fully reportable outcomes (prereg's own
decision rule), not a failed exercise."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, FrozenSet, List

from costs_v7 import ALPHA, BETA, GAMMA, DELTA, LATENCY_NORMALIZATION_MS, observation_costs_v7
from domain_v4 import CANDIDATE_PROPERTIES_V4, executable_reachable_tuples_v4
from losses_v4 import load_loss_registry_v4
from reduct import exact_reducts, sufficiency
from synthesis import find_minimum_cardinality_contract, find_minimum_cost_contract

OUTPUT_PATH = Path("out/checkers/ch_b2_check.json")

COST_TIE_EPSILON = 1e-9


def _certify(name: str, members: FrozenSet[str], reachable: List[Any], registry: Dict[str, Any]) -> Dict[str, Any]:
    """Definition 4's own sufficiency check, run directly against one
    candidate contract -- the safety-equivalence certificate: proof this
    contract actually closes the loss-discrimination gap, independent of
    its cost or cardinality."""
    is_sufficient, cert_or_counterexample = sufficiency(tuple(sorted(members)), reachable, registry)
    return {
        "members": sorted(members),
        "is_sufficient": is_sufficient,
        "sufficiency_certificate": cert_or_counterexample if is_sufficient else None,
        "counterexample": None if is_sufficient else cert_or_counterexample,
    }


def run() -> Dict[str, Any]:
    reachable = executable_reachable_tuples_v4()
    registry = load_loss_registry_v4()
    costs = observation_costs_v7()

    missing = set(CANDIDATE_PROPERTIES_V4) - set(costs)
    if missing:
        raise ValueError(f"costs_v7 declares no cost for: {sorted(missing)}")

    # Tie rule (prereg's own): "the minimum-cardinality set" is every
    # reduct exact_reducts finds at the minimum cardinality, not one
    # arbitrary solver model.
    reducts, subsets_considered = exact_reducts(CANDIDATE_PROPERTIES_V4, reachable, registry)
    minimum_cardinality = min(len(r) for r in reducts)
    minimum_cardinality_reducts = sorted(
        (sorted(r) for r in reducts if len(r) == minimum_cardinality),
        key=lambda r: r,
    )

    min_cost_contract = find_minimum_cost_contract(CANDIDATE_PROPERTIES_V4, reachable, registry, costs)
    # Cross-check only: a single RC2 model from the cardinality-only
    # backend, independent of the cost model entirely.
    min_cardinality_single_model = find_minimum_cardinality_contract(CANDIDATE_PROPERTIES_V4, reachable, registry)

    certificates: Dict[str, Any] = {"minimum_cost_contract": _certify("minimum_cost_contract", min_cost_contract, reachable, registry)}
    reduct_costs: Dict[str, float] = {}
    for i, r in enumerate(minimum_cardinality_reducts, start=1):
        key = f"minimum_cardinality_reduct_{i}"
        certificates[key] = _certify(key, frozenset(r), reachable, registry)
        reduct_costs[key] = sum(costs[p] for p in r)

    # Summed over `sorted(...)`, not the frozenset directly: floating-
    # point addition is not associative, and frozenset iteration order
    # depends on Python's per-process string-hash randomization -- an
    # unsorted sum here produced a different last-bit float (6.124 vs.
    # 6.123999999999999 vs. 6.1240000000000006, confirmed by direct
    # test) across separate processes, breaking release-check's own
    # formal-double-run byte-identity gate. A fixed iteration order
    # makes the summation, and so this float, reproducible.
    min_cost_total = sum(costs[p] for p in sorted(min_cost_contract))
    all_safety_equivalent = all(c["is_sufficient"] for c in certificates.values())

    strictly_cheaper_than = [k for k, rc in reduct_costs.items() if min_cost_total < rc - COST_TIE_EPSILON]
    supported = certificates["minimum_cost_contract"]["is_sufficient"] and bool(strictly_cheaper_than)

    if len(minimum_cardinality_reducts) < 2:
        outcome_subcase = "negative_single_reduct"
    elif strictly_cheaper_than:
        outcome_subcase = "positive_strict_cost_separation"
    else:
        outcome_subcase = "negative_tie"

    result: Dict[str, Any] = {
        "reachable_tuples_swept": len(reachable),
        "candidate_properties": list(CANDIDATE_PROPERTIES_V4),
        "cost_model": {
            "alpha": ALPHA, "beta": BETA, "gamma": GAMMA, "delta": DELTA,
            "latency_normalization_ms": LATENCY_NORMALIZATION_MS,
            "observation_costs": costs,
        },
        "minimum_cardinality": minimum_cardinality,
        "minimum_cardinality_reducts": minimum_cardinality_reducts,
        "minimum_cardinality_reduct_costs": reduct_costs,
        "minimum_cost_contract": sorted(min_cost_contract),
        "minimum_cost_contract_total_cost": min_cost_total,
        "minimum_cost_contract_is_a_minimum_cardinality_reduct": sorted(min_cost_contract) in minimum_cardinality_reducts,
        "minimum_cardinality_single_model_cross_check": {
            "members": sorted(min_cardinality_single_model),
            "is_a_minimum_cardinality_reduct": sorted(min_cardinality_single_model) in minimum_cardinality_reducts,
        },
        "safety_equivalence_certificates": certificates,
        "all_alternatives_safety_equivalent": all_safety_equivalent,
        "strictly_cheaper_than": strictly_cheaper_than,
        "subsets_considered": subsets_considered,
        "outcome_subcase": outcome_subcase,
        "supported": supported,
    }
    return result


def main() -> None:
    result = run()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"\nCH-B2: {'SUPPORTED' if result['supported'] else 'NOT SUPPORTED'} ({result['outcome_subcase']})")


if __name__ == "__main__":
    main()
