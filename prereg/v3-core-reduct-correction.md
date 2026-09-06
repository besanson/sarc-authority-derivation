# v3: Core-Versus-Reduct Correction (pre-registration)

Status: PRE-REGISTRATION. Definitions and propositions to be proved, plus
two-sided hypotheses to be decided -- no results in this document. To be
tagged `prereg-p5-v3` on commit, by the author, via the GitHub web
interface (this pipeline never creates or pushes tags). No v3 formal-model
or checker code may be written before this file is committed and tagged,
per this project's own registration discipline (already applied to v1's
`prereg-p5-v1` and v2's `prereg-p5-v2`).

v0.1's and v0.2's own results stay frozen and cited as prior iterations.
Nothing already committed is retroactively edited to match v3's outcome.

## Provenance of the correction

An external, AI-assisted research review, commissioned by the author, is
committed unedited at `review-secondary/external-research-review-2026-09-06.pdf`
(sha256 `b205faf65fe84d773260d1ed514b20f5b04e420380d3136c23bff1cde4506b0b`,
verified before that commit and again here). Its central finding: this
artifact's Definition 1 (participation.py) identifies properties for
which a *singleton discernibility witness* exists -- in rough-set /
decision-reduct terminology, the **core** (the set of individually
indispensable attributes) -- and v0.1/v0.2 (Proposition 1) interpreted
that set as a **reduct**: a minimal *jointly sufficient* observation set.
Core is always contained in every reduct, but a core need not itself be
sufficient, so Proposition 1's generality claim is false. The review's
concrete verdict on the v2 result is more limited: it does not dispute
that the nine-property v2 output actually is sufficient on the v2
model -- it disputes that Definition 1's *method* generally computes a
sufficient set, and that the v2 instance's sufficiency was ever actually
checked rather than assumed.

Per the review-PDF commit's own attestation, this document does not
apply the review's findings directly: the review is a signal, adjudicated
here against this artifact's own definitions and re-derived independently
(the counterexample below is re-derived from first principles, not
copied from the review's prose, and the exact citations for the
rough-set/reduct/discernibility-matrix framing and the capability-system
comparison the review raises are listed below to be fetch-verified in
Phase B, not asserted from the review's own say-so). The adjudicator
(this pipeline, in an earlier turn) independently recomputed, on the
committed v2 model and v2 registry, that the nine-property core is in
fact sufficient, is the unique reduct, and has minimum cardinality nine
-- Phase B recomputes this itself (CH-A8, CH-A10); those numbers are not
copied forward from that recomputation into this prereg or into any v3
result file.

## Definitions (extending Definitions 1-3, `appendix-a-proofs.md`)

**Definition 4 (sufficiency).** A property set `S ⊆ candidate_properties`
is *sufficient* for loss model `M` on reachable set `R` iff for every
pair of reachable tuples `a, a' ∈ R` that agree on every property in `S`
(project identically onto `S`), `M`'s verdict on `a` equals `M`'s
verdict on `a'`. Equivalently: the projection onto `S` determines the
verdict everywhere on `R` -- no two `S`-indistinguishable reachable
tuples are ever loss-model-distinguishable.

**Definition 5 (reduct).** A *reduct* is a property set `S` that is
sufficient (Definition 4) and *minimal*: no proper subset of `S` is
sufficient. `candidate_properties` itself is always sufficient (trivially:
two tuples agreeing on every candidate property are the same tuple), so
at least one reduct always exists; there can be more than one.

**Definition 6 (core).** The *core* is the intersection of every reduct:
`core = ∩ {S : S is a reduct}`. Standard rough-set fact, restated here
because Proposition 1' below both depends on it and re-derives it rather
than citing it uncritically: a candidate property `p` is in the core iff
some reduct fails to be sufficient once `p` is removed from it, iff `p`
is *indispensable* -- iff there exist reachable tuples `a, a'` differing
only in `p` with different verdicts. This last characterization is
*exactly* Definition 1's own participation criterion.

**The identity this document registers, to be proved in Phase B
(`appendix-a-proofs.md`), not assumed here:** `domain`'s executable-reachable
sweep under Definition 1 (`participation.compute_p_star`'s first return
value, historically named `P*` / `participating_properties`) computes
*exactly* the core (Definition 6), for any tuple type, loss registry, and
reachable set -- not merely for this artifact's own declared model. This
is a general claim about Definition 1's machinery (mirroring how
Proposition 0-general was proved for the reachability-redundancy
argument, `appendix-a-proofs.md`), to be proved and machine-checked
against synthetic models in the same domain-agnostic style
`test_participation.py` and `checkers/general_reachability_check.py`
already use.

