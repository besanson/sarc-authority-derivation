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

## Proposition 0-general (equal reachable sets give equal P\*, independent of tuple design; prereg/v2-reachability-redesign.md, tag prereg-p5-v2)

**Statement.** Let `Reach_0` be the rank-0 reachable set under a given
declared construction, and let `R` be any remediation operator
characterized as producing an image set `Reach_R` (every tuple `R` can
produce from some rank-0 input). If `Reach_R subset-of Reach_0` -- every
tuple `R` could produce is already independently rank-0 reachable --
then `Reach_0 union Reach_R = Reach_0` exactly, so `P*(Reach_0 union
Reach_R) = P*(Reach_0)` and `coverage_list(Reach_0 union Reach_R) =
coverage_list(Reach_0)`: including `R` in the reachable-set construction
cannot change P\*, the coverage list, or any witness, regardless of what
`R`'s transformation actually computes internally.

**Proof.** Definitions 2-3 are computed purely from the *set* Definition
1's witness search sweeps (`participation.compute_p_star`) and the loss
registry -- `find_witness` groups reachable tuples by fingerprint and
compares M-verdicts within each group; it never inspects how a tuple
entered the reachable set, only whether it is *in* it. If `Reach_R
subset-of Reach_0`, then as sets `Reach_0 union Reach_R = Reach_0`, so
the two runs sweep the identical set and must return identical output.
This argument uses nothing about `StateTuple`'s specific fields or
`losses.py`'s specific predicates -- it holds for any tuple type
exposing `with_property()` and any loss registry, exactly the same
domain-agnosticism `participation.py`'s own docstring claims and
`test_participation.py` already exercises against a synthetic type.

PROOF-STATUS: machine-checked (`checkers/general_reachability_check.py`),
`structural_lemma`: 4 independent synthetic loss predicates, each tried
against 5 differently-shaped remediator-image characterizations (empty,
singleton, partial, alternating, and the full reachable set) over one
32-tuple synthetic universe unrelated to `StateTuple`/`StateTupleV2` --
20 enumerated cases total, every one confirming P\* and the coverage
list are unchanged whenever the tried image is a subset of the universe
(`all_cases_hold: true` in `out/checkers/general_reachability_check.json`).

**Corollary 1 (evidence substitution is derivation-irrelevant under this
framework, whenever rank-0 is the unconstrained product over all
candidate domains).** Evidence substitution is characterized, unchanged
from v1, as moving `order_value` to any other point in its own declared
domain while holding the other candidate fields fixed. Whenever rank-0
is the unconstrained product over every candidate domain with no
cross-field filter (v1's construction, for any choice of declared
`order_value` domain), rank-0 already contains every
`(other-fields, any-order-value)` combination, so substitution's image
is always a subset of rank-0 by Proposition 0-general above -- not
because of the *specific* order_value points chosen (v0.1's were
600/1200/2500; Proposition 0 measured this one instance), but because
the argument depends only on rank-0's unconstrained-product *shape*.

PROOF-STATUS: machine-checked (`checkers/general_reachability_check.py`),
`corollary_1_across_domains`: v1's own `rank0_reachable_tuples()` and
`remediation_reachable_tuples()`, called unmodified against 4 order_value
domains other than the declared one (one a 4-point domain producing a
10,368-tuple rank-0), every one producing exactly 0 new tuples beyond
rank-0 (`all_redundant_regardless_of_domain: true`) -- confirming
Proposition 0's zero-new-tuples result generalizes across domain
choices, not only the specific 7,776-tuple grid Proposition 0 itself
measured.

