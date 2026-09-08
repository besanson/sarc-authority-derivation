# v6: AuthorityBench -- Loss-Derived Minimality Against a Reimplemented Mining Baseline (pre-registration)

Status: PRE-REGISTRATION. No code beyond E1 (`src/authority_compiler`,
already committed and unmodified by this document). Specifically: the
reimplemented mining baseline, the comparison-running code, and any new
checker reading this file's declared structure may NOT be written before
this file is committed and tagged `prereg-p5-v6`, by the author, via the
GitHub web interface (this pipeline never creates or pushes tags).

v0.1-v5's own results, checkers, and outputs stay frozen and cited as
prior iterations. Nothing already committed is retroactively edited to
match AuthorityBench's outcome.

## Provenance and motivation

`NOVELTY.md`'s own "ABAC policy mining" literature paragraph draws a
specific, testable distinction that has never actually been exercised
against this artifact's own results: ABAC policy mining (Xu and Stoller,
2014-2015, `xu-stoller-abac-mining` in `verified-citations.json`)
reconstructs attribute-based rules from an *existing* grant relation, and
"has no minimality claim (or ground truth to check one against)" -- while
this project's own derivation (Definitions 1-6) starts from a declared
loss model and carries a machine-checked minimality guarantee (core,
reducts, and now `synthesis.py`'s SAT-backed minimum-cardinality
contract). AuthorityBench asks the question that comparison implies but
this artifact has never actually run: given the SAME ground truth (the
executable-reachable set and its true grant/deny labels, already fully
characterized by v1/v2/v4's own loss models), does a faithful
reimplementation of the mining approach's core algorithm recover an
attribute set that matches this project's own minimum-cardinality reduct
-- or does it, as the "no minimality claim" framing predicts is possible
in principle, sometimes use more attributes than necessary?

This is the first time in this project's history that an external
method's ALGORITHM (not merely its citation) is reimplemented and run
against this artifact's own data, so the same discipline
`review-secondary/`'s adjudicated PDF review already established for
prose findings applies here to code: reimplemented faithfully from the
published method, never patched or tuned toward a preferred outcome, with
this document's own registration fixed before any of it is written.

## E1 (already committed, unmodified by this document): `src/authority_compiler`

`src/authority_compiler/api.py`'s `derive_authority_contract()` packages
`reduct.compute_core`, `reduct.sufficiency`, and `synthesis.
find_minimum_cardinality_contract` -- all three unmodified -- behind one
call, returning an `AuthorityContract` (core, coverage list, whether the
core is sufficient, and a minimum-cardinality reduct). AuthorityBench's
own comparison (E4) calls this one packaged entry point for "this
project's own answer," rather than calling the three wrapped functions
separately, exercising the packaged product this milestone's own name
promises, not just the underlying research code.

## The three domains

Reused, not new: v1 (`domain.py`/`losses.py`, the original 9-property
retail-procurement model, `executable_reachable_tuples()`, 7,776 tuples),
v2 (`domain.py`/`losses.py`'s v2 functions, the redesigned 10-property
model with `min_order_quantity`, `executable_reachable_tuples_v2()`,
24,624 tuples), and v4 (`domain_v4.py`/`losses_v4.py`, the independently-
built software-and-cloud domain, `executable_reachable_tuples_v4()`,
15,120 tuples) -- the same three real domains D5's own cost-aware
experiment already reuses. No fourth domain is constructed for this
milestone: v1 and v2 are genuinely different finite models (different
candidate-property sets and reachable sets, not merely two labels for the
same result -- CH-A5 already established `min_order_quantity`
participates in v2's P\* and not in v1's), and v4 is independently built
from a different application area with externally-sourced loss
predicates. All three already have a fully machine-checked core and
reduct enumeration (CH-A8/CH-A10, CH-B1) to compare the mined result
against.

## The ground-truth grant relation

Xu and Stoller's algorithm consumes a user-permission relation UP (which
accesses are granted) plus attribute data; it does not consume a loss
model. This artifact's own translation, fixed here: for a domain's
executable-reachable set `R` and its declared loss registry, define
`granted(t) = not m_verdict(t, registry)` for every `t` in `R` -- a tuple
is granted exactly when no declared loss fires, the same zero-loss
criterion `experiments.py`'s own derived-policy arm already applies
empirically. This is a full labeling (every reachable tuple is either
granted or denied, nothing withheld), stronger than Xu and Stoller's own
real-world setting (where only the positive UP relation is directly
observed and everything else is treated as implicitly negative) --
registered here as a genuine difference from their setting, not
smoothed over: this artifact's baseline gets to see explicit negatives
Xu and Stoller's own algorithm was designed to work without.

