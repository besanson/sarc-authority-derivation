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
Phase 3: the 30-seed x 2-workflow statistical sweep (prereg/seeds.json),
CH-A1, CH-A3, and CH-A4's per-cell robustness readout. Pattern (per-seed
checkpointing, order-stable t-based mean_ci95) ported with attribution
from sarc-suite-one-pass's sweep.py (ADR-001-foundation.md); the metric
bodies are this paper's own (experiments.py), not one-pass's CH1-CH8.

SEED = 26313 (first entry of prereg/seeds.json)
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, List

import scipy.stats

from experiments import run_seed_workflow

SEEDS_PATH = "prereg/seeds.json"
WORKFLOWS = ("W1", "W2")
SWEEP_DIR = Path("out/results/sweep")
SWEEP_SUMMARY_PATH = Path("out/results/sweep_summary.json")

# 95% two-tailed t-critical value for df = 30 - 1 = 29, computed exactly
# at runtime (ported convention, sarc-suite-one-pass's sweep.py finding
# F6: a rounded constant diverges from the exact value). The registered
# seed list is fixed at exactly 30 entries, so this single value is
# always the correct one. Cast to plain float: scipy.stats.t.ppf returns
# a numpy float64, not JSON-serializable by json.dump.
T_CRIT_DF29 = float(scipy.stats.t.ppf(0.975, 29))


def load_seeds() -> List[int]:
    return json.loads(Path(SEEDS_PATH).read_text())["seeds"]


def mean_ci95(values: List[float]) -> Dict[str, float]:
    """Order-stable (ported convention): mean and variance via math.fsum
    over explicitly sorted inputs, not naive sum()/len(), so the result
    cannot depend on the order `values` happened to arrive in."""
    n = len(values)
    if n == 0:
        return {"mean": 0.0, "ci95_low": 0.0, "ci95_high": 0.0, "n": 0}
    ordered = sorted(values)
    m = math.fsum(ordered) / n
    if n < 2:
        return {"mean": m, "ci95_low": m, "ci95_high": m, "n": n}
    squared_deviations = sorted((v - m) ** 2 for v in ordered)
    variance = math.fsum(squared_deviations) / (n - 1)
    se = math.sqrt(variance) / math.sqrt(n)
    half = T_CRIT_DF29 * se
    return {"mean": m, "ci95_low": m - half, "ci95_high": m + half, "n": n}


def run_sweep() -> None:
    SWEEP_DIR.mkdir(parents=True, exist_ok=True)
    seeds = load_seeds()
    for seed in seeds:
        for workflow in WORKFLOWS:
            seed_path = SWEEP_DIR / f"seed_{seed}_{workflow}.json"
            if seed_path.exists():
                print(f"seed {seed} {workflow}: already computed, skipping", flush=True)
                continue
            print(f"seed {seed} {workflow}: running ...", flush=True)
            result = run_seed_workflow(seed, workflow)
            seed_path.write_text(json.dumps(result, indent=2, sort_keys=True))
            print(f"seed {seed} {workflow}: done", flush=True)


