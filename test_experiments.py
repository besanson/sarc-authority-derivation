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
"""Tests for experiments.py. Marked slow: exercises the real imported
simulation end to end (seconds, not milliseconds)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from experiments import calibrate_period_budget, enrich_plan, run_seed_workflow

pytestmark = pytest.mark.slow


def test_run_seed_workflow_is_deterministic():
    r1 = run_seed_workflow(26313, "W1")
    r2 = run_seed_workflow(26313, "W1")
    assert r1 == r2


def test_run_seed_workflow_derived_never_misses():
    """CH-A1's decision rule, checked directly (not just assumed): the
    derived-P* policy admits a decision iff the declared loss model
    itself says safe, so it can never miss a violation by construction
    -- this test fails if a future change breaks that invariant."""
    for workflow in ("W1", "W2"):
        result = run_seed_workflow(26313, workflow)
        assert result["derived_missed"] == 0


def test_run_seed_workflow_grant_binding_on_blocks_all_replays():
    for workflow in ("W1", "W2"):
        result = run_seed_workflow(26313, workflow)
        assert result["replay_admissions_grant_binding_on"] == 0


def test_run_seed_workflow_grant_binding_off_admits_every_replay_probe():
    for workflow in ("W1", "W2"):
        result = run_seed_workflow(26313, workflow)
        assert result["replay_admissions_grant_binding_off"] == result["replay_probe_count"]


def test_different_seeds_produce_different_role_assignments():
    """Sanity check that DELEGATE_RATE-based enrichment is actually seed-
    sensitive, not accidentally constant."""
    from suite_sim import RetailSimulation

    from experiments import DATA_PATH, ROLE_BY_WORKFLOW
    from domain import load_all_skus

    sim = RetailSimulation(DATA_PATH)
    plan = sim.generate_plan(seed=1, unauthorized_role_rate=0.0, authorized_roles=[ROLE_BY_WORKFLOW["W1"]])
    all_skus = load_all_skus(DATA_PATH)
    enriched_a = enrich_plan(plan, seed=1, workflow="W1", all_skus=all_skus)
    enriched_b = enrich_plan(plan, seed=2, workflow="W1", all_skus=all_skus)
    roles_a = [d.actor_role for d in enriched_a]
    roles_b = [d.actor_role for d in enriched_b]
    assert roles_a != roles_b
    assert "agent-delegate" in roles_a
    assert "agent-delegate" in roles_b


def test_calibrate_period_budget_is_positive_and_reproducible():
    from experiments import DATA_PATH, ROLE_BY_WORKFLOW
    from suite_sim import RetailSimulation
    from domain import load_all_skus

    sim = RetailSimulation(DATA_PATH)
    plan = sim.generate_plan(seed=26313, unauthorized_role_rate=0.0, authorized_roles=[ROLE_BY_WORKFLOW["W1"]])
    all_skus = load_all_skus(DATA_PATH)
    enriched = enrich_plan(plan, seed=26313, workflow="W1", all_skus=all_skus)
    b1 = calibrate_period_budget(enriched)
    b2 = calibrate_period_budget(enriched)
    assert b1 == b2
    assert b1 > 0


def test_committed_seed_replay_byte_identical():
    """Mirrors sarc-suite-one-pass's own test_sweep_replay.py pattern
    (ADR-001-foundation.md): the registered SEED's committed per-cell
    output must be byte-reproducible from a fresh run."""
    committed_path = Path("out/results/sweep/seed_26313_W1.json")
    if not committed_path.exists():
        pytest.skip("sweep not yet run for this checkout; `make sweep` populates out/results/sweep/")
    committed = json.loads(committed_path.read_text())
    fresh = run_seed_workflow(26313, "W1")
    assert fresh == committed
