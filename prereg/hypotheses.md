# Pre-registered Hypotheses CH-A1 to CH-A4

Status: PRE-REGISTRATION. Definitions only -- no results. Tagged `prereg-p5-v1`.

Transcribed from the task brief that pre-registered them (Phase 1), made
exact and measurable. Every count and CI below is produced by Phase 3's
committed machine output, through the slots pipeline (`populate_draft.py`)
-- never typed into the paper draft directly.

## CH-A1 (derived coverage strictly exceeds the declared-only baseline)

**Decision rule**: over the registered seeds and both workflows, the
derived-P* policy (Phase 2's `derive.py` output, enforced as new
predicates registered into the imported `sarc_governance` authority
gate) detects 100% of injected loss-violations -- decisions on which at
least one of the six `loss-model.yaml` predicates fires -- that the
declared-only baseline policy (the imported sarc-suite-one-pass
`specs/authority.yaml`: `role_unauthorised` + `order_value_over_cap`
only) misses (i.e. the baseline admits, the derived-P* policy does not).
Direction is registered ahead of time: derived-P* is hypothesized to
strictly dominate the baseline's detection set, never the reverse
(dominance is a one-way containment claim -- see the coverage-honesty
note below for what this does and does not claim).

**Measured**: for each of the six losses, the count of baseline-missed
violations and the count of derived-P*-missed violations (hypothesized
zero), per seed; aggregated counts and 95% CIs across the 30-seed list.
`NOT SUPPORTED` is printed if any derived-P*-missed count is nonzero on
any registered seed.

**Coverage-honesty note**: CH-A1 is a claim about the six declared
losses in `loss-model.yaml`, not about authority violations in general.
It does not claim the derived-P* policy is complete against any loss
outside this declared model -- see Definition 3's coverage list and the
paper's limitations section.

## CH-A2 (pair testing recovers exactly the derived set)

**Decision rule**: `checkers/pairtest_check.py`'s pair-test harness,
run over `pair-test-grid.yaml`'s enumerated finite model, recovers
exactly the same participation set `checkers/participation_check.py`
verifies as P* -- no property pair-testing flags as participating that
P* excludes (no false participants), and no property P* includes that
pair-testing fails to flag (no missed participants). The decision rule
is exhaustive equality over the enumerated domain, not a sample: `P*_
pairtest == P*_derived`, both computed independently (pair-testing by
sweeping the enumerated grid for any witness pair; derivation by
`derive.py`'s own procedure), then compared.

**Measured**: the two sets, their symmetric difference (hypothesized
empty), and the enumerated domain size actually swept (a generated
count, not estimated).

**Registered blind spot** (per the brief's own instruction: pair
testing "probes the representation, not the loss model"): CH-A2 tests
agreement between two computational procedures over one fixed
representation of the four-tuple domain. It cannot detect a loss the
declared model failed to state, or a property missing from the
representation entirely -- both are checked_scope_only limitations of
CH-A2 specifically, not of the derivation.

## CH-A3 (grant binding eliminates replay admissions)

**Decision rule**: with consumable execution-grant binding active
(Phase 2), replayed-execution admissions -- an executed action whose
presented `grant_id` was already in `control_state.consumed_grant_ids`
at evaluation time -- are exactly zero on the registered seeds, for
both workflows. With grant binding switched off (the ablation), replay
admissions are hypothesized nonzero on at least one registered seed
(a positive control: the replay hazard is real and reachable absent the
mechanism, not just theoretically stated).

**Measured**: replay-admission counts on and off, per seed; escalation
overhead (the count and rate of decisions that grant binding causes to
require a fresh grant-issuance round trip before admission) is
**reported, not registered** -- the brief fixes only the on/off
zero/nonzero direction, not the overhead's magnitude.

## CH-A4 (robustness across seeds and workflows)

**Decision rule**: CH-A1, CH-A2, and CH-A3's conclusions (not
magnitudes) hold across all 30 registered seeds and both workflows
(W1, W2). CH-A2 is exhaustive/formal-track (Phase 4-equivalent) and is
evaluated once against the enumerated model, not per seed -- it is
included in CH-A4 as "holds or does not," same treatment as
sarc-suite-one-pass's own CH7 in its CH8. CH-A1 and CH-A3 are evaluated
per seed x workflow; report means and 95% CIs (`mean_ci95`, the
order-stable t-based helper pattern ported from `sweep.py`, see
ADR-001-foundation.md) and the count of seed x workflow cells where
each hypothesis's own decision rule held. Any failure -- CH-A2's sets
disagreeing, or any seed x workflow cell where CH-A1's zero-missed or
CH-A3's zero-replay condition does not hold -- is reported as such, not
smoothed into the aggregate.

## Registration discipline

- No experiment code implementing CH-A1 to CH-A4 (Phase 3) may run
  before this file, plus `loss-model.yaml`, `seeds.json`,
  `pair-test-grid.yaml`, and the two schemas under `schemas/` are
  committed and tagged `prereg-p5-v1`.
- Every later result's manifest records the `prereg-p5-v1` commit sha.
- A test asserts the `prereg-p5-v1` tag's tree contains no results (no
  `out/`, no populated paper draft).
- CH-A3's escalation-overhead magnitude is explicitly registered as
  descriptive/non-directional -- reported with counts, not claimed as a
  specific rate ahead of time.
