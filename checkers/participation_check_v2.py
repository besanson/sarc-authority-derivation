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
CH-A6, first half (prereg/v2-reachability-redesign.md, tag prereg-p5-v2):
"checkers/participation_check.py ... re-run against
executable_reachable_tuples_v2()." This is that re-run: v1's
participation_check.py is untouched; this module mirrors its exact
two-check structure (fresh-recomputation identity against the committed
file derive_v2.py produces, then witness-certificate re-execution)
against the v2 model instead. See checkers/pairtest_check_v2.py for the
second, algorithmically-independent half CH-A6 compares this against.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from domain import (
    CANDIDATE_PROPERTIES_V2,
    executable_reachable_tuples_v2,
    field_names_v2,
    load_loss_model,
    load_pair_test_grid,
    property_domains_v2,
)
from losses import load_loss_registry_v2, m_verdict
from participation import compute_p_star

DERIVATION_OUTPUT_V2_PATH = Path("out/checkers/derivation_output_v2.json")
OUTPUT_PATH = Path("out/checkers/participation_check_v2.json")


def _tuples_differ_in_exactly(t_a: Dict[str, Any], t_b: Dict[str, Any], prop: str) -> bool:
    differing = [f for f in field_names_v2() if _norm(t_a[f]) != _norm(t_b[f])]
    return differing == [prop]


def _norm(v: Any) -> Any:
    if isinstance(v, (list, frozenset, set)):
        return tuple(sorted(v))
    return v


def verify_certificates(derived: Dict[str, Any], reachable_set: set, registry: Dict[str, Any]) -> Dict[str, Any]:
    def find_reachable(tuple_dict: Dict[str, Any]):
        for t in reachable_set:
            if all(_norm(getattr(t, f)) == _norm(tuple_dict[f]) for f in field_names_v2()):
                return t
        return None

    bad_certificates = []
    for prop, witness_list in derived["witnesses"].items():
        for witness in witness_list:
            a = find_reachable(witness["tuple_a"])
            a_prime = find_reachable(witness["tuple_a_prime"])
            problems = []
            if a is None:
                problems.append("tuple_a not in freshly-recomputed reachable set")
            if a_prime is None:
                problems.append("tuple_a_prime not in freshly-recomputed reachable set")
            if a is not None and a_prime is not None:
                if not _tuples_differ_in_exactly(witness["tuple_a"], witness["tuple_a_prime"], prop):
                    problems.append(f"tuples do not differ in exactly {prop!r}")
                if m_verdict(a, registry) != witness["verdict_a"]:
                    problems.append("verdict_a does not match fresh re-execution")
                if m_verdict(a_prime, registry) != witness["verdict_a_prime"]:
                    problems.append("verdict_a_prime does not match fresh re-execution")
                if m_verdict(a, registry) == m_verdict(a_prime, registry):
                    problems.append("witness pair's fresh verdicts do not actually differ")
            if problems:
                bad_certificates.append({"property": prop, "problems": problems})
    return {"total_witnesses_checked": sum(len(w) for w in derived["witnesses"].values()), "bad_certificates": bad_certificates}


def run() -> Dict[str, Any]:
    loss_model = load_loss_model()
    grid = load_pair_test_grid()
    registry = load_loss_registry_v2(loss_model)
    domains = property_domains_v2(grid)
    reachable = executable_reachable_tuples_v2(domains)

    fresh_p_star, fresh_coverage, _ = compute_p_star(reachable, registry, CANDIDATE_PROPERTIES_V2)

    derived = json.loads(DERIVATION_OUTPUT_V2_PATH.read_text())
    committed_p_star = sorted(derived["participating_properties"])
    committed_coverage = sorted(derived["coverage_list"])

    identity_ok = fresh_p_star == committed_p_star and fresh_coverage == committed_coverage

    cert_report = verify_certificates(derived, set(reachable), registry)

    return {
        "fresh_participating_properties": fresh_p_star,
        "fresh_coverage_list": fresh_coverage,
        "committed_participating_properties": committed_p_star,
        "committed_coverage_list": committed_coverage,
        "fresh_recomputation_matches_committed": identity_ok,
        "certificate_verification": cert_report,
        "reachable_tuples_swept": len(reachable),
        "sound_and_minimal": identity_ok and not cert_report["bad_certificates"],
    }


def main() -> None:
    result = run()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["sound_and_minimal"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
