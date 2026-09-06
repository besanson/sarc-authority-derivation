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
Proposition 0-general (prereg/v2-reachability-redesign.md;
appendix-a-proofs.md). Three independent machine-checks:

(a) The fully general structural lemma -- equal reachable sets give
equal P*, so a remediator whose image is a subset of Reach_0 cannot
change P* regardless of what it computes internally -- checked against
synthetic tuple types unrelated to StateTuple/StateTupleV2 (same
domain-agnostic style test_participation.py already uses), across
several different loss predicates and several different remediator-image
shapes. This checks Definition 1's MACHINERY in general, not merely this
artifact's own specific model (which checkers/reachability_check.py, for
Proposition 0, and checkers/ch_a5_check.py, for CH-A5, already cover).

(b) Corollary 1 across MULTIPLE order_value domains, calling v1's own
rank0_reachable_tuples()/remediation_reachable_tuples() UNMODIFIED with
several order_value domains other than the declared {600.0, 1200.0,
2500.0} -- confirming Proposition 0's zero-new-tuples result is a
structural consequence of rank-0's unconstrained-product SHAPE, not a
coincidence of this artifact's particular domain values.

(c) Corollary 2 on v2's own two mechanisms (downroute, retry-delay):
neither's characterized image is a subset of rank0_v2 -- both are
confirmed, not merely asserted, to fall outside Corollary 1's coverage,
which is exactly why CH-A7's targeted, sharp check (rather than a
Corollary-1-style blanket argument) is needed to decide whether either
actually changes P*.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

from domain import (
    downroute_reachable_tuples_v2,
    load_pair_test_grid,
    property_domains,
    property_domains_v2,
    rank0_reachable_tuples,
    rank0_reachable_tuples_v2,
    remediation_reachable_tuples,
    retry_delay_reachable_tuples_v2,
)
from participation import compute_p_star

OUTPUT_PATH = Path("out/checkers/general_reachability_check.json")


# -- (a) the fully general structural lemma, synthetic models ---------------

@dataclass(frozen=True)
class _Toy:
    a: int
    b: int
    c: str

    def with_property(self, name: str, value: Any) -> "_Toy":
        return replace(self, **{name: value})


def _lemma_holds_for(
    universe: List[_Toy],
    remediator_image_indices: List[int],
    verdict: Callable[[_Toy], bool],
    candidates: Tuple[str, ...],
) -> bool:
    """Reach_0 = universe; Reach_R = [universe[i] for i in
    remediator_image_indices] -- a subset of Reach_0 by construction,
    exactly Proposition 0-general's hypothesis. Confirms P*(Reach_0) ==
    P*(Reach_0 union Reach_R) and coverage_list(Reach_0) ==
    coverage_list(Reach_0 union Reach_R), which must hold whenever
    Reach_R subset-of Reach_0 (the union then equals Reach_0 exactly)."""
    registry = {"only_loss": verdict}
    reach_0 = universe
    reach_r = [universe[i] for i in remediator_image_indices]
    combined = list(dict.fromkeys(reach_0 + reach_r))
    p_star_0, coverage_0, _ = compute_p_star(reach_0, registry, candidates)
    p_star_combined, coverage_combined, _ = compute_p_star(combined, registry, candidates)
    image_is_subset = set(reach_r) <= set(reach_0)
    return image_is_subset and p_star_0 == p_star_combined and coverage_0 == coverage_combined


