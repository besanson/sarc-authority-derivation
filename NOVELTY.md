# Novelty

Phase R output (task brief R2). One paragraph per neighbouring literature
cluster: what it established, and what this paper adds. Every source cited
below is fetch-verified in `verified-citations.json`.

## STPA and its descendants (STPA Handbook; STPA-Sec; PHASE; Mylius 2025;
## DeepSTPA)

Leveson and Thomas's STPA Handbook (2018) establishes System-Theoretic
Process Analysis: a structured but human-driven analyst process in which
an engineer enumerates losses and hazards, models a system as a hierarchy
of controllers, and writes safety constraints and unsafe-control-action
requirements by hand, checked by expert review. Young and Leveson's
STPA-Sec (CACM 2014) carries the same analyst process into security.
Rismani, Dobbe, and Moon's PHASE (2024) and Mylius (2025) carry it into AI
governance and frontier-AI hazard analysis respectively; Qi et al.'s
DeepSTPA (2023) extends STPA's control-loop model to the stages of the ML
development lifecycle. In every one of these five sources, the output is
a set of natural-language or semi-structured constraints produced and
reviewed by a person; none of them derive, from a declared loss model, a
machine-checked *minimal* property set for a runtime authorization gate,
and none formalize soundness or minimality as machine-checkable claims
over an enumerated model. This paper's derivation procedure is inspired
by STPA's loss-to-constraint direction of travel but replaces the analyst
step with a deterministic, exhaustively-verified derivation.

## ABAC policy mining (Xu and Stoller 2014-2015; Nobi et al. 2022 survey)

Xu and Stoller (TDSC 2015) establish the ABAC policy-mining problem:
given an *existing* lower-level policy (an ACL or RBAC policy) plus
attribute data, algorithmically reconstruct which attributes already
participate in the deployed access decisions. Nobi et al.'s 2022
taxonomy and survey catalogue the many machine-learning extensions of
that same reconstruction problem published since. Both directions of
work start from grants that already exist and infer structure backward
from them. This paper runs the derivation in the opposite direction and
from a different starting point: not from existing grants, but from a
declared loss model, forward to the minimal property set a *new* gate
must observe -- with a machine-checked soundness and minimality
guarantee that mining, which has no ground-truth "correct" policy to
verify against, cannot by construction provide.

## Policy-language completeness (PTaCL; SACMAT 2016 canonical completeness)

Crampton and Morisset's PTaCL (POST 2012) and Crampton and Williams's
canonical-completeness result (SACMAT 2016) establish what a policy
*combination* language can express once the participating attributes and
base decisions are already fixed -- completeness is a property of the
combinator algebra over a given attribute set. Neither work asks which
attributes must be observed by the gate in the first place; both assume
that question already answered. This paper contributes exactly the
question PTaCL and the SACMAT 2016 result assume away: which properties
a gate must observe at all, derived from a declared loss model, before
any question of how to combine decisions over them arises.

## Non-interference (Goguen and Meseguer 1982)

Goguen and Meseguer define non-interference as a semantic criterion for
whether one user's or domain's actions can affect what another observes
-- a *check* of whether a dependence exists between two fixed parties in
a given system. It is not a procedure for deriving, from a declared loss
model, the complete set of properties a decision must consult, and it
does not produce a minimality guarantee over that set. This paper's
Definition 1 (participation) borrows non-interference's underlying
comparison -- does changing X change the observable verdict? -- but
turns it into a derivation swept over every candidate property against
every loss predicate, with soundness and minimality verified
exhaustively over the enumerated model, rather than a single
dependence check between two designated parties.

## Counterfactual fairness (Kusner et al. 2017)

Kusner, Loftus, Russell, and Silva define counterfactual fairness as
invariance of a decision to a counterfactual change in one designated
protected attribute, with the causal graph over the remaining variables
held fixed. This is structurally the same comparison this paper's
Definition 1 uses -- does changing one property change the verdict? --
but Kusner et al. apply it to evaluate a single pre-chosen sensitive
attribute against a fairness objective, once. This paper generalizes the
comparison to sweep every candidate property in the
(action, context, evidence, control-state) space against a declared loss
model, and adds an exhaustive, machine-checked minimality result -- that
the recovered set is both sufficient and irreducible -- which the
counterfactual-fairness literature neither claims nor checks.