## Proposition 1' (replacing Proposition 1)

**Statement**, registered here to be proved and machine-checked in
Phase B, replacing v0.1/v0.2's Proposition 1 in full (not amending it in
place -- the general claim it made is false, per Negative Proposition N
below, and is superseded, not patched):

1. Definition 1 (`participation.compute_p_star`) computes the core
   (Definition 6). [The identity above, restated as part of this
   proposition's own claim.]
2. The core is contained in every reduct: `core ⊆ S` for every reduct
   `S`. [Immediate from Definition 6's own intersection form -- restated
   as a numbered claim because Proposition 1' as a whole replaces
   Proposition 1 as a whole, not by cross-reference to the definition
   alone.]
3. **If** the core is sufficient (Definition 4) on `R`, **then** the core
   is the unique reduct. [If core is sufficient and core ⊆ every reduct,
   then no proper subset of any reduct can also be sufficient without
   contradicting that reduct's own minimality unless it equals the core;
   full proof in Phase B.]

Claim 3's antecedent -- "if the core is sufficient" -- is not assumed to
hold in general and is not part of what this proposition asserts
unconditionally: whether it holds is decided *per instance*, by a
sufficiency certificate (Definition 4's own defining check, run
directly) or a concrete counterexample pair, never asserted from the
core's mere existence or from a prior instance's outcome. This is
exactly the discipline Negative Proposition N below exists to make
unavoidable.

PROOF-STATUS (to be assigned in Phase B, not here): machine-checked,
named checker, enumerated domain -- per this project's own lint
(`checkers/proof_status_lint.py`), unchanged.

## Negative Proposition N (the core need not be sufficient)

**Statement.** There exist a reachable set `R`, a loss model `M`, and
candidate properties for which the core (as Definition 1 / Definition 6
compute it) is *not* sufficient (Definition 4) -- i.e., a case where
Proposition 1's original generality claim fails concretely, not merely
in principle.

**The registered counterexample**, re-derived here from first
principles (not copied from the external review's own prose), encoded
machine-readably at `prereg/fixtures/negative-proposition-n-counterexample.json`:

Two candidate properties `x, y ∈ {0, 1}`. Reachable set
`R = {(x=0, y=0), (x=1, y=1)}` -- exactly two tuples, the only two ever
reachable. Verdict `M(x, y) = x` (equivalently `= y`, since `x` and `y`
are always equal on `R`; the fixture records this as `verdict_field: "x"`
so a checker can compute it mechanically without evaluating a formula).

- **Core, via Definition 1 directly:** is there a reachable pair
  differing in *exactly* `x` (holding `y` fixed)? `R`'s only two members
  differ in *both* `x` and `y` simultaneously -- there is no such pair.
  Symmetrically for `y`. Neither property has a singleton witness, so
  `core = ∅` (`participating_properties` would be empty on this `R`).
- **Sufficiency of the core:** is `∅` sufficient? Both reachable tuples
  agree trivially on the empty projection, but `M(0,0) = 0 ≠ 1 = M(1,1)`
  -- the empty set does *not* determine the verdict. `core = ∅` is
  **not** sufficient: this is the counterexample.
- **The actual reducts:** `{x}` is sufficient (projection onto `x`
  determines `M` directly) and minimal (the only proper subset is `∅`,
  already shown insufficient) -- a reduct. Symmetrically `{y}` is a
  reduct. `core = {x} ∩ {y} = ∅`, confirming Definition 6's intersection
  directly, and `minimum_reduct_cardinality = 1 > 0 = |core|`.

This is the sharpest possible instance of the failure: an empty core
that is trivially insufficient, with two singleton reducts neither of
which is the core. It is registered as a **machine-checked instance**
(Phase B: `checkers/core_insufficiency_counterexample.py` loads the
fixture, computes the core and the reducts generically -- the same
`reduct.py` machinery CH-A8/CH-A10 use, not a hand-written special case
-- and confirms the `expected` block the fixture itself records).

PROOF-STATUS (Phase B): machine-checked, `checkers/core_insufficiency_counterexample.py`,
domain size 2 reachable tuples x 2 candidate properties x 4-element power
set -- exhaustive, not sampled.

## Optional stretch (pending-human-review if only conjectured)

**Conjecture (structural sufficiency-of-core condition).** If, for every
pair of distinct candidate properties `(p, q)` and every pair of domain
values, there exists a reachable tuple realizing that `(p, q)` value
pair while every *other* candidate property is held at some common
baseline tuple's values -- informally, no two candidate properties are
ever forced to co-vary together across the whole reachable set -- then
the core is sufficient and is the unique reduct. This is exactly the
shape v1's and v2's own rank-0 constructions satisfy when unconstrained
(ADR-002 removed v1's one cross-field filter; v2's `rank0_constraint_v2`
constrains `order_value`/`min_order_quantity` together but every *other*
pair of fields remains freely co-varying), which is consistent with
(does not contradict) v1's and v2's own core happening to be sufficient
in every instance measured so far. **Not proved, not machine-checked,
registered as a conjecture only** -- CH-A9's constrained variant below
is designed specifically to probe whether violating this condition (by
declaring two properties that DO co-vary) actually breaks sufficiency in
one of this artifact's own models, which would be independent evidence
for the conjecture without proving it in general.

PROOF-STATUS: pending-human-review (this is the *only* pending-human-review
item this document adds; per `checkers/proof_status_lint.py`'s own
allowed-values discipline, this tag is never upgraded to machine-checked
by this pipeline without an actual proof and checker to back it).

## Hypotheses (registered two-sided; "either outcome is a result")

**CH-A8 (is the v2 core sufficient on the v2 executable-reachable set?)**
Decision rule: run `checkers/sufficiency_check.py` (Phase B) against
`domain.executable_reachable_tuples_v2()` and the committed v2 loss
registry, using v2's own already-derived core (`out/checkers/derivation_output_v2.json`'s
`participating_properties`, to be read and reported under its renamed
key -- see Renaming plan below -- not recomputed differently). CH-A8 is
**SUPPORTED** iff the sufficiency certificate (Definition 4's check,
computed directly, not inferred) holds for every pair of v2-reachable
tuples; **NOT SUPPORTED** iff at least one concrete counterexample pair
is found, printed as such together with the pair. Exhaustive over the
full v2 reachable set (24,624 tuples as of the v2 commit `7112031`,
recomputed fresh in Phase B, not copied forward). Either outcome is
reported; the adjudicator's own prior recomputation (see Provenance
above) is not substituted for this run.