def check_structural_lemma() -> Dict[str, Any]:
    universe = [_Toy(a=x, b=y, c=z) for x in range(4) for y in range(4) for z in ("p", "q")]
    verdicts: Dict[str, Callable[[_Toy], bool]] = {
        "a_threshold": lambda t: t.a >= 2,
        "b_threshold": lambda t: t.b < 1,
        "c_is_q": lambda t: t.c == "q",
        "a_plus_b_even": lambda t: (t.a + t.b) % 2 == 0,
    }
    # Five differently-shaped remediator-image characterizations tried
    # against each verdict, not just one trivial case.
    images = [
        list(range(0, len(universe), 2)),        # every other element
        list(range(0, min(5, len(universe)))),    # first few elements
        [0],                                       # a single element
        [],                                        # no new tuples at all
        list(range(len(universe))),                # R reproduces all of Reach_0
    ]
    cases = []
    all_hold = True
    for verdict_name, verdict_fn in verdicts.items():
        for image_idx, image in enumerate(images):
            holds = _lemma_holds_for(universe, image, verdict_fn, ("a", "b", "c"))
            cases.append({
                "verdict": verdict_name,
                "image_case": image_idx,
                "image_size": len(image),
                "lemma_holds": holds,
            })
            all_hold = all_hold and holds
    return {"universe_size": len(universe), "cases_checked": len(cases), "all_cases_hold": all_hold, "cases": cases}


# -- (b) Corollary 1 across multiple order_value domains ---------------------

def check_corollary_1_across_domains() -> Dict[str, Any]:
    """v1's own rank0_reachable_tuples()/remediation_reachable_tuples()
    (imported unmodified) called against several order_value domains
    OTHER than the real declared {600.0, 1200.0, 2500.0}. All nine v1
    candidate fields' domains are otherwise the real declared ones
    (prereg/pair-test-grid.yaml); only order_value is substituted, in an
    in-memory dict copy, never written back to that file."""
    grid = load_pair_test_grid()
    base_domains = property_domains(grid)
    alternate_order_value_domains = [
        [1.0, 2.0, 3.0],
        [0.0, 50.0, 999999.0],
        [10.0, 20.0, 30.0, 40.0],
        [-5.0, 0.0, 5.0],
    ]
    results = []
    all_redundant = True
    for alt_domain in alternate_order_value_domains:
        domains = dict(base_domains)
        domains["order_value"] = alt_domain
        rank0 = rank0_reachable_tuples(domains)
        new_tuples = remediation_reachable_tuples(rank0, domains["order_value"])
        redundant = len(new_tuples) == 0
        all_redundant = all_redundant and redundant
        results.append({
            "order_value_domain": alt_domain,
            "rank0_size": len(rank0),
            "remediation_reachable_new_tuples": len(new_tuples),
            "redundant": redundant,
        })
    return {
        "domains_checked": len(results),
        "all_redundant_regardless_of_domain": all_redundant,
        "results": results,
    }


# -- (c) Corollary 2: neither of v2's actual mechanisms is automatically ----
# -- covered by Corollary 1 (both have image NOT subset of rank0_v2) -------

def check_corollary_2_on_v2_mechanisms() -> Dict[str, Any]:
    grid = load_pair_test_grid()
    domains = property_domains_v2(grid)
    rank0 = rank0_reachable_tuples_v2(domains)
    downroute_new = downroute_reachable_tuples_v2(rank0, domains["order_value"])
    retry_new = retry_delay_reachable_tuples_v2(rank0)
    return {
        "rank0_v2_size": len(rank0),
        "downroute_new_tuples": len(downroute_new),
        "downroute_image_subset_of_rank0_v2": len(downroute_new) == 0,
        "retry_delay_new_tuples": len(retry_new),
        "retry_delay_image_subset_of_rank0_v2": len(retry_new) == 0,
        "neither_mechanism_automatically_covered_by_corollary_1": len(downroute_new) > 0 and len(retry_new) > 0,
    }


def run() -> Dict[str, Any]:
    structural = check_structural_lemma()
    corollary_1 = check_corollary_1_across_domains()
    corollary_2 = check_corollary_2_on_v2_mechanisms()
    return {
        "structural_lemma": structural,
        "corollary_1_across_domains": corollary_1,
        "corollary_2_on_v2_mechanisms": corollary_2,
        "proposition_0_general_machine_checked": (
            structural["all_cases_hold"] and corollary_1["all_redundant_regardless_of_domain"]
        ),
    }


def main() -> None:
    result = run()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["proposition_0_general_machine_checked"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
