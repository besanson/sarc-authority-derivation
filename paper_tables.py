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

from checkers.proof_status_lint import lint as _lint_proof_status
from domain import load_loss_model


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
    derivation_v2_path: str = "out/checkers/derivation_output_v2.json",
    ch_a5_check_path: str = "out/checkers/ch_a5_check.json",
    ch_a7_check_path: str = "out/checkers/ch_a7_check.json",
    reachability_check_path: str = "out/checkers/reachability_check.json",
    sufficiency_check_path: str = "out/checkers/sufficiency_check.json",
    reduct_check_path: str = "out/checkers/reduct_check.json",
    core_insufficiency_counterexample_path: str = "out/checkers/core_insufficiency_counterexample.json",
    isolation_delta_check_path: str = "out/checkers/isolation_delta_check.json",
    authority_compiler_check_path: str = "out/checkers/authority_compiler_check.json",
    ch_b1_check_path: str = "out/checkers/ch_b1_check.json",
    discernibility_scaling_v5_1_path: str = "out/results/discernibility_scaling_v5_1.json",
    discernibility_scaling_v5_3_path: str = "out/results/discernibility_scaling_v5_3.json",
    authority_bench_v6_1_path: str = "out/results/authority_bench_v6_1.json",
) -> Dict[str, str]:
    derivation = json.loads(Path(derivation_path).read_text())
    pcheck = json.loads(Path(participation_check_path).read_text())
    ptcheck = json.loads(Path(pairtest_check_path).read_text())
    gcheck = json.loads(Path(grant_check_path).read_text())
    sweep = json.loads(Path(sweep_summary_path).read_text())
    derivation_v2 = json.loads(Path(derivation_v2_path).read_text())
    ch_a5 = json.loads(Path(ch_a5_check_path).read_text())
    ch_a7 = json.loads(Path(ch_a7_check_path).read_text())
    rcheck = json.loads(Path(reachability_check_path).read_text())
    ch_a8 = json.loads(Path(sufficiency_check_path).read_text())
    ch_a10 = json.loads(Path(reduct_check_path).read_text())
    ac_check = json.loads(Path(authority_compiler_check_path).read_text())
    neg_n_and_ch_a9 = json.loads(Path(core_insufficiency_counterexample_path).read_text())
    neg_prop_n_case = next(c for c in neg_n_and_ch_a9["cases"] if c["name"] == "negative_proposition_n")
    ch_a9_case = next(c for c in neg_n_and_ch_a9["cases"] if c["name"] == "ch_a9_constrained_procurement_variant")
    isolation_delta = json.loads(Path(isolation_delta_check_path).read_text())
    ch_b1 = json.loads(Path(ch_b1_check_path).read_text())
    v5_1 = json.loads(Path(discernibility_scaling_v5_1_path).read_text())
    v5_3 = json.loads(Path(discernibility_scaling_v5_3_path).read_text())
    ab = json.loads(Path(authority_bench_v6_1_path).read_text())
    proof_status = _lint_proof_status()
    pending_human_review_tag_count = sum(
        1 for f in proof_status["files"] for t in f["tags"] if t == "pending-human-review"
    )
    loss_model = load_loss_model()
    v1_loss_count = len(loss_model["losses"])
    v2_loss_count = v1_loss_count + len(loss_model["v2_losses"])

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
        "v1_loss_count": str(v1_loss_count),
        "v2_loss_count": str(v2_loss_count),

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

        # v2 (prereg/v2-reachability-redesign.md, tag prereg-p5-v2): every
        # CH-A5-CH-A7 count, sourced solely from derivation_output_v2.json,
        # ch_a5_check.json, and ch_a7_check.json -- no independent
        # re-derivation, no typed numbers, same discipline as v1's slots
        # above.
        "v2_candidate_property_count": str(len(derivation_v2["candidate_properties"])),
        "v2_p_star_count": str(len(derivation_v2["participating_properties"])),
        "v2_grid_size_reachable": f"{derivation_v2['grid_size_reachable']:,}",

        "v2_rank0_size": f"{ch_a5['rank0_v2_size']:,}",
        "v2_downroute_new_tuples": f"{ch_a5['downroute_reachable_new_tuples']:,}",
        "v2_retry_delay_new_tuples": f"{ch_a5['retry_delay_reachable_new_tuples']:,}",
        "ch_a5_reachable_size": f"{ch_a5['executable_reachable_v2_size']:,}",

        "ch_a7_reachable_size_a": f"{ch_a7['reachable_size_a_full_v2']:,}",
        "ch_a7_reachable_size_b": f"{ch_a7['reachable_size_b_downroute_excluded']:,}",

        # v1 numbers already hand-typed in prose before the typed-numerals
        # gate existed (repair 2b) -- sourced here rather than exempted,
        # since a proper slot source was directly available.
        "remediation_reachable_new_tuples": str(rcheck["remediation_reachable_new_tuples"]),
        "pending_human_review_tag_count": str(pending_human_review_tag_count),

        # v3 (prereg/v3-core-reduct-correction.md, tag prereg-p5-v3): every
        # Proposition 1'/Negative Proposition N/CH-A8-CH-A10 count, sourced
        # solely from sufficiency_check.json, reduct_check.json, and
        # core_insufficiency_counterexample.json.
        "v3_identity_holds": str(ch_a10["proposition_1_prime_claim_1_identity_holds"]),
        "v3_core_subset_holds": str(ch_a10["proposition_1_prime_claim_2_core_subset_of_every_reduct"]),

        "ch_a8_status": _supported(ch_a8["is_sufficient"]),
        "ch_a8_partition_cells": f"{ch_a8['sufficiency_certificate']['partition_cell_count']:,}",
        "ch_a8_reachable_swept": f"{ch_a8['reachable_tuples_swept']:,}",

        "ch_a10_num_reducts": str(len(ch_a10["reducts"])),
        "ch_a10_min_cardinality": str(ch_a10["minimum_reduct_cardinality"]),
        "ch_a10_core_is_unique_reduct": str(ch_a10["core_is_unique_reduct"]),
        "ch_a10_subsets_considered": f"{ch_a10['subsets_considered']:,}",
        "ch_a10_power_set_size": f"{2 ** len(ch_a10['candidate_properties']):,}",
        "ch_a10_candidate_property_count": str(len(ch_a10["candidate_properties"])),

        # E1 (prereg/v6.1-authoritybench-amendment.md): does the packaged
        # src/authority_compiler entry point agree with CH-A10's own,
        # separately-verified core/reduct result -- confirmed, not assumed.
        "authority_compiler_confirms_ch_a10": str(ac_check["clean"]),

        "neg_prop_n_status": _supported(neg_prop_n_case["supported"]),
        "neg_prop_n_matches_fixture": str(neg_prop_n_case["matches_registered_fixture_expectation"]),

        "ch_a9_status": _supported(ch_a9_case["supported"]),
        "ch_a9_core_cardinality": str(len(ch_a9_case["core_attributes"])),

        # v3.1/v0.4 (prereg/v3.1-isolated-arms.md, tag prereg-p5-v3.1):
        # the isolation hypothesis's own delta table and the budget-
        # predicate-fire diagnostic that mechanistically explains it,
        # sourced solely from isolation_delta_check.json.
        "v4_isolation_status": _supported(isolation_delta["isolation_hypothesis_supported"]),
        "v4_material_movement_field_count": str(len(isolation_delta["material_movement_fields"])),
        "v4_budget_predicate_fires": f"{isolation_delta['budget_predicate_fire_diagnostic']['total_budget_predicate_fires']:,}",
        "v4_budget_predicate_decisions_swept": f"{isolation_delta['budget_predicate_fire_diagnostic']['total_decisions_swept']:,}",
        "v4_budget_predicate_cells_with_fire": str(isolation_delta["budget_predicate_fire_diagnostic"]["cells_with_at_least_one_fire"]),
        "v4_budget_predicate_n_cells": str(isolation_delta["budget_predicate_fire_diagnostic"]["n_cells"]),
    }
    slots.update(_v05_slots(ch_b1, v5_1, v5_3, ab))
    return slots


