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

from derive import derive
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