## The reimplemented baseline: scoped seed-and-generalize mining

Fetched and quoted directly from the paper's own abstract (arXiv:1306.2401,
the preprint of `xu-stoller-abac-mining`'s eventual TDSC 2015 form,
2026-09-08): "Our algorithm iterates over tuples in the given
user-permission relation, uses selected tuples as seeds for constructing
candidate rules, and attempts to generalize each candidate rule to cover
additional tuples in the user-permission relation by replacing conjuncts
in attribute expressions with constraints. Our algorithm attempts to
improve the policy by merging and simplifying candidate rules, and then
it selects the highest-quality candidate rules for inclusion in the
generated policy."

**Scope declared honestly, before implementation, per this project's own
"reimplemented never patched" discipline applied to code as well as
prose:** this reimplementation is of the seed-and-generalize-and-select
CORE the abstract describes above -- a real, working instance of that
approach, not a strawman -- and explicitly NOT a reproduction of the
paper's full multi-phase algorithm (their specific `mergeRules`
pseudocode referenced on the authors' own policy-mining page, any
set-valued/"don't-care" generalization beyond simple attribute-dropping,
or their own rule-quality scoring formula, none of which are visible in
the abstract alone and none of which this document claims to reimplement
faithfully). E4's own committed code and this document both say so
plainly; the comparison below is a comparison against this STATED,
scoped algorithm, not against the paper's full method.

**The algorithm, fixed precisely enough to be unambiguous and
deterministic (E4 may not adjust any rule below to change the outcome
once measured):**

1. **Seed order.** Iterate the domain's reachable set in its own
   construction order (`executable_reachable_tuples[_v2/_v4]()`'s own
   returned list order -- already deterministic, no seed, no
   randomness, consistent with this project's own standing convention).
   Skip any tuple already covered by an already-accepted rule (its
   attribute-value assignment satisfies some already-accepted rule's
   pinned constraints) or any tuple that is not granted. The first
   granted, not-yet-covered tuple encountered is the next seed; stop
   when no such tuple remains.
2. **Most specific starting rule.** A candidate rule is a partial
   assignment: a subset of `candidate_properties` each pinned to a
   specific value, the rest wildcarded (unconstrained). The seed's own
   rule starts with EVERY candidate property pinned to the seed's own
   value -- by construction this rule matches only the seed itself,
   hence never matches a denied tuple.
3. **Generalize by dropping conjuncts, one pass, fixed order.** Try
   dropping each currently-pinned property's constraint, in
   `candidate_properties`' own declared order, once each: after
   wildcarding a property, if the resulting more-general rule still
   matches zero denied tuples across the WHOLE reachable set, the drop
   is kept (permanently, for this rule); if it would newly match at
   least one denied tuple, the drop is rejected and that property stays
   pinned for the rest of this rule's construction. One left-to-right
   pass, no backtracking, no re-trying an already-rejected property
   later in the same pass -- this is the specific, deterministic
   generalization order this registration fixes.
4. **Accept the rule; repeat from step 1** with the next uncovered
   seed, until every granted tuple is covered by at least one accepted
   rule.
5. **Simplify (the scoped stand-in for "merging and simplifying"):**
   after all rules are constructed, drop any accepted rule whose entire
   matched-tuple set is already a subset of the union of the OTHER
   accepted rules' matched sets (a redundant rule, contributing no
   coverage of its own) -- checked once, in the rules' own construction
   order, removing a rule only if it is redundant against the rules that
   remain after every earlier removal decision in the same pass (so a
   removal cannot itself be undone by a later removal), not the fuller
   rule-merging their own `mergeRules` procedure performs.
6. **Report.** The final policy is the surviving rule set. The
   comparison attribute set is the UNION of properties pinned (non-
   wildcarded) across every surviving rule -- not any single rule's own
   pinned set, since a sound policy may distribute different attribute
   needs across different rules covering different regions (the hand
   derivation below traces a concrete case of exactly this).

**Determinism and no minimality claim of its own.** Every step above is
fixed and order-dependent by construction (seed order, per-rule
generalization order, simplify order) -- registered as-is because
standard greedy seed-and-generalize/set-cover algorithms carry no
general minimality guarantee (this is the exact "no minimality claim (or
ground truth to check one against)" gap `NOVELTY.md` already names, not
a defect specific to this scoped reimplementation), so a DIFFERENT fixed
order could in principle produce a different, possibly smaller or larger,
attribute union. This document registers ONE specific, fully
deterministic order rather than search over orderings for a favorable
one -- the standing rule that registered semantics are never retuned to
chase a result applies to this choice of order as much as to any other
registered construction.

