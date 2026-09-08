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

## Fifth amendment (v4, tag `prereg-p5-v4`, core-versus-reduct on an independently-built domain)

The first four amendments all concern this artifact's own single retail-
procurement domain. This one asks whether core-versus-reduct
(Definitions 4-6) shows up at all on a domain built independently, from
a different application area, with loss predicates transcribed from
published security/access-control sources (RBAC96, NIST SP 800-53,
CWE-798, the CSA Cloud Controls Matrix, MITRE ATT&CK) rather than
authored for this project -- a software-and-cloud execution-agent
domain: ten candidate observations, six loss predicates, registered
`prereg/v4-realistic-domain.md` before any code existed.

The registered outcome, machine-checked, not assumed:

- **CH-B1** (does this independently-built domain's core fail to be
  sufficient, or does more than one reduct exist?): **SUPPORTED**
  (`checkers/ch_b1_check.py`) -- over the domain's 15,120-tuple
  executable-reachable set, the 6-property core (`approval_token`,
  `data_classification`, `delegated_role`, `operation`, `repository`,
  `resource_owner`) is **not sufficient**: a concrete counterexample pair
  agrees on all six core properties (same actor, role, repository,
  tenant, operation `deploy`, `approval_token` absent) yet differs in
  verdict, because they differ in `branch`/`environment` -- and exactly
  **two** reducts exist, both of cardinality seven, one adding `branch`
  to the core and the other adding `environment`.

The mechanism is exactly Negative Proposition N's abstract shape (an
empty-or-partial core with multiple singleton-or-larger reducts),
occurring here for a concrete, explainable reason instead of a toy
fixture: the prereg's own "production branch implies production
environment" reachability rule declares `branch` and `environment` as a
one-to-one pairing, so neither ever has an *individual* singleton-
perturbation witness holding the other fixed (Definition 1's own
criterion) even though `production_deployment_without_approval` reads
`environment` directly -- each is redundant given the other, so the core
excludes both, and either one alone (not neither) is needed to restore
sufficiency. `actor_identity` and `deployment_window` are also redundant
(no predicate above reads either), a different, unsurprising kind of
non-participation from `branch`/`environment`'s co-variation-driven one
-- both kinds are named separately in the checker's own output, not
conflated.

This is independent evidence that the procurement domain's own core-
happens-to-be-sufficient result (CH-A8, CH-A10) is a fact about that
domain's particular structure, not a general property core-versus-
reduct analysis tends to find: a second, independently-built domain
shows the opposite, for a real, declared, explainable reason. Neither
result generalizes to a domain not yet built; `reduct.py`'s own machinery
is unmodified by this milestone.

## Sixth amendment (v5, tag `prereg-p5-v5`, synthesis scaling and cost-aware results)