## The fence

STPA derives safety constraints from declared losses as an analyst
methodology; ABAC mining reconstructs policies from existing grants;
interference-style criteria detect dependence but do not derive. This
paper contributes a formal participation criterion over the
executable-reachable action set, a machine-checkable derivation from a
declared loss model to the minimal property set a pre-action authority
gate must observe, with the excluded residue emitted as a derived
coverage list, in the remediation-coupled setting sarc-suite-one-pass
establishes.

## Amendment (v0.1.2, round-0 adjudicator review, finding F0)

The fence above originally ended "...in a setting where remediation
changes the reachable set," per the task brief's own verbatim-start
text. Verification during round-0 review found this specific clause
false of this artifact's own formal model as built:
`domain.rank0_reachable_tuples()` is the unconstrained full product of
all nine candidate properties' declared domains (7,776 tuples), which
already contains every (other-eight-fields, any-order-value)
combination `remediation_reachable_tuples()` could ever produce by
swapping order_value alone -- so `executable_reachable_tuples()` (the
union of the two) equals rank-0 exactly; remediation adds zero new
tuples (verified directly:
`len(remediation_reachable_tuples(rank0, domains['order_value']))` is
0, not a sample). The setting genuinely is remediation-coupled --
Phase 3's real simulation computes two different order_values (pre-
and post-remediation) per decision and every policy is evaluated on the
executed, post-remediation value -- but that fact lives in the
empirical layer (Section 8 of the paper), not in this artifact's own
formal reachable-set construction, as built. The fence above is
corrected to claim only what is instantiated by Definition 1's actual
finite model. A redesigned formal model in which remediation is not
reachability-redundant -- so the fence's original claim can actually be
tested rather than merely asserted -- is scoped as v0.2
(`prereg/v2-reachability-redesign.md`), gated behind its own prereg tag
before any new experiment code, exactly as this project's own
registration discipline requires. This paragraph is the honest record
the task brief's own rigor standard asks for: printed, not smoothed
over, and not retroactively hidden by rewriting the fence's history --
see the original wording preserved at the `prereg-p5-v1` tag.

## Second amendment (v0.2, tag `prereg-p5-v2`, CH-A5/CH-A6/CH-A7 outcomes)

The amendment above registered a real, two-sided open question: whether
a redesigned formal model could make remediation reachability-relevant,
so the fence's original claim could actually be tested rather than
merely asserted. `prereg/v2-reachability-redesign.md` registered the
redesign -- a new candidate property (`min_order_quantity`), one
declared cross-field rank-0 filter (`order_value >= min_order_quantity`
at rank-0), and two characterized remediation mechanisms (downroute,
grounded in `composition._maybe_downroute`'s real budget-fitting
calculation; retry-delay, secondary) -- before any v2 code existed,
per this project's own registration discipline. That question is now
answered, machine-checked, not asserted:

- **CH-A5 (does the redesign make remediation reachability-relevant, in
  general?): reachability_relevant.** `min_order_quantity` participates
  in v2's P\* (`checkers/ch_a5_check.py`,
  `out/checkers/ch_a5_check.json`); the nine original properties'
  participation/coverage split is unchanged from v1
  (`nine_original_properties_unchanged_from_v1: true`). Unlike v0.1's
  model (Proposition 0, redundant by construction), v2's redesigned
  reachable set genuinely does contain tuples remediation reaches that
  rank-0 alone would not -- the fence's original claim is now
  instantiated, for this specific redesigned model and this specific
  property, not merely asserted.