### Hand-worked example (majority-of-three), verified before registration

Three boolean candidate properties `p, q, r`; reachable = all 8
combinations; `granted(t) = majority(p, q, r)` (at least two of three
true) -- chosen because its TRUE reduct is easy to verify by hand: every
one of `p, q, r` has an individual singleton-perturbation witness (fix
the other two at a 1-1 split and flip the third; e.g. `p=1,q=1,r=0`
(granted) vs `p=0,q=1,r=0` (not granted) witnesses `p`), so the core
already equals `{p,q,r}`, and since the core here is the full candidate
set it is trivially sufficient (Definition 5's own remark) -- `{p,q,r}`
is the unique reduct, cardinality 3, no smaller set possible.

Seeds processed in reachable-set order `(0,0,0)..(1,1,1)` (binary count
of `p,q,r`): the granted tuples encountered, in order, are `(0,1,1)`,
`(1,0,1)`, `(1,1,0)`, `(1,1,1)`.

- **Seed `(0,1,1)`:** start `{p=0,q=1,r=1}`. Drop `p`: `{q=1,r=1}` matches
  `(0,1,1)` and `(1,1,1)`, both granted -- safe, drop kept. Drop `q`:
  `{r=1}` alone matches `(0,0,1)` too, which is NOT granted (majority of
  `0,0,1` is false) -- unsafe, `q` stays pinned. Drop `r`: `{q=1}` alone
  matches `(0,1,0)`, NOT granted -- unsafe, `r` stays pinned. Final rule:
  `{q=1, r=1}`, covering `(0,1,1)` and `(1,1,1)`. Attributes pinned:
  `{q, r}`.
- **Seed `(1,0,1)`** (next uncovered granted tuple -- `(1,1,1)` is
  already covered): start `{p=1,q=0,r=1}`. Drop `p`: `{q=0,r=1}` matches
  `(0,0,1)`, NOT granted -- unsafe, `p` stays. Drop `q`: `{p=1,r=1}`
  matches `(1,0,1)` and `(1,1,1)`, both granted -- safe, drop kept. Drop
  `r`: `{p=1}` alone matches `(1,0,0)`, NOT granted -- unsafe, `r` stays.
  Final rule: `{p=1, r=1}`. Attributes pinned: `{p, r}`.
- **Seed `(1,1,0)`** (last uncovered granted tuple): start
  `{p=1,q=1,r=0}`. Drop `p`: `{q=1,r=0}` matches `(0,1,0)`, NOT granted
  -- unsafe, `p` stays. Drop `q`: `{p=1,r=0}` matches `(1,0,0)`, NOT
  granted -- unsafe, `q` stays. Drop `r`: `{p=1,q=1}` matches `(1,1,0)`
  and `(1,1,1)`, both granted -- safe, drop kept. Final rule:
  `{p=1, q=1}`. Attributes pinned: `{p, q}`.

Every granted tuple is now covered by the 3 rules above; none is
redundant (each covers at least one tuple -- `(0,1,1)`, `(1,0,1)`, and
`(1,1,0)` respectively -- no other rule does), so the simplify step
removes nothing. **Union of pinned attributes across all 3 rules:
`{q,r} union {p,r} union {p,q} = {p,q,r}`** -- exactly the true unique
reduct, cardinality 3, verified by this trace, not assumed. The
mechanism worth naming plainly: no SINGLE rule above pins all three
attributes (each pins only 2, and is a sound, valid rule on its own
local neighborhood), yet the union across the three seeds' own different
local neighborhoods still recovers the full 3-attribute requirement --
confirming the comparison metric (the union, not any one rule) is the
right one to register, and that this scoped algorithm's mechanics behave
correctly and terminate on a real, hand-checkable case before being
pointed at v1/v2/v4.

## Soundness cross-check (registered, checked at E4 runtime)

For every rule the algorithm accepts, step 3's own construction already
guarantees it never matches a denied tuple in the reachable set it was
built against -- but E4 verifies this DIRECTLY, once, over the full
policy (every reachable tuple is granted by the true labels if and only
if it is granted by the mined rule set), rather than trusting step 3's
per-rule invariant to have composed correctly across the whole run. A
soundness failure, if found, is reported as a real finding about this
scoped reimplementation, not silently patched before reporting.

## Comparison metrics and decision rule

For each of the 3 domains: `mined_attributes` = the union defined above;
`this_project_answer` = `derive_authority_contract(...)
.minimum_cardinality_contract` (`src/authority_compiler`, E1). Reported
per domain: `len(mined_attributes)` vs `len(this_project_answer)`,
whether `mined_attributes == this_project_answer` (as sets), whether
`mined_attributes` is a strict superset (mining used avoidably more
attributes), a strict subset (a soundness concern, checked directly
against the cross-check above -- Definition 5's own minimality proof
means a strict subset of a reduct cannot be sufficient, so this case
implies either a bug or a genuine limit of the scoped algorithm, reported
as such either way), or neither (a genuine mismatch in which specific
attributes, not just how many). Wall-clock time and rule count are
reported descriptively per domain (no pass/fail threshold on either, the
same "reported as data" treatment Experiment 1's scaling numbers already
received in `prereg/v5-synthesis.md`).

**Decision rule (two-sided; registered before any domain is run):**
**SUPPORTED** (this project's derivation offers a genuine, measurable
minimality advantage over the scoped mining baseline) iff, on at least
one of the 3 domains, `mined_attributes` is a strict superset of
`this_project_answer` (mining sound but avoidably larger) -- the
specific, concrete form of the abstract "no minimality claim" gap
`NOVELTY.md` already names. **NOT SUPPORTED** iff `mined_attributes ==
this_project_answer` on all 3 domains -- registered as a fully valid
outcome (this scoped greedy algorithm, on these three particular
domains' particular structure, happening to already land on the minimum
every time), not a failed exercise. A strict-subset or genuine-mismatch
outcome on any domain is registered as a THIRD, separately-reported
finding (a soundness concern for the scoped reimplementation specifically,
investigated and reported honestly, not folded into either SUPPORTED or
NOT SUPPORTED) -- the hand-derivation above gives no reason to expect it
(step 3's per-rule construction makes an unsound accepted rule
structurally hard to produce), but it is not asserted impossible without
the soundness cross-check actually running.

## Tractability contingency (registered in advance, not decided after seeing timings)

v1's/v2's reachable sets (7,776 / 24,624 tuples) are large enough that a
naive implementation of step 3's "does this generalization match any
denied tuple" check, run once per candidate-property-drop-attempt per
seed, could be slow; `benchmarks.py`'s own Makefile comment already
documents comparable real costs (discernibility-family construction over
these same reachable sets takes on the order of a minute per domain).
E4 may implement step 3's check efficiently (e.g. grouping/indexing by
attribute projection, the same technique `reduct.sufficiency` already
uses, rather than a linear scan) -- an implementation-speed choice, not a
change to the algorithm's OBSERVABLE rule-by-rule output, exactly the
"engineering discipline, not retuning registered semantics" distinction
`synthesis.py`'s own `contract_change_delta` docstring already draws
between incremental and batch computation. If a domain's full mining pass
still does not complete within 20 minutes wall-clock, E4 stops it,
reports `tractable: false` for that domain with whatever partial rule
set had been accepted so far, and does not redesign the algorithm
post-hoc to force completion -- a real, honestly-reported finding about
this scoped algorithm's own scalability relative to `synthesis.py`'s
SAT-backed approach, itself a legitimate comparison point AuthorityBench
did not originally set out to measure but would not hide if it occurred.