The first five amendments concern what the derivation computes (Definition
1's participation criterion, reachability, core-versus-reduct). This one
concerns whether `discernibility.py`/`synthesis.py`'s SAT/MaxSAT contract
synthesis (Milestone D1/D2) actually scales past exhaustive enumeration,
and whether minimum-cardinality and minimum-cost synthesis are genuinely
different capabilities on any domain this artifact has built -- two
purpose-built benchmarks (`benchmarks.py`), both hand-derived and
brute-force-verified before registration, `prereg/v5-synthesis.md`.

The registered outcomes, machine-checked, not assumed:

- **Experiment 1 (planted-reduct scaling)**: **`exact` holds at every
  registered `n`** (10, 30, 50, 100) -- `find_minimum_cardinality_
  contract` returns exactly the five planted signal properties every
  time, cross-checked against `reduct.exact_reducts()`'s independent,
  from-first-principles answer at `n = 10` (the only size where 2^10
  exhaustion is affordable). Wall time stays sub-millisecond at every
  `n` (0.0005s at `n=10` down to 0.0007s at `n=100`, no distinguishable
  growth trend at this scale) and measured peak memory delta is 0 at
  every `n` -- both descriptive, not pass/fail, per the prereg's own
  registration. Mechanism, not just the number: the reachable set stays
  fixed at `k + 1 = 6` tuples regardless of `n` by construction, and the
  `n - 5` noise properties never appear in any discernibility-family
  clause, so they cost `synthesis.py` nothing beyond one additional SAT
  variable each -- exactly why `n = 100` stays cheap.
- **Experiment 2 (cost-aware synthesis)**: **SUPPORTED** -- on the one
  purpose-built domain with a genuine declared cost asymmetry
  (`xor_bijection`: `cost(a) = 4.0` vs. `cost(b1) = cost(b2) = 0.5`),
  `find_minimum_cardinality_contract` and `find_minimum_cost_contract`
  disagree exactly as hand-derived: `{a}` (cardinality 1, cost 4.00)
  vs. `{b1, b2}` (cardinality 2, cost 1.00), a cost delta of 3.00. This
  artifact's own three real domains (v1, v2, v4) show **no** divergence
  (`contracts_differ: false`, `cost_delta: 0.00` on each) -- reported
  honestly as a fact about those domains' structure, not a shortfall of
  the experiment: v1 and v2 each have a *unique* reduct (nothing else
  sufficient to prefer on any objective), v4's two reducts are both
  cardinality seven, and none of the three has a declared per-property
  cost model of its own, so `_real_domain_costs` assigns every property
  the identical floor cost -- under uniform cost, minimum-cardinality
  and minimum-cost trivially coincide by construction. The registered
  decision rule needed only one of the four domains to diverge; it was
  always going to be the purpose-built one, not the other three, and
  that is exactly what the hand-derivation before registration expected.
- **`contract_change_delta` demonstration** (not a registered pass/fail
  experiment, D5's own worked illustration): on a small model where a
  new transition genuinely collides with an existing tuple under the
  base contract's own projection, `was_still_sufficient: false`, the
  incremental update (`{x} -> {x, z}`, `x` pinned throughout) is
  independently confirmed sufficient, and matches the free-choice
  `full_recomputation_contract` exactly in this illustration
  (`full_recomputation_cardinality_gap: 0`) -- not a general guarantee:
  `test_synthesis.py`'s own direct unit tests separately construct a
  case (a deliberately non-minimal but still-sufficient `base_contract`)
  where the gap is genuinely nonzero, the honest "price of
  incrementality" the function's own docstring registers rather than
  hides.

Neither experiment required retuning `discernibility.py`/`synthesis.py`
(D1/D2, unmodified by this milestone) to reach these outcomes; both
constructions are exactly what `prereg/v5-synthesis.md` registered before
`benchmarks.py` existed. v0.1-v4's own results stay frozen and cited as
prior iterations; nothing about them is retroactively edited to match
this amendment.

## Seventh amendment (v6, tag `prereg-p5-v6`, AuthorityBench)

The sixth amendment concerns `synthesis.py`'s own capability (does it
scale, does cost-aware synthesis diverge from cardinality-aware
synthesis). This one asks the question `NOVELTY.md`'s own "ABAC policy
mining" paragraph poses but had never been run: does a faithful,
scoped reimplementation of Xu and Stoller's seed-and-generalize mining
core (`mining_baseline.py`, registered precisely in `prereg/
v6-authority-bench.md` before it was written) recover an attribute set
that matches this project's own loss-derived minimum-cardinality reduct
(`src/authority_compiler`'s packaged `derive_authority_contract`), on
v1, v2, and v4 -- this artifact's entire existing domain portfolio, no
new domain built for this milestone.

The registered outcome, machine-checked, not assumed:

- **v1**: **equal** -- the mined policy's attribute union (8 properties,
  42 rules before simplify, 42 after -- none redundant) is identical to
  `derive_authority_contract`'s own minimum-cardinality contract, both
  matching v1's own core exactly (`core_is_sufficient: true`). Sound
  (`checkers`-independent, direct: 0 mismatches between the mined
  policy's grant decisions and the true labels over the full
  7,776-tuple reachable set). Tractable in 1.44 seconds.
- **v2**: **equal** -- 9 properties, 54 rules (none redundant), again
  identical to `derive_authority_contract`'s answer and to v2's own core
  (CH-A8/CH-A10's own "unique reduct" finding leaves no tie for either
  method to land on differently). Sound, 0 mismatches. Tractable in 6.32
  seconds.
- **v4**: **mismatch** (as SETS: `derive_authority_contract`'s answer is
  `{approval_token, branch, data_classification, delegated_role,
  operation, repository, resource_owner}`; the mined policy's union is
  `{approval_token, data_classification, delegated_role, environment,
  operation, repository, resource_owner}`) -- but investigated, not left
  as an unexplained anomaly, and NOT a soundness concern this
  registration's own decision rule anticipated a mismatch might be:
  `checkers/ch_b1_check.py`'s own already-committed, exhaustively-
  enumerated `minimum_reducts` (Milestone C, `out/checkers/
  ch_b1_check.json`) is **exactly these same two sets** -- v4's 6-property
  core is not sufficient, and there are exactly two cardinality-7
  reducts, one adding `branch` and the other adding `environment`
  (Fifth amendment's own branch/environment co-variation explanation).
  `derive_authority_contract`'s SAT-backed search happened to return the
  `branch` variant; the independently-designed, independently-
  implemented mining baseline happened to land on the `environment`
  variant -- both are genuine, already-known, machine-verified minimum
  reducts of the identical model, confirmed sound here too (16 rules
  after simplify, dropped from 17; 0 mismatches between the mined
  policy's grants and the true labels). A tie-break divergence between
  two independently-computed, equally-valid global minima, not a
  disagreement about which properties actually matter. Tractable in 1.26
  seconds.

**Decision: INCONCLUSIVE**, per the registered rule applied honestly to
what was actually measured -- SUPPORTED needed a strict superset on at
least one domain (mining using avoidably more attributes than
necessary); NOT SUPPORTED needed equality on all three. Neither
occurred: two domains equal, one a genuine mismatch that turned out, on
investigation, to be the benign kind the registration's own third
category exists for, not the soundness-concern kind. All 3 domains:
`tractable: true`, `sound: true` -- the 20-minute-per-domain
tractability budget was never approached (slowest domain, v2, finished
in 6.32 seconds), and the scoped mining baseline never once granted a
truly-denied tuple across 47,520 combined reachable tuples.

This is independent evidence, from an external method reimplemented
faithfully rather than authored to make a point, that this artifact's
own core-versus-reduct results (CH-A8, CH-A10, CH-B1) describe genuine
structural properties of these models -- recoverable by more than one
method -- rather than an artifact of `synthesis.py`'s own particular
search procedure. It is also a registered non-result for the specific
question AuthorityBench set out to answer (does mining tend to be
avoidably non-minimal): on these three domains, this scoped
reimplementation was not avoidably non-minimal even once, honestly
reported as such rather than framed as a win. `mining_baseline.py`
implements exactly the algorithm `prereg/v6-authority-bench.md`
registered, unmodified after this result was seen; nothing about the
registered decision rule or the algorithm's seed order, generalization
order, or simplify rule was adjusted to produce this outcome.

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
