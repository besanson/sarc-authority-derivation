# v5: Synthesis Benchmarks -- Scaling and Cost-Awareness (pre-registration)

Status: PRE-REGISTRATION. No code beyond D1 (`discernibility.py`) and D2
(`synthesis.py`), both already committed and unmodified by this document.
To be tagged `prereg-p5-v5` on this commit, by the author, via the
GitHub web interface (this pipeline never creates or pushes tags). No
benchmark-running code (`benchmarks.py`, or any script executing the
experiments below) may be written before this file is committed and
tagged, per this project's own registration discipline.

v0.1-v4's own results, checkers, and outputs stay frozen and cited as
prior iterations. Nothing already committed is retroactively edited to
match v5's outcome.

## Provenance and motivation

D1/D2 built a general-purpose SAT/MaxSAT contract-synthesis engine and
machine-checked it against this artifact's own real, small (9-10
candidate property) models. Two questions that requires purpose-built
experiments, not just re-running the existing models:

1. **Does the engine scale** past the point exhaustive enumeration
   (`reduct.exact_reducts()`, 2^n subsets) stops being affordable?
2. **Does minimum cardinality ever diverge from minimum cost** -- i.e.,
   is `find_minimum_cost_contract` a distinct, useful capability, or
   does it always agree with `find_minimum_cardinality_contract` on the
   models this artifact happens to have built so far?

Both experiments reuse `discernibility.py`/`synthesis.py` unmodified;
neither is a change to the engine, only to what it is pointed at.

## Experiment 1: scaling benchmark on synthetic families with planted reducts

**The planted-reduct construction** (registered here, to be transcribed
into `benchmarks.py` unchanged in Phase D5): for candidate-property
count `n` and a FIXED planted reduct size `k = 5`, `n` boolean (0/1)
properties are named `p_1 .. p_n`; the first 5 (`p_1 .. p_5`) are the
*signal* properties, the remaining `n - 5` are *noise*. The reachable
set is exactly `k + 1 = 6` tuples, regardless of `n` (this is what makes
`n = 100` tractable at all -- the reachable set does not grow with `n`):
one tuple with every signal property set to 1 (call it `T_0`), and for
each `i` in `1..5`, one tuple `T_i` identical to `T_0` except `p_i = 0`.
Every noise property is held at the SAME fixed value (0) across all 6
tuples -- never varied, so by Definition 1's own witness search it can
never have a perturbation witness, and is therefore correctly excluded
from the core without needing to be exercised at every combination.
Verdict: `M(tuple) = p_1 AND p_2 AND p_3 AND p_4 AND p_5` (noise
properties never read). `T_0` -> True; every `T_i` -> False (`p_i = 0`
breaks the AND) -- `T_0` vs. `T_i` witnesses `p_i`'s own necessity
directly, for every `i` in `1..5`, so the core is proved (not assumed)
to already equal all 5 signal properties, hence sufficient, hence
(Proposition 1' claim 3) the unique reduct -- exactly the `n = 10`
case's own cross-check via `reduct.exact_reducts()` (2^10 = 1,024
subsets, still cheap) confirms this identically to the construction's
own by-hand proof above, before trusting the same construction
unchecked at `n = 30, 50, 100` where exhaustion is no longer feasible.

**Registered runs**: `n` in `{10, 30, 50, 100}`, once each (the
construction is deterministic -- no seed, no randomness, so repeated
runs at the same `n` are not additional evidence). **Metrics**, per run:
- `exact`: does `find_minimum_cardinality_contract` return exactly
  `{p_1, p_2, p_3, p_4, p_5}` -- checked against the CONSTRUCTION's own
  known-by-design answer at every `n`, and additionally against
  `reduct.exact_reducts()`'s independent, from-first-principles answer
  at `n = 10` only (where 2^10 subsets is affordable; `n = 30/50/100`
  are not cross-checked against exhaustion -- 2^30 alone is already
  infeasible -- consistent with D2's own "where exhaustion is feasible"
  scoping).
- `wall_time_seconds`: wall-clock time of the `find_minimum_cardinality_
  contract` call alone (`time.perf_counter()`, stdlib, no new
  dependency), separately from family-construction time (also reported,
  since the reachable set is fixed-size but the discernibility family
  and the CNF both still scale with `n`, the SAT variable count).
- `peak_memory_bytes`: `resource.getrusage(resource.RUSAGE_SELF).
  ru_maxrss` (stdlib, no new dependency) sampled immediately after the
  call, reported as a delta from a baseline sample taken before it.

No pass/fail hypothesis is registered for the scaling numbers themselves
(wall time and memory are reported descriptively, as data, not tested
against a threshold) -- `exact` is the only boolean-scored metric, and it
is expected to hold at every `n` given the construction's own proof
above; a failure at any `n` is a real, reportable finding (an engine bug
or a proof error), not smoothed over.

## Experiment 2: cost-aware synthesis

