# Appendix A: Proofs

Every numbered claim below carries a `PROOF-STATUS` tag:
`machine-checked` (an executable `checkers/*.py` module verifies the
claim over an explicitly enumerated finite domain), `checked-scope-only`
(the certified scope is narrower than the general prose and is stated
exactly), or `pending-human-review` (asserted, not yet machine-verified).
`proven` is never written by this pipeline -- `checkers/proof_status_lint.py`
enforces this on every build. Ported convention, ADR-001-foundation.md.

## Definitions (restated from prereg/loss-model.yaml and participation.py)

**Definition 1 (participation).** Property p is authority-bearing for
loss model M iff there exist executable-reachable tuples a, a' differing
only in p whose M-verdicts differ.

**Definition 2 (the minimal participation set P\*).**
P\* = {p in candidate_properties : p is authority-bearing for M}.

**Definition 3 (the derived coverage list).**
coverage_list = candidate_properties − P\*.

## Proposition 0 (remediation-reachability is redundant in this formal model)

`domain.executable_reachable_tuples()` (rank-0 union remediation-
reachable) equals `domain.rank0_reachable_tuples()` alone: remediation
adds zero tuples beyond what rank-0 (the unconstrained full product of
the nine candidate properties' declared domains) already contains.
Consequently P\*, the coverage list, and every recorded witness are
identical whether or not remediation-reachable tuples are included in
the swept domain.

This corrects v0.1's fence and abstract (round-0 adjudicator review,
finding F0; `NOVELTY.md`'s Amendment), which claimed "remediation
changes the reachable set" without this having been checked against the
model as built. `rank0_reachable_tuples()` iterates the full Cartesian
product of all nine domains with no cross-field filter (ADR-002 removed
the one filter that existed, per-role policy consistency, when policy
stopped being a separate field); `remediation_reachable_tuples()` only
ever varies `order_value` within its own three-point declared domain --
every (other-eight-fields, any-order-value) combination it could
produce is therefore already present in rank-0 by construction, for any
choice of declared order_value domain, not merely the current one. This
is a structural fact about how the two functions compose, not a
coincidence of the specific 7,776-tuple grid.

PROOF-STATUS: machine-checked (`checkers/reachability_check.py`), over
the full 7,776-tuple rank-0 domain. `remediation_reachable_new_tuples: 0`
in `out/checkers/reachability_check.json`; `internally_consistent: true`
confirms the union equals rank-0 plus whatever remediation actually
added (zero), not merely equals rank-0 by omission.

**What this does not show.** Section 8's empirical layer is unaffected
by this proposition: `experiments.py` computes two distinct order_values
per real decision (pre- and post-remediation, from `read_cost` and
`true_cost`) and evaluates every policy against the executed
(post-remediation) value, exactly as the imported baseline's own
`composition.py` does. Proposition 0 is a fact about this artifact's
*formal, finite-model abstraction* of that setting, not about whether
remediation matters empirically -- it does, and CH-A1/CH-A3's numbers
already depend on it. Whether a *different* finite-model abstraction
could make remediation reachability-relevant, and whether P\* would then
differ, is registered as an open, two-sided question for v0.2
(`prereg/v2-reachability-redesign.md`, once committed), not assumed to
resolve either way.

## Proposition 1 (P\* is sound and minimal)

A gate that observes exactly P\* can always compute M's true verdict on
any executable-reachable tuple (soundness: dropping any P\* member
admits a loss-violating pair it could no longer distinguish from a safe
one); no proper subset of P\* has this property (minimality: no
non-member is required).

By Definitions 1-2, both halves restate exactly what "p is authority-
bearing" and "p is not authority-bearing" already mean: soundness-of-
dropping-p failing for p in P\* is definitionally p having a witness;
minimality of q not in P\* is definitionally q having none. This makes
Proposition 1 true by construction of P\* -- but only as true as the
witness search that computed P\* is bug-free, which is exactly what
independent re-verification checks, not re-assertion of the definition.

PROOF-STATUS: machine-checked (`checkers/participation_check.py`).
Three independent checks over the full 7,776-tuple executable-reachable
set (prereg/pair-test-grid.yaml's nine declared domains, not a sample):
(1) a fresh, from-scratch recomputation of P\*/coverage_list exactly
matches the committed `out/checkers/derivation_output.json` (catches
staleness or non-determinism in `derive.py`); (2) every recorded witness
pair is independently re-executed and confirmed to be reachable, to
differ in exactly its claimed property, and to actually produce
different M-verdicts (catches a bug in how a witness was recorded, not
just whether one exists); (3) minimality follows from (1)'s exhaustive
sweep covering every one of the nine candidates, not a subset.

## Proposition 2 (CH-A2: two independent derivations of P\* agree exactly)

The pair-test harness (`checkers/pairtest_check.py`, credited to the
Moona Intelligence replication report as the method's origin --
REPLICATIONS.md), implemented as a one-factor-at-a-time sweep relative
to every reachable tuple as a baseline -- an algorithm independent of
`participation.py`'s fingerprint-grouped pairwise search -- recovers
exactly `derive.py`'s committed P\*: no missed participants, no false
participants.

PROOF-STATUS: machine-checked (`checkers/pairtest_check.py`), over the
same 7,776-tuple executable-reachable set. `ch_a2_exact_recovery: true`
in `out/checkers/pairtest_check.json`; `missed_participants` and
`false_participants` both empty.

**Registered blind spot** (task brief, CH-A2): pair testing probes the
representation -- pair-test-grid.yaml's declared finite domain values --
not the loss model. It cannot detect a hazard whose true threshold falls
strictly between two declared values, or a property never represented
in the grid at all. `checkers/pairtest_check.py` emits this note in its
own output (`blind_spot_note`) rather than leaving it only in prose here.

## Proposition 3 (the execution-grant mechanism is single-use)

For any sequence of `GrantLedger.consume()` calls, at most one call ever
admits (returns `True`) for a given `grant_id`, and any call that admits
did so for exactly the sealed action that `grant_id` was issued against.

PROOF-STATUS: machine-checked (`checkers/grant_check.py`). Exhaustive
over 85 sequences: two grant_ids, each issued against a distinct sealed
action, every sequence of length 0-3 of consume attempts drawn from all
four (grant_id, presented_action) combinations -- the entire relevant
finite state space for this invariant (a longer sequence exercises no
new case: once a grant_id has produced one admitted consumption, every
later attempt for it is symmetric to cases already covered by the
length-1..3 sequences, since `consumed_grant_ids()` is a monotonically
growing set and the invariant is checked after every single step, not
only at sequence end).

## Remark (not a numbered claim the paper's results depend on): candidate-property coupling

An earlier tuple design (ADR-002-participation-tuple-design.md) exposed
per-role policy (entitlement ceiling, temporal window, allowed resource
classes) as separate tuple fields, each a pure deterministic function of
`actor_role`. Running `derive.py` against it found that Definition 1's
single-field perturbation test can never isolate a candidate property
that is a deterministic function of another candidate property the test
always holds fixed while testing it -- both the function's output field
and (unless some other, non-derived field also distinguishes the cases)
the field it is a function of are derived as non-participating, correct
under Definition 1 as literally stated but potentially misleading about
what a gate must observe if the derived field is in fact needed. This
artifact avoided the failure mode by construction (ADR-002: per-role
policy is background configuration, not a candidate property) rather
than by verifying the general claim above. The general claim itself --
which is a statement about Definition 1's method, not about this
artifact's specific loss model -- has not been checked against an
exhaustive sweep of coupling configurations.

PROOF-STATUS: pending-human-review.
