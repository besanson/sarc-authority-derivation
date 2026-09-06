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
v2 (prereg/v2-reachability-redesign.md, tag prereg-p5-v2): the v2
derivation procedure, CH-A5/CH-A6's primary computation. Mirrors
derive.py's pipeline exactly -- loss model in, P* + coverage list out --
against the v2 model (domain.executable_reachable_tuples_v2,
losses.load_loss_registry_v2, domain.CANDIDATE_PROPERTIES_V2) instead of
v1's. derive.py itself is imported for two small provenance helpers
(_sha256_file, _head_sha) and is otherwise untouched: this module never
calls derive() or writes derive.py's own output path.

Writes out/checkers/derivation_output_v2.json -- a sibling of, not a
replacement for, out/checkers/derivation_output.json.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from derive import _head_sha, _sha256_file
from domain import (
    CANDIDATE_PROPERTIES_V2,
    LOSS_MODEL_PATH,
    PAIR_TEST_GRID_PATH,
    executable_reachable_tuples_v2,
    load_loss_model,
    load_pair_test_grid,
    property_domains_v2,
)
from losses import load_loss_registry_v2
from participation import compute_p_star

OUTPUT_PATH = Path("out/checkers/derivation_output_v2.json")


def derive_v2(loss_model_path: str = LOSS_MODEL_PATH, grid_path: str = PAIR_TEST_GRID_PATH) -> Dict[str, Any]:
    loss_model = load_loss_model(loss_model_path)
    grid = load_pair_test_grid(grid_path)
    registry = load_loss_registry_v2(loss_model)
    domains = property_domains_v2(grid)

    reachable = executable_reachable_tuples_v2(domains)
    p_star, coverage, witnesses = compute_p_star(reachable, registry, CANDIDATE_PROPERTIES_V2)

    return {
        "schema_version": 1,
        "model_version": "v2",
        "loss_model_sha256": _sha256_file(loss_model_path),
        "grid_sha256": _sha256_file(grid_path),
        "candidate_properties": list(CANDIDATE_PROPERTIES_V2),
        "participating_properties": p_star,
        "coverage_list": coverage,
        "witnesses": witnesses,
        "grid_size_reachable": len(reachable),
        "generated_at_head_sha": _head_sha(),
    }


def main() -> None:
    result = derive_v2()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"\nv2 P* ({len(result['participating_properties'])}): {result['participating_properties']}")
    print(f"v2 coverage list ({len(result['coverage_list'])}): {result['coverage_list']}")
    print(f"v2 reachable tuples enumerated: {result['grid_size_reachable']}")


if __name__ == "__main__":
    main()