**The observation-cost model** (registered here, applied unchanged in
Phase D5): each candidate property `p` in a tested domain is assigned
four declared sub-scores, each on a `[0, 1]` scale, no further weighting
applied (a plain sum, not a weighted one -- a weighted combination is
itself a modeling choice with no principled weights available yet, so
the un-weighted sum is the honest default, not a partial analysis
presented as complete):

- `latency(p)`: cost of the round trip to observe `p` at decision time
  (0 = already in hand, e.g. from the request itself; 1 = an external
  call).
- `privacy(p)`: sensitivity of observing `p` (0 = non-sensitive; 1 =
  directly identifying or regulated data).
- `staleness(p)`: how quickly `p`'s observed value can go stale relative
  to the decision (0 = always current; 1 = frequently stale by the time
  it is read).
- `failure_probability(p)`: probability the observation itself fails or
  errors (0 = never; 1 = frequently).

`cost(p) = latency(p) + privacy(p) + staleness(p) + failure_probability(p)`,
range `[0, 4]`. Every declared cost must be strictly positive
(`synthesis.find_minimum_cost_contract`'s own precondition, D2) -- a
property scoring exactly 0 on all four sub-factors is assigned a floor
cost of `0.01` rather than `0`, registered here so Phase D5 does not
have to make that call ad hoc.

**Registered test domains**: this artifact's three existing real models
(v1, v2, v4) -- each already known (CH-A10, CH-B1) to have either a
unique reduct (v1, v2) or reducts of EQUAL cardinality (v4, both 7) --
PLUS one new, purpose-built synthetic domain, registered here by
construction, hand-derived and proved below (to be independently
machine-checked in D5 against `reduct.exact_reducts()`, not trusted from
the derivation alone): three candidate properties `a` (domain `{0, 1, 2,
3}`), `b1`, `b2` (both boolean). Reachability is restricted to exactly
four tuples via a declared bijection `a = 0 <-> (b1=0, b2=0)`,
`a = 1 <-> (b1=0, b2=1)`, `a = 2 <-> (b1=1, b2=0)`, `a = 3 <-> (b1=1,
b2=1)`. Verdict: `M = True` iff `a` in `{1, 2}` (equivalently, `M = b1
XOR b2`). By hand: `{a}` is sufficient (verdict is a direct function of
`a`) and minimal (the empty set is not sufficient: `a=0` and `a=3` both
give `False` but `a=1`/`a=2` give `True`, so *some* uniformity failure
exists, meaning at least `a` is needed) -- a reduct of cardinality 1.
`{b1}` alone is not sufficient (`b1=0` covers both `a=0` (`False`) and
`a=1` (`True`)); `{b2}` alone is not sufficient by the symmetric
argument; `{b1, b2}` together is sufficient (they jointly determine `a`
via the bijection, hence the verdict) and, since neither singleton
alone works, minimal -- a second reduct, of cardinality 2. Declared
costs: `cost(a) = 4.0` (ceiling of the model, e.g. an expensive
external-identity lookup); `cost(b1) = cost(b2) = 0.5` each (e.g. two
already-in-hand boolean flags), so `{b1, b2}`'s total cost (1.0) is
lower than `{a}`'s (4.0) despite its larger cardinality.

**Decision rule (two-sided; either outcome is a result, not assumed
from the by-hand construction above until D5 machine-checks it):**
**SUPPORTED** iff, on at least one of the four registered domains,
`find_minimum_cardinality_contract`'s result and `find_minimum_cost_
contract`'s result are different SETS -- the measured cost delta
(`cost(minimum_cardinality_contract) - cost(minimum_cost_contract)`,
expected positive on the domain where they diverge) is reported
alongside, not just the fact of disagreement. **NOT SUPPORTED** iff
every one of the four domains' two backends agree exactly -- registered
as a fully valid, reportable outcome (this project's own standing rule:
"a registered negative outcome is reported as NOT SUPPORTED and kept"),
though the hand-derivation above is offered as a reason to expect
SUPPORTED, not as a substitute for actually running it.

## Machine-readable registration (this commit)

- `prereg/v5-synthesis.md` (this file) is the only file this commit
  touches. `discernibility.py`/`synthesis.py` (D1/D2, already committed)
  are read, not modified, by the benchmarks this document registers.
- No benchmark-running code (`benchmarks.py`, or equivalent) exists yet
  or is written in this commit -- registration only.

## Registration discipline

- No v5 benchmark code may run before this file is committed and tagged
  `prereg-p5-v5`, by the author, via the GitHub web interface.
- v0.1-v4's own results, checkers, and outputs stay exactly as committed
  -- byte-frozen apart from the informational `generated_at_head_sha`
  stamp any fresh `make formal` run naturally refreshes.
- The planted-reduct construction (Experiment 1) and the cost-aware
  synthetic domain's bijection, verdict, and declared costs
  (Experiment 2) are fixed by this registration; Phase D5 may not adjust
  either to change a metric or the two-sided hypothesis's outcome once
  measured -- the standing rule "registered semantics are never retuned
  to chase a result."
- `NOVELTY.md` gains a sixth amendment once both experiments' outcomes
  are known, stating plainly which registered outcome obtained for each,
  the same discipline every prior amendment already follows.