## Machine-readable registration (this commit)

- `prereg/v6-authority-bench.md` (this file) and `src/authority_compiler/`
  (E1: `__init__.py`, `api.py`) plus `test_authority_compiler.py` and
  `pyproject.toml`'s mutation-testing target extension are the only
  additions this commit makes -- registration and packaging only, no
  mining-baseline code and no `authority_bench.py` comparison-runner
  exist yet.
- v1/v2/v4's own domain, loss, and derivation modules
  (`domain.py`/`domain_v4.py`, `losses.py`/`losses_v4.py`,
  `participation.py`, `reduct.py`, `synthesis.py`) are READ, not
  modified, by this document or by `src/authority_compiler`.

## Registration discipline

- No AuthorityBench-running code (the mining baseline, `authority_bench.py`
  or equivalent, any new checker) may run before this file is committed
  and tagged `prereg-p5-v6`, by the author, via the GitHub web interface.
- v0.1-v5's own results, checkers, and outputs stay exactly as committed
  -- byte-frozen apart from the informational `generated_at_head_sha`
  stamp any fresh `make formal` run naturally refreshes.
- The mining algorithm's seed order, generalization order, simplify rule,
  and the 20-minute tractability budget are fixed by this registration;
  Phase E4 may not adjust any of them to change the comparison's outcome
  once measured -- the standing rule "registered semantics are never
  retuned to chase a result," applied here to an algorithm's specification
  for the first time, not only to a domain's construction.
- `NOVELTY.md` gains a seventh amendment once AuthorityBench's outcome is
  known on all 3 domains, stating plainly which registered outcome
  obtained, the same discipline every prior amendment already follows.
