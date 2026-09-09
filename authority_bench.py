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
Milestone E, Step 4 (`prereg/v6.1-authoritybench-amendment.md`, tag
`prereg-p5-v6.1`): "authority-bench run all" -- every one of the four
registered baselines (manual least-privilege, ABAC policy mining
reimplemented from Xu and Stoller, essential-variable analysis,
exhaustive reduct), on all three registered domains (v2, v4,
data-and-communications), all six registered metrics (correctness,
contract size, contract cost, runtime, memory, counterexamples) per
baseline per domain.

This IS "the FULL rewrite" the v6.0/Step-0-through-2 module docstrings
already named as a later, separate commit -- it replaces this file's own
prior content entirely (the exploratory two-baseline, three-domain
`run()`/`run_domain()`/`_relationship()` this project used from Milestone
E4 through Step 2). That EXPLORATORY result is not lost: it is already
committed and byte-frozen at `out/results/authority_bench.json` (commit
`0ecfeb3`, marked `exploratory_v6_0`/`excluded_from_benchmark_tables` at
its last regeneration, Step 1) -- this script no longer writes to that
path at all, the same "frozen, superseded by a new version" convention
this project already uses for the paper draft's own v0.1/v0.2/v0.3 files.
This script's own current output lives at `out/results/
authority_bench_v6_1.json`.

Baseline 2 (mining) is gated on Step 3's own validation
(`out/results/xu_stoller_validation.json`, `xu_stoller_validation.py`):
read here, not re-decided -- a baseline this file finds unvalidated would
be reported `excluded: True` with the registered reason, never silently
run anyway. As of Step 3's own commit, that gate is VALIDATED.

Baseline 4 (exhaustive reduct) IS this project's own canonical answer
(`reduct.exact_reducts`, the same call `src/authority_compiler`'s
`minimal_reducts` field also makes when tractable) -- reported here as
its own named row, not duplicated behind a second `derive_authority_
contract` call, since that would just be the identical computation under
a second name. The other three baselines' `correctness`/`contract_size`
rows are directly comparable against it without a fifth comparator.
"""
from __future__ import annotations

import argparse
import json
import resource
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import yaml

from mining_baseline import mine_policy, verify_soundness
from reduct import compute_core, exact_reducts, sufficiency

OUTPUT_PATH = Path("out/results/authority_bench_v6_1.json")
VALIDATION_PATH = Path("out/results/xu_stoller_validation.json")
DOMAIN_ROOT = Path("authority_bench_domains")
TIME_BUDGET_SECONDS = 1200.0  # prereg's own "Tractability contingency": 20 minutes per domain

# The already-committed, already machine-checked core/reduct facts each
# domain's own essential-variable-analysis baseline is cross-checked
# against (a genuine two-sided confirmation, not a definitional tautology
# -- `make formal` regenerates these independently of this script).
CHECKER_OUTPUT_PATHS: Dict[str, Path] = {
    "v2": Path("out/checkers/reduct_check.json"),
    "v4": Path("out/checkers/ch_b1_check.json"),
    "data-and-communications": Path("out/checkers/ch_datacomms_check.json"),
}


@dataclass(frozen=True)
class DomainSpec:
    name: str
    candidate_properties: Tuple[str, ...]
    reachable: List[Any]
    registry: Dict[str, Callable[[Any], bool]]
    manual_attributes: Tuple[str, ...]
    costs: Dict[str, float]


def _load_yaml(domain_folder: str, filename: str) -> Dict[str, Any]:
    return yaml.safe_load((DOMAIN_ROOT / domain_folder / filename).read_text())


def _manual_attributes(domain_folder: str) -> Tuple[str, ...]:
    """Step 2's own committed YAML packaging is the single source for
    the manual-least-privilege baseline's attribute set -- read here
    rather than re-typed a second time, so the two can never drift."""
    return tuple(_load_yaml(domain_folder, "baseline-manual-policy.yaml")["attributes"])


def _costs(domain_folder: str, candidate_properties: Tuple[str, ...]) -> Dict[str, float]:
    """REAL per-property costs where `candidate-context.yaml` declares
    them (data-and-communications, completed this Step -- see
    `build_authority_bench_domain_yaml.py`'s own Step 4 addendum); the
    uniform floor (`benchmarks._real_domain_costs`) where it does not
    (v2, v4 -- no per-property cost data was ever declared for them,
    prereg's own text: not retroactively invented here)."""
    from benchmarks import _real_domain_costs, declared_cost

    context = _load_yaml(domain_folder, "candidate-context.yaml")
    by_name = {p["name"]: p for p in context["candidate_properties"]}
    if all("observation_cost" in by_name[p] for p in candidate_properties):
        return {p: declared_cost(by_name[p]["observation_cost"]) for p in candidate_properties}
    return _real_domain_costs(candidate_properties)


def _domains() -> List[DomainSpec]:
    from domain import CANDIDATE_PROPERTIES_V2, executable_reachable_tuples_v2, load_loss_model, load_pair_test_grid, property_domains_v2
    from domain_datacomms import CANDIDATE_PROPERTIES_DATACOMMS, executable_reachable_tuples_datacomms
    from domain_v4 import CANDIDATE_PROPERTIES_V4, executable_reachable_tuples_v4
    from losses import load_loss_registry_v2
    from losses_datacomms import load_loss_registry_datacomms
    from losses_v4 import load_loss_registry_v4

    grid = load_pair_test_grid()
    loss_model = load_loss_model()

    raw = [
        ("v2", CANDIDATE_PROPERTIES_V2, executable_reachable_tuples_v2(property_domains_v2(grid)), load_loss_registry_v2(loss_model)),
        ("v4", CANDIDATE_PROPERTIES_V4, executable_reachable_tuples_v4(), load_loss_registry_v4()),
        ("data-and-communications", CANDIDATE_PROPERTIES_DATACOMMS, executable_reachable_tuples_datacomms(), load_loss_registry_datacomms()),
    ]
    return [
        DomainSpec(
            name=name,
            candidate_properties=candidate_properties,
            reachable=reachable,
            registry=registry,
            manual_attributes=_manual_attributes(name),
            costs=_costs(name, candidate_properties),
        )
        for name, candidate_properties, reachable, registry in raw
    ]


def _timed(fn: Callable[[], Any]) -> Tuple[Any, float, int]:
    """`benchmarks.py`'s own established runtime/memory pattern
    (`ru_maxrss` before/after): measures exactly the baseline's own
    derivation call, not the cheap bookkeeping (`_contract_row`) after
    it."""
    baseline_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    t0 = time.perf_counter()
    result = fn()
    elapsed = time.perf_counter() - t0
    peak_rss_delta = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss - baseline_rss
    return result, elapsed, peak_rss_delta


def _contract_row(attributes: Tuple[str, ...], reachable: List[Any], registry: Dict[str, Any], costs: Dict[str, float]) -> Dict[str, Any]:
    """The four per-contract metrics common to every baseline:
    correctness (Definition 4 sufficiency, `reduct.sufficiency`),
    contract size, contract cost, and counterexamples (the sufficiency
    certificate's own counterexample when correctness is false --
    `_serialize`d already, safe to embed directly)."""
    attrs_sorted = tuple(sorted(attributes))
    is_sufficient, cert_or_counterexample = sufficiency(attrs_sorted, reachable, registry)
    return {
        "attributes": list(attrs_sorted),
        "correctness": is_sufficient,
        "contract_size": len(attrs_sorted),
        "contract_cost": round(sum(costs[p] for p in attrs_sorted), 6) if attrs_sorted else 0.0,
        "counterexamples": None if is_sufficient else cert_or_counterexample,
    }


def run_manual_least_privilege(spec: DomainSpec) -> Dict[str, Any]:
    attrs, elapsed, peak_rss_delta = _timed(lambda: spec.manual_attributes)
    row = _contract_row(attrs, spec.reachable, spec.registry, spec.costs)
    return {"baseline": "manual_least_privilege", "excluded": False, "runtime_seconds": elapsed, "peak_rss_delta_kb": peak_rss_delta, **row}


def run_xu_stoller_mining(spec: DomainSpec, validated: bool, validation_result: Dict[str, Any]) -> Dict[str, Any]:
    if not validated:
        return {
            "baseline": "xu_stoller_mining",
            "excluded": True,
            "exclusion_reason": (
                "Step 3's validation gate (out/results/xu_stoller_validation.json) reported "
                f"disposition={validation_result.get('disposition')!r}; an unvalidated baseline "
                "is reported excluded, never used (prereg/v6.1-authoritybench-amendment.md)."
            ),
        }
    mining_result, elapsed, peak_rss_delta = _timed(
        lambda: mine_policy(spec.candidate_properties, spec.reachable, spec.registry, time_budget_seconds=TIME_BUDGET_SECONDS)
    )
    soundness = verify_soundness(spec.candidate_properties, spec.reachable, spec.registry, mining_result["rules"])
    row = _contract_row(mining_result["mined_attributes"], spec.reachable, spec.registry, spec.costs)
    return {
        "baseline": "xu_stoller_mining",
        "excluded": False,
        "runtime_seconds": elapsed,
        "peak_rss_delta_kb": peak_rss_delta,
        **row,
        "mining_rule_count": mining_result["rule_count_after_simplify"],
        "mining_tractable": mining_result["tractable"],
        "mining_rule_level_sound": soundness["sound"],
        "mining_rule_level_mismatch_count": soundness["mismatch_count"],
    }


def run_essential_variable_analysis(spec: DomainSpec) -> Dict[str, Any]:
    (core_attrs, _redundant, _witnesses), elapsed, peak_rss_delta = _timed(
        lambda: compute_core(spec.reachable, spec.registry, spec.candidate_properties)
    )
    row = _contract_row(tuple(core_attrs), spec.reachable, spec.registry, spec.costs)

    committed = json.loads(CHECKER_OUTPUT_PATHS[spec.name].read_text())
    identity_confirmed = sorted(core_attrs) == sorted(committed["core_attributes"])

    return {
        "baseline": "essential_variable_analysis",
        "excluded": False,
        "runtime_seconds": elapsed,
        "peak_rss_delta_kb": peak_rss_delta,
        **row,
        "matches_already_committed_checker_core": identity_confirmed,
        "committed_checker_source": str(CHECKER_OUTPUT_PATHS[spec.name]),
    }


def run_exhaustive_reduct(spec: DomainSpec) -> Dict[str, Any]:
    (reducts, subsets_considered), elapsed, peak_rss_delta = _timed(
        lambda: exact_reducts(spec.candidate_properties, spec.reachable, spec.registry)
    )
    rows = [_contract_row(tuple(r), spec.reachable, spec.registry, spec.costs) for r in reducts]
    cardinalities = [len(r) for r in reducts]
    return {
        "baseline": "exhaustive_reduct",
        "excluded": False,
        "runtime_seconds": elapsed,
        "peak_rss_delta_kb": peak_rss_delta,
        "subsets_considered": subsets_considered,
        "reduct_count": len(reducts),
        "minimum_cardinality": min(cardinalities) if cardinalities else 0,
        "reducts": rows,
    }


def run_domain(spec: DomainSpec, mining_validated: bool, validation_result: Dict[str, Any]) -> Dict[str, Any]:
    baselines = {
        "manual_least_privilege": run_manual_least_privilege(spec),
        "xu_stoller_mining": run_xu_stoller_mining(spec, mining_validated, validation_result),
        "essential_variable_analysis": run_essential_variable_analysis(spec),
        "exhaustive_reduct": run_exhaustive_reduct(spec),
    }

    # Descriptive only (not a registered decision rule): which of the
    # three single-contract baselines (exhaustive_reduct reports a SET,
    # not one row, so it is not itself "sufficient"/"insufficient" here)
    # are sufficient on this domain, and the cheapest/smallest among them.
    single_contract = {k: v for k, v in baselines.items() if k != "exhaustive_reduct" and not v.get("excluded")}
    sufficient = {k: v for k, v in single_contract.items() if v["correctness"]}
    summary = {
        "sufficient_baselines": sorted(sufficient),
        "insufficient_baselines": sorted(set(single_contract) - set(sufficient)),
        "smallest_sufficient_baseline_by_size": (min(sufficient, key=lambda k: sufficient[k]["contract_size"]) if sufficient else None),
        "cheapest_sufficient_baseline_by_cost": (min(sufficient, key=lambda k: sufficient[k]["contract_cost"]) if sufficient else None),
    }

    return {
        "domain": spec.name,
        "candidate_property_count": len(spec.candidate_properties),
        "reachable_tuple_count": len(spec.reachable),
        "manual_attributes": list(spec.manual_attributes),
        "costs": spec.costs,
        "baselines": baselines,
        "summary": summary,
    }


def run() -> Dict[str, Any]:
    validation_result = json.loads(VALIDATION_PATH.read_text())
    mining_validated = bool(validation_result["validated"])

    specs = _domains()
    domains = [run_domain(spec, mining_validated, validation_result) for spec in specs]

    return {
        "prereg": "prereg/v6.1-authoritybench-amendment.md",
        "supersedes": "out/results/authority_bench.json (commit 0ecfeb3, exploratory_v6_0 -- kept, frozen, not re-read or re-written by this script)",
        "xu_stoller_mining_validated": mining_validated,
        "xu_stoller_validation_source": str(VALIDATION_PATH),
        "domains": domains,
    }


def _json_default(obj: Any) -> Any:
    """A mined rule (baseline 2) may pin a frozenset-valued property
    (v2's `consumed_grant_ids`) to one specific value -- the same
    long-standing reason `participation._serialize`/this file's own
    prior version needed this hook, kept for the same class of field."""
    if isinstance(obj, frozenset):
        return sorted(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def main() -> None:
    # Package A (review-secondary/final-gap-plan-9.5-2026-09-09.pdf's
    # own mandatory CI smoke test): the console script previously took
    # no arguments at all, so `authority-bench --help` silently ran the
    # full four-baseline/three-domain benchmark instead of printing
    # usage and exiting -- argparse's own free `-h`/`--help` (any parser,
    # even one with zero declared arguments, gets it) fixes that without
    # changing the no-argument case `make authority-bench` already relies on.
    argparse.ArgumentParser(
        prog="authority-bench",
        description="AuthorityBench (prereg-p5-v6.1): four baselines x three domains x six metrics. "
                     "Writes out/results/authority_bench_v6_1.json.",
    ).parse_args()
    result = run()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True, default=_json_default))
    print(json.dumps(result, indent=2, sort_keys=True, default=_json_default))


if __name__ == "__main__":
    main()
