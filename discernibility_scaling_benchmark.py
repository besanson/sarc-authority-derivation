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
`prereg/v5.1-discernibility-scaling.md` (tag `prereg-p5-v5.1`): the
successor to `benchmarks.py`'s Experiment 1 (planted-reduct scaling,
which scales candidate-property count while holding the reachable set
fixed at 6 tuples). This scales the REACHABLE SET itself (>=10^3, 10^4,
10^5 tuples) on a family with TWO planted minimal reducts, not one, and
measures all three `synthesis.py` backends (not just cardinality) on it
and on this artifact's own v2/v4/data-and-communications domains.

Writes `out/results/discernibility_scaling_v5_1.json` --
`out/results/synthesis_benchmarks.json` (Experiment 1's own frozen
output) is untouched; `benchmarks.py` itself is not modified, the same
"kept, frozen, superseded by a new file" convention already used for
`out/results/authority_bench.json`/`authority_bench_v6_1.json`.
"""
from __future__ import annotations

import json
import resource
import time
from dataclasses import make_dataclass
from pathlib import Path
from typing import Any, Callable, Dict, FrozenSet, List, Tuple

from discernibility import build_discernibility_family, remove_redundant_supersets
from reduct import exact_reducts, sufficiency
from synthesis import find_any_sufficient_contract, find_minimum_cardinality_contract, find_minimum_cost_contract

OUTPUT_PATH = Path("out/results/discernibility_scaling_v5_1.json")
NOISE_DOMAIN_SIZE = 10
REGISTERED_Q_VALUES = (3, 4, 5)


def make_multi_reduct_family(q: int, r: int = NOISE_DOMAIN_SIZE) -> Tuple[Tuple[str, ...], List[Any]]:
    """`prereg/v5.1`'s own construction, hand-derived and proved there
    before this function was written: two "twin" boolean properties
    (`twin_a`, `twin_b`, always equal in every tuple this function
    builds) plus `q` boolean-valued-domain noise properties each
    ranging over `r` values. Reachable set = one True tuple (`T_0`:
    twins=1, noise at baseline) plus one False tuple per noise
    assignment (twins=0) -- exactly `1 + r**q` tuples, matching the
    prereg's own predicted sizes (1001/10001/100001 for q=3/4/5)."""
    noise_names = tuple(f"noise_{i + 1}" for i in range(q))
    names = ("twin_a", "twin_b") + noise_names
    FamilyTuple = make_dataclass(f"MultiReductTuple{q}", [(name, int) for name in names], frozen=True)

    def noise_combo(index: int) -> Dict[str, int]:
        digits = {}
        remaining = index
        for name in noise_names:
            digits[name] = remaining % r
            remaining //= r
        return digits

    tuples = [FamilyTuple(twin_a=1, twin_b=1, **{name: 0 for name in noise_names})]
    for index in range(r ** q):
        tuples.append(FamilyTuple(twin_a=0, twin_b=0, **noise_combo(index)))
    return names, tuples


def multi_reduct_registry() -> Dict[str, Callable[[Any], bool]]:
    return {"twin_both_set": lambda t: t.twin_a == 1 and t.twin_b == 1}


def multi_reduct_costs(candidate_properties: Tuple[str, ...]) -> Dict[str, float]:
    """`prereg/v5.1`'s own declared costs: `twin_a` cheaper than
    `twin_b`, so minimum-cost synthesis has a single predicted correct
    answer (`{twin_a}`) distinguishable from minimum-cardinality's
    two-way tie; every noise property priced low and uniformly (never
    part of any reduct, so its exact price does not matter to the
    result, only that it is declared and positive, `synthesis.py`'s own
    precondition)."""
    costs = {"twin_a": 1.0, "twin_b": 2.0}
    for p in candidate_properties:
        if p not in costs:
            costs[p] = 0.1
    return costs


def _timed(fn: Callable[[], Any]) -> Tuple[Any, float, int]:
    baseline_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    t0 = time.perf_counter()
    result = fn()
    elapsed = time.perf_counter() - t0
    peak_rss_delta = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss - baseline_rss
    return result, elapsed, peak_rss_delta