**CH-A9 (does a real, declared co-variation between two properties break
core sufficiency in a constrained variant of this artifact's own
model?)** A registered constrained-reachability variant of the v2
procurement model, machine-readably declared in `pair-test-grid.yaml`'s
new `v3` section: reachability is restricted to `workflow == "W2"`
tuples only (not unioned with `W1`), and `actor_role` is forced to
co-vary with `resource_class` by a declared staffing/specialization
table -- each role is provisioned to handle exactly one resource class
(`agent-replenish` -> `consumables`; `agent-w2-replenish` ->
`capital-equipment`; `agent-delegate` -> `durable-goods`;
`agent-unauthorized` -> `consumables`) -- analogous in kind to the
per-role entitlement/window/allowed-class tables `loss-model.yaml`
already declares, not a new kind of modeling device. Every other v2
candidate property keeps its full v2 domain, unconstrained. Decision
rule: compute the core and the minimum reduct cardinality on this
constrained reachable set, using the unchanged seven-loss v2 registry
(`resource_class_not_entitled` reads both `actor_role`, via policy, and
`resource_class`, so the constrained pairing is exactly the kind of
joint dependency Definition 4 is sensitive to and Definition 1 alone may
miss). CH-A9 is **SUPPORTED** iff the core is *not* sufficient on this
constrained set AND the minimum reduct cardinality strictly exceeds the
core's cardinality; **NOT SUPPORTED** iff the core is already sufficient
here, printed as such -- itself a checkable, explainable finding (it
would mean this particular declared co-variation does not happen to
break sufficiency for this specific loss registry), not smoothed over.
Exhaustive over the constrained reachable set and the fixed loss
registry.

**CH-A10 (exact reduct enumeration on the v2 model)** Decision rule:
`checkers/reduct_check.py` (Phase B) enumerates every subset of v2's ten
candidate properties (`2^10 = 1024` subsets, exhaustive, with subset
pruning -- once a set is confirmed sufficient, no superset need be
tested for minimality against it, and once a set is confirmed
insufficient, no subset needs to be tested for sufficiency), reports
every reduct found, the number of reducts, the minimum cardinality among
them, and whether the core (CH-A8's own output) equals the *unique*
reduct. No two-sided pass/fail here -- CH-A10 is a full enumeration
whose reported numbers are the result, not a hypothesis that holds or
fails.

## Machine-readable registration (this commit)

- `prereg/pair-test-grid.yaml`: new sibling top-level key `v3`,
  containing CH-A9's constrained-reachability declaration (the
  `workflow == "W2"`-only restriction and the `actor_role`/`resource_class`
  co-variation table) -- a sibling key existing v1/v2 code never reads,
  exactly the same non-interference pattern the `v2` key already
  established relative to `v1`.
