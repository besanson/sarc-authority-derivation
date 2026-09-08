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
"""Tests for build_authority_bench_domain_yaml.py -- confirms all five
files exist per domain, parse as valid YAML, and the frozenset-valued
consumed_grant_ids domain (v2) is converted, not left to crash the
dumper."""
from __future__ import annotations

from pathlib import Path

import yaml

from build_authority_bench_domain_yaml import OUTPUT_ROOT, _yaml_safe, build

EXPECTED_FILES = ["candidate-context.yaml", "loss-model.yaml", "reachability.yaml", "baseline-manual-policy.yaml", "expected-certificates.yaml"]
EXPECTED_DOMAINS = ["v2", "v4", "data-and-communications"]


def test_yaml_safe_converts_a_frozenset_recursively():
    assert _yaml_safe({"domain": [frozenset({"b", "a"}), frozenset()]}) == {"domain": [["a", "b"], []]}


def test_build_writes_all_five_files_for_all_three_domains_as_valid_yaml():
    build()
    for domain in EXPECTED_DOMAINS:
        for filename in EXPECTED_FILES:
            path = OUTPUT_ROOT / domain / filename
            assert path.exists(), f"missing {path}"
            parsed = yaml.safe_load(path.read_text())
            assert isinstance(parsed, dict)
            assert parsed["domain"] in (domain, "procurement-v2", "software-and-cloud-v4", "data-and-communications")


def test_candidate_context_yaml_matches_the_declared_candidate_properties():
    from domain_datacomms import CANDIDATE_PROPERTIES_DATACOMMS

    build()
    path = OUTPUT_ROOT / "data-and-communications" / "candidate-context.yaml"
    parsed = yaml.safe_load(path.read_text())
    names = [p["name"] for p in parsed["candidate_properties"]]
    assert tuple(names) == CANDIDATE_PROPERTIES_DATACOMMS