def run_family(
    name: str,
    candidate_properties: Tuple[str, ...],
    reachable: List[Any],
    registry: Dict[str, Callable[[Any], bool]],
    costs: Dict[str, float],
) -> Dict[str, Any]:
    """The four registered metrics (discernibility family size after
    superset removal, exact, wall time, peak memory), for each of the
    three `synthesis.py` backends, on one family. "Exact" is checked
    against `reduct.exact_reducts()`'s own from-first-principles answer
    -- feasible at every registered family (`prereg/v5.1`'s own
    hand-derivation: candidate-property count never exceeds 10 here),
    not against this module's own predicted answer alone."""
    family = remove_redundant_supersets(build_discernibility_family(candidate_properties, reachable, registry))

    (reducts, subsets_considered), reducts_elapsed, reducts_rss = _timed(
        lambda: exact_reducts(candidate_properties, reachable, registry)
    )
    minimum_cardinality = min((len(r) for r in reducts), default=0)
    reduct_costs = {r: sum(costs[p] for p in r) for r in reducts}
    minimum_cost = min(reduct_costs.values()) if reduct_costs else 0.0

    def contract_cost(contract: FrozenSet[str]) -> float:
        return sum(costs[p] for p in contract)

    any_contract, any_elapsed, any_rss = _timed(lambda: find_any_sufficient_contract(candidate_properties, reachable, registry))
    any_is_sufficient, _ = sufficiency(tuple(sorted(any_contract)), reachable, registry)

    card_contract, card_elapsed, card_rss = _timed(lambda: find_minimum_cardinality_contract(candidate_properties, reachable, registry))
    card_exact = frozenset(card_contract) in reducts and len(card_contract) == minimum_cardinality

    cost_contract, cost_elapsed, cost_rss = _timed(lambda: find_minimum_cost_contract(candidate_properties, reachable, registry, costs))
    cost_exact = frozenset(cost_contract) in reducts and contract_cost(cost_contract) == minimum_cost

    return {
        "family": name,
        "candidate_property_count": len(candidate_properties),
        "reachable_tuple_count": len(reachable),
        "discernibility_family_size_after_superset_removal": len(family),
        "exhaustive_cross_check": {
            "reducts": [sorted(r) for r in reducts],
            "minimum_cardinality": minimum_cardinality,
            "minimum_cost": minimum_cost,
            "subsets_considered": subsets_considered,
            "wall_time_seconds": reducts_elapsed,
            "peak_memory_kb_delta": reducts_rss,
        },
        "backends": {
            "sat_any_sufficient": {
                "contract": sorted(any_contract),
                "is_sufficient": any_is_sufficient,
                "matches_a_known_minimal_reduct": frozenset(any_contract) in reducts,
                "wall_time_seconds": any_elapsed,
                "peak_memory_kb_delta": any_rss,
            },
            "cardinality_maxsat": {
                "contract": sorted(card_contract),
                "exact": card_exact,
                "wall_time_seconds": card_elapsed,
                "peak_memory_kb_delta": card_rss,
            },
            "weighted_maxsat_cost": {
                "contract": sorted(cost_contract),
                "exact": cost_exact,
                "contract_cost": contract_cost(cost_contract),
                "wall_time_seconds": cost_elapsed,
                "peak_memory_kb_delta": cost_rss,
            },
        },
    }


def _real_domain_families() -> List[Tuple[str, Tuple[str, ...], List[Any], Dict[str, Any], Dict[str, float]]]:
    from benchmarks import _real_domain_costs, declared_cost
    from domain import CANDIDATE_PROPERTIES_V2, executable_reachable_tuples_v2, load_loss_model, load_pair_test_grid, property_domains_v2
    from domain_datacomms import CANDIDATE_PROPERTIES_DATACOMMS, PROPERTY_OBSERVATION_COSTS_DATACOMMS, executable_reachable_tuples_datacomms
    from domain_v4 import CANDIDATE_PROPERTIES_V4, executable_reachable_tuples_v4
    from losses import load_loss_registry_v2
    from losses_datacomms import load_loss_registry_datacomms
    from losses_v4 import load_loss_registry_v4

    grid = load_pair_test_grid()
    loss_model = load_loss_model()

    return [
        ("v2", CANDIDATE_PROPERTIES_V2, executable_reachable_tuples_v2(property_domains_v2(grid)), load_loss_registry_v2(loss_model),
         _real_domain_costs(CANDIDATE_PROPERTIES_V2)),
        ("v4", CANDIDATE_PROPERTIES_V4, executable_reachable_tuples_v4(), load_loss_registry_v4(),
         _real_domain_costs(CANDIDATE_PROPERTIES_V4)),
        ("data-and-communications", CANDIDATE_PROPERTIES_DATACOMMS, executable_reachable_tuples_datacomms(), load_loss_registry_datacomms(),
         {p: declared_cost(PROPERTY_OBSERVATION_COSTS_DATACOMMS[p]) for p in CANDIDATE_PROPERTIES_DATACOMMS}),
    ]


def run() -> Dict[str, Any]:
    synthetic = []
    for q in REGISTERED_Q_VALUES:
        names, tuples = make_multi_reduct_family(q)
        synthetic.append(run_family(f"multi_reduct_q{q}", names, tuples, multi_reduct_registry(), multi_reduct_costs(names)))

    real = [run_family(name, props, reachable, registry, costs) for name, props, reachable, registry, costs in _real_domain_families()]

    return {
        "prereg": "prereg/v5.1-discernibility-scaling.md",
        "supersedes": "out/results/synthesis_benchmarks.json's experiment_1_scaling (relabelled exploratory_v5_0, NOVELTY.md) -- kept, frozen, not re-read or re-written by this script",
        "synthetic_families": synthetic,
        "real_domains": real,
    }


def main() -> None:
    result = run()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
