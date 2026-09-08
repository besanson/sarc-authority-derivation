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
Milestone E4 (`prereg/v6-authority-bench.md`, tag `prereg-p5-v6`):
AuthorityBench's own EXPLORATORY v6.0 run -- the registered comparison
(`mining_baseline.py`'s scoped Xu-and-Stoller-style mining vs. `src.
authority_compiler.derive_authority_contract`'s loss-derived minimum-
cardinality reduct) on v1, v2, and v4 (reused unmodified), applying the
prereg's own registered comparison metric and two-sided decision rule --
neither adjusted here to change the outcome once measured.

Per `prereg/v6.1-authoritybench-amendment.md`'s own "Disposition"
section: this result is kept, not retracted, and marked
`exploratory_v6_0: true` below -- it predates that amendment's full E2
registration (three domains including a newly-built one, four
baselines, six metrics) and is excluded from AuthorityBench's own
benchmark tables. This module's own call sites are updated here only to
track `src/authority_compiler`'s new four-parameter API (Step 1) so
nothing is left broken between commits; the FULL rewrite (all four
baselines, all three domains, all six metrics) is Step 4's own,
separate, later commit."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# pyproject.toml's `pythonpath = ["src"]` resolves `authority_compiler`
# for pytest only; a plain `python3 authority_bench.py` invocation needs
# its own sys.path entry, same src-layout reasoning as pyproject.toml's
# own comment (mutmut's configuration.py treats a top-level `src/` as a
# source root to import THROUGH, not a real dotted package component).
sys.path.insert(0, str(Path(__file__).parent / "src"))

from authority_compiler import derive_authority_contract  # noqa: E402
from mining_baseline import mine_policy, verify_soundness  # noqa: E402

OUTPUT_PATH = Path("out/results/authority_bench.json")
TIME_BUDGET_SECONDS = 1200.0  # prereg's own "Tractability contingency": 20 minutes per domain


def _relationship(mined: frozenset, this_project_answer: frozenset) -> str:
    """The prereg's own registered comparison categories. `mined ==
    this_project_answer` is checked first since Python's `<`/`>` are
    already false for equal sets, but naming "equal" explicitly (rather
    than falling through to "mismatch") matches the decision rule's own
    vocabulary directly."""
    if mined == this_project_answer:
        return "equal"
    if this_project_answer < mined:
        return "mining_strict_superset"
    if mined < this_project_answer:
        return "mining_strict_subset"
    return "mismatch"


def run_domain(
    name: str,
    candidate_properties: Tuple[str, ...],
    reachable: List[Any],
    registry: Dict[str, Any],
) -> Dict[str, Any]:
    mining_result = mine_policy(candidate_properties, reachable, registry, time_budget_seconds=TIME_BUDGET_SECONDS)
    soundness = verify_soundness(candidate_properties, reachable, registry, mining_result["rules"])

    candidate_context = {p: sorted({getattr(t, p) for t in reachable}, key=repr) for p in candidate_properties}
    this_project = derive_authority_contract(registry, reachable, candidate_context)
    this_project_answer = this_project.minimum_cardinality_reduct
    mined = mining_result["mined_attributes"]
    relationship = _relationship(mined, this_project_answer)

    return {
        "domain": name,
        "candidate_property_count": len(candidate_properties),
        "reachable_tuple_count": len(reachable),
        "mining": {
            "rules": [dict(r) for r in mining_result["rules"]],
            "mined_attributes": sorted(mined),
            "mined_attribute_count": len(mined),
            "rule_count_before_simplify": mining_result["rule_count_before_simplify"],
            "rule_count_after_simplify": mining_result["rule_count_after_simplify"],
            "tractable": mining_result["tractable"],
            "elapsed_seconds": mining_result["elapsed_seconds"],
        },
        "soundness": soundness,
        "this_project_core": sorted(this_project.core_attributes),
        "this_project_core_is_sufficient": this_project.counterexamples is None,
        "this_project_answer": sorted(this_project_answer),
        "this_project_answer_count": len(this_project_answer),
        "relationship": relationship,
    }


def run() -> Dict[str, Any]:
    from domain import (
        CANDIDATE_PROPERTIES,
        CANDIDATE_PROPERTIES_V2,
        executable_reachable_tuples,
        executable_reachable_tuples_v2,
        load_loss_model,
        load_pair_test_grid,
        property_domains,
        property_domains_v2,
    )
    from domain_v4 import CANDIDATE_PROPERTIES_V4, executable_reachable_tuples_v4
    from losses import load_loss_registry, load_loss_registry_v2
    from losses_v4 import load_loss_registry_v4

    grid = load_pair_test_grid()
    loss_model = load_loss_model()

    domains = [
        ("v1", CANDIDATE_PROPERTIES, executable_reachable_tuples(property_domains(grid)), load_loss_registry(loss_model)),
        ("v2", CANDIDATE_PROPERTIES_V2, executable_reachable_tuples_v2(property_domains_v2(grid)), load_loss_registry_v2(loss_model)),
        ("v4", CANDIDATE_PROPERTIES_V4, executable_reachable_tuples_v4(), load_loss_registry_v4()),
    ]

    results = [run_domain(name, cp, reachable, registry) for name, cp, reachable, registry in domains]

    supported = any(r["relationship"] == "mining_strict_superset" for r in results)
    all_equal = all(r["relationship"] == "equal" for r in results)
    anomalous = [r["domain"] for r in results if r["relationship"] in ("mining_strict_subset", "mismatch")]
    unsound = [r["domain"] for r in results if not r["soundness"]["sound"]]
    intractable = [r["domain"] for r in results if not r["mining"]["tractable"]]

    decision = "SUPPORTED" if supported else ("NOT_SUPPORTED" if all_equal else "INCONCLUSIVE")

    return {
        "exploratory_v6_0": True,
        "excluded_from_benchmark_tables": True,
        "superseded_by": "prereg/v6.1-authoritybench-amendment.md (Step 4's own authority-bench harness)",
        "domains": results,
        "decision": decision,
        "anomalous_domains": anomalous,
        "unsound_domains": unsound,
        "intractable_domains": intractable,
    }


def _json_default(obj: Any) -> Any:
    """v1/v2's `consumed_grant_ids` is a frozenset-valued candidate
    property (`participation._serialize`'s own long-standing reason for
    existing); a mined rule may legitimately pin it to one specific
    frozenset value (this algorithm's step 3 treats every candidate
    property uniformly, by equality, regardless of its value's own
    type), so that exact value can end up embedded in `rules`/
    `soundness.mismatches` here -- converted to a sorted list only at
    the JSON boundary, the same representation `_serialize` already
    uses, not a change to what `mine_policy`/`verify_soundness`
    themselves compare or return."""
    if isinstance(obj, frozenset):
        return sorted(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def main() -> None:
    result = run()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True, default=_json_default))
    print(json.dumps(result, indent=2, sort_keys=True, default=_json_default))


if __name__ == "__main__":
    main()
