# v7: Cost-Sensitive Contracts on the Code/Cloud Domain (pre-registration)

Status: PRE-REGISTRATION. No code in this commit. To be tagged
`prereg-p5-v7` on this commit, by the author, via the GitHub web
interface (this pipeline never creates or pushes tags). No v7 code (a
cost-model module, any driver script invoking
`synthesis.find_minimum_cost_contract`/`find_minimum_cardinality_contract`
against it, any new checker) may be written before this file is
committed and tagged, per this project's own registration discipline.

v0.1-v0.4's own results, checkers, and outputs, and v4's own CH-B1
result, stay frozen and cited as prior iterations. Nothing already
committed is retroactively edited to match this package's outcome.

## Provenance and motivation

CH-B1 (`prereg/v4-realistic-domain.md`, tag `prereg-p5-v4`) established
that the code/cloud domain's six-property core is *not* sufficient, and
that exactly two seven-property reducts close the gap: the core plus
`branch`, or the core plus `environment` -- a genuine, non-planted
cardinality tie. That result never asked *which* of the two an operator
should prefer; Definitions 4-6 (sufficiency, core, reduct) are silent on
cost. `synthesis.find_minimum_cost_contract` (Milestone D5,
`prereg/v5-synthesis.md`) already implements weighted-MaxSAT cost-aware
synthesis and is already exactness-tested against a small hand-derived
domain (`benchmarks.py`'s XOR-bijection construction) -- but has never
been applied to a real, independently-built domain's own registered
result. This package asks exactly that question, reusing the domain and
the synthesis backend both unmodified: does a registered, source-grounded
observation-cost model select a strictly cheaper contract than at least
one minimum-cardinality reduct, on CH-B1's own domain? Both outcomes are
registered as valid below.

## The domain (reused unmodified; not re-declared)

`domain_v4.py`/`losses_v4.py`, frozen since Milestone C: the same ten
candidate properties, the same six loss predicates, the same declared
background-configuration tables and reachability rules
`prereg/v4-realistic-domain.md` registered. This package adds a cost
model on top; it does not touch, re-derive, or re-run anything about the
domain's own reachable set or loss registry. The frozen CH-B1 facts this
package builds on (`out/checkers/ch_b1_check.json`, unedited):

- Core (6 of 10 candidates, **not** sufficient): `approval_token`,
  `data_classification`, `delegated_role`, `operation`, `repository`,
  `resource_owner`.
- Exactly two minimum-cardinality reducts, both cardinality 7: the core
  plus `branch`, or the core plus `environment`.

## Cost model (Definition 5's "minimum cost", instantiated)

Every candidate property `p` gets a declared, strictly-positive
observation cost, a weighted sum of four components, each a value in
`[0, 1]` (latency is normalized before weighting so no single component
dominates purely from unit choice):

```
cost(p) = alpha * normalized_latency(p)
        + beta  * privacy_exposure(p)
        + gamma * staleness_risk(p)
        + delta * lookup_failure_probability(p)

normalized_latency(p) = min(raw_latency_ms(p) / 250, 1.0)
alpha = 1.0   beta = 2.0   gamma = 1.5   delta = 3.0
```

**Component meaning**, each grounded in which real-world source class a
decision-time lookup of that property would actually hit, not asserted
in the abstract:

- `raw_latency_ms`: expected wall-clock cost of obtaining the value at
  decision time.
- `privacy_exposure`: how much the lookup itself discloses beyond what
  the decision strictly needs (a local field the agent already carries
  discloses nothing new; a remote identity/ownership lookup does).
- `staleness_risk`: probability the observed value is already stale by
  the time the decision executes (local, agent-carried fields are
  observed fresh; remote control-plane state can have changed between
  observation and action).
- `lookup_failure_probability`: probability the lookup itself fails or
  times out at decision time (a field the agent already holds cannot
  fail to be read; a remote service call can).

**Registered weights**: `alpha=1.0, beta=2.0, gamma=1.5, delta=3.0` --
lookup failure weighted highest (a failed observation blocks the
decision entirely), privacy next (an authority gate that itself becomes
a new exposure surface is a real cost this project's own threat model
cares about), staleness third, raw latency lowest (the only component
already bounded to at most 1.0 pre-weighting).

**Registered per-property values** (`raw_latency_ms`, `privacy_exposure`,
`staleness_risk`, `lookup_failure_probability`, source class):

| Property | latency (ms) | privacy | staleness | failure prob. | Source class |
|---|---|---|---|---|---|
| `branch` | 5 | 0.05 | 0.05 | 0.01 | local repository metadata |
| `repository` | 5 | 0.05 | 0.05 | 0.01 | local repository metadata |
| `actor_identity` | 5 | 0.10 | 0.05 | 0.01 | local identity context |
| `delegated_role` | 5 | 0.10 | 0.05 | 0.01 | local identity context |
| `operation` | 1 | 0.02 | 0.00 | 0.00 | local request metadata (the action itself) |
| `environment` | 120 | 0.15 | 0.35 | 0.05 | remote deployment-control lookup |
| `deployment_window` | 120 | 0.10 | 0.40 | 0.05 | remote deployment-control lookup |
| `approval_token` | 250 | 0.20 | 0.15 | 0.20 | remote approval service |
| `resource_owner` | 150 | 0.30 | 0.20 | 0.08 | IAM/CMDB lookup |
| `data_classification` | 100 | 0.35 | 0.10 | 0.03 | policy metadata lookup |

Rationale for the shape of these values (not the specific decimals,
which are declared, not derived): properties an agent already carries as
part of its own request (`operation`, `branch`, `repository`,
`actor_identity`, `delegated_role`) are cheap on every component --
local, already in hand, nothing to fail. Properties requiring a
control-plane or governance-service round trip (`environment`,
`deployment_window`, `approval_token`, `resource_owner`,
`data_classification`) are expensive on every component -- a real network
call, a real chance of staleness between observation and action, a real
failure mode, and (for identity/ownership/classification lookups) real
disclosure beyond the request itself. `approval_token` is registered as
the single most expensive property (a synchronous external approval
service is slower and less reliable than any read-only lookup here).

## Predicted outcome (hand-computed from the table above; registered before any v7 code exists)

`cost(p)` for every candidate, by direct application of the formula
above (shown so the real implementation's own numbers can be checked
against this registration, not the reverse):

| Property | normalized latency | cost |
|---|---|---|
| `branch` | 0.020 | 0.225 |
| `repository` | 0.020 | 0.225 |
| `actor_identity` | 0.020 | 0.325 |
| `delegated_role` | 0.020 | 0.325 |
| `operation` | 0.004 | 0.044 |
| `environment` | 0.480 | 1.455 |
| `deployment_window` | 0.480 | 1.430 |
| `approval_token` | 1.000 | 2.225 |
| `resource_owner` | 0.600 | 1.740 |
| `data_classification` | 0.400 | 1.340 |

Core cost (sum over `approval_token, data_classification,
delegated_role, operation, repository, resource_owner`): **5.899**.
Reduct-plus-`branch` cost: 5.899 + 0.225 = **6.124**. Reduct-plus-
`environment` cost: 5.899 + 1.455 = **7.354**.

**A structural argument, not just an arithmetic coincidence**: every
registered cost above is strictly positive, and sufficiency is monotone
under adding properties (a superset of a sufficient set is always
sufficient -- finer partitions only ever separate more, never fewer,
verdict-disagreeing pairs). So the minimum-COST sufficient contract, over
*all* sufficient subsets of the ten candidates (not just the two known
reducts), cannot properly contain a reduct: if it did, dropping the
extra property would strictly lower cost while staying sufficient,
contradicting minimality. It therefore must itself be inclusion-minimal
-- a reduct. CH-B1's own `exact_reducts()` call already exhaustively
enumerated *every* inclusion-minimal sufficient subset of this exact
domain (not a sample) and found exactly two. Consequently, for *any*
assignment of strictly-positive per-property costs to this already-
frozen domain, `find_minimum_cost_contract` can only ever return one of
those same two reducts -- this package's registered weights and values
decide *which* one and by how much, not *whether* the answer lies
outside that already-known pair. Given the table above, the predicted
answer is core+`branch` at cost 6.124, strictly less than core+
`environment` at cost 7.354 -- a real, non-tied separation (a ratio of
about 1.2x, not a rounding-distance difference).

## Decision rule (two-sided; tie and single-contract outcomes registered explicitly)

**CH-B2 (does a registered, source-grounded cost model select a
strictly cheaper contract than at least one minimum-cardinality reduct,
on the code/cloud domain?)** Decision rule: run
`synthesis.find_minimum_cost_contract` and
`synthesis.find_minimum_cardinality_contract` (both unmodified,
Milestone D) against `domain_v4`/`losses_v4` (unmodified, Milestone C)
under the cost table above; cross-check against `reduct.exact_reducts()`
(unmodified, Milestone B) for the full set of minimum-cardinality
reducts, per the tie rule below.

- **Tie rule**: "the minimum-cardinality set" means the set of *all*
  minimum-cardinality reducts (from `exact_reducts()`), not an arbitrary
  single model a solver happens to return first -- CH-B1 already
  registered that this set has two members here.
- **SUPPORTED** iff the minimum-cost contract found is itself exactly
  sufficient (`reduct.sufficiency` certificate, not a bare boolean) AND
  its registered total cost is strictly lower than at least one member
  of the minimum-cardinality set.
- **NOT SUPPORTED, and registered as a fully valid, fully retained
  result** iff either: (a) every minimum-cardinality reduct has exactly
  equal registered cost (a genuine tie -- cost-awareness had nothing to
  discriminate on), or (b) exactly one minimum-cardinality reduct exists
  (no choice for cost to inform in the first place). Either sub-case is
  reported as NOT SUPPORTED, not hidden or reframed, exactly the standing
  rule "a registered negative outcome is kept."
- Every alternative contract considered (the minimum-cost contract and
  every minimum-cardinality reduct) is separately confirmed exactly
  sufficient via `reduct.sufficiency` before any cost comparison is
  reported -- a **safety-equivalence certificate**: proof that the
  contracts being compared on cost differ only in cost/cardinality, not
  in whether they actually close the loss-discrimination gap.

No hypothesis is registered about the exact numeric cost values the real
code will compute beyond the Predicted outcome section above, which is
itself falsifiable: if the real, executed formula disagrees with the
hand computation above, that contradiction is reported per this
project's own standing rule ("stop if a result contradicts the
preregistration and report the contradiction"), not silently reconciled
by adjusting either the code or this document.

## Machine-readable registration (this commit)

- `prereg/v7-cost-sensitive-contracts.md` (this file) is the only file
  this commit touches. The cost-model formula, the four registered
  weights, and the ten-row per-property parameter table above are
  registered by the table text itself -- Package C's implementation
  transcribes them into a cost-model module unchanged, not re-decided
  during implementation.
- No v7 code (a cost-model module, a driver script, any new checker)
  exists yet or is written in this commit -- registration only.

## Registration discipline

- No v7 cost-model or driver code may run before this file is committed
  and tagged `prereg-p5-v7`, by the author, via the GitHub web interface.
- `domain_v4.py`/`losses_v4.py` and every v0.1-v0.4/CH-B1 result, checker,
  and output stay exactly as committed -- byte-frozen apart from the
  informational `generated_at_head_sha` stamp any fresh `make formal` run
  naturally refreshes.
- The cost-model formula, the four weights, and the ten per-property
  values above are fixed by this registration; the implementation may
  not adjust a weight or a per-property value to change CH-B2's outcome
  once measured -- exactly the standing rule "registered semantics are
  never retuned to chase a result."
- `NOVELTY.md` gains an amendment once CH-B2's outcome is known, stating
  plainly which registered outcome obtained, the same discipline every
  prior amendment already follows.
- This package's own reviewer rules (verbatim, binding on this
  registration and its implementation alike): do not alter any frozen
  prior result; registration precedes implementation for any new
  scientific result; separate bug fixes from new evidence; do not tune
  parameters after seeing outcomes; preserve negative findings; run the
  full release-check before commit; produce a machine-readable result
  artifact and a concise human summary; do not change scientific wording
  unless the underlying evidence changed; stop if a result contradicts
  the preregistration and report the contradiction; never use prose to
  compensate for a missing test or certificate.
