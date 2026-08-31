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
CH-A2 / the pair-test harness as a formal object (task brief Phase 2),
credited to the Moona Intelligence replication report as the method's
origin (REPLICATIONS.md): eight adversarial pair tests against the
imported baseline's authority policy, varying one coverage-relevant
factor at a time. This module formalizes that method -- not
participation.py's own witness search -- as an independently
implemented, exhaustive sweep, so CH-A2 compares two GENUINELY DIFFERENT
computations of the same claim, not one computation checked against
itself.

Algorithm (deliberately different from participation.py.find_witness's
fingerprint-grouped pairwise search): one-factor-at-a-time (OFAT). For
every reachable tuple as a baseline, and every candidate property, swap
in every OTHER domain value for that property alone; if the resulting
variant is ALSO reachable and its M-verdict differs from the baseline's,
that property is pair-test-participating. This is the direct formal
reading of the eight-test pattern the replication report ran by hand,
generalized to sweep the full declared grid rather than eight
hand-picked cases.

Registered blind spot (emitted below, not just in prose): pair testing
probes the REPRESENTATION -- whatever finite domain values pair-test-
grid.yaml declares -- not the loss model itself. It cannot detect a
hazard whose threshold falls between two declared domain values, or a
property missing from the representation entirely. This is a structural
property of the method, independent of this artifact's specific
instantiation (see ADR-002-participation-tuple-design.md, which found
the SAME limitation applies to Definition 1's own checker whenever it is
run over a point-enumerated finite domain rather than a symbolic one).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Set

from domain import (
    CANDIDATE_PROPERTIES,
    executable_reachable_tuples,
    load_loss_model,
    load_pair_test_grid,
    property_domains,
)
from losses import load_loss_registry, m_verdict

DERIVATION_OUTPUT_PATH = Path("out/checkers/derivation_output.json")
OUTPUT_PATH = Path("out/checkers/pairtest_check.json")

BLIND_SPOT_NOTE = (
    "Pair testing probes the representation, not the loss model: it can "
    "only detect participation that a witness pair constructible from "
    "pair-test-grid.yaml's declared domain values actually exhibits. A "
    "hazard whose true threshold falls strictly between two declared "
    "domain values, or a property never represented in the grid at all, "
    "is invisible to this method regardless of how exhaustively the "
    "declared grid itself is swept."
)


def ofat_participating_properties(
    reachable: List[Any], domains: Dict[str, List[Any]], registry: Dict[str, Any]
) -> Set[str]:
    reachable_set = set(reachable)
    participating: Set[str] = set()
    for baseline in reachable:
        base_verdict = m_verdict(baseline, registry)
        for prop in CANDIDATE_PROPERTIES:
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
    registry = load_loss_registry(loss_model)
    domains = property_domains(grid)
    reachable = executable_reachable_tuples(domains)

    pairtest_p_star = sorted(ofat_participating_properties(reachable, domains, registry))
    pairtest_coverage = sorted(set(CANDIDATE_PROPERTIES) - set(pairtest_p_star))

    derived = json.loads(DERIVATION_OUTPUT_PATH.read_text())
    derived_p_star = sorted(derived["participating_properties"])

    missed_participants = sorted(set(derived_p_star) - set(pairtest_p_star))
    false_participants = sorted(set(pairtest_p_star) - set(derived_p_star))

    result = {
        "pairtest_participating_properties": pairtest_p_star,
        "pairtest_coverage_list": pairtest_coverage,
        "derived_participating_properties": derived_p_star,
        "missed_participants": missed_participants,
        "false_participants": false_participants,
        "ch_a2_exact_recovery": missed_participants == [] and false_participants == [],
        "reachable_tuples_swept": len(reachable),
        "blind_spot_note": BLIND_SPOT_NOTE,
    }
    return result


def main() -> None:
    result = run()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["ch_a2_exact_recovery"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
