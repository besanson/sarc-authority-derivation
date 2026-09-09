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
`prereg/v5.2-budget-binding-scenario.md` (tag `prereg-p5-v5.2`): the one
registered scenario where `spend_against_depleted_delegated_budget` is
given a real chance to fire -- the SAME 30 seeds x 2 workflows,
`period_budget_multiplier = 0.25` instead of the frozen v0.4 sweep's
`1.15`, via `experiments.run_seed_workflow`'s new optional parameter.
Writes to its own output directory (`out/results/budget_binding_
scenario/`) -- `out/results/sweep/` and `out/results/sweep_summary.json`
(the frozen v0.4 sweep at the original multiplier) are untouched.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from sweep import WORKFLOWS, load_seeds, mean_ci95
from experiments import run_seed_workflow

# Import order matters here, and is not just tidiness:
# experiments.py's own top-level code inserts sarc-suite-one-pass's
# directory at sys.path[0] (so it can import that sibling's composition/
# suite_sim modules) -- sarc-suite-one-pass ALSO happens to have its own
# sweep.py (this project's own sweep.py was ported from it, ADR-001).
# Importing `sweep` (this repo's own) BEFORE `experiments` resolves and
# caches the correct, local sweep.py first; importing it after would
# resolve `from sweep import ...` against the now-front-of-path sibling
# directory instead and fail with ImportError (found directly, by this
# module's own first run, not hypothesized in advance).

OUTPUT_DIR = Path("out/results/budget_binding_scenario")
OUTPUT_SUMMARY_PATH = Path("out/results/budget_binding_scenario_summary.json")
PERIOD_BUDGET_MULTIPLIER = 0.25


def run_scenario() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    seeds = load_seeds()
    for seed in seeds:
        for workflow in WORKFLOWS:
            seed_path = OUTPUT_DIR / f"seed_{seed}_{workflow}.json"
            if seed_path.exists():
                print(f"seed {seed} {workflow}: already computed, skipping", flush=True)
                continue
            print(f"seed {seed} {workflow}: running (multiplier={PERIOD_BUDGET_MULTIPLIER})...", flush=True)
            result = run_seed_workflow(seed, workflow, period_budget_multiplier=PERIOD_BUDGET_MULTIPLIER)
            seed_path.write_text(json.dumps(result, indent=2, sort_keys=True))
            print(f"seed {seed} {workflow}: done (budget_loss_fire_count={result['budget_loss_fire_count']})", flush=True)


def aggregate_scenario() -> Dict[str, Any]:
    seeds = load_seeds()
    per_cell: List[Dict[str, Any]] = []
    for seed in seeds:
        for workflow in WORKFLOWS:
            seed_path = OUTPUT_DIR / f"seed_{seed}_{workflow}.json"
            if not seed_path.exists():
                raise FileNotFoundError(f"missing scenario result for seed {seed} {workflow}: run run_scenario() first")
            per_cell.append(json.loads(seed_path.read_text()))

    total_fires = sum(r["budget_loss_fire_count"] for r in per_cell)
    firing_cells = [r for r in per_cell if r["budget_loss_fire_count"] > 0]
    budget_loss_fired_at_least_once = total_fires > 0

    # CH-A1 (prereg/hypotheses.md): derived_missed hypothesized zero.
    # Registered here at two granularities -- every cell (matching
    # sweep.py's own aggregate_sweep convention) and, the decisive
    # check this scenario exists for, only the cells where the budget
    # loss actually fired (prereg/v5.2's own decision rule).
    ch_a1_holds_on_all_cells = all(r["derived_missed"] == 0 for r in per_cell)
    ch_a1_holds_on_firing_cells = all(r["derived_missed"] == 0 for r in firing_cells) if firing_cells else None

    if not budget_loss_fired_at_least_once:
        decision = "NOT_EXERCISED: spend_against_depleted_delegated_budget did not fire even once under this multiplier"
    elif ch_a1_holds_on_firing_cells:
        decision = "SUPPORTED: budget loss fired, CH-A1's derived-zero-miss guarantee held on every cell where it fired"
    else:
        decision = "CH_A1_VIOLATED_ON_FIRING_CELLS: budget loss fired, but derived_missed was nonzero on at least one firing cell"

    return {
        "prereg": "prereg/v5.2-budget-binding-scenario.md",
        "period_budget_multiplier": PERIOD_BUDGET_MULTIPLIER,
        "n_cells": len(per_cell),
        "budget_loss_fired_at_least_once": budget_loss_fired_at_least_once,
        "total_budget_loss_fire_count": total_fires,
        "budget_loss_fire_count_ci": mean_ci95([float(r["budget_loss_fire_count"]) for r in per_cell]),
        "cells_with_at_least_one_fire": len(firing_cells),
        "ch_a1_baseline_missed_ci": mean_ci95([float(r["baseline_missed"]) for r in per_cell]),
        "ch_a1_derived_missed_ci": mean_ci95([float(r["derived_missed"]) for r in per_cell]),
        "ch_a1_holds_on_all_cells": ch_a1_holds_on_all_cells,
        "ch_a1_holds_on_cells_where_budget_loss_fired": ch_a1_holds_on_firing_cells,
        "decision": decision,
    }


def main() -> None:
    run_scenario()
    summary = aggregate_scenario()
    OUTPUT_SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_SUMMARY_PATH.write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
