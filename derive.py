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
Phase 2: the derivation procedure. Loss model in, P* + coverage list out,
deterministic. Wires domain.py (reachability enumeration) + losses.py
(the registered predicates) + participation.py (Definitions 1-3) and
writes out/checkers/derivation_output.json against
schemas/derivation_output.schema.json.

SEED = 26313 (inherited; not used directly -- see participation.py's
docstring)
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Dict

from domain import (
    CANDIDATE_PROPERTIES,
    LOSS_MODEL_PATH,
    PAIR_TEST_GRID_PATH,
    executable_reachable_tuples,
    load_loss_model,
    load_pair_test_grid,
    property_domains,
)
from losses import load_loss_registry
from participation import compute_p_star

OUTPUT_PATH = Path("out/checkers/derivation_output.json")


def _sha256_file(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _head_sha() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:
        return "unknown"


def derive(loss_model_path: str = LOSS_MODEL_PATH, grid_path: str = PAIR_TEST_GRID_PATH) -> Dict[str, Any]:
    loss_model = load_loss_model(loss_model_path)
    grid = load_pair_test_grid(grid_path)
    registry = load_loss_registry(loss_model)
    domains = property_domains(grid)

    reachable = executable_reachable_tuples(domains)
    p_star, coverage, witnesses = compute_p_star(reachable, registry, CANDIDATE_PROPERTIES)

    return {
        "schema_version": 1,
        "loss_model_sha256": _sha256_file(loss_model_path),
        "grid_sha256": _sha256_file(grid_path),
        "candidate_properties": list(CANDIDATE_PROPERTIES),
        "participating_properties": p_star,
        "coverage_list": coverage,
        "witnesses": witnesses,
        "grid_size_reachable": len(reachable),
        "generated_at_head_sha": _head_sha(),
    }


def main() -> None:
    result = derive()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"\nP* ({len(result['participating_properties'])}): {result['participating_properties']}")
    print(f"coverage list ({len(result['coverage_list'])}): {result['coverage_list']}")
    print(f"reachable tuples enumerated: {result['grid_size_reachable']}")


if __name__ == "__main__":
    main()
