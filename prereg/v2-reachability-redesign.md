# v2: Reachability Redesign (pre-registration)

Status: PRE-REGISTRATION. Definitions only -- no results. To be tagged
`prereg-p5-v2` on commit. No v2 experiment or formal-model code may be
written before this file is committed and tagged, per this project's
own registration discipline (task brief Phase 1; applied to itself here
exactly as the round-0 adjudicator review's Section 4 requires).

**Pre-tag revision note.** This supersedes an earlier draft of this same
file (primary mechanism: retry-delay only, no Proposition 0-general, no
remediation-induced loss). The earlier draft was committed locally and a
`prereg-p5-v2` tag was created pointing at it, but neither the commit nor
the tag was ever pushed, and no v2 code was written against it -- so the
tag is being moved to the commit that adds this revision, not left as a
divergent historical marker the way `prereg-p5-v1`'s original wording
was preserved after code already depended on it. Nothing has run against
the version this replaces.

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

## Proposition 0-general (structural; to be proved in appendix-a-proofs.md
## and machine-checked directly on this artifact's model, once v2 formal-
## model code exists -- not proved in this prereg document, which
## registers what will be tested, not the result)

**Statement.** Let `Reach_0` be the rank-0 reachable set under a given
declared construction, and let `R` be any remediation operator
characterized as producing an image set `Reach_R` (every tuple `R` can
produce from some rank-0 input). If `Reach_R subset-of Reach_0` --
every tuple `R` could produce is already independently rank-0 reachable
-- then `Reach_0 union Reach_R = Reach_0`, so `P*(Reach_0 union Reach_R)
= P*(Reach_0)` exactly: including `R` in the reachable-set construction
cannot change P\*, the coverage list, or any witness, regardless of what
`R`'s transformation actually computes internally. This follows purely
from Definition 1 depending only on set membership -- it has no notion
of provenance, i.e. which mechanism, or how many distinct paths, put a
given tuple in the reachable set.

**Corollary 1 (evidence substitution is derivation-irrelevant under this
framework, for any declared order_value domain).** Evidence
substitution is characterized, unchanged from v1, as moving
`order_value` to any other point in its own declared domain while
holding the other candidate fields fixed. Whenever rank-0 is the
unconstrained product over all candidate domains (v1's construction,
and v2's for every field except the new one below), rank-0 already
contains every `(other-fields, any-order-value)` combination, so
substitution's image is always a subset of rank-0 -- not because of the
*specific* order_value points chosen (v0.1's were 600/1200/2500;
Proposition 0, `appendix-a-proofs.md`, measured this for that one
instance), but because the argument depends only on rank-0's
unconstrained-product *shape*. Proposition 0-general is the general
argument that v0.1's measured instance was not a coincidence of its
particular domain values.

**Corollary 2 (mechanism-specific remediators are not automatically
covered by Corollary 1).** A remediator whose characterized image is
*not* a subset of rank-0 -- because rank-0 is declared to exclude the
value range only that remediator can reach, as the downroute mechanism
below does -- is not covered by Corollary 1, and whether it actually
changes P\* is not decided by Proposition 0-general either way; it
depends on whether some loss predicate discriminates the newly
reachable tuples. This is exactly what CH-A7 below is designed to test,
decided by the checkers' output, not assumed here.

## The obstacle a naive order_value-only fix does not clear

(Retained from the prior draft; Proposition 0-general above is the
generalization of this specific observation, not a replacement for it.)

Restricting `order_value`'s rank-0 domain to "corrupted-evidence"
values only, with evidence-substitution remediation as the sole path to
the "true" value, does not work: the clean case (`evidence_corrupted =
False`) must still independently be rank-0 reachable at the true value,
because a clean case is exactly a decision that was never corrupted in
the first place -- a real, independently-occurring case in the declared
model, not one that only arises by correcting a corrupted one. Evidence
substitution's output therefore always coincides with a tuple that must
already be rank-0 reachable for the clean case to exist at all. This is
Corollary 1 above, stated concretely before the general argument was
available.

## Primary mechanism (v2): downroute-only-reachable quantities,
## characterized from the imported W2 operator

Grounded directly in the real remediator, not a paraphrase of it:
`composition._maybe_downroute` (`sarc-suite-one-pass`, pinned, read
directly before writing this section) computes

```
feasible_qty = max(0, min(proposed_qty, max_qty_by_cost, max_qty_by_carbon))
```

-- the largest quantity whose predicted cost AND carbon both fit the
remaining W2 budget, applied only when `feasible_qty < proposed_qty`
(strictly decreasing when it fires; a no-op otherwise), W1 untouched
unconditionally. **There is no minimum-order-quantity term anywhere in
this calculation** -- it is a pure budget-fitting computation, oblivious
to any supplier-side floor on order size. That gap is real in the
imported baseline's own code, not invented for this redesign, and it is
exactly the property that makes downroute's characterized image
NOT a subset of rank-0, unlike evidence substitution's.

**New candidate property: `min_order_quantity`.** A declared per-decision
supplier minimum order quantity. Proposed domain (three points, mirroring
`order_value`'s own domain design -- chosen to guarantee at least one
rank-0-valid `order_value` pairing for every value, while still producing
genuine below-threshold combinations; finalized when `pair-test-grid.yaml`
itself is edited in the v2 code phase, not pinned irrevocably here):
`{500.0, 900.0, 2000.0}` against `order_value`'s existing `{600.0,
1200.0, 2500.0}`.

**Declared rank-0 constraint:** `order_value >= min_order_quantity`
always holds at rank-0 -- a declared assumption that a well-formed,
demand-driven initial proposal never falls below the supplier's own
declared minimum (plausible: ordinary replenishment demand is sized
well above a typical MOQ; this is a declared modeling choice, stated
as such, exactly like `agent-unauthorized`'s empty window in
`loss-model.yaml` v1). Concretely, at rank-0: `min_order_quantity =
500` pairs with all three `order_value` points (all satisfy >= 500);
`min_order_quantity = 900` pairs only with `{1200, 2500}` (`600` is
excluded from rank-0 under this pairing); `min_order_quantity = 2000`
pairs only with `{2500}` (`600` and `1200` both excluded).

**New loss (loss #7, to be added to `loss-model.yaml` in the v2 code
phase): `downrouted_quantity_below_supplier_minimum`.** Fires when
`order_value < min_order_quantity`. Simplification flagged explicitly:
`order_value` stands in for the downroute-scaled quantity itself (the
real mechanism scales `proposed_qty`, and `order_value` is `qty` times a
held-fixed unit cost); reusing `order_value` keeps this loss consistent
with how downroute is already characterized for `order_value` in v1's
own reachability section, rather than introducing a separate quantity
axis for one loss alone.

**Downroute-reachable tuples:** from any rank-0 tuple with `workflow ==
"W2"` and `order_value >= min_order_quantity` (i.e. every rank-0-valid
W2 tuple, by the constraint above), tuples with `order_value` moved to
any strictly lower point in the domain are downroute-reachable --
including points that now violate `order_value >= min_order_quantity`,
since the real mechanism this characterizes has no MOQ term to respect
that boundary. Concretely: `(order_value=600, min_order_quantity=900)`
and `(order_value=600 or 1200, min_order_quantity=2000)` exist nowhere
in rank-0 (excluded by the declared constraint) and enter the reachable
set only through this characterization -- genuinely new relative to
rank-0, unlike evidence substitution's image.

## Secondary mechanism (v2): retry-delay

(Retained from the prior draft, demoted to secondary per this
amendment -- still characterized and still swept by CH-A5/CH-A6 below,
but no longer the mechanism CH-A7's targeted ablation is built around.)

A fourth declared `day` value, `day = 200`, declared rank-0-unreachable
(no decision is ever *initially* proposed on day 200) and reachable only
via a characterized retry-delay operator: a decision whose evidence was
rejected at its originally-proposed day (one of the existing `{50, 140,
300}`) can be resubmitted once, at `day = 200`, every other field
unchanged. `200` is outside `agent-delegate`'s `[100, 180]` window
(verified by direct computation before the prior draft was committed),
so this addition does not disturb v1's existing `procurement_outside_
temporal_window` witnesses.

## Hypotheses (registered two-sided; "either outcome is a result")

**CH-A5 (does the redesign make remediation reachability-relevant, in
general?)** Decision rule: compute P\*, the coverage list, and the
witness set under `executable_reachable_tuples_v2()` = rank-0 union
downroute-reachable union retry-delay-reachable, using the seven losses
(six from v1, unchanged, plus the new loss above) over ten candidate
properties (nine from v1 plus `min_order_quantity`). Compare against
v1's committed P\*/coverage list. Two possible outcomes, decided by the
checkers, not assumed: if P\* or the coverage list differs, the fence's
original claim is demonstrated for the redesigned model and NOVELTY.md/
the paper are corrected a second time, citing the changed witness(es);
if unchanged, reported as "this artifact's derivation is reachability-
robust in this declared model" -- a real finding, not a failure.

**CH-A6 (exhaustiveness of the redesigned checkers, mirroring CH-A2,
unchanged in spirit):** `checkers/participation_check.py` and
`checkers/pairtest_check.py`, re-run against `executable_reachable_
tuples_v2()`, must still agree exactly.

**CH-A7 (new; targeted, sharp, machine-checked ablation on the
remediation-induced property):** removing downroute from the
reachable-set construction changes P\* membership for `min_order_
quantity`. Decision rule: compute P\* twice over the same seven-loss,
ten-property model -- (a) rank-0 union downroute-reachable union
retry-delay-reachable (the full v2 set) and (b) rank-0 union retry-
delay-reachable only, downroute excluded. **CH-A7 is SUPPORTED** iff
`min_order_quantity` is an element of P\*(a) but not of P\*(b) --
downroute demonstrated derivation-relevant for this specific property,
machine-checked, not asserted. If membership is unchanged between (a)
and (b), **CH-A7 is NOT SUPPORTED**, printed as such (this project's own
discipline for a registered hypothesis that does not hold), and would
itself be a checkable, explainable finding: some other already-rank-0-
reachable combination would have to already witness `min_order_
quantity`'s participation via the same loss, independent of downroute --
verifiable directly once observed, not hand-waved away.

## What does not change from v1, and what does

Unchanged: the grant mechanism and its Proposition 3; Phase 3's real
empirical layer (which already computes genuinely different pre- and
post-remediation `order_value`s from the real simulation, independent of
this formal-model-only redesign); six of the seven losses; nine of the
ten candidate properties; the retry-delay characterization as drafted
previously.

Changed from the prior (retry-delay-only) draft of this file: downroute
is now the primary mechanism, fully characterized from the real `_maybe_
downroute` code rather than asserted; one new loss and one new candidate
property are registered; CH-A5 is restated over the amended model; CH-A7
is added as a second, sharper hypothesis targeting the one property the
downroute mechanism is specifically designed to make participate.

## Registration discipline

- No v2 formal-model or checker code implementing CH-A5/CH-A6/CH-A7 may
  run before this file is committed and tagged `prereg-p5-v2`.
- `loss-model.yaml`'s seventh loss and `pair-test-grid.yaml`'s tenth
  property do not exist as committed files yet -- this document
  registers their design; writing them is v2 formal-core work, gated
  behind this tag exactly as v1's `loss-model.yaml` was gated behind
  `prereg-p5-v1`.
- v0.1's results stay frozen and cited as the first iteration; nothing
  already committed is retroactively edited to match v2's outcome,
  whichever it is.
- `NOVELTY.md` gains a second amendment paragraph once CH-A5/CH-A7's
  outcomes are known, stating plainly which registered outcome
  obtained -- worth recording either way.
