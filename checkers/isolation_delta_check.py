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
v0.4 isolation-hypothesis delta check (prereg/v3.1-isolated-arms.md,
tag `prereg-p5-v3.1`, "Hypothesis" section). Compares the freshly re-run
`out/results/sweep_summary.json` (isolated ArmState, v0.4) against
v0.1-v0.3's own frozen sweep result -- unchanged since commit `7b57f08`
(`git log -- out/results/sweep_summary.json` has exactly one entry; no
v0.2/v0.2.1/v0.3 revision ever touched the experiment's decision rules
or parameters, only this v0.4 one does) -- read via `git show`, not a
duplicated file, so there is exactly one committed copy of any given
sweep result at any time.

Material movement, per the registered decision rule: a CI-bearing
metric's v0.4 mean falls outside v0.3's own committed 95% CI, OR a
boolean flips between the two. Decided mechanically here, not eyeballed;
`do not reinterpret` (task brief) means this script's verdict is what
the paper reports, not a starting point for adjustment.

Also recomputes, directly and exhaustively (not sampled), whether
`spend_against_depleted_delegated_budget` -- the one loss predicate that
actually reads `budget_remaining`, the one field v0.1-v0.3's shared-state
bug could have made wrong -- ever fires across the full 30-seed x
2-workflow sweep under the new isolated `derived` arm trajectory. This is
the direct, mechanistic explanation for whatever the delta table shows
(a real structural bug can still produce zero measured consequence if
the field it corrupted never happens to be the deciding one for any
actual decision in this declared parameter set) -- computed, not assumed
from the delta table's shape alone.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict

from domain import load_all_skus, load_loss_model
from experiments import (
    ARM_NAMES,
    DATA_PATH,
    ROLE_BY_WORKFLOW,
    UNAUTHORIZED_RATE,
    UNAUTHORIZED_ROLE,
    _make_arm_states,
    calibrate_period_budget,
    enrich_plan,
    process_decision,
)
from losses import load_loss_registry
from suite_sim import RetailSimulation

OUTPUT_PATH = Path("out/checkers/isolation_delta_check.json")
CURRENT_SUMMARY_PATH = Path("out/results/sweep_summary.json")
FROZEN_SUMMARY_COMMIT = "7b57f08"  # last (only) commit to touch out/results/sweep_summary.json before v0.4
SEEDS_PATH = "prereg/seeds.json"
WORKFLOWS = ("W1", "W2")

CI_FIELDS = [
    "ch_a1_baseline_missed", "ch_a1_true_violations", "ch_a3_off_admissions",
    "ch_a3_replay_probe_count", "ch_a3_escalation_overhead", "spurious_escalations_overinclusive",
]
BOOL_FIELDS = ["ch_a1_derived_zero_every_cell", "ch_a3_on_zero_every_cell", "ch_a3_off_nonzero_at_least_one_cell"]


def _load_frozen_v03_summary() -> Dict[str, Any]:
    raw = subprocess.run(
        ["git", "show", f"{FROZEN_SUMMARY_COMMIT}:out/results/sweep_summary.json"],
        capture_output=True, text=True, check=True,
    ).stdout
    return json.loads(raw)


def compute_delta(old: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
    ci_deltas = {}
    material = []
    for f in CI_FIELDS:
        o, n = old[f], new[f]
        outside = not (o["ci95_low"] <= n["mean"] <= o["ci95_high"])
        ci_deltas[f] = {"v03_mean": o["mean"], "v03_ci95": [o["ci95_low"], o["ci95_high"]], "v04_mean": n["mean"], "v04_ci95": [n["ci95_low"], n["ci95_high"]], "material": outside}
        if outside:
            material.append(f)
    bool_deltas = {}
    for f in BOOL_FIELDS:
        flip = old[f] != new[f]
        bool_deltas[f] = {"v03": old[f], "v04": new[f], "material": flip}
        if flip:
            material.append(f)
    robustness_flip = old["ch_a4_robustness"] != new["ch_a4_robustness"]
    if robustness_flip:
        material.append("ch_a4_robustness")
    return {
        "ci_field_deltas": ci_deltas,
        "bool_field_deltas": bool_deltas,
        "ch_a4_robustness_v03": old["ch_a4_robustness"],
        "ch_a4_robustness_v04": new["ch_a4_robustness"],
        "ch_a4_robustness_flip": robustness_flip,
        "material_movement_fields": material,
        "isolation_hypothesis_supported": len(material) > 0,
    }


def count_budget_predicate_fires() -> Dict[str, Any]:
    """Exhaustive over the full registered sweep (all 30 seeds x 2
    workflows): how many decisions would have `order_value_post >
    derived's own budget_remaining` -- the one condition v0.1-v0.3's
    shared-budget bug could have gotten wrong -- true at all, under the
    isolated `derived` arm. A run with zero fires directly explains a
    byte-identical delta table: the corrupted field was never load-
    bearing for this declared parameter set, not that the fix did nothing."""
    seeds = json.loads(Path(SEEDS_PATH).read_text())["seeds"]
    loss_model = load_loss_model()
    registry = load_loss_registry(loss_model)
    all_skus = load_all_skus(DATA_PATH)

    total_decisions = 0
    total_fires = 0
    per_cell_fires = {}
    for seed in seeds:
        for workflow in WORKFLOWS:
            full_role = ROLE_BY_WORKFLOW[workflow]
            sim = RetailSimulation(DATA_PATH)
            plan = sim.generate_plan(
                seed=seed, unauthorized_role_rate=UNAUTHORIZED_RATE, authorized_roles=[full_role],
                unauthorized_role=UNAUTHORIZED_ROLE, workflow=workflow,
                commitment_period_days=(7 if workflow == "W2" else 1),
            )
            enriched = enrich_plan(plan, seed, workflow, all_skus)
            period_budget = calibrate_period_budget(enriched)
            arms = _make_arm_states(period_budget)
            current_day = enriched[0].day if enriched else 0
            fires = 0
            for d in enriched:
                if d.day != current_day:
                    for a in arms.values():
                        a.budget_remaining = period_budget
                    current_day = d.day
                if d.order_value_post > arms["derived"].budget_remaining:
                    fires += 1
                process_decision(
                    arms, actor_role=d.actor_role, resource_class=d.resource_class,
                    order_value=d.order_value_post, day=d.day, workflow=d.workflow, frozen=False,
                    decision_id=d.decision_id, sku=d.sku, registry=registry, baseline_admits=True,
                )
            total_decisions += len(enriched)
            total_fires += fires
            per_cell_fires[f"{seed}_{workflow}"] = fires

    return {
        "total_decisions_swept": total_decisions,
        "total_budget_predicate_fires": total_fires,
        "cells_with_at_least_one_fire": sum(1 for v in per_cell_fires.values() if v > 0),
        "n_cells": len(per_cell_fires),
    }


def run() -> Dict[str, Any]:
    old = _load_frozen_v03_summary()
    new = json.loads(CURRENT_SUMMARY_PATH.read_text())
    delta = compute_delta(old, new)
    budget_fires = count_budget_predicate_fires()
    return {
        "frozen_v03_summary_commit": FROZEN_SUMMARY_COMMIT,
        **delta,
        "budget_predicate_fire_diagnostic": budget_fires,
    }


def main() -> None:
    result = run()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
