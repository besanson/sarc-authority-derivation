# v2: Reachability Redesign (pre-registration)

Status: PRE-REGISTRATION. Definitions only -- no results. To be tagged
`prereg-p5-v2` on commit. No v2 experiment or formal-model code may be
written before this file is committed and tagged, per this project's
own registration discipline (task brief Phase 1; applied to itself here
exactly as the round-0 adjudicator review's Section 4 requires).

## Motivation

Round-0 review (finding F0; `NOVELTY.md`'s Amendment; `appendix-a-
proofs.md`'s Proposition 0) found, and this artifact independently
verified before acting on it, that v0.1's formal model makes
remediation-reachability redundant: `rank0_reachable_tuples()` is the
unconstrained full product of all nine candidate properties' declared
domains, so it already contains everything `remediation_reachable_
tuples()` could add by varying `order_value` alone. v0.1's fence claim
("remediation changes the reachable set") was corrected to drop that
specific assertion rather than left standing. This file registers the
redesign that would let the original question actually be tested.

## The obstacle a naive fix does not clear

The obvious first idea -- restrict `order_value`'s rank-0 domain to
"corrupted-evidence" values only, and make evidence-substitution
remediation the only path to the "true" value -- does not work, and it
is worth stating precisely why before proposing something that does.

Call the true/clean value `v_true` and the corrupted values `v_low`,
`v_high`. If rank-0 is restricted so a *corrupted* tuple can only carry
`order_value in {v_low, v_high}`, the *clean* case (`evidence_corrupted
= False`) must still independently be rank-0 reachable at `order_value =
v_true` -- because a clean case is exactly a decision that was never
corrupted in the first place, which is a real, independently-occurring
case in the declared model, not one that only arises by correcting a
corrupted one. Evidence-substitution remediation, applied to a corrupted
tuple, produces exactly `(evidence_corrupted = False, order_value =
v_true)` -- a tuple that must already be rank-0 reachable for the
"never corrupted" case to exist at all. Under set-membership reachability
(a tuple either is or is not in the reachable set; Definition 1 does not
track *how many ways* or *by what path* a tuple is reached), remediation
therefore still adds nothing new to the set, for the same structural
reason as v0.1: a remediated state and a "genuinely clean" state are
semantically the same tuple, and the clean case's own independent
existence in the declared model already puts that tuple in rank-0.

This is not specific to this artifact's domain choices; it is a general
property of any remediator whose job is to *restore* a value that a
clean, uncorrupted run could equally have produced directly. Evidence
substitution is exactly such a remediator (`composition.py`'s own
description: it corrects corrupted evidence to the true value). A
redesign that wants remediation to add genuinely new reachable tuples
needs a remediator whose output is not semantically identical to some
independently-occurring clean case -- i.e. a mechanism-specific value
that would not otherwise be in the declared model at all.

## The proposed mechanism: retry-delay reachability

Resource downroute (W2's remediator) and a new declared retry-delay
concept both have this property; downroute because its output quantity
is a budget-fitting artifact of the mechanism itself (not a demand
value any clean newsvendor computation would produce), and retry-delay
because a *delayed* decision is a different real-world event from one
*originally proposed* at the later day, not merely a relabeling of it.
v2 adds retry-delay as the primary mechanism (fully specified below);
downroute-only-reachable quantities are noted as a second, structurally
similar extension, deferred to a later revision rather than specified
to the same precision here, so v2 tests one mechanism cleanly rather
than two mechanisms partially.

**Declared addition to the domain:** a fourth `day` value, `day = 200`,
declared to be **rank-0 unreachable** -- no decision in this artifact's
model is ever *initially* proposed on day 200 (a declared fact about
the model, not a derived one, exactly as `agent-unauthorized`'s empty
window is a declared fact in `loss-model.yaml`). `day = 200` falls
inside `agent-delegate`'s permitted window `[100, 180]`? No -- 200 is
chosen strictly outside it, so this addition does not change which
*existing* witness pairs discriminate `procurement_outside_temporal_
window`; it adds a new point without disturbing v0.1's already-verified
witnesses for the other three `day` values.

**Declared new remediation operator characterization: retry-delay.** A
decision whose evidence was rejected at its originally-proposed day (one
of the existing three, `{50, 140, 300}`) can be resubmitted once, at
`day = 200`, with every other field unchanged except `day` itself. This
is declared as a *characterization* of a delay-and-retry pattern the
imported baseline's own remediation vocabulary does not currently
implement (task brief: this paper "adds no new remediation logic" to
`sarc-suite-one-pass` itself) -- v2's formal model characterizes a
retry pattern for the exhaustive checkers only, exactly as v0.1's
`pair-test-grid.yaml` already characterizes evidence substitution and
downroute as declared abstractions rather than by invoking the real
engines inside the finite-model sweep. Whether Phase 3's *empirical*
layer should also implement a real retry mechanism against the imported
simulation is an open question for v2's own Phase 3, not decided here.

**Redesigned reachability:**
`rank0_reachable_tuples()` restricted so `day = 200` never appears (the
other eight fields' domains, and `day`'s other three values, are
unchanged from v1's `pair-test-grid.yaml`).
`retry_delay_reachable_tuples()`: for every rank-0 tuple with `day in
{50, 140, 300}`, the tuple with `day = 200` and every other field
identical is retry-delay-reachable. This produces genuinely new tuples
by construction: `day = 200` tuples exist nowhere in rank-0, so every
one produced this way is new to the union, unlike v1's `order_value`
swap.
`executable_reachable_tuples_v2()` = rank-0 union retry-delay-reachable
(and, if downroute-only reachability is later added in the same v2
cycle, union that too) -- the same "declared abstraction, union of
operator-characterized additions" shape v1 already used, corrected to
actually be non-redundant.

## Hypotheses (registered two-sided, per the review's own framing:
## "either outcome is a result")

**CH-A5 (does the redesign make remediation reachability-relevant?)**
Decision rule: compute P*, the coverage list, and the witness set under
`executable_reachable_tuples_v2()`, using the unchanged six losses from
`loss-model.yaml` (`procurement_outside_temporal_window` is the only
predicate that reads `day`, so it is the only predicate this redesign
can possibly affect). Compare against v1's committed P*/coverage list.
Two possible, equally reportable outcomes, decided by the checkers'
output, not assumed in advance:
- **If P* or the coverage list differs from v1's**: the fence's original
  claim is demonstrated for the redesigned model, reported with the
  new witness(es) that changed, and NOVELTY.md/the paper are corrected
  a second time to state the (now true) claim precisely, citing which
  witness pair is responsible.
- **If P* and the coverage list are unchanged**: reported as "this
  artifact's derivation is reachability-robust with respect to
  retry-delay in this declared model" -- not a failure, a real finding
  about this specific loss model (`procurement_outside_temporal_window`
  already derives `day` as participating via existing rank-0 witnesses;
  a new retry-delay-only witness would only change *which* witness is
  recorded for `day`, not whether `day` participates, unless retry-delay
  reachability changes some OTHER property's participation status too,
  which the checkers, not this document, will determine).

**CH-A6 (exhaustiveness of the redesigned checkers, mirroring CH-A2):**
`checkers/participation_check.py` and `checkers/pairtest_check.py`,
re-run against `executable_reachable_tuples_v2()`, must still agree
exactly (CH-A2's original decision rule, unchanged, re-applied to the
new reachable set).

## What does not change from v1

The six declared losses (`loss-model.yaml`), the nine candidate
properties, the grant mechanism and its Proposition 3, and Phase 3's
real empirical layer (which already computes genuinely different pre-
and post-remediation `order_value`s from the real simulation, unaffected
by this formal-model-only redesign) are all unchanged. v2 is scoped
narrowly: one new declared reachability mechanism, one new hypothesis
pair, re-run of the existing exhaustive checkers against the new
reachable set.

## Registration discipline

- No v2 formal-model or checker code implementing CH-A5/CH-A6 may run
  before this file is committed and tagged `prereg-p5-v2`.
- v0.1's results (`out/checkers/*.json` at the `prereg-p5-v1`..v0.1.2
  history) stay frozen and cited as the first iteration; nothing already
  committed is retroactively edited to match v2's outcome, whichever it
  is.
- `NOVELTY.md` gains a second amendment paragraph once CH-A5's outcome
  is known, stating plainly which of the two registered outcomes
  obtained -- the admission is worth recording either way, not only if
  the fence turns out to be demonstrable.