**Scope note (v2's cross-field filter is a boundary this corollary's
general wording does not spell out).** The "whenever rank-0 is the
unconstrained product" premise above is exactly true of v1's
construction. v2 additionally declares one cross-field rank-0 filter
absent from v1 (`rank0_constraint_v2`, `prereg/pair-test-grid.yaml`'s
`v2` section): `order_value >= min_order_quantity` always holds at
rank-0. Evidence substitution, characterized as varying `order_value`
alone while holding `min_order_quantity` fixed, would NOT have an image
fully inside `rank0_reachable_tuples_v2()` for every
`(min_order_quantity, target order_value)` pairing once that filter is
in force -- e.g. moving `order_value` down to 600.0 while
`min_order_quantity` stays fixed at 900.0 produces exactly the tuple
`rank0_constraint_v2` excludes. This is not a defect in v2's design:
`domain.executable_reachable_tuples_v2()` (CH-A5's decision rule,
`prereg/v2-reachability-redesign.md`) does not include evidence
substitution as a term at all -- only downroute and retry-delay -- so
this boundary is never actually exercised by this artifact's v2
construction. It is recorded here, rather than left for a reader to
discover by trying it, because Corollary 1's premise is a general-
sounding claim about "any declared order_value domain" that does not by
itself spell out what changes once a *second* field enters a cross-field
rank-0 relationship with `order_value` -- stating a certified scope
exactly, per this project's own `checked-scope-only` discipline, rather
than leaving a general claim standing uncontradicted by a case nobody
checked.

**Corollary 2 (mechanism-specific remediators are not automatically
covered by Corollary 1).** A remediator whose characterized image is
*not* a subset of rank-0 -- because rank-0 is declared to exclude the
value range only that remediator can reach -- is not covered by
Corollary 1, and whether it actually changes P\* is not decided by
Proposition 0-general either way; it depends on whether some loss
predicate discriminates the newly reachable tuples.

PROOF-STATUS: machine-checked (`checkers/general_reachability_check.py`),
`corollary_2_on_v2_mechanisms`: neither of v2's two characterized
mechanisms has an image inside `rank0_reachable_tuples_v2()`'s
15,552 tuples -- downroute produces 3,888 tuples outside it, retry-delay
produces 5,184 tuples outside it (`downroute_image_subset_of_rank0_v2:
false`, `retry_delay_image_subset_of_rank0_v2: false`) -- confirming,
not merely asserting, that neither is automatically covered by
Corollary 1. Whether either actually changes P\* is exactly what CH-A5
and CH-A7 decide (`paper5-authority-derivation-draft-v0.3.md`, the live
draft; raw output `out/checkers/ch_a5_check.json` and
`out/checkers/ch_a7_check.json`), not this proposition, which only
establishes that the question is open rather than pre-decided.

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

