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
Phase 2 / task brief's V2 gate: exhaustive verification that the
committed P* (out/checkers/derivation_output.json, produced by
derive.py) is sound (dropping any member admits a loss-violating pair)
and minimal (no non-member is required).

Three independent checks, all against a FRESH recomputation from source
(prereg/loss-model.yaml, prereg/pair-test-grid.yaml) in this process --
not the committed file's own claims taken on faith:

1. Fresh derivation identity: recompute P*/coverage from scratch via the
   same domain.py/participation.py functions derive.py used, and require
   EXACT set equality against the committed file -- the same double-run
   byte-identity pattern release-check's formal gate already applies to
   the imported baseline's own checkers, applied here to the derivation
   itself. Catches staleness (a committed file that does not match its
   own declared inputs) and non-determinism.
2. Certificate verification (soundness): every witness pair recorded for
   a P* member is independently re-executed -- both tuples confirmed
   reachable, confirmed to differ in EXACTLY the claimed property, and
   confirmed to actually produce different M-verdicts under the claimed
   loss. A witness that does not hold up under re-execution is a lint
   failure, not a trusted record.
3. Minimality, by construction of check 1: the fresh sweep in check 1 is
   itself exhaustive over the ENTIRE reachable set (prereg/pair-test-
   grid.yaml's declared domains, not a sample) for every one of the nine
   candidate properties, so a coverage-list member for which some
   witness actually existed would have been found and would fail check
   1's exact-equality requirement.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from domain import (
    CANDIDATE_PROPERTIES,
    executable_reachable_tuples,
    field_names,
    load_loss_model,
    load_pair_test_grid,
    property_domains,
)
from losses import load_loss_registry, m_verdict
from participation import compute_p_star

DERIVATION_OUTPUT_PATH = Path("out/checkers/derivation_output.json")
OUTPUT_PATH = Path("out/checkers/participation_check.json")


def _tuples_differ_in_exactly(t_a: Dict[str, Any], t_b: Dict[str, Any], prop: str) -> bool:
    differing = [f for f in field_names() if _norm(t_a[f]) != _norm(t_b[f])]
    return differing == [prop]


def _norm(v: Any) -> Any:
    """Normalize frozenset (live StateTuple side) / list (JSON round-trip
    side) representational differences to the same canonical sorted-tuple
    form, so equality comparison works regardless of which side a value
    came from."""
    if isinstance(v, (list, frozenset, set)):
        return tuple(sorted(v))
    return v


def verify_certificates(derived: Dict[str, Any], reachable_set: set, registry: Dict[str, Any]) -> Dict[str, Any]:
    reachable_lookup = {tuple(sorted(t.__dict__.items(), key=lambda kv: kv[0])): t for t in reachable_set}

    def find_reachable(tuple_dict: Dict[str, Any]):
        for t in reachable_set:
            if all(_norm(getattr(t, f)) == _norm(tuple_dict[f]) for f in field_names()):
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
    registry = load_loss_registry(loss_model)
    domains = property_domains(grid)
    reachable = executable_reachable_tuples(domains)

    fresh_p_star, fresh_coverage, _ = compute_p_star(reachable, registry, CANDIDATE_PROPERTIES)

    derived = json.loads(DERIVATION_OUTPUT_PATH.read_text())
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
