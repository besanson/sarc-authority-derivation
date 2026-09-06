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
CH-A6, second half (prereg/v2-reachability-redesign.md, tag
prereg-p5-v2): "checkers/pairtest_check.py ... re-run against
executable_reachable_tuples_v2()." v1's pairtest_check.py is untouched;
this module mirrors its one-factor-at-a-time algorithm -- independent
of participation.compute_p_star's fingerprint-grouped search, exactly as
CH-A2 requires of v1 -- against the v2 model, and reports
ch_a6_exact_recovery against checkers/participation_check_v2.py's
committed derivation (out/checkers/derivation_output_v2.json), the same
two-independent-algorithms-agree structure CH-A2 already established.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Set

from domain import (
    CANDIDATE_PROPERTIES_V2,
    executable_reachable_tuples_v2,
    load_loss_model,
    load_pair_test_grid,
    property_domains_v2,
)
from losses import load_loss_registry_v2, m_verdict

DERIVATION_OUTPUT_V2_PATH = Path("out/checkers/derivation_output_v2.json")
OUTPUT_PATH = Path("out/checkers/pairtest_check_v2.json")

BLIND_SPOT_NOTE = (
    "Pair testing probes the representation, not the loss model (same "
    "registered blind spot as checkers/pairtest_check.py's v1 run, "
    "unchanged in kind by the v2 redesign): it can only detect "
    "participation that a witness pair constructible from pair-test-"
    "grid.yaml's declared v1+v2 domain values actually exhibits."
)


def ofat_participating_properties_v2(
    reachable: List[Any], domains: Dict[str, List[Any]], registry: Dict[str, Any]
) -> Set[str]:
    reachable_set = set(reachable)
    participating: Set[str] = set()
    for baseline in reachable:
        base_verdict = m_verdict(baseline, registry)
        for prop in CANDIDATE_PROPERTIES_V2:
            if prop in participating:
                continue
            for value in domains[prop]:
                if value == getattr(baseline, prop):
                    continue
                variant = baseline.with_property(prop, value)
                if variant not in reachable_set:
                    continue
                if m_verdict(variant, registry) != base_verdict:
                    participating.add(prop)
                    break
    return participating


def run() -> Dict[str, Any]:
    loss_model = load_loss_model()
    grid = load_pair_test_grid()
    registry = load_loss_registry_v2(loss_model)
    domains = property_domains_v2(grid)
    reachable = executable_reachable_tuples_v2(domains)

    pairtest_p_star = sorted(ofat_participating_properties_v2(reachable, domains, registry))
    pairtest_coverage = sorted(set(CANDIDATE_PROPERTIES_V2) - set(pairtest_p_star))

    derived = json.loads(DERIVATION_OUTPUT_V2_PATH.read_text())
    derived_p_star = sorted(derived["participating_properties"])

    missed_participants = sorted(set(derived_p_star) - set(pairtest_p_star))
    false_participants = sorted(set(pairtest_p_star) - set(derived_p_star))

    result = {
        "pairtest_participating_properties": pairtest_p_star,
        "pairtest_coverage_list": pairtest_coverage,
        "derived_participating_properties": derived_p_star,
        "missed_participants": missed_participants,
        "false_participants": false_participants,
        "ch_a6_exact_recovery": missed_participants == [] and false_participants == [],
        "reachable_tuples_swept": len(reachable),
        "blind_spot_note": BLIND_SPOT_NOTE,
    }
    return result


def main() -> None:
    result = run()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["ch_a6_exact_recovery"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