PROOF-STATUS: checked-scope-only (v0.3 correction below).
`checkers/participation_check.py`'s three checks, over the full
7,776-tuple executable-reachable set (prereg/pair-test-grid.yaml's nine
declared domains, not a sample), certify only that P\* is the **core**
(Definition 6, `prereg/v3-core-reduct-correction.md`): (1) a fresh,
from-scratch recomputation of P\*/coverage_list exactly matches the
committed `out/checkers/derivation_output.json`; (2) every recorded
witness pair is independently re-executed and confirmed to be reachable,
to differ in exactly its claimed property, and to actually produce
different M-verdicts; (3) this exhaustive sweep covers every one of the
nine candidates, not a subset. None of the three certifies this
statement's own wording above -- that observing exactly P\* lets a gate
"always compute M's true verdict on any executable-reachable tuple"
(Definition 4's sufficiency, a joint property no per-property witness
search establishes) or that "no proper subset of P\* has this property"
in the sufficiency sense (Definition 5's minimality). See the correction
immediately below.

**Correction (v0.3, external review + adjudication; see
`prereg/v3-core-reduct-correction.md`,
`review-secondary/external-research-review-2026-09-06.pdf`).** The
statement above conflates two different properties. In rough-set /
decision-reduct terminology: P\* (as Definition 1 computes it) is the
**core** -- properties with an individual witnessing pair -- not
necessarily a **reduct** -- a minimal set that is *jointly sufficient*
to determine every verdict (Definition 4). The core is always a subset
of every reduct (Proposition 1' claim 2, below), but a core need not
itself be sufficient: Negative Proposition N (below) exhibits a
reachable set on which the core is empty and *not* sufficient, while two
disjoint singleton sets are each independently sufficient reducts. This
artifact's own v1/v2 instances happen not to exhibit that failure --
CH-A8 (`checkers/sufficiency_check.py`) confirms the v2 core *is*
sufficient, and CH-A10 (`checkers/reduct_check.py`) confirms it is the
*unique* reduct, of minimum cardinality nine -- but that is a fact about
this artifact's particular declared model, decided per instance
(Proposition 1' claim 3), not a consequence of Definition 1's method
holding in general, which Proposition 1 above asserted and Negative
Proposition N shows is false. Proposition 1 is superseded by
Proposition 1' below, not deleted: its original wording is preserved
above as an honest record of the error, the same no-silent-rewrite
principle this project applies throughout (`NOVELTY.md`'s own
amendments; `REPLICATIONS.md`).

## Proposition 1' (replacing Proposition 1; `prereg/v3-core-reduct-correction.md`, tag `prereg-p5-v3`)

**Statement.**

1. Definition 1 (`participation.compute_p_star`) computes the core
   (Definition 6).
2. The core is a subset of every reduct.
3. **If** the core is sufficient (Definition 4) on `R`, **then** the
   core is the unique reduct.

Claim 3's antecedent is never assumed to hold; it is decided per
instance by a sufficiency certificate or a concrete counterexample
(`reduct.sufficiency`), exactly the discipline Negative Proposition N
below makes unavoidable.

**Proof.**

*Claim 1.* A property `p` is in the core iff `candidate_properties \ {p}`
is *not* sufficient (standard rough-set fact: if it were sufficient,
some minimal sufficient subset of it -- not containing `p` -- would be a
reduct `p` is absent from, so `p` could not be in every reduct; if it is
*not* sufficient, no reduct can avoid containing `p`, since a reduct
without `p` would be a sufficient subset of `candidate_properties \
{p}`, contradicting that set's own insufficiency via sufficiency's own
monotonicity -- a superset of a sufficient set is always itself
sufficient). `candidate_properties \ {p}` is not sufficient iff two
reachable tuples agree on every property except possibly `p` yet have
different verdicts -- and since a `StateTuple`/`StateTupleV2` is exactly
characterized by its candidate-property values, two *distinct* reachable
tuples agreeing on everything but `p` must differ in `p` specifically.
This is exactly Definition 1's own participation criterion: `p`
participates iff such a pair exists. The two conditions coincide
exactly, so Definition 1's output *is* the core.

*Claim 2.* Immediate from Definition 6's own intersection form: every
element of `∩{S : S is a reduct}` is, by definition, in every reduct.

*Claim 3.* Suppose the core is sufficient. For any reduct `R`,
`core ⊆ R` (claim 2) and the core is sufficient (assumption); since `R`
is *minimal* sufficient, no proper subset of `R` is sufficient, so the
core -- sufficient and a subset of `R` -- cannot be a proper subset of
`R`, forcing `core = R`. This holds for every reduct `R`, so every
reduct equals the core: the core is a reduct, and it is the only one.

PROOF-STATUS: machine-checked (`checkers/reduct_check.py`), over the
full 10-candidate v2 model, 24,624-tuple reachable set, 1,023 of
`2^10 = 1,024` candidate subsets actually tested after subset pruning
(the one skipped subset is the full candidate set itself, a superset of
the one reduct found). `proposition_1_prime_claim_1_identity_holds:
true` (the core recomputed via Definition 1's witness search
byte-matches the core recomputed independently via the intersection of
every enumerated reduct); `proposition_1_prime_claim_2_core_subset_of_
every_reduct: true` (checked against each of the 1 reduct(s) found
individually, not only inferred from the intersection arithmetic).
Claim 3's antecedent is confirmed to hold for the v2 model specifically
by CH-A8 (`checkers/sufficiency_check.py`, `sufficiency_certificate`:
14,256 partition cells, uniform verdict within every one), and
`core_is_unique_reduct: true` in the same `reduct_check.json` output
confirms the consequent directly -- claim 3 is checked as a real
conditional on this model, not merely assumed to fire.

## Negative Proposition N (the core need not be sufficient; `prereg/v3-core-reduct-correction.md`)

**Statement.** There exist a reachable set `R`, a loss model `M`, and
candidate properties for which the core (Definition 1 / Definition 6) is
*not* sufficient (Definition 4).

**The registered counterexample**
(`prereg/fixtures/negative-proposition-n-counterexample.json`, committed
before any v3 checker code, per this project's own registration
discipline): candidate properties `x, y ∈ {0, 1}`; reachable set
`R = {(x=0, y=0), (x=1, y=1)}`; verdict `M(x, y) = x` (`= y` equivalently,
since `x` and `y` are always equal on `R`).

- **Core:** no reachable pair differs in exactly `x` (holding `y`
  fixed) or exactly `y` (holding `x` fixed) -- `R`'s only two members
  differ in *both* simultaneously. `core = ∅`.
- **Sufficiency of the core:** both tuples agree trivially on the empty
  projection, but `M(0,0) = false ≠ true = M(1,1)` -- `∅` does not
  determine the verdict. **Not sufficient.**
- **The actual reducts:** `{x}` (projection onto `x` determines `M`
  directly; its only proper subset, `∅`, is already shown insufficient)
  and, symmetrically, `{y}` -- two singleton reducts, cardinality 1,
  neither equal to the (empty) core.

This is the sharpest possible instance: an empty core that is trivially
insufficient, with two singleton reducts neither of which is the core,
directly falsifying Proposition 1's original generality claim (a
concrete instance, not merely a possibility in principle).

PROOF-STATUS: machine-checked
(`checkers/core_insufficiency_counterexample.py`), exhaustive over the
2-tuple reachable set and its full `2^2 = 4`-element candidate power
set. `matches_registered_fixture_expectation: true` in
`out/checkers/core_insufficiency_counterexample.json` -- the checker's
live computation (core `[]`, not sufficient, reducts `[["x"], ["y"]]`,
minimum cardinality 1) matches the fixture's own `expected` block
exactly, and that block was committed at the `prereg-p5-v3` tag before
this checker existed, so this is confirmation against a pre-registered
expectation, not a result fitted to whatever the checker happened to
compute.

**What this does not show.** Negative Proposition N establishes that
Definition 1's method does not *in general* guarantee sufficiency; it
says nothing about whether any *specific* reachable set (this
artifact's own v1/v2 models included) actually exhibits the failure --
that is decided per instance (Proposition 1' claim 3) and, for v2, CH-A8
decides it does not. CH-A9 (`checkers/core_insufficiency_counterexample.py`,
same output file, case `ch_a9_constrained_procurement_variant`) probes
whether a *real*, declared co-variation inside this artifact's own
procurement vocabulary (rather than an abstract `x`/`y` toy) can trigger
the failure: a registered constrained-reachability variant restricting
`workflow == "W2"` and forcing `actor_role` to co-vary with
`resource_class` by a declared staffing table. Measured result: **CH-A9
is NOT SUPPORTED** -- the constrained variant's own core (six
properties) is already sufficient (`is_core_sufficient: true`,
`minimum_reduct_cardinality: 6 = |core|`). Explanation, not smoothed
over: the declared pairing maps four roles onto three resource classes
(pigeonhole), so two roles (`agent-replenish`, `agent-unauthorized`)
share the same resource class (`consumables`) -- a residual case where
`actor_role` still varies while `resource_class` does not, which
`order_value_beyond_entitlement` and `procurement_outside_temporal_window`
(both actor_role-sensitive, resource_class-blind) can still witness
directly. The co-variation is real but not total, and this specific
loss registry does not need `resource_class` and `actor_role` jointly
to detect what it already detects from `actor_role` alone in this
instance. A finding, not a failure: CH-A9's own registration anticipated
exactly this possible outcome ("if the core happens to already be
sufficient on this constrained set... itself a checkable, explainable
finding, not smoothed over") and this pipeline's own discipline forbids
tuning the registered co-variation table after the fact to chase a
different result.

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
