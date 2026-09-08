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
Milestone D5 (`prereg/v5-synthesis.md`, tag `prereg-p5-v5`): the two
registered synthesis benchmarks, transcribed unchanged from the
prereg's own constructions (Registration discipline: neither is
adjusted here to change its outcome), plus `contract_change_delta`
(`synthesis.py`) demonstrated on one concrete before/after pair.

Every tuple below is a real (frozen) dataclass instance, built via
`dataclasses.make_dataclass` where the field count is only known at run
time (Experiment 1's own `n`) -- NOT a `types.SimpleNamespace`:
`discernibility.py`/`reduct.py`/`synthesis.py` only ever call
`getattr(t, property_name)` and would accept a SimpleNamespace too, but
`reduct.sufficiency`'s own counterexample path serializes a witness pair
through `participation._serialize`, which calls `dataclasses.asdict` --
requiring an actual dataclass instance, not merely an attribute-bearing
object (found directly, by this module's own first run raising
`TypeError: asdict() should be called on dataclass instances`, not
assumed from reading `_serialize`'s source)."""
from __future__ import annotations

import json
import resource
import time
from dataclasses import make_dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

from reduct import exact_reducts
from synthesis import contract_change_delta, find_minimum_cardinality_contract, find_minimum_cost_contract

OUTPUT_PATH = Path("out/results/synthesis_benchmarks.json")

PLANTED_REDUCT_SIZE = 5


# -- Experiment 1: scaling benchmark on synthetic families with planted reducts --

def make_planted_family(n: int, k: int = PLANTED_REDUCT_SIZE) -> Tuple[Tuple[str, ...], List[Any]]:
    """prereg/v5-synthesis.md's own construction: n boolean properties
    p_1..p_n, the first k "signal", the rest "noise" (held at 0 across
    every tuple, never varied). k+1 tuples regardless of n: T_0 (every
    signal property 1) and, for each signal property, one T_i with that
    property alone flipped to 0."""
    names = tuple(f"p_{i + 1}" for i in range(n))
    PlantedTuple = make_dataclass(f"PlantedTuple{n}", [(name, int) for name in names], frozen=True)

    def make_tuple(flip_index: int = None) -> Any:
        values = {name: 0 for name in names}
        for i in range(k):
            values[names[i]] = 1
        if flip_index is not None:
            values[names[flip_index]] = 0
        return PlantedTuple(**values)

    tuples = [make_tuple()] + [make_tuple(i) for i in range(k)]
    return names, tuples


def planted_verdict_registry(k: int = PLANTED_REDUCT_SIZE):
    def verdict(t: Any) -> bool:
        return all(getattr(t, f"p_{i + 1}") == 1 for i in range(k))
    return {"all_signal_properties_set": verdict}


def run_scaling_experiment() -> Dict[str, Any]:
    planted = {f"p_{i + 1}" for i in range(PLANTED_REDUCT_SIZE)}
    results = []
    for n in (10, 30, 50, 100):
        names, tuples = make_planted_family(n)
        registry = planted_verdict_registry()

        baseline_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        t0 = time.perf_counter()
        contract = find_minimum_cardinality_contract(names, tuples, registry)
        elapsed = time.perf_counter() - t0
        peak_rss_delta = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss - baseline_rss

        exact = set(contract) == planted
        exhaustive_cross_check = None
        if n == 10:
            exhaustive_reducts, _ = exact_reducts(names, tuples, registry)
            exhaustive_cross_check = (
                len(exhaustive_reducts) == 1 and set(exhaustive_reducts[0]) == planted
            )

        results.append({
            "n": n,
            "reachable_tuple_count": len(tuples),
            "contract": sorted(contract),
            "exact": exact,
            "exhaustive_cross_check": exhaustive_cross_check,
            "wall_time_seconds": elapsed,
            "peak_memory_kb_delta": peak_rss_delta,
        })
    return {"planted_reduct_size": PLANTED_REDUCT_SIZE, "runs": results, "all_exact": all(r["exact"] for r in results)}


# -- Experiment 2: cost-aware synthesis --

COST_SUB_FACTOR_NAMES = ("latency", "privacy", "staleness", "failure_probability")
FLOOR_COST = 0.01


def declared_cost(sub_scores: Dict[str, float]) -> float:
    missing = set(COST_SUB_FACTOR_NAMES) - set(sub_scores)
    if missing:
        raise ValueError(f"missing sub-factor(s): {sorted(missing)}")
    total = sum(sub_scores[f] for f in COST_SUB_FACTOR_NAMES)
    return total if total > 0 else FLOOR_COST


def make_xor_bijection_domain() -> Tuple[Tuple[str, ...], List[Any], Dict[str, Any], Dict[str, float]]:
    """prereg/v5-synthesis.md's own construction, hand-derived and
    brute-force-verified before registration: a=0..3 <-> (b1,b2) via a
    declared bijection; verdict = a in {1,2} (equivalently b1 XOR b2).
    Reducts {a} (cardinality 1, cost 4.0) and {b1,b2} (cardinality 2,
    cost 1.0) -- registered, not discovered here."""
    XorTuple = make_dataclass("XorTuple", [("a", int), ("b1", int), ("b2", int)], frozen=True)
    bijection = {0: (0, 0), 1: (0, 1), 2: (1, 0), 3: (1, 1)}
    tuples = [XorTuple(a=a, b1=b1, b2=b2) for a, (b1, b2) in bijection.items()]
    registry = {"a_in_1_2": lambda t: t.a in (1, 2)}
    costs = {
        "a": declared_cost({"latency": 1.0, "privacy": 1.0, "staleness": 1.0, "failure_probability": 1.0}),
        "b1": declared_cost({"latency": 0.2, "privacy": 0.1, "staleness": 0.1, "failure_probability": 0.1}),
        "b2": declared_cost({"latency": 0.2, "privacy": 0.1, "staleness": 0.1, "failure_probability": 0.1}),
    }
    return ("a", "b1", "b2"), tuples, registry, costs


def _real_domain_costs(candidate_properties: Tuple[str, ...]) -> Dict[str, float]:
    """Uniform declared cost for this artifact's own real domains
    (v1/v2/v4): no per-property cost data has been declared for them
    (out of scope for those domains' own preregistrations), so every
    property is assigned the identical floor sub-scores -- with equal
    cost, minimum-cost and minimum-cardinality can never disagree on
    WHICH properties, only possibly on tie-breaking among equal-cost
    options, reported honestly as such, not disguised as a real
    per-property cost model that does not exist for these domains."""
    return {p: declared_cost({"latency": 0.25, "privacy": 0.25, "staleness": 0.25, "failure_probability": 0.25}) for p in candidate_properties}


def run_cost_aware_experiment() -> Dict[str, Any]:
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
    xor_props, xor_tuples, xor_registry, xor_costs = make_xor_bijection_domain()

    domains = [
        ("v1", CANDIDATE_PROPERTIES, executable_reachable_tuples(property_domains(grid)), load_loss_registry(loss_model), None),
        ("v2", CANDIDATE_PROPERTIES_V2, executable_reachable_tuples_v2(property_domains_v2(grid)), load_loss_registry_v2(loss_model), None),
        ("v4", CANDIDATE_PROPERTIES_V4, executable_reachable_tuples_v4(), load_loss_registry_v4(), None),
        ("xor_bijection", xor_props, xor_tuples, xor_registry, xor_costs),
    ]

    results = []
    for name, props, reachable, registry, declared_costs in domains:
        costs = declared_costs if declared_costs is not None else _real_domain_costs(props)
        min_card = find_minimum_cardinality_contract(props, reachable, registry)
        min_cost = find_minimum_cost_contract(props, reachable, registry, costs)
        differ = set(min_card) != set(min_cost)
        cost_of = lambda contract: sum(costs[p] for p in contract)
        results.append({
            "domain": name,
            "costs": costs,
            "minimum_cardinality_contract": sorted(min_card),
            "minimum_cardinality_contract_cost": cost_of(min_card),
            "minimum_cost_contract": sorted(min_cost),
            "minimum_cost_contract_cost": cost_of(min_cost),
            "contracts_differ": differ,
            "cost_delta": cost_of(min_card) - cost_of(min_cost),
        })
    return {"domains": results, "supported": any(r["contracts_differ"] for r in results)}


# -- contract_change_delta demonstration --

def run_contract_change_demo() -> Dict[str, Any]:
    """A small, hand-verified illustrative model (not this artifact's
    own real domain -- v1's own reachable set is already the full
    unconstrained product of its nine declared domains, so it has no
    "gap" a new transition could newly occupy without first shrinking
    it, which would be a different demonstration; a purpose-built model
    isolates the one thing being shown). Three candidate properties
    x, y, z; OLD reachable set and OLD registry (`x_ge_5` only) is
    exactly `test_synthesis.py`'s own fixture, whose reduct is already
    known to be `{x}` alone.

    The new transition: a tuple sharing x=1, y=1 with an existing OLD
    tuple (so it is indistinguishable from that tuple under `{x}`
    alone) but with a new `z` value ("c") a NEW predicate
    (`z_is_dangerous`, this demonstration's own stand-in for a newly
    added remediation operator's hazard) treats as hazardous -- the
    two tuples now disagree on verdict while still agreeing on `x`,
    which is exactly what breaks `{x}`'s sufficiency (Definition 4) and
    forces a genuine, not merely nominal, `contract_change_delta`."""
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class DemoTuple:
        x: int
        y: int
        z: str

    old_reachable = [DemoTuple(x=1, y=1, z="a"), DemoTuple(x=9, y=1, z="a"), DemoTuple(x=1, y=2, z="b")]
    candidate_properties = ("x", "y", "z")
    old_registry = {"x_ge_5": lambda t: t.x >= 5}

    base_contract = find_minimum_cardinality_contract(candidate_properties, old_reachable, old_registry)

    new_tuples = [DemoTuple(x=1, y=1, z="c")]
    combined_registry = {"x_ge_5": old_registry["x_ge_5"], "z_is_dangerous": lambda t: t.z == "c"}

    delta = contract_change_delta(base_contract, candidate_properties, old_reachable, new_tuples, combined_registry)
    return delta


def run() -> Dict[str, Any]:
    return {
        "experiment_1_scaling": run_scaling_experiment(),
        "experiment_2_cost_aware": run_cost_aware_experiment(),
        "contract_change_delta_demo": run_contract_change_demo(),
    }


def main() -> None:
    result = run()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
