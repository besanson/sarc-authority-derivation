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
Phase 3: experiments. Runs the real imported baseline's decision stream
(sarc-suite-one-pass's RetailSimulation, real UCI retail data, real
per-class defect injection) through three authority policies -- baseline
declared-only, derived-P*, and an over-inclusive all-properties ablation
-- plus a grant-binding on/off ablation with injected replay, for one
(seed, workflow) pair. sweep.py drives this across all 30 registered
seeds and both workflows and aggregates with CIs.

sarc-suite-one-pass is imported (sys.path), never edited (ADR-001-
foundation.md, task brief Out of scope). Enrichment beyond what one-pass
generates -- actor_role's finer tiering, resource_class, budget_
remaining, frozen, grant issuance/consumption -- is this repo's own new
code, deterministic given `seed`, layered on top of one-pass's real
decision_id/sku/proposed_qty/read_cost/true_cost/evidence/injected_defect
stream exactly as one-pass's own suite_sim.py already layers seeded role
assignment and defect injection on top of the raw UCI CSV.

Remediation (task brief: reachability "includes post-remediation actions
produced by the one-pass operators"): order_value is computed twice per
decision -- pre-remediation from read_cost (the observed, possibly
corrupted evidence) and post-remediation from true_cost (what one-pass's
own evidence-substitution remediator corrects to) -- mirroring
composition.py's real substitution rule (corrupted -> true) without
re-running the full three-gate composition, which is paper 4's own
separate contribution and out of this paper's scope. Every policy below
is evaluated against the EXECUTED (post-remediation) value, per
one-pass's own "the executed action still uses the remediated value" rule.

Methodological note on CH-A1 (stated here, not just in the paper): the
"true_verdict" ground truth and the derived-P* policy's own admission
decision are BOTH computed from the same loss-model.yaml registry (the
declared loss model IS the ground truth this artifact derives against)
-- so derived_missed is trivially zero by construction, not an
independent empirical finding. The genuine empirical comparison CH-A1
measures is baseline_missed: the imported baseline evaluates a
DIFFERENT, coarser check (role membership + a single value cap, via the
real sarc_governance evaluation of specs/authority.yaml), so whether it
misses violations the loss model declares is a real, non-tautological
question this run answers.

SEED = 26313 (inherited; every per-decision seeded choice below derives
from the run's own `seed` argument via a dedicated random.Random
instance, never the module-level default, so seeds never leak across
runs)
"""
from __future__ import annotations

import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

ONE_PASS_DIR = str(Path(__file__).resolve().parent.parent / "sarc-suite-one-pass")
if ONE_PASS_DIR not in sys.path:
    sys.path.insert(0, ONE_PASS_DIR)

import composition as op_composition  # noqa: E402  (one-pass, imported not copied)
from suite_sim import DecisionPlan, RetailSimulation  # noqa: E402

from domain import StateTuple, load_all_skus, load_loss_model, sku_resource_class  # noqa: E402
from grant import GrantLedger  # noqa: E402
from losses import load_loss_registry, m_verdict  # noqa: E402

DATA_PATH = str(Path(ONE_PASS_DIR) / "data" / "open_retail_daily.csv")
AUTHORITY_SPEC_PATH = str(Path(ONE_PASS_DIR) / "specs" / "authority.yaml")

ROLE_BY_WORKFLOW = {"W1": "agent-replenish", "W2": "agent-w2-replenish"}
UNAUTHORIZED_ROLE = "agent-unauthorized"
DELEGATE_RATE = 0.20  # of otherwise-authorized decisions, seeded
UNAUTHORIZED_RATE = 0.05  # matches one-pass's own S3 rate
FROZEN_INJECTION_RATE = 0.02  # matches one-pass's own per-class defect rate
REPLAY_INJECTION_RATE = 0.05
PERIOD_BUDGET_MULTIPLIER = 1.15  # applied to the median per-period demand -- deliberately tight enough to bind sometimes


@dataclass(frozen=True)
class EnrichedDecision:
    decision_id: int
    day: int
    sku: str
    proposed_qty: float
    order_value_post: float  # executed (post-remediation) value
    remediated: bool
    actor_role: str
    resource_class: str
    workflow: str
    is_replay_probe: bool


def calibrate_period_budget(enriched: List["EnrichedDecision"]) -> float:
    """The resource gate's delegated pool, per period (one day for W1,
    one commitment window for W2 -- both are exactly 'one distinct `day`
    value', since W2's plan already contains only one entry per SKU per
    7-day window). Calibrated from the real per-period demand
    distribution (median total order_value_post across all periods this
    plan actually produced), not hand-picked -- PERIOD_BUDGET_MULTIPLIER
    is deliberately just above 1.0 so the pool binds on above-median
    periods without being either always-empty or never-binding."""
    totals: Dict[int, float] = {}
    for d in enriched:
        totals[d.day] = totals.get(d.day, 0.0) + d.order_value_post
    ordered = sorted(totals.values())
    median = ordered[len(ordered) // 2]
    return median * PERIOD_BUDGET_MULTIPLIER


def _authority_role_ceiling(role: str, loss_model: Dict[str, Any]) -> float:
    ceilings = next(
        loss["declared_parameters"]["role_entitlement_ceiling"]
        for loss in loss_model["losses"] if loss["id"] == "order_value_beyond_entitlement"
    )
    return float(ceilings[role])


WORKFLOW_STREAM_OFFSET = {"W1": 0, "W2": 41}  # deterministic, workflow-distinct RNG stream offset --
# NOT Python's built-in hash() on a string, which is randomized per
# process (PYTHONHASHSEED) by default and previously made enrich_plan's
# own role/replay-probe assignment non-reproducible ACROSS separate
# process invocations, even though a single process's own two calls
# agreed with each other -- exactly the failure test_committed_seed_
# replay_byte_identical (test_experiments.py) exists to catch, and did.


def enrich_plan(plan: List[DecisionPlan], seed: int, workflow: str, all_skus: List[str]) -> List[EnrichedDecision]:
    rng = random.Random(seed * 1_000_003 + WORKFLOW_STREAM_OFFSET[workflow])
    full_role = ROLE_BY_WORKFLOW[workflow]
    out = []
    for p in plan:
        if p.role == "agent-unauthorized":
            role = UNAUTHORIZED_ROLE
        elif rng.random() < DELEGATE_RATE:
            role = "agent-delegate"
        else:
            role = full_role
        order_value_pre = p.proposed_qty * p.read_cost
        order_value_post = p.proposed_qty * p.true_cost
        out.append(EnrichedDecision(
            decision_id=p.decision_id,
            day=p.day,
            sku=p.sku,
            proposed_qty=p.proposed_qty,
            order_value_post=order_value_post,
            remediated=(order_value_pre != order_value_post),
            actor_role=role,
            resource_class=sku_resource_class(p.sku, all_skus),
            workflow=workflow,
            is_replay_probe=(rng.random() < REPLAY_INJECTION_RATE),
        ))
    return out


def run_seed_workflow(seed: int, workflow: str) -> Dict[str, Any]:
    """Runs both grant_binding=on and grant_binding=off in one pass over
    the same decision stream (CH-A3's paired comparison): 'on' consults a
    real GrantLedger per decision, so a replay probe's second consumption
    is genuinely checked and rejected per Proposition 3; 'off' is a
    policy that never consults grant state at all, so a replay probe is
    admitted unconditionally -- not a second ledger with the same
    single-use logic (that would not be an ablation of anything)."""
    sim = RetailSimulation(DATA_PATH)
    full_role = ROLE_BY_WORKFLOW[workflow]

    plan = sim.generate_plan(
        seed=seed, unauthorized_role_rate=UNAUTHORIZED_RATE,
        authorized_roles=[full_role], unauthorized_role=UNAUTHORIZED_ROLE,
        workflow=workflow, commitment_period_days=(7 if workflow == "W2" else 1),
    )
    all_skus = load_all_skus(DATA_PATH)
    enriched = enrich_plan(plan, seed, workflow, all_skus)
    period_budget = calibrate_period_budget(enriched)

    loss_model = load_loss_model()
    registry = load_loss_registry(loss_model)
    baseline_cap = _authority_role_ceiling(full_role, loss_model)  # same ceiling as the top authorized tier
    baseline_spec = op_composition.load_sarc_spec(AUTHORITY_SPEC_PATH)

    budget_remaining = period_budget
    current_period_day: int = enriched[0].day if enriched else 0
    frozen_rng = random.Random(seed * 7 + 1)
    ledger = GrantLedger()

    true_violations = 0
    baseline_missed = 0
    derived_missed = 0
    spurious_escalations_overinclusive = 0
    replay_probe_count = 0
    replay_admissions_grant_binding_on = 0
    replay_admissions_grant_binding_off = 0

    for d in enriched:
        if d.day != current_period_day:
            budget_remaining = period_budget  # the delegated pool replenishes each new period, like Greensarc's own daily_cost_budget
            current_period_day = d.day
        frozen = frozen_rng.random() < FROZEN_INJECTION_RATE

        state = StateTuple(
            actor_role=d.actor_role,
            resource_class=d.resource_class,
            order_value=d.order_value_post,
            day=d.day,
            workflow=d.workflow,
            grant_id=None,  # a fresh (first) presentation is never itself a replay
            consumed_grant_ids=ledger.consumed_grant_ids(),
            budget_remaining=budget_remaining,
            frozen=frozen,
        )
        true_verdict = m_verdict(state, registry)  # the declared loss model IS the ground truth
        if true_verdict:
            true_violations += 1

        # -- baseline: real sarc_governance evaluation of the imported authority.yaml --
        baseline_response, _ = op_composition.evaluate_sarc_pag(
            baseline_spec, role=d.actor_role, allowed_roles=(full_role,),
            order_value=d.order_value_post, order_value_cap=baseline_cap,
        )
        baseline_admits = baseline_response == op_composition.Response.ADMIT
        if baseline_admits and true_verdict:
            baseline_missed += 1

        # -- derived-P*: admits iff the loss registry it directly implements
        # says safe -- trivially complete against this same loss model by
        # construction (see module docstring); kept as an explicit
        # variable, not assumed, so a future change here is caught by
        # test_experiments.py rather than silently staying "always zero".
        derived_admits = not true_verdict
        if derived_admits and true_verdict:
            derived_missed += 1

        # -- over-inclusive ablation: derived-P* PLUS a spurious escalation on
        # the one non-participating candidate (workflow == W2) -- the measured
        # cost of treating "everything" as authority-bearing instead of
        # deriving the minimal set. Only counted as SPURIOUS when the
        # underlying decision was genuinely safe (escalating an actual
        # violation is not spurious, it is redundant-but-correct).
        if workflow == "W2" and not true_verdict:
            spurious_escalations_overinclusive += 1

        # -- grant issuance + first (legitimate) consumption --
        sealed_action = {"decision_id": d.decision_id, "sku": d.sku, "order_value": d.order_value_post, "day": d.day}
        grant_id = f"g-{d.decision_id}"
        ledger.issue(grant_id, sealed_action, d.decision_id, d.day)
        ledger.consume(grant_id, sealed_action, d.decision_id, d.day)
        if baseline_admits or derived_admits:
            budget_remaining = max(0.0, budget_remaining - d.order_value_post)

        # -- replay probe: re-present the SAME grant a second time --
        if d.is_replay_probe:
            replay_probe_count += 1
            admitted_on = ledger.consume(grant_id, sealed_action, d.decision_id, d.day)
            if admitted_on:
                replay_admissions_grant_binding_on += 1
            # "grant binding off": a policy that never consults grant/ledger
            # state at all admits any presented grant unconditionally --
            # this IS the ablation, not a second ledger instance.
            replay_admissions_grant_binding_off += 1

    return {
        "seed": seed,
        "workflow": workflow,
        "n_decisions": len(enriched),
        "true_violations": true_violations,
        "baseline_missed": baseline_missed,
        "derived_missed": derived_missed,
        "spurious_escalations_overinclusive": spurious_escalations_overinclusive,
        "replay_probe_count": replay_probe_count,
        "replay_admissions_grant_binding_on": replay_admissions_grant_binding_on,
        "replay_admissions_grant_binding_off": replay_admissions_grant_binding_off,
    }