- **CH-A6 (do two independently implemented derivations of v2's P\*
  agree exactly?): yes.** `checkers/participation_check_v2.py`
  (fingerprint-grouped search, `sound_and_minimal: true`) and
  `checkers/pairtest_check_v2.py` (one-factor-at-a-time sweep,
  `ch_a6_exact_recovery: true`) agree exactly over the same
  24,624-tuple v2 executable-reachable set: no missed participants, no
  false participants.
- **CH-A7 (does removing downroute from the reachable-set construction
  change P\* membership for `min_order_quantity`, specifically?):
  SUPPORTED.** `checkers/ch_a7_check.py`
  (`out/checkers/ch_a7_check.json`): `min_order_quantity` participates
  when downroute is included (24,624-tuple reachable set) and does not
  when downroute is excluded (20,736-tuple reachable set, rank-0 union
  retry-delay only) -- downroute demonstrated derivation-relevant for
  exactly the one property it was designed to make participate, not
  merely designed to in prose.

Registered two-sided, and the outcome that in fact obtained is the one
that vindicates the redesign; recorded here either way, per this
project's own discipline for a registered hypothesis, and not a
foregone conclusion at registration time -- CH-A7's decision rule was
satisfiable in either direction, and Proposition 0-general
(`appendix-a-proofs.md`) separately confirms, rather than assumes, that
neither of v2's two mechanisms was automatically guaranteed to matter
merely by being included (Corollary 2: neither downroute's nor
retry-delay's characterized image is a subset of `rank0_reachable_
tuples_v2()`, so which one(s) actually move P\* was still an open,
checkable question CH-A5/CH-A7 had to decide, not a restatement of
Corollary 2 itself). v0.1's results (Proposition 0, the original
7,776-tuple model) stay frozen and cited as the first iteration, per
`prereg/v2-reachability-redesign.md`'s own registration discipline;
nothing about v0.1's own model or its own measured redundancy is
retroactively edited to match v2's outcome.

## Third amendment (v0.3, tag `prereg-p5-v3`, core-versus-reduct correction)

The fence and Definition 1 above describe a *participation* criterion --
the amendments so far corrected what it found *reachable*, not what the
criterion itself *computes*. A commissioned external, AI-assisted
research review (`review-secondary/external-research-review-2026-09-06.pdf`,
sha256 `b205faf65fe84d773260d1ed514b20f5b04e420380d3136c23bff1cde4506b0b`)
identified that v0.1/v0.2's Proposition 1 mischaracterized Definition
1's output: P\* is the **core** (in decision-reduct / rough-set
terminology, Pawlak 1982; Skowron and Rauszer 1992 -- individually
indispensable properties, each with its own singleton-perturbation
witness), not in general a **reduct** (a minimal set that is *jointly
sufficient* to determine every verdict). Core is always a subset of
every reduct, but need not itself be sufficient. Per this project's own
discipline, the review's finding was not applied directly: it was
adjudicated against this artifact's own definitions, and the
counterexample demonstrating the failure was re-derived from first
principles, not copied from the review's prose
(`prereg/v3-core-reduct-correction.md` records the adjudication).

The registered outcome, machine-checked, not assumed:

- **Negative Proposition N** (the core need not be sufficient, in
  general): **SUPPORTED** -- the registered two-state counterexample
  (`prereg/fixtures/negative-proposition-n-counterexample.json`: reachable
  set `{(x=0,y=0),(x=1,y=1)}`, verdict `M(x,y)=x`) has an empty, trivially
  insufficient core, with `{x}` and `{y}` each an independent singleton
  reduct -- matching the fixture's own pre-committed expectation exactly
  (`checkers/core_insufficiency_counterexample.py`).
- **CH-A8** (is the v2 core sufficient on the v2 executable-reachable
  set?): **SUPPORTED** (`checkers/sufficiency_check.py`) -- a real
  sufficiency certificate, not an assumption, over the full 24,624-tuple
  v2 reachable set.
- **CH-A10** (exact reduct enumeration on the v2 model, all 1,024
  candidate subsets, 1,023 actually tested after subset pruning): the
  nine-property core is the **unique reduct**, of **minimum cardinality
  nine** (`checkers/reduct_check.py`) -- confirmed by direct enumeration,
  not inferred from CH-A8 alone.
- **CH-A9** (does a real, declared co-variation between `actor_role` and
  `resource_class` break core sufficiency in a constrained variant of
  this artifact's own procurement model?): **NOT SUPPORTED** -- the
  declared pairing maps four roles onto three resource classes
  (pigeonhole), so two roles share a resource class, leaving a residual
  case two other losses can still witness `actor_role` through directly.
  A real, explainable negative finding
  (`checkers/core_insufficiency_counterexample.py`), not evidence
  against Negative Proposition N's general (abstract, total) claim, and
  not smoothed over or re-tuned to chase a different outcome.

Registered two-sided throughout (Proposition 1' claim 3's antecedent --
core sufficiency -- and CH-A9's outcome were both open questions at
registration time, decided by the checkers, not assumed). v0.1's and
v0.2's own committed results stay frozen and cited as prior iterations;
nothing about them is retroactively edited to match v0.3's correction.
Proposition 1 itself is not deleted from `appendix-a-proofs.md`: its
original wording is preserved as an honest record, with its PROOF-STATUS
narrowed to `checked-scope-only` and a correction attached directly to
it, the same principle this amendment itself follows.

## Fourth amendment (v0.4, tag `prereg-p5-v3.1`, isolated per-arm experiment state)

The three amendments above all concern the formal/derivation side
(participation, reachability, core-vs-reduct). This one concerns Section
8's experiment: direct inspection of `experiments.py` (v0.1 through v0.3,
unchanged by any of those revisions) found that the baseline, derived,
and over-inclusive policy arms were evaluated inside one decision loop
against one shared `budget_remaining` float and one shared grant ledger
-- a real threat to the experiment's internal validity, found by this
paper's own code inspection, not an external review this time.
Registered (`prereg/v3.1-isolated-arms.md`) before any fix was written,
two-sided: isolating the three arms' state may or may not change any
CH-A1/CH-A3/CH-A4 measured quantity.

The registered outcome, machine-checked, not assumed:

- **v0.4 isolation hypothesis**: **NOT SUPPORTED** -- all 30 registered
  seeds x 2 workflows re-run under `experiments.py`'s new isolated
  `ArmState` design produce CH-A1/CH-A3/CH-A4 means, 95% CIs, and
  booleans byte-identical to v0.3's frozen (shared-state) result
  (`checkers/isolation_delta_check.py`). Not left unexplained: a direct,
  exhaustive diagnostic over the full 349,020-decision sweep confirms
  `spend_against_depleted_delegated_budget` -- the one loss predicate
  reading the one field the shared-state bug could have corrupted --
  fires zero times in any of the 60 (seed, workflow) cells, so the bug,
  while real, was never load-bearing for this declared parameter set.

The isolation fix (`ArmState`, `process_decision`, and
`test_experiments.py`'s new contamination regression test) is kept
regardless of this null result: it is the structurally correct
experimental design independent of today's numbers, and now guards
against a future declared parameter set where budget genuinely binds
tightly enough to matter. v0.1/v0.2/v0.3's own committed results stay
frozen and cited as prior iterations; nothing about them is
retroactively edited to match this correction.

## Kill-criteria check (task brief R3)

Searched explicitly, across all five literature clusters above, for
prior work that derives a runtime authorization property set from a
loss or hazard model *with machine-checked minimality*. Found: none.
STPA and its descendants derive constraints as an analyst methodology,
not a machine-checked derivation, and do not claim or check minimality.
ABAC mining reconstructs from existing grants, not from a declared loss
model, and has no minimality claim (or ground truth to check one
against). PTaCL/SACMAT completeness is a property of a combinator
algebra over an already-fixed attribute set, not a derivation of that
set. Non-interference and counterfactual fairness are both single
dependence/invariance *checks*, not derivations, and carry no
minimality result. Kill criteria not triggered. Proceeding to Phase 0.