def aggregate_sweep() -> Dict[str, Any]:
    seeds = load_seeds()
    per_cell: List[Dict[str, Any]] = []
    for seed in seeds:
        for workflow in WORKFLOWS:
            seed_path = SWEEP_DIR / f"seed_{seed}_{workflow}.json"
            if not seed_path.exists():
                raise FileNotFoundError(f"missing sweep result for seed {seed} {workflow}: run run_sweep() first")
            per_cell.append(json.loads(seed_path.read_text()))

    # CH-A1: derived_missed is zero on every cell (decision rule); baseline_missed reported with CIs.
    ch_a1_derived_zero_every_cell = all(r["derived_missed"] == 0 for r in per_cell)
    ch_a1_baseline_missed_ci = mean_ci95([float(r["baseline_missed"]) for r in per_cell])
    ch_a1_true_violations_ci = mean_ci95([float(r["true_violations"]) for r in per_cell])

    # CH-A3: replay admissions are zero (on) on every cell; nonzero (off) on at least one -- positive control.
    ch_a3_on_zero_every_cell = all(r["replay_admissions_grant_binding_on"] == 0 for r in per_cell)
    ch_a3_off_nonzero_at_least_one = any(r["replay_admissions_grant_binding_off"] > 0 for r in per_cell)
    ch_a3_off_admissions_ci = mean_ci95([float(r["replay_admissions_grant_binding_off"]) for r in per_cell])
    ch_a3_replay_probe_count_ci = mean_ci95([float(r["replay_probe_count"]) for r in per_cell])
    # Escalation overhead (task brief CH-A3: "reported, not registered"): with
    # grant binding on, every correctly-rejected replay probe is a decision
    # that needs a fresh grant issuance round trip before it can be admitted
    # at all -- since replay_admissions_grant_binding_on is zero on every
    # cell (ch_a3_on_zero_every_cell), that is exactly every injected replay
    # probe, given its own name here rather than left implicit under
    # replay_probe_count's name.
    escalation_overhead_ci = mean_ci95([float(r["replay_probe_count"] - r["replay_admissions_grant_binding_on"]) for r in per_cell])

    # Overderivation ablation (spurious escalation cost), reported descriptively.
    spurious_escalations_ci = mean_ci95([float(r["spurious_escalations_overinclusive"]) for r in per_cell])

    per_workflow: Dict[str, Any] = {}
    for workflow in WORKFLOWS:
        cells = [r for r in per_cell if r["workflow"] == workflow]
        per_workflow[workflow] = {
            "n_seeds": len(cells),
            "ch_a1_derived_zero_every_seed": all(r["derived_missed"] == 0 for r in cells),
            "ch_a1_baseline_missed": mean_ci95([float(r["baseline_missed"]) for r in cells]),
            "ch_a3_on_zero_every_seed": all(r["replay_admissions_grant_binding_on"] == 0 for r in cells),
            "ch_a3_off_nonzero_at_least_one_seed": any(r["replay_admissions_grant_binding_off"] > 0 for r in cells),
            "spurious_escalations_overinclusive": mean_ci95([float(r["spurious_escalations_overinclusive"]) for r in cells]),
        }

    summary: Dict[str, Any] = {
        "n_cells": len(per_cell),
        "seeds": seeds,
        "workflows": list(WORKFLOWS),
        "ch_a1_derived_zero_every_cell": ch_a1_derived_zero_every_cell,
        "ch_a1_baseline_missed": ch_a1_baseline_missed_ci,
        "ch_a1_true_violations": ch_a1_true_violations_ci,
        "ch_a3_on_zero_every_cell": ch_a3_on_zero_every_cell,
        "ch_a3_off_nonzero_at_least_one_cell": ch_a3_off_nonzero_at_least_one,
        "ch_a3_off_admissions": ch_a3_off_admissions_ci,
        "ch_a3_replay_probe_count": ch_a3_replay_probe_count_ci,
        "ch_a3_escalation_overhead": escalation_overhead_ci,
        "spurious_escalations_overinclusive": spurious_escalations_ci,
        "per_workflow": per_workflow,
        "ch_a4_robustness": {
            "ch_a1_robust": ch_a1_derived_zero_every_cell,
            "ch_a3_robust": ch_a3_on_zero_every_cell and ch_a3_off_nonzero_at_least_one,
            "all_robust": ch_a1_derived_zero_every_cell and ch_a3_on_zero_every_cell and ch_a3_off_nonzero_at_least_one,
        },
    }
    SWEEP_SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SWEEP_SUMMARY_PATH.write_text(json.dumps(summary, indent=2, sort_keys=True))
    return summary


if __name__ == "__main__":
    run_sweep()
    summary = aggregate_sweep()
    print(json.dumps(summary, indent=2, sort_keys=True))
