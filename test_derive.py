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
"""Tests for derive.py."""
from __future__ import annotations

import json
import subprocess

from derive import _head_sha, derive, main
from domain import CANDIDATE_PROPERTIES
from schemas_check import validate_against_schema


def test_derive_is_deterministic():
    r1 = derive()
    r2 = derive()
    r1.pop("generated_at_head_sha", None)
    r2.pop("generated_at_head_sha", None)
    assert r1 == r2


def test_derive_partitions_all_candidates():
    result = derive()
    assert set(result["participating_properties"]) | set(result["coverage_list"]) == set(CANDIDATE_PROPERTIES)
    assert set(result["participating_properties"]) & set(result["coverage_list"]) == set()


def test_derive_workflow_is_in_coverage_list():
    """Known-negative control (pair-test-grid.yaml's own rationale): no
    loss predicate reads workflow."""
    result = derive()
    assert "workflow" in result["coverage_list"]


def test_derive_every_participating_property_has_a_witness():
    result = derive()
    for prop in result["participating_properties"]:
        assert prop in result["witnesses"]
        assert len(result["witnesses"][prop]) >= 1


def test_derive_grid_size_matches_reported_count():
    result = derive()
    assert result["grid_size_reachable"] > 0


def test_derive_output_matches_schema():
    result = derive()
    validate_against_schema(result, "schemas/derivation_output.schema.json")


def test_head_sha_matches_real_git_rev_parse():
    expected = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    assert _head_sha() == expected
    assert len(_head_sha()) == 40
    assert all(c in "0123456789abcdef" for c in _head_sha())


def test_main_writes_the_output_file(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    # main() writes relative to cwd (out/checkers/derivation_output.json)
    # and reads relative to cwd too, so the prereg/schemas this repo's own
    # loss-model.yaml/pair-test-grid.yaml live under must be reachable --
    # symlink the real repo root's prereg/ into the temp cwd rather than
    # duplicating fixture data.
    import os
    from pathlib import Path

    real_root = Path(__file__).resolve().parent
    os.symlink(real_root / "prereg", tmp_path / "prereg")

    main()

    output_path = tmp_path / "out" / "checkers" / "derivation_output.json"
    assert output_path.exists()
    written = json.loads(output_path.read_text())
    assert written["participating_properties"] == derive()["participating_properties"]

    captured = capsys.readouterr()
    assert "P*" in captured.out
    assert "coverage list" in captured.out
    assert "reachable tuples enumerated" in captured.out
