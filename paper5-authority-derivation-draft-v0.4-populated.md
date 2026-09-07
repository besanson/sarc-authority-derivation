# Deriving Authority: A Machine-Checkable Derivation from a Declared Loss Model to the Core Attribute Set a Pre-Action Authority Gate Must Observe -- Certified Sufficient and the Unique Reduct on the Registered Model

Gaston Besanson[^1]

[^1]: Universidad Torcuato Di Tella

Companion artifact: `sarc-authority-derivation`. Paper 5 of the SARC
series, built on the pinned `sarc-suite-one-pass` artifact (arXiv
[2608.18360](https://arxiv.org/abs/2608.18360), commit `782261e`) as a
read-only imported baseline (`ADR-001-foundation.md`).

**Status**: draft v0.4. Not submission-ready, not independently reviewed.
See the human checklist at the end of this document. v0.1.2 corrected a
finding from an author-side, AI-assisted adjudication pass, not
independent review: v0.1's fence and abstract claimed remediation
changes this artifact's formal reachable set; it did not, in v0.1's own
model (Section 5, Section 9). v0.2 executed a registered redesign under
which remediation genuinely is reachability-relevant for one property
(`min_order_quantity`), machine-checked (CH-A5-CH-A7). v0.3 corrected a
more fundamental error, surfaced by a commissioned external,
AI-assisted research review (`review-secondary/external-research-review-2026-09-06.pdf`)
and independently adjudicated and re-derived here, not applied directly:
v0.1/v0.2's Proposition 1 interpreted Definition 1's output (P\*) as a
minimal *sufficient* observation set (a reduct, in decision-reduct /
rough-set terminology); it computes the **core** -- individually
indispensable properties -- which need not itself be sufficient in
general (Negative Proposition N). **v0.4 corrects a threat to the
Section 8 experiment's internal validity**, found by this paper's own
direct code inspection, not an external review: the baseline/derived/
over-inclusive policy arms shared one budget trajectory and one grant
ledger across one decision loop. See the Corrections (v0.3) and
Corrections (v0.4) sections immediately below for the full account of
each; nothing about v0.1's, v0.2's, or v0.3's own committed results is
retroactively edited to match a later correction -- each stays frozen
and cited as a prior iteration, per this project's own registration
discipline.

## Corrections (v0.3)

**The overclaim.** v0.1 and v0.2's Proposition 1 stated: "A gate that
observes exactly P\* can always compute M's true verdict on any
executable-reachable tuple... no proper subset of P\* has this
property." This claims P\* is a minimal *sufficient* observation set --
in decision-reduct / rough-set terminology (Pawlak, 1982; Skowron and
Rauszer, 1992), a **reduct**. What Definition 1 actually computes --
correctly, and unchanged by this correction -- is the **core**: the set
of properties with an individual singleton-perturbation witness (a
reachable pair differing in exactly that property with different
verdicts). The core is always a subset of every reduct, but a core need
not itself be sufficient: an empty core, in particular, is trivially
insufficient whenever the reachable set is nonempty and not
verdict-uniform. Proposition 1's generality claim is false; the specific
v1/v2 numbers it reported were never wrong, only mischaracterized.

**The source.** A commissioned external, AI-assisted research review
(`review-secondary/external-research-review-2026-09-06.pdf`, sha256
`b205faf65fe84d773260d1ed514b20f5b04e420380d3136c23bff1cde4506b0b`)
identified the core-versus-reduct conflation, among other questions and
suggested directions. Per this project's own discipline, the review's
findings were not applied directly: they were adjudicated against this
artifact's own definitions, and the counterexample used to demonstrate
the failure (Negative Proposition N, below) was re-derived from first
principles rather than copied from the review's own prose
(`prereg/v3-core-reduct-correction.md` records the adjudication).

**The correction.** `prereg/v3-core-reduct-correction.md` (tag
`prereg-p5-v3`) registers, before any v3 code: Definitions 4-6
(sufficiency, reduct, core, Section 5 below), Proposition 1' (replacing
Proposition 1: Definition 1 computes the core; the core is a subset of
every reduct; if the core is sufficient it is the unique reduct --
decided per instance, by certificate, never assumed), and Negative
Proposition N (a reachable set on which the core is empty and not
sufficient, machine-checked). `appendix-a-proofs.md` proves both:
Proposition 1's own entry there is not deleted -- its original wording
stays, as an honest record, with its PROOF-STATUS narrowed from
`machine-checked` to `checked-scope-only` and a correction note attached
directly to it, the same no-silent-rewrite principle `NOVELTY.md`'s own
amendments already follow.

**What was checked, and what it found (`reduct.py`; `checkers/sufficiency_check.py`,
`checkers/reduct_check.py`, `checkers/core_insufficiency_counterexample.py`).**

- **Proposition 1' claim 1** (Definition 1 computes the core): the core
  recomputed via Definition 1's witness search matches the core
  recomputed independently via the intersection of every reduct
  `reduct.exact_reducts()` finds by direct enumeration --
  True -- two different algorithms, confirmed
  to agree, mirroring this project's own established CH-A2/CH-A6
  discipline of never trusting one computation of the same claim.
- **CH-A8** (is the v2 core sufficient on the v2 executable-reachable
  set?): **SUPPORTED**. `sufficiency_certificate`:
  14,256 partition cells, uniform verdict
  within every one, over 24,624 reachable
  tuples.
- **CH-A10** (exact reduct enumeration on the v2 model): **1
  reduct(s) found**, minimum cardinality **9**,
  core is the unique reduct: **True**
  (1,023 of
  `2^10 = 1,024`
  candidate subsets tested after pruning). Together with CH-A8, this certifies --
  for this registered model specifically, not as a general property of
  the method -- that the core is sufficient and is the unique reduct, at
  minimum cardinality nine: the title's and abstract's "core, certified
  sufficient and the unique reduct on the registered model" is licensed
  by this specific result, not asserted independently of it.
- **Negative Proposition N**: **SUPPORTED**, exactly
  matching the registered fixture's own pre-committed expectation
  (True) -- confirmation against an
  expectation fixed before this checker existed, not a result fitted
  after the fact.
- **CH-A9** (does a real, declared co-variation between `actor_role` and
  `resource_class` break core sufficiency in a constrained variant of
  this artifact's own procurement model?): **NOT SUPPORTED**.
  The constrained variant's own core
  (6 properties) is already sufficient.
  Not smoothed over: the declared pairing maps four roles onto three
  resource classes (pigeonhole), so two roles share one resource class,
  leaving a residual case two `actor_role`-sensitive,
  `resource_class`-blind losses can still witness directly -- a real,
  explainable negative finding, not evidence against Negative
  Proposition N's general claim (which concerns whether the failure
  *can* occur, not whether *this* declared variant triggers it).

**Renamed outputs (going forward; v1's and v2's own committed files are
byte-frozen, apart from the informational `generated_at_head_sha` stamp
any fresh `make formal` run refreshes).** `participating_properties`
becomes `core_attributes` in v3's own new outputs; `coverage_list`'s
v3-equivalent is `redundant_attributes`; new fields `is_core_sufficient`
(with a `sufficiency_certificate` or a `counterexample`), `reducts`, and
`minimum_reducts` make the previously-undistinguished core/reduct
concepts separately reportable, per instance, going forward.

**Grant binding, repositioned.** Section 6's execution-grant mechanism
is engineering informed by established capability-system patterns --
Macaroons (Birgisson et al., 2014), UCAN, and Biscuit all bind a token
to a specific, attenuated scope of authority -- not a claim of novelty
in its own right. It closes a real coverage boundary the Moona
Intelligence replication's finding A7 named, but the mechanism itself
follows prior art; this paper's own contribution is the derivation
(Definitions 1-6) that motivated observing the boundary at all, not the
binding primitive.

## Corrections (v0.4)

**The issue.** Direct inspection of `experiments.py` (v0.1 through v0.3,
unchanged by any of those revisions) found that the three policy arms
Section 8 compares -- baseline, derived, over-inclusive -- were
evaluated inside one decision loop against one shared `budget_remaining`
float and one shared grant ledger: baseline's own admission could
deplete the pool derived's later verdict then read, and the
over-inclusive arm had no admission trajectory of its own at all to
diverge from derived's. This is a threat to the Section 8 experiment's
internal validity, not a proof-claim error (contrast the Corrections
(v0.3) section above) -- registered (`prereg/v3.1-isolated-arms.md`, tag
`prereg-p5-v3.1`) before any fix was written, with a two-sided
hypothesis: isolating the three arms' state may or may not change any
CH-A1/CH-A3/CH-A4 measured quantity. Either outcome was registered as a
valid result before the re-measurement ran.

**The fix.** `experiments.py`'s `ArmState` now gives each arm its own
`{budget_remaining, ledger, admission_history}`, initialised identically
per (seed, workflow) run and mutated only by that arm's own admission
decisions (`process_decision`; `test_experiments.py`'s contamination
regression test directly witnesses this: a decision where baseline
ADMITS and derived BLOCKS changes only baseline's own budget). Decision
rules themselves are unchanged -- only which state each rule reads
changed, from shared to arm-local; `true_verdict` is defined against
derived's own trajectory specifically, the one arm whose rule ("admit
iff the loss registry says safe") already shared the registry, and now
also shares the state that registry reads.

**What the re-measurement found.** All 30 registered
seeds and both registered workflows (W1, W2) were
re-run under the isolated arms. The isolation hypothesis is
**NOT SUPPORTED**: every CH-A1/CH-A3/CH-A4 mean,
confidence interval, and boolean is byte-identical between v0.3's frozen (shared-state)
result and this re-measurement's (isolated-state) one
(0 fields moved). Not left
as an unexplained null result: a direct, exhaustive diagnostic
(`checkers/isolation_delta_check.py`) confirms `spend_against_depleted_
delegated_budget` -- the one loss predicate that reads `budget_
remaining`, the one field the shared-state bug could have gotten wrong
(`consumed_grant_ids`, the other shared field, is read by
`replayed_consumed_grant`, which this module's per-decision `state_for`
always evaluates against a `grant_id` of `None` and so cannot fire there
regardless -- verified directly, not assumed, before relying on it) --
fires **0** times across
**349,020** decisions swept
(0 of
60 cells). The bug was real and is
now fixed; for this declared parameter set, it never had the
opportunity to change a measured number, because the delegated budget
never actually bound tightly enough, in practice, to be the deciding
factor for any real decision in this dataset. The fix is kept
regardless of today's numbers: it is the correct experimental design on
its own terms, and the contamination regression test now guards against
a future declared parameter set (e.g. a tighter `PERIOD_BUDGET_
MULTIPLIER`) where it would matter.

**What this does not show.** A byte-identical result on this declared
model is not evidence that arm isolation never matters -- only that it
did not matter here, mechanistically explained rather than assumed. A
different declared loss model, budget multiplier, or seed set could
still see it bind (Threats to validity, Section 9). CH-A1's headline
finding (the imported baseline misses a large share of declared
violations the derived policy catches) and CH-A3's grant-replay result
are unchanged, in both number and interpretation, by this correction.

## Abstract

Prior work in this setting either declares which properties an
authority gate must observe (this artifact's own imported baseline,
`sarc-suite-one-pass`'s `specs/authority.yaml`: role plus a single value
cap) or derives safety constraints from losses as a human-driven analyst
methodology (the STPA lineage). We formalize a participation criterion
-- property p is authority-bearing for a declared loss model M iff two
executable-reachable actions differing only in p produce different
M-verdicts -- and a derivation procedure that computes the **core**
attribute set (individually indispensable properties) and an honestly
emitted list of redundant properties, in the remediation-coupled setting
`sarc-suite-one-pass` establishes. Correcting an overclaim from v0.1/v0.2
(surfaced by a commissioned external review, independently adjudicated
and re-derived, not applied directly -- Corrections above), we prove the
core is not in general a **reduct** (a minimal *jointly sufficient*
observation set): Negative Proposition N exhibits a reachable set on
which the core is empty and insufficient. For this artifact's own
registered v2 model, we machine-check, per instance rather than assume,
that the core *is* sufficient and is the *unique* reduct (CH-A8, CH-A10).
We exhaustively verify the core exactly (Definition 1's witness search
and a second, independent reduct-enumeration algorithm agree), recover
it via a formalized pair-testing method (credited to an independent
replication of the imported baseline), and add a consumable
per-execution grant mechanism -- capability-system engineering informed
by prior art (Macaroons, UCAN, Biscuit), not a novelty claim -- that
binds one authorization to exactly
one sealed execution. Against the real imported simulation, 30 seeds,
both workflows: CH-A1 (SUPPORTED), CH-A2 (SUPPORTED), CH-A3 (SUPPORTED), and CH-A4 (SUPPORTED).

## 1. Introduction

Once a pre-action authority gate is permitted to observe only the
properties someone thought to declare, the gate is exactly as complete
as that person's foresight -- and no more. `sarc-suite-one-pass`'s own
imported baseline (`specs/authority.yaml`) observes two things: whether
the acting role is on an allow-list, and whether an order value exceeds
a single scenario-wide cap. Its own roadmap names the gap directly:
"Authority-completeness: deriving which properties must be
authority-bearing from a consequence model, rather than declaring them"
(`sarc-suite-one-pass`'s `README.md`), motivated by an independent
replication's coverage-boundary findings (`REPLICATIONS.md`; Section 4
below).

This paper closes that gap for one declared loss model. We do not derive
the loss model itself -- that stays a human, out-of-scope act of
judgment (Section 8) -- but given one, we derive, deterministically and
machine-checkably, the **core** property set (Definition 6) an authority
gate must observe to correctly detect every loss the model declares --
certified, per instance and never assumed, to also be sufficient and the
unique reduct (Definitions 4-5) for this artifact's own registered v2
model (CH-A8, CH-A10; Corrections above) -- and we honestly emit the
properties it does not need, rather than silently dropping them.

### 1.1 Novelty fence

STPA derives safety constraints from declared losses as an analyst
methodology; ABAC mining reconstructs policies from existing grants;
interference-style criteria detect dependence but do not derive. This
paper contributes a formal participation criterion over the
executable-reachable action set, a machine-checkable derivation from a
declared loss model to the minimal property set a pre-action authority
gate must observe, with the excluded residue emitted as a derived
coverage list, in the remediation-coupled setting sarc-suite-one-pass
establishes.

(Verbatim from `NOVELTY.md` as corrected in v0.1.2; the original
Phase R wording and the correction's full account are in `NOVELTY.md`'s
Amendment section and this paper's Section 5 and Section 9 -- the
original clause claimed remediation changes this artifact's own formal
reachable set, which round-0 review found false; the corrected fence
above claims only what Section 5 shows is actually instantiated. See
Section 3 for the full
per-cluster novelty comparison this fence summarizes, and
`verified-citations.json` for every source's fetch-verification record.
The fence's own "minimal property set" phrase predates the v0.3
core-vs-reduct correction (Corrections above): in general this artifact
derives the **core** (Definition 6); sufficiency-and-minimality
(Definition 5's reduct) is certified only per instance (CH-A8, CH-A10),
never assumed for an arbitrary declared loss model (Negative
Proposition N).)

## 2. Setting

We inherit `sarc-suite-one-pass`'s retail simulation without editing it:
real UCI Online Retail data (CC BY 4.0, `data/PROVENANCE.md`), a
deterministic decision stream (`suite_sim.RetailSimulation`), two
workflows (W1 daily, W2 weekly commitment, `prereg/w2-workflow.md`
carried over by reference), and two remediation operators (evidence
substitution, resource downroute) whose composition paper 4 already
establishes is sound under `remediate_regate` (`composition.py`,
Theorem 1 there). This paper adds no new remediation logic; it asks a
different question of the same remediation-coupled setting: which
properties must the authority gate observe to detect a declared loss
model, given the executable-reachable action set that setting produces?
(Section 5 states precisely how this artifact's own formal reachable
set does and does not depend on remediation -- narrower than the
question as originally posed, and stated exactly, not assumed.)

We declare six losses (`prereg/loss-model.yaml`, tagged `prereg-p5-v1`)
as machine-evaluable hazard predicates over an (action, context,
evidence, control_state) four-tuple: order value beyond a per-role
entitlement ceiling, procurement outside a per-role permitted temporal
window, action on a resource class the role is not entitled to, replayed
execution of a consumed authorization, spend against a depleted
resource-gate budget, and action on a control state marked frozen. Nine
per-decision fields are candidates for observation (`domain.py`'s
`CANDIDATE_PROPERTIES`); per-role policy itself (the entitlement
ceiling/window/allowed-class tables) is declared background
configuration the gate is built with, not a per-decision observable
input -- see `ADR-002-participation-tuple-design.md` for why an earlier
design that exposed resolved policy values as separate fields produced a
mathematically correct but practically unimplementable P\*.

## 3. Related work (novelty comparison)

One paragraph per neighbouring cluster, reproduced from `NOVELTY.md`
(Phase R; every source fetch-verified in `verified-citations.json`):

**STPA and its descendants.** Leveson and Thomas's STPA Handbook (2018)
establishes System-Theoretic Process Analysis: a structured but
human-driven analyst process. Young and Leveson's STPA-Sec (CACM 2014)
carries the same process into security; Rismani, Dobbe, and Moon's PHASE
(2024) and Mylius (2025) into AI governance and frontier-AI hazard
analysis; Qi et al.'s DeepSTPA (2023) into the ML development lifecycle.
In every case the output is human-authored, expert-reviewed constraints,
not a machine-checked **core** (Definition 6), and none formalize
soundness or minimality as machine-checkable claims over an enumerated
model.

**ABAC policy mining.** Xu and Stoller (TDSC 2015) establish the
problem of reconstructing which attributes already participate in an
*existing* deployed policy from grants and attribute data; Nobi et al.'s
2022 survey catalogues the ML extensions of that same reconstruction
problem. This paper derives forward, from a declared loss model to a
*new* gate's **core** property set (Definition 6), with a machine-checked
soundness-and-minimality guarantee (Definition 1's own witness search)
mining has no ground truth to check itself against.

**Policy-language completeness.** Crampton and Morisset's PTaCL (POST
2012) and Crampton and Williams's canonical-completeness result (SACMAT
2016) establish what a policy *combination* language can express once
the participating attributes are already fixed. Neither asks which
attributes must be observed in the first place; this paper contributes
exactly that prior question.

**Non-interference.** Goguen and Meseguer (1982) define non-interference
as a semantic *check* of whether a dependence exists between two fixed
parties in a given system. This paper's Definition 1 borrows the
underlying comparison -- does changing X change the verdict? -- but
turns it into a derivation swept over every candidate property against
every loss predicate, with the **core** (Definition 6) soundness and
minimality verified exhaustively, not a single dependence check.

**Counterfactual fairness.** Kusner et al. (NeurIPS 2017) evaluate one
pre-chosen sensitive attribute's counterfactual invariance, once. This
paper generalizes the same comparison to every candidate property
against a declared loss model, with an exhaustive **core**-minimality
result (Definition 6) the
fairness literature neither claims nor checks.

**A scope note on "sound" and "minimal" in this section (v0.3
Corrections above).** Every comparison above was written before
Definitions 4-6 existed and describes this artifact's Definition 1
witness search: sound in the sense that every recorded witness is
independently re-verified reachable and verdict-differing, minimal in
the sense that no property survives in P\* without its own witness --
both properties of the **core** computation itself (Definition 6), true
by the witness search's own construction (`checkers/participation_
check.py`/`_v2.py`), not a claim that the core suffices to determine
every verdict jointly. Sufficiency and reduct-minimality in Definitions
4-5's sense are certified only per instance -- CH-A8 and CH-A10 for this
artifact's own registered v2 model -- never assumed for an arbitrary
declared loss model (Negative Proposition N).

## 4. The Moona Intelligence replication and its method's origin

An independent replication of the imported baseline (Moona Intelligence,
published 28 August 2026 under the organisation's then-name, Belay
Intelligence; `REPLICATIONS.md`), beyond confirming a clean-clone
reproduction of `sarc-suite-one-pass`'s full release-check, ran eight
adversarial pair tests against the deployed `specs/authority.yaml` on a
separate branch with zero edits to existing code, and reported four
coverage boundaries: resource identity is present in the execution
context but not authority-bearing in the configured policy; the policy
is role-based rather than actor-specific; temporal context is recorded
but not authority-bearing; and, in finding A7,

> "nothing in the authority path exposes an authorization identifier,
> an approval identifier, a nonce, or any consume on use mechanism that
> would bind one authority verdict to exactly one execution"

(Moona Intelligence, 2026). This is the method's origin for CH-A2's
pair-testing formalization below, and finding A7 is this paper's direct
motivation for Section 6's grant mechanism. On the scope of the eight
tests themselves, the report is explicit about what it does and does not
claim:

> "I want to be plain about the framing here. Nothing below is a report
> of SARC breaking. It is a report of what SARC's own authority policy
> was configured to look at, produced by testing that policy directly
> rather than by editing it."

(Moona Intelligence, 2026). We take this framing seriously in Section 7
below: our own formalized pair-test checker inherits exactly this
scope limit, stated as a registered blind spot, not smoothed over.

The report's own closing synthesis states the general principle this
paper's derivation exists to act on, not just observe:

> "a re-evaluation mechanism is only as complete as the policy it
> re-evaluates, and a policy's completeness is a property of what it
> was configured to read, not of the architecture that calls it"

(Moona Intelligence, 2026). Definitions 1-3 below are one way to make
that property -- what a policy is configured to read -- itself derived
rather than declared, for one stated loss model.

## 5. Definitions

**Definition 1 (participation).** Property p is authority-bearing for
loss model M iff there exist executable-reachable tuples a, a′
differing only in p whose M-verdicts differ.

**Definition 2 (the minimal participation set P\*).**
P\* = {p in candidate_properties : p is authority-bearing for M}.

**Definition 3 (the derived coverage list).**
coverage_list = candidate_properties − P\*, emitted, not dropped.

**Definition 4 (sufficiency; v0.3, `prereg/v3-core-reduct-correction.md`).**
A property set S ⊆ candidate_properties is sufficient for M on a
reachable set R iff every pair of reachable tuples agreeing on every
property in S has the same M-verdict -- the projection onto S determines
the verdict everywhere on R.

**Definition 5 (reduct).** A reduct is a property set that is sufficient
(Definition 4) and minimal: no proper subset of it is sufficient.
candidate_properties itself is always sufficient, so at least one reduct
always exists; there can be more than one.

**Definition 6 (core).** The core is the intersection of every reduct.
Standard rough-set fact, proved in `appendix-a-proofs.md` (Proposition
1' claim 1): a property p is in the core iff some reachable pair
differing only in p has a different verdict -- exactly Definition 1's
own participation criterion. **P\* (Definitions 1-2) is the core, not in
general a reduct** -- see Corrections above and Section 5's v0.3 update
below.

"Executable-reachable" (task brief) includes post-remediation actions:
`prereg/pair-test-grid.yaml`'s reachability section characterizes what
the imported baseline's two remediation operators can produce (evidence
substitution: any other order-value point in the declared domain,
either direction; resource downroute, W2 only: strictly lower only),
and `domain.executable_reachable_tuples()` is the union of rank-0 and
remediation-reachable tuples. This finite-model characterization is a
declared abstraction of the imported baseline's two remediation
operators, used only by the exhaustive checkers (Section 7); Section 8's
empirics call the real operators themselves, through the pinned
`sarc-suite-one-pass` sibling, not this abstraction.

**Reachability-robustness (Proposition 0, corrected from v0.1; see
`NOVELTY.md`'s Amendment and `appendix-a-proofs.md`).** In this
artifact's own formal model, remediation-reachability is redundant:
`domain.rank0_reachable_tuples()` is the unconstrained full product of
all nine candidate properties' declared domains (7,776 tuples), which
already contains every tuple `remediation_reachable_tuples()` can
produce by swapping `order_value` alone, so `executable_reachable_
tuples()` (the union of the two) equals rank-0 exactly -- measured, not
asserted: `len(remediation_reachable_tuples(rank0, domains['order_
value']))` is 0. Concretely: P\*, the coverage list, and every witness
below are identical whether or not remediation-reachable tuples are
included, because there are none beyond rank-0. This is narrower than
v0.1's fence claimed (Section 1.1's correction): this formal model does
not instantiate a case where remediation changes what Definition 1
finds authority-bearing, though the *setting* remains genuinely
remediation-coupled at the empirical layer (Section 8, where two
different order_values -- pre- and post-remediation -- really are
computed per decision and the executed one is what every policy is
evaluated against). Whether a formal model *can* be built in which
remediation is not reachability-redundant, and whether P\* would then
differ, is exactly the question v0.2 (`prereg/v2-reachability-redesign.md`,
once committed) is designed to answer -- registered as a real, two-sided
question, not assumed to come out either way.

**v0.2 update: the redesign executed (CH-A5-CH-A7, tag `prereg-p5-v2`).**
The question above is answered. v0.2 adds one candidate property
(`min_order_quantity`, ten total), one declared cross-field rank-0
filter absent from v1 (`order_value >= min_order_quantity` always holds
at rank-0, `domain.rank0_reachable_tuples_v2()`), and two characterized
remediation mechanisms: downroute, grounded directly in
`composition._maybe_downroute`'s real budget-fitting calculation
(`feasible_qty = max(0, min(proposed_qty, max_qty_by_cost,
max_qty_by_carbon))`, W2 only, no minimum-order-quantity term anywhere
in it -- a real gap in the imported baseline's own code, not invented
for this redesign); and retry-delay (secondary), a declared
resubmission-at-day-200 operator. `domain.executable_reachable_
tuples_v2()` is their union with rank-0 (24,624
tuples: 15,552 rank-0, 3,888
new via downroute, 5,184 new via retry-delay).

- **CH-A5 (does the redesign make remediation reachability-relevant, in
  general?): reachability_relevant.** `min_order_quantity` participates
  in v2's P\* (9 of 10
  candidates participate; only `workflow` remains in coverage, unchanged
  from v1); the nine original properties' own participation/coverage
  split is byte-identical to v1's (`checkers/ch_a5_check.py`).
- **CH-A6 (do two independently implemented derivations of v2's P\*
  agree exactly, mirroring CH-A2): yes.**
  `checkers/participation_check_v2.py` (fingerprint-grouped search) and
  `checkers/pairtest_check_v2.py` (one-factor-at-a-time sweep, the same
  algorithm CH-A2 already runs independently of Definition 1's own
  search) agree exactly over the full 24,624-tuple
  v2 reachable set: no missed participants, no false participants.
- **CH-A7 (targeted ablation: does removing downroute specifically
  change P\* membership for `min_order_quantity`?): SUPPORTED.**
  `min_order_quantity` participates when downroute is included in the
  reachable-set construction (24,624 tuples)
  and does not when it is excluded (20,736
  tuples: rank-0 union retry-delay only) --
  `checkers/ch_a7_check.py` computes both P\*s directly rather than
  inferring the answer from CH-A5 alone, since Proposition 0-general's
  Corollary 2 (`appendix-a-proofs.md`) confirms neither downroute's nor
  retry-delay's characterized image is a subset of `rank0_reachable_
  tuples_v2()`, so which mechanism (if either) actually moves P\* was
  not decided in advance.

This is a real, machine-checked instantiation of v0.1's original fence
claim, not a rerun of v0.1's own (correctly negative) result: v0.1's
model is unaffected and its own measured redundancy stands (Proposition
0 above). **Re-derivation trigger.** Any edit to `prereg/loss-
model.yaml`'s `v2_losses` key, `prereg/pair-test-grid.yaml`'s `v2` key,
`domain.py`'s `*_v2` functions, or `losses.py`'s `load_loss_registry_v2`/
`downrouted_quantity_below_supplier_minimum` invalidates every
CH-A5/CH-A6/CH-A7 number above until `make formal` (which runs
`derive_v2` and all five v2 checkers) is re-run -- the same
inputs-hash-defines-freshness discipline `checkers/_provenance.py`
already states for v1, applied to v2's own generating inputs.

**v0.3 update: core versus reduct, corrected and machine-checked
(Proposition 1', Negative Proposition N, CH-A8-CH-A10, tag
`prereg-p5-v3`).** The Corrections section above summarizes why; this is
what was actually checked. `reduct.py` implements Definitions 4-6
directly: `sufficiency()` partitions a reachable set by projection onto
a property set and confirms (or refutes, with a concrete counterexample)
a uniform verdict within every partition cell; `exact_reducts()`
enumerates every subset of the candidate properties in increasing size
order with subset pruning (a superset of an already-confirmed reduct is
never re-tested), so every confirmed-sufficient set found this way is,
by construction, minimal.

- **Proposition 1' claim 1** (Definition 1 computes the core): recomputing
  the core two independent ways -- Definition 1's own witness search,
  and the intersection of every reduct `exact_reducts()` finds --
  True. Claim 2 (core subset of every reduct):
  True, checked against each reduct found
  individually.
- **CH-A8** (is the v2 core sufficient on the v2 executable-reachable
  set?): **SUPPORTED**, over
  24,624 reachable tuples
  (`checkers/sufficiency_check.py`).
- **CH-A10** (exact reduct enumeration on the v2 model, all
  `2^10 = 1,024`
  candidate subsets, 1,023
  actually tested after pruning): **1 reduct(s)**,
  minimum cardinality **9**, core is
  the unique reduct: **True**
  (`checkers/reduct_check.py`). Claim 3's antecedent (core sufficient)
  holds for this model per CH-A8, and its consequent (unique reduct)
  is confirmed directly, not inferred.
- **Negative Proposition N** (registered counterexample,
  `prereg/fixtures/negative-proposition-n-counterexample.json`):
  **SUPPORTED**, matching the fixture's own
  pre-committed expectation
  (True).
- **CH-A9** (constrained-reachability variant, `actor_role`/`resource_class`
  forced to co-vary): **NOT SUPPORTED** -- the constrained
  variant's own core (6 properties) is
  already sufficient; the declared pairing maps four roles onto three
  resource classes, so two roles share a resource class, leaving a
  residual case two `actor_role`-sensitive, `resource_class`-blind
  losses can still witness (`checkers/core_insufficiency_counterexample.py`).
  A real, explainable negative finding, not evidence against Negative
  Proposition N's general claim.

**Re-derivation trigger (v3).** Any edit to `reduct.py`,
`prereg/pair-test-grid.yaml`'s `v3` key, or `domain.py`'s
`*_ch_a9*`/`*_v3*` functions invalidates every Proposition 1'/CH-A8-CH-A10
number above until `make formal` (which now also runs
`checkers.sufficiency_check`, `checkers.reduct_check`, and
`checkers.core_insufficiency_counterexample`) is re-run.

## 6. The derivation procedure and the grant mechanism

`derive.py` wires the declared loss model (`losses.load_loss_registry`)
against the executable-reachable set (`domain.py`) through
`participation.compute_p_star`, which finds a witness for each candidate
property by grouping reachable tuples on every OTHER field and checking
for a verdict difference within each group -- an O(n) sweep, not O(n²).
The result, `out/checkers/derivation_output.json`
(`schemas/derivation_output.schema.json`):

- P\* / core (8 of 9
  candidates): actor_role, budget_remaining, consumed_grant_ids, day, frozen, grant_id, order_value, resource_class
- Coverage list (1): workflow
- Executable-reachable tuples enumerated: 7,776

`out/checkers/derivation_output.json`'s own field names
(`participating_properties`, `coverage_list`) are unchanged and
byte-frozen (v0.3's renaming, Corrections above, applies to v3's own new
outputs only); this section calls the same values by their corrected
name, core and redundant properties, per Definition 6. Every core
property carries a recorded witness pair, checked independently (not
re-asserted) by `checkers/participation_check.py` (Proposition 1',
`appendix-a-proofs.md`) -- Proposition 1's own original entry there is
preserved, narrowed, and superseded, not deleted.

**The syntactic-footprint bound (round-0 review, finding F1).** P\* is
always a subset of the syntactic footprint of the loss predicates --
the fields they read at all, listed exhaustively by inspecting
`losses.py`'s six predicate bodies: eight of the nine `StateTuple`
fields (every candidate except `workflow`, which no predicate reads),
plus the three `role_entitlement_ceiling`/`role_window`/`role_allowed_
classes` policy-table lookups the three role-dependent predicates
consult -- eleven syntactic reads in total. A field never read by any
predicate can never flip a verdict, so it is trivially excluded before
Definition 1 does any semantic work at all; `workflow`'s exclusion is
exactly this trivial case, confirmed, not just plausible, by direct
inspection of the source above. For *this* declared loss model, P\*
(eight properties) equals the syntactic footprint restricted to
`StateTuple` fields (also eight) exactly -- Definition 1 found no field
that is read but never actually determines a verdict once reachability
is accounted for, so semantic minimization did no further pruning
beyond the syntactic one in this instance. This is the honest shape of
the result: the derivation is a certified semantic minimization of the
syntactic footprint under reachability, not a discovery of unread
properties -- unread properties are excluded by inspection, not by
Definition 1's machinery -- and this declared loss model's own
one-property pruning ratio (`workflow` alone) is a fact about *this*
loss model's design, not a limitation of the method. `prereg/loss-
model.yaml`'s six losses were written broadly enough to exercise all
eight `StateTuple` fields directly; a loss model with a field read by
some predicate but never actually reachable-distinguishing would be
needed to see semantic minimization prune something syntactic
inspection alone would have kept -- exactly the kind of enrichment v0.2
(Section 5's Proposition 0 note) can also register alongside the
reachability redesign.

**Grant binding, positioned as engineering, not a novelty claim
(v0.3, Corrections above).** Directly motivated by finding A7 above,
`grant.GrantLedger` binds one consumable execution-grant id to the
content hash (sha256, canonical JSON) of one sealed post-remediation
action. Issuance and every consumption attempt -- admitted or rejected
-- append a new entry; nothing is mutated in place, mirroring the
imported baseline's own governed-buffer write-history design. The
single-use invariant is machine-checked exhaustively over 85 sequences
(`checkers/grant_check.py`, Proposition 3). The mechanism follows
established capability-system prior art -- Macaroons (Birgisson et al.,
2014) bind a bearer token to contextual caveats via a chained-HMAC
construction; UCAN and Biscuit both bind a token to a specific,
attenuated, independently verifiable scope of authority -- and this
paper claims no novelty for the binding primitive itself; its
contribution is the derivation (Definitions 1-6) that motivated
observing execution-specific binding as a real coverage boundary in the
first place, not the binding mechanism's own design.

## 7. Pair testing, formalized (CH-A2)

`checkers/pairtest_check.py` formalizes the eight-test method Section 4
credits, generalized from eight hand-picked cases to a full sweep of the
declared grid: for every reachable tuple as a baseline and every
candidate property, swap in every other declared domain value for that
property alone and check for a verdict change -- a one-factor-at-a-time
sweep, algorithmically independent of Definition 1's own
fingerprint-grouped search. Result: 7,776
tuples swept; missed participants: (none);
false participants: (none). **CH-A2:
SUPPORTED**.

**Registered blind spot**, in the same spirit as Section 4's quoted
framing: pair testing probes the representation -- `pair-test-grid.yaml`'s
declared finite domain values -- not the loss model. It cannot detect a
hazard whose true threshold falls strictly between two declared values,
or a property never represented in the grid at all. This is a structural
limit of the method, not a defect in this run; `checkers/pairtest_check.py`
emits the note in its own machine output, not only here.

## 8. Empirical section (CH-A1, CH-A3, CH-A4, and the overderivation ablation)

`experiments.py` runs the real imported decision stream (real UCI data,
real per-class defect injection, real `sarc_governance` evaluation of
the imported `specs/authority.yaml` for the baseline arm) through three
policies per decision -- baseline declared-only, derived-P\*, and an
over-inclusive ablation that adds one spurious rule (escalate whenever
`workflow == W2`, the one derived-non-participating candidate) -- plus a
grant-binding on/off ablation with an injected replay rate, across all
30 registered seeds (`prereg/seeds.json`) and both workflows.

**CH-A1** (derived coverage strictly exceeds the baseline). The
declared-only baseline missed 1515.7 (95% CI [1214.3, 1817.1], n=60) of
2800.6 (95% CI [2243.7, 3357.5], n=60) declared loss-violations across the
sweep. The derived-P\* policy's own admission decision is computed
directly from the same loss registry the ground truth is defined by, so
zero missed violations (`derived_missed`, True
on every seed x workflow cell) is a checked structural consequence of
that construction, not an independent empirical claim -- stated plainly,
not oversold; the genuine empirical content is the baseline comparison.
**CH-A1: SUPPORTED**.

**CH-A3** (grant binding eliminates replay admissions). Across the
sweep, 288.8 (95% CI [231.2, 346.5], n=60) replayed-presentation
probes were injected per cell on average. With grant binding on,
replay admissions were zero on every cell
(True). With grant binding off (a
policy that never consults ledger state), replay admissions averaged
288.8 (95% CI [231.2, 346.5], n=60) -- nonzero on at least one cell
(True), the positive control
confirming the hazard is real and reachable absent the mechanism, not
just theoretically stated. Escalation overhead is reported, not
registered (magnitude not pre-committed, per `prereg/hypotheses.md`):
288.8 (95% CI [231.2, 346.5], n=60) decisions per cell on average
needed a fresh grant-issuance round trip after a correctly-rejected
replay attempt before they could be admitted at all. **CH-A3:
SUPPORTED**.

**Overderivation ablation (spurious escalation cost).** The
over-inclusive policy's one extra rule spuriously escalated
380.4 (95% CI [279.1, 481.7], n=60) genuinely safe decisions
per cell on average -- the measured cost of defensively treating a
non-participating candidate as though it mattered, instead of deriving
the minimal set. This number is definitionally tied to how large a
share of decisions carry the one excluded candidate's non-default value
(`workflow == "W2"`) in this declared model and this simulation's own
W1/W2 mix; it is reported as exactly what it is -- the cost of not
deriving minimality on this declared model -- not generalized beyond it.

**CH-A4** (robustness). CH-A1 and CH-A3's conclusions (not magnitudes)
held across all 30 seeds and W1, W2
workflows (60 seed x workflow cells); CH-A2 is
formal-track, evaluated once, not per seed. **CH-A4: SUPPORTED**.

### Claims and evidence

| Claim | Evidence | PROOF-STATUS / decision rule |
|---|---|---|
| P\* is the core, exhaustively (Definition 1's own claim; NOT general sufficiency -- Proposition 1', Corrections above) | `checkers/participation_check.py`, 7,776 tuples | checked-scope-only |
| CH-A2 (pair testing recovers P\* exactly) | `checkers/pairtest_check.py` | machine-checked |
| Grant mechanism is single-use | `checkers/grant_check.py`, 85 sequences | machine-checked |
| CH-A1 (baseline misses what derived-P\* does not) | `sweep.py` / `out/results/sweep_summary.json` | SUPPORTED, decision rule per `prereg/hypotheses.md` |
| CH-A3 (grant binding eliminates replay admissions) | `sweep.py` / `out/results/sweep_summary.json` | SUPPORTED, decision rule per `prereg/hypotheses.md` |
| CH-A4 (robustness) | `sweep.py` / `out/results/sweep_summary.json` | SUPPORTED |
| CH-A5 (v0.2 redesign makes remediation reachability-relevant) | `checkers/ch_a5_check.py`, 24,624 tuples | machine-checked: reachability_relevant |
| CH-A6 (v0.2: two independent derivations of P\* agree exactly) | `checkers/participation_check_v2.py` + `checkers/pairtest_check_v2.py` | machine-checked |
| CH-A7 (targeted ablation: downroute is derivation-relevant for `min_order_quantity`) | `checkers/ch_a7_check.py`, 24,624 vs. 20,736 tuples | machine-checked: SUPPORTED |
| Proposition 1' claims 1-2 (Definition 1 computes the core; core subset of every reduct) | `checkers/reduct_check.py` | machine-checked |
| CH-A8 (v2 core is sufficient on the v2 reachable set) | `checkers/sufficiency_check.py`, 24,624 tuples | machine-checked: SUPPORTED |
| CH-A9 (real co-variation breaks core sufficiency in a constrained procurement variant) | `checkers/core_insufficiency_counterexample.py` | machine-checked: NOT SUPPORTED |
| CH-A10 (exact reduct enumeration on the v2 model) | `checkers/reduct_check.py`, 1,023 of 1,024 subsets | machine-checked: 1 reduct(s), min. cardinality 9 |
| Negative Proposition N (the core need not be sufficient) | `checkers/core_insufficiency_counterexample.py` | machine-checked: SUPPORTED |
| v0.4 isolation hypothesis (isolating the three experiment arms' state changes a CH-A1/CH-A3/CH-A4 measured quantity) | `checkers/isolation_delta_check.py`, `test_experiments.py`'s contamination regression test | machine-checked: NOT SUPPORTED |

## 9. Threats to validity (written against this paper's own results)

- **v0.1 through v0.3's Section 8 experiment shared one budget trajectory
  and one grant ledger across all three policy arms, found by this
  paper's own direct code inspection, not an external review.** Fixed in
  v0.4 (Corrections above; `prereg/v3.1-isolated-arms.md`); the
  re-measurement is byte-identical to v0.3's frozen result and a direct
  diagnostic confirms the corrupted field never actually determined a
  verdict in this dataset, but this is a property of this declared
  parameter set, not a proof that isolation never matters -- a tighter
  budget multiplier or a different declared loss model could still see
  it bind, and the isolated design (and its own regression test) is now
  in place either way.
- **v0.1 and v0.2's Proposition 1 overclaimed a general sufficiency
  guarantee Definition 1's method does not provide, and an external
  review caught it, not this paper's own drafting or its formal
  double-run.** P\* is the core (individually indispensable properties),
  not in general a reduct (minimal jointly sufficient set) -- Negative
  Proposition N exhibits a reachable set where the core is empty and
  insufficient. This artifact's own v1/v2 core happens to be sufficient
  and the unique reduct (CH-A8, CH-A10), but that is now a per-instance
  certified fact, not a structural guarantee of the method; a reader who
  took v0.1/v0.2's "sound and minimal" wording as the latter has been
  misled by a claim this paper no longer makes (Corrections above,
  `appendix-a-proofs.md`'s Proposition 1 entry and its correction).
- **CH-A9's constrained variant did not, in the end, break sufficiency,
  and this paper reports that rather than tuning the registration to
  get a different answer.** The declared `actor_role`/`resource_class`
  co-variation is real but not total (four roles onto three resource
  classes, pigeonhole), so a residual case let two other losses witness
  `actor_role` regardless. This bounds what CH-A9 demonstrates: it shows
  this *particular* declared variant does not break sufficiency for this
  loss registry, not that no real co-variation could; Negative
  Proposition N's own (abstract, total) counterexample is what
  establishes the general claim.
- **v0.1's fence overclaimed relative to its own model, and a round-0
  review caught it (finding F0), not this paper's own drafting pass.**
  "Remediation changes the reachable set" was asserted in v0.1's fence
  and abstract without being instantiated: this artifact's own rank-0
  reachable set is already the unconstrained full product over every
  candidate property's declared domain, so it already contains
  everything remediation-reachability could add, and the two coincide
  exactly (7,776 tuples either way, measured directly). v0.1.2 corrects
  the claim (Section 5's Proposition 0) rather than leaving it standing
  with a footnote; this item exists so a reader of v0.1 specifically,
  or of a summary that quoted the original fence, is not misled by a
  claim this paper no longer makes. A follow-up formal model in which
  remediation genuinely is reachability-relevant is scoped, not yet
  built (v0.2, see `prereg/v2-reachability-redesign.md` once committed).
- **P\* equals the syntactic footprint exactly for this loss model, and
  a reader could reasonably call that a tautology if the paper did not
  say so itself (finding F1).** Every property in P\* is a property some
  predicate reads in source; Definition 1's exhaustive check confirmed
  each one also flips a verdict on some reachable pair, but for *this*
  declared model it did not additionally prune anything syntactic
  inspection would have missed. The derivation is real machinery doing
  real, independently-checked work (Propositions 1-2), but its
  demonstrated value in this instance is confirming a footprint a human
  could have read off `losses.py` directly, not finding something
  hidden from syntactic inspection. A loss model engineered so some
  predicate reads a field that reachability nonetheless makes
  non-participating would be needed to show the semantic step earning
  its keep beyond the syntactic one; this artifact's six losses do not
  happen to contain such a field.
- **CH-A1's derived-zero result is circular by construction, and we say
  so rather than let it read as a surprise finding.** The ground truth
  and the derived policy's admission rule share one registry
  (`losses.m_verdict`). The only non-tautological empirical content in
  CH-A1 is the baseline comparison; a reader who takes "100% detection"
  as an independent empirical triumph has misread the claim, and this
  section exists so they cannot reasonably do so.
- **The candidate-property representation is a modeling choice, and a
  different one gives a different P\*.** `ADR-002-participation-
  tuple-design.md` documents a design that exposed per-role policy as
  separate fields and derived actor_role itself as non-participating --
  mathematically correct for that representation, practically
  unimplementable. The corrected design avoids that specific failure by
  construction, not by a general proof; the general claim ("a candidate
  coupled to an always-held-fixed field can never be derived as
  participating") is tagged `pending-human-review` in
  `appendix-a-proofs.md`, not machine-checked, because we have not swept
  an exhaustive space of coupling configurations to confirm no other
  failure mode of the same shape survives in the current nine-field
  design.
- **The role/entitlement/window/class-set declared values are this
  paper's own design choices, not measurements.** `agent-delegate`'s
  800-value ceiling, [100, 180] window, and single-class entitlement
  were chosen to make L1-L3 each independently exercisable against the
  role structure (see `prereg/loss-model.yaml`'s comments) -- they are
  not calibrated from any real organizational policy, unlike the
  imported baseline's own scenario budgets, which paper 4 calibrates
  from real order-value/cost/carbon distributions. A different set of
  declared values would change CH-A1's baseline-missed count and the
  overderivation ablation's spurious-escalation count in magnitude,
  though not CH-A2's exact-recovery claim or Proposition 1's structural
  guarantee.
- **The overderivation ablation's one added rule (escalate on
  `workflow == W2`) targets exactly the one property Phase 2 already
  found excluded.** This is not circular -- the point of the ablation is
  precisely to cost out treating a known-irrelevant candidate as
  relevant -- but it does mean the reported spurious-escalation count is
  a direct function of how large the W2 population is in this
  simulation's own daily/weekly decision mix, not a general estimate of
  "the cost of overderivation" applicable beyond this declared model and
  this simulation.
- **The budget-depletion loss (`spend_against_depleted_delegated_budget`)
  uses a period budget calibrated from this run's own median per-period
  demand (`experiments.calibrate_period_budget`), deliberately tuned to
  bind on above-median periods.** This is a declared modeling choice
  (documented in the function's own docstring), not a measurement of any
  real resource-gate policy; a materially looser or tighter multiplier
  than the declared 1.15x would shift true_violations and, through it,
  every downstream count in this section, without changing which
  properties Phase 2 derives as participating (a fact about the loss
  predicates' structure, not about how often they fire).
- **The pair-test checker and Definition 1's own checker share the same
  declared finite domain (`pair-test-grid.yaml`).** CH-A2's exact-
  recovery claim demonstrates the two ALGORITHMS agree, not that either
  is complete against the true (much larger, partly continuous) action
  space -- Section 7's registered blind spot applies to both, not only
  to the one named "pair testing."

## 10. Limitations

- **Deriving the loss model itself is out of scope.** This paper starts
  from `prereg/loss-model.yaml` as given and derives the **core**
  observation set (Definition 6) a gate needs to check it; it does not
  derive, verify, or validate that these losses are the right or
  complete set of things an organization should declare. A declared loss
  model with a missing loss still produces a P\* that is the core *for
  the declared model* (Definition 1's witness search is sound and
  minimal by construction), silently uninformative about the missing
  one -- and sufficiency is never assumed for it either (Definition 4;
  Negative Proposition N).
- **Multi-agent settings, the evidence-integrity layer, and any
  runtime LLM involvement are out of scope** (task brief). The grant
  mechanism assumes a single sealing/execution path per decision, not
  concurrent or adversarial multi-agent claims on the same grant.
- **The finite enumerated model is a deliberate abstraction for
  exhaustive checking**, not the full (in principle continuous)
  action space the real simulation draws order values, days, and
  budgets from. Section 7's blind spot is the general statement of what
  this abstraction cannot see.
- **This is a mechanism demonstration on open payload data with a
  declared synthetic metadata layer** (role tiers, resource-class
  assignment, temporal windows) layered on the real UCI Online Retail
  data, following the imported baseline's own precedent and disclosure
  style (`sarc-suite-one-pass README.md`'s Artifact scope section) --
  not a live deployment, not a prevalence study, not the proprietary
  Suite.

## Coverage-honesty banner

**6 declared losses, 9
candidate properties, one derived coverage list at v1 (`prereg-p5-v1`);
7 declared losses, 10
candidate properties at v2 (`prereg-p5-v2`), core cardinality
9 and certified the unique reduct for
that registered model (CH-A8, CH-A10; Definitions 4-6) -- neither count
generalizes to an arbitrary declared loss model. `workflow` is derived
non-participating (v1) / redundant (v2) for these declared loss models
and is reported as such, not omitted. The overderivation ablation's
spurious-escalation count is specific to this simulation's own workflow
mix and declared parameter values, not a general estimate. CH-A1's
zero-miss result for the derived policy is a checked structural
consequence of sharing one registry with the ground truth, disclosed as
such in Section 9, not an independent empirical claim.**

## 11. Conclusion

Given a declared loss model, this paper derives -- not declares -- the
**core** attribute set (Definition 6) a pre-action authority gate's
individually indispensable observations must include, exhaustively
machine-checks that computation two independent ways, and independently
recovers it via a formalized version of the method an outside
replication used by hand. Correcting v0.1/v0.2's own overclaim
(Corrections above), the core is not in general sufficient to determine
every verdict -- Negative Proposition N exhibits a reachable set where
it is not -- but for this artifact's own registered v2 model, it is
certified sufficient and the unique reduct, per instance, not assumed
(CH-A8, CH-A10). The declared-only baseline this paper compares against
is not a straw man: it is the actual imported artifact's own shipped
policy. What the derivation adds is not more caution, but the right
amount, honestly accounted for in both directions -- the redundant-
attribute list names what a gate need not check, and the overderivation
ablation prices out what it costs to guess wrong about that in the
direction of "everything, just in case." A consumable execution-grant
mechanism closes the specific coverage boundary (execution-specific
binding) that replication's finding A7 named, with a machine-checked
single-use guarantee -- engineering informed by established
capability-system prior art (Macaroons, UCAN, Biscuit), not a novelty
claim in its own right.

**Acknowledgements.** Drafting, engineering, formal derivation, and
citation verification were AI-assisted (Claude); the author is solely
responsible for all claims.

## References

See `verified-citations.json` for the complete fetch-verified record
(url, title, first author, year, and how each was verified) of every
source cited above, and `sarc-suite-one-pass/verified-citations.json`
(pinned sibling, commit `782261e`) for the imported baseline's own
citations (the SARC, Green SARC, and sarc-dq engine papers; the UCI
Online Retail dataset; and the composition-theory literature paper 4
cites), referenced here by pointer rather than re-verified, since this
paper edits none of that artifact.

## Human checklist

- [ ] Novelty fence reviewed by the author against `NOVELTY.md`'s
      sources.
- [ ] Corrections section (v0.3) reviewed by the author against
      `prereg/v3-core-reduct-correction.md` and the external review it
      credits.
- [ ] Corrections section (v0.4) reviewed by the author against
      `prereg/v3.1-isolated-arms.md`.
- [ ] `pending-human-review` tags counted and individually assessed:
      1 (`appendix-a-proofs.md`'s coupling-generalization remark).
- [ ] Push and any review chain are the author's decision, not
      automated by this pipeline.

**Not submission-ready. Not independently reviewed. Not claimed
complete against any loss model other than the one declared in
`prereg/loss-model.yaml`.**
