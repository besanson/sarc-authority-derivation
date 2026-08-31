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
Phase 5 (slots pipeline, pattern ported with attribution from
sarc-suite-one-pass's paper_tables.py -- ADR-001-foundation.md): builds
every `[GENERATED: ...]` slot the paper draft uses, solely from committed
machine output (out/checkers/*.json, out/results/sweep_summary.json) --
no independent re-derivation, no typed numbers.

The abstract's results sentence (task brief Phase 4) is built the same
way: from the measured CH-A1..CH-A4 booleans in sweep_summary.json's
ch_a4_robustness block, printing "NOT SUPPORTED" wherever a decision
rule did not hold, never assumed to have held.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def _fmt_ci(ci: Dict[str, float], decimals: int = 1) -> str:
    return f"{ci['mean']:.{decimals}f} (95% CI [{ci['ci95_low']:.{decimals}f}, {ci['ci95_high']:.{decimals}f}], n={ci['n']})"


def _supported(flag: bool) -> str:
    return "SUPPORTED" if flag else "NOT SUPPORTED"


def build_slots(
    derivation_path: str = "out/checkers/derivation_output.json",
    participation_check_path: str = "out/checkers/participation_check.json",
    pairtest_check_path: str = "out/checkers/pairtest_check.json",
    grant_check_path: str = "out/checkers/grant_check.json",
    sweep_summary_path: str = "out/results/sweep_summary.json",
) -> Dict[str, str]:
    derivation = json.loads(Path(derivation_path).read_text())
    pcheck = json.loads(Path(participation_check_path).read_text())
    ptcheck = json.loads(Path(pairtest_check_path).read_text())
    gcheck = json.loads(Path(grant_check_path).read_text())
    sweep = json.loads(Path(sweep_summary_path).read_text())

    p_star = sorted(derivation["participating_properties"])
    coverage = sorted(derivation["coverage_list"])
    ch_a4 = sweep["ch_a4_robustness"]

    ch_a1_supported = ch_a4["ch_a1_robust"] and sweep["ch_a1_baseline_missed"]["mean"] > 0
    ch_a2_supported = bool(ptcheck["ch_a2_exact_recovery"]) and bool(pcheck["sound_and_minimal"])
    ch_a3_supported = ch_a4["ch_a3_robust"]
    ch_a4_supported = bool(ch_a4["all_robust"])

    slots: Dict[str, str] = {
        "p_star_list": ", ".join(p_star),
        "p_star_count": str(len(p_star)),
        "coverage_list": ", ".join(coverage) if coverage else "(empty)",
        "coverage_count": str(len(coverage)),
        "candidate_property_count": str(len(derivation["candidate_properties"])),
        "grid_size_reachable": f"{derivation['grid_size_reachable']:,}",

        "ch_a1_baseline_missed": _fmt_ci(sweep["ch_a1_baseline_missed"]),
        "ch_a1_true_violations": _fmt_ci(sweep["ch_a1_true_violations"]),
        "ch_a1_derived_zero_every_cell": str(sweep["ch_a1_derived_zero_every_cell"]),
        "ch_a1_status": _supported(ch_a1_supported),

        "ch_a2_pairtest_reachable_tuples": f"{ptcheck['reachable_tuples_swept']:,}",
        "ch_a2_missed_participants": ", ".join(ptcheck["missed_participants"]) or "(none)",
        "ch_a2_false_participants": ", ".join(ptcheck["false_participants"]) or "(none)",
        "ch_a2_status": _supported(ch_a2_supported),

        "ch_a3_off_admissions": _fmt_ci(sweep["ch_a3_off_admissions"]),
        "ch_a3_replay_probe_count": _fmt_ci(sweep["ch_a3_replay_probe_count"]),
        "ch_a3_escalation_overhead": _fmt_ci(sweep["ch_a3_escalation_overhead"]),
        "ch_a3_on_zero_every_cell": str(sweep["ch_a3_on_zero_every_cell"]),
        "ch_a3_off_nonzero_at_least_one_cell": str(sweep["ch_a3_off_nonzero_at_least_one_cell"]),
        "ch_a3_status": _supported(ch_a3_supported),

        "ch_a4_status": _supported(ch_a4_supported),

        "spurious_escalations_overinclusive": _fmt_ci(sweep["spurious_escalations_overinclusive"]),

        "grant_check_sequences": str(gcheck["sequences_checked"]),
        "grant_single_use_holds": str(gcheck["single_use_holds_exhaustively"]),

        "n_seeds": str(len(sweep["seeds"])),
        "n_cells": str(sweep["n_cells"]),
        "workflows": ", ".join(sweep["workflows"]),

        "abstract_results_sentence": (
            f"CH-A1 ({_supported(ch_a1_supported)}), CH-A2 ({_supported(ch_a2_supported)}), "
            f"CH-A3 ({_supported(ch_a3_supported)}), and CH-A4 ({_supported(ch_a4_supported)})."
        ),
    }
    return slots


if __name__ == "__main__":
    print(json.dumps(build_slots(), indent=2, sort_keys=True))