def _v05_slots(ch_b1: Dict[str, Any], v5_1: Dict[str, Any], v5_3: Dict[str, Any], ab: Dict[str, Any]) -> Dict[str, str]:
    """v0.5 (Package B, review-secondary/final-gap-plan-9.5-2026-09-09.pdf):
    slots for the code/cloud flagship (CH-B1), the tuple-scaling and
    combinatorial-hardness results (v5.1/v5.3), and AuthorityBench
    (v6.1) -- sourced solely from their own already-committed JSON, same
    discipline as every slot above."""
    reduct_branch = next(r for r in ch_b1["minimum_reducts"] if "branch" in r)
    reduct_environment = next(r for r in ch_b1["minimum_reducts"] if "environment" in r)

    v5_1_by_family = {f["family"]: f for f in v5_1["synthetic_families"]}
    v5_1_q5 = v5_1_by_family["multi_reduct_q5"]

    v5_3_by_family = {f["family"]: f for f in v5_3["families"]}

    ab_by_domain = {d["domain"]: d for d in ab["domains"]}
    ab_v2, ab_v4, ab_dc = ab_by_domain["v2"], ab_by_domain["v4"], ab_by_domain["data-and-communications"]

    def ab_manual_correct(dom: Dict[str, Any]) -> str:
        return _supported(bool(dom["baselines"]["manual_least_privilege"]["correctness"]))

    def ab_mining_size(dom: Dict[str, Any]) -> str:
        return str(dom["baselines"]["xu_stoller_mining"]["contract_size"])

    slots: Dict[str, str] = {
        # CH-B1 (prereg/v4-realistic-domain.md, tag prereg-p5-v4): the
        # code/cloud flagship -- a real domain (not planted for this
        # purpose) whose core is insufficient and which has two distinct
        # minimum reducts, `out/checkers/ch_b1_check.json`.
        "ch_b1_candidate_property_count": str(len(ch_b1["candidate_properties"])),
        "ch_b1_core_cardinality": str(ch_b1["core_cardinality"]),
        "ch_b1_core_list": ", ".join(sorted(ch_b1["core_attributes"])),
        "ch_b1_core_sufficient_status": _supported(ch_b1["is_core_sufficient"]),
        "ch_b1_num_reducts": str(ch_b1["num_reducts"]),
        "ch_b1_min_reduct_cardinality": str(ch_b1["minimum_reduct_cardinality"]),
        "ch_b1_reduct_branch_list": ", ".join(sorted(reduct_branch)),
        "ch_b1_reduct_environment_list": ", ".join(sorted(reduct_environment)),
        "ch_b1_reachable_swept": f"{ch_b1['reachable_tuples_swept']:,}",
        "ch_b1_power_set_size": f"{ch_b1['power_set_size']:,}",

        # v5.1 (prereg/v5.1-discernibility-scaling.md, tag prereg-p5-v5.1):
        # the tuple-scaling result -- kept, cited, not exploratory (v5.3's
        # own registration text). Largest registered family only; all
        # three share the same predicted structure (two singleton
        # reducts, pruned family size 1), `out/results/
        # discernibility_scaling_v5_1.json`.
        "v5_1_max_reachable_tuples": f"{v5_1_q5['reachable_tuple_count']:,}",
        "v5_1_family_size_after_pruning": str(v5_1_q5["discernibility_family_size_after_superset_removal"]),
        "v5_1_num_reducts": str(len(v5_1_q5["exhaustive_cross_check"]["reducts"])),

        # v5.3 (prereg/v5.3-combinatorial-hardness-scaling.md, tag
        # prereg-p5-v5.3): the primary scaling table -- three families
        # pairing planted minimum-reduct size with a large candidate-
        # attribute universe, `out/results/discernibility_scaling_v5_3.json`.
        "v5_3_family_a_k": str(v5_3_by_family["family_a"]["k"]),
        "v5_3_family_a_n": str(v5_3_by_family["family_a"]["n"]),
        "v5_3_family_a_reachable": f"{v5_3_by_family['family_a']['reachable_tuple_count']:,}",
        "v5_3_family_a_pruned_family_size": str(v5_3_by_family["family_a"]["discernibility_family_size_after_superset_removal"]),
        "v5_3_family_b_k": str(v5_3_by_family["family_b"]["k"]),
        "v5_3_family_b_n": str(v5_3_by_family["family_b"]["n"]),
        "v5_3_family_b_reachable": f"{v5_3_by_family['family_b']['reachable_tuple_count']:,}",
        "v5_3_family_b_pruned_family_size": str(v5_3_by_family["family_b"]["discernibility_family_size_after_superset_removal"]),
        "v5_3_family_c_k": str(v5_3_by_family["family_c"]["k"]),
        "v5_3_family_c_n": str(v5_3_by_family["family_c"]["n"]),
        "v5_3_family_c_reachable": f"{v5_3_by_family['family_c']['reachable_tuple_count']:,}",
        "v5_3_family_c_pruned_family_size": str(v5_3_by_family["family_c"]["discernibility_family_size_after_superset_removal"]),
        "v5_3_exhaustive_budget_seconds": str(v5_3_by_family["family_a"]["exhaustive_cross_check"]["budget_seconds"]),
        "v5_3_maxsat_advantage_any_family": _supported(
            any(f["maxsat_advantage"]["meaningful_cardinality_advantage"] for f in v5_3["families"])
        ),

        # v6.1 (prereg/v6.1-authoritybench-amendment.md, tag
        # prereg-p5-v6.1): AuthorityBench run all, `out/results/
        # authority_bench_v6_1.json`. Domain names as registered: "v2"
        # (procurement), "v4" (code/cloud), "data-and-communications".
        "ab_domain_count": str(len(ab["domains"])),
        "ab_v2_candidate_property_count": str(ab_v2["candidate_property_count"]),
        "ab_v2_reachable_tuple_count": f"{ab_v2['reachable_tuple_count']:,}",
        "ab_v2_manual_correct": ab_manual_correct(ab_v2),
        "ab_v2_mining_size": ab_mining_size(ab_v2),
        "ab_v4_candidate_property_count": str(ab_v4["candidate_property_count"]),
        "ab_v4_reachable_tuple_count": f"{ab_v4['reachable_tuple_count']:,}",
        "ab_v4_manual_correct": ab_manual_correct(ab_v4),
        "ab_v4_mining_size": ab_mining_size(ab_v4),
        "ab_dc_candidate_property_count": str(ab_dc["candidate_property_count"]),
        "ab_dc_reachable_tuple_count": f"{ab_dc['reachable_tuple_count']:,}",
        "ab_dc_manual_correct": ab_manual_correct(ab_dc),
        "ab_dc_mining_size": ab_mining_size(ab_dc),
        "ab_xu_stoller_mining_validated": _supported(ab["xu_stoller_mining_validated"]),
    }
    return slots


if __name__ == "__main__":
    print(json.dumps(build_slots(), indent=2, sort_keys=True))