- `schemas/sufficiency_check.schema.json`, `schemas/reduct_check.schema.json`,
  `schemas/core_insufficiency_counterexample.schema.json`: the committed
  output contracts for Phase B's three new checkers, written now,
  spec-first, exactly as `schemas/derivation_output.schema.json` and
  `schemas/grant_state.schema.json` already preceded the outputs they
  validate.
- `prereg/fixtures/negative-proposition-n-counterexample.json`: the
  two-state counterexample above, encoded as data (candidate properties,
  reachable tuples, which field is the verdict, and the expected core /
  reducts / sufficiency block) so Phase B's checker loads and checks it
  mechanically rather than re-deriving it from this document's prose.

No v3 code (no `reduct.py`, no new checker, no `domain.py` function
reading the `v3` grid key) exists yet or is written in this commit --
registration only, per this project's own discipline.

## Renaming plan for outputs (Phase B; not applied to any file in this commit)

Applies to v3's own new outputs only. `out/checkers/derivation_output.json`
(v1) and `out/checkers/derivation_output_v2.json` (v2) keep their
existing field names (`participating_properties`, `coverage_list`)
unchanged, byte-frozen apart from the informational `generated_at_head_sha`
stamp -- this is a naming correction for what v3 computes and reports
under new field names, not a retraction of what v1/v2 already reported
under their own, now-superseded-in-name-only terminology (v1/v2's
*numbers* are unaffected; only v3's own vocabulary changes).

- `participating_properties` -> `core_attributes` (Definition 6's core,
  computed exactly as `participating_properties` always was --
  `participation.compute_p_star`'s first return value is unchanged code,
  only the field name changes going forward).
- New: `is_core_sufficient` (bool) with either a `sufficiency_certificate`
  (Definition 4's check having held, plus enough detail to replay it) or
  a `counterexample` (one concrete reachable pair agreeing on the core
  with different verdicts), never both, never neither.
- New: `reducts` (every reduct found, each a sorted list of property
  names), `minimum_reducts` (the subset of `reducts` with minimum
  cardinality), `redundant_attributes` (`candidate_properties - core_attributes`
  -- properties dispensable from *some* reduct, the direct analogue of
  today's `coverage_list` under the corrected vocabulary).
- New: `counterexample_certificates` -- for any candidate subset tested
  and found insufficient during reduct enumeration (not only the core
  itself), the concrete witnessing pair, keyed by the subset tested, so
  a negative finding is exactly as replayable as a positive one.

## Citations to be fetch-verified in Phase B (not verified in this commit)

- Pawlak, on rough sets and reducts (the source of the core/reduct/
  discernibility distinction this correction turns on).
- A discernibility-matrix source (the standard computational device for
  exact reduct enumeration -- `reduct.py`'s own algorithm, Phase B,
  should be positioned against it honestly, whether or not it is used
  directly).
- Macaroons, UCAN, and Biscuit, as capability-system prior art for the
  execution grant (`grant.GrantLedger`) -- per v0.3's own repositioning
  (draft v0.3, Phase B) of grant binding as engineering with named prior
  art, not a novelty claim.

None of these are cited as verified anywhere in this document; each is
listed here as work Phase B owes, per this project's own citation
discipline (`citation_check.py`) -- fetched, recorded in
`verified-citations.json` with url/title/first_author/year, before it
enters any paper draft text.

## Registration discipline

- No v3 formal-model or checker code (`reduct.py`,
  `checkers/sufficiency_check.py`, `checkers/reduct_check.py`,
  `checkers/core_insufficiency_counterexample.py`, or any `domain.py`
  function reading `pair-test-grid.yaml`'s new `v3` key) may run before
  this file is committed and tagged `prereg-p5-v3`, by the author, via
  the GitHub web interface.
- v0.1's and v0.2's own results, checkers, and outputs stay exactly as
  committed -- byte-frozen apart from the informational
  `generated_at_head_sha` stamp any fresh `make formal` run naturally
  refreshes.
- `NOVELTY.md` gains a third amendment once CH-A8/CH-A9/CH-A10's
  outcomes are known, stating plainly which registered outcome obtained,
  exactly as the second amendment did for CH-A5/CH-A7.
- The external review PDF (`review-secondary/`) is evidence and
  provenance, not a source of unverified claims: every factual claim
  this document makes that traces back to it has been independently
  re-derived (Negative Proposition N's counterexample) or is explicitly
  deferred to Phase B's own verification (the citations above), per the
  review-commit's own attestation.
