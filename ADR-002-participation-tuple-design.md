# ADR-002: Participation Tuple Design — Policy as Configuration, Not a Candidate Property

**Status**: Accepted
**Date**: 2026-08-31
**Author**: SARC Suite Demo (paper 5, sarc-authority-derivation)

## Context

Phase 2 implements Definition 1 (participation): property p is
authority-bearing for loss model M iff there exist executable-reachable
tuples a, a' differing only in p whose M-verdicts differ.

The first implementation modeled the four-tuple (action, context,
evidence, control_state) by exposing per-role policy -- entitlement
ceiling, temporal window, allowed resource classes -- as three separate
`context` fields, each populated per tuple by looking up
`declared_parameters[actor_role]` from `loss-model.yaml`.

Running `derive.py` against this design (during Phase 2 development,
before any Phase 3 experiment or CH-A1-CH-A4 result existed) produced:

```
P* (7): [budget_remaining, consumed_grant_ids, day, frozen, grant_id, order_value, resource_class]
coverage list (5): [actor_role, role_allowed_classes, role_entitlement_ceiling, role_window, workflow]
```

`actor_role` and all three resolved-policy context fields landed in the
coverage list.

## Diagnosis

This is mathematically correct under that tuple design, and structural,
not a numeric coincidence of the specific declared values: each context
field was generated as `policy[actor_role][field]`, a pure deterministic
function of `actor_role`. Definition 1's witness search holds every
field except the one under test fixed. For a context field, that means
`actor_role` is held fixed -- and a field that is a pure function of an
always-fixed field can never independently vary, by construction, for
ANY choice of declared values. Symmetrically, `actor_role` itself could
only participate via a pair of *different* roles sharing every context
value except the one field being tested; because every declared role's
three policy values move together (either identical across two roles --
`agent-replenish` and `agent-w2-replenish` are declared with identical
ceiling/window/classes -- or different in more than one field at once),
no such pair exists either. All four fields are structurally coupled and
none can be isolated.

The result correctly answers the question that specific tuple design
asked, but the question was wrong for this artifact's purpose: P*
is meant to name the fields a working authority gate must observe. A
gate that observes neither `actor_role` nor the resolved ceiling/
window/classes cannot evaluate `order_value_beyond_entitlement`,
`procurement_outside_temporal_window`, or `resource_class_not_entitled`
at all -- it has no way to know which threshold applies to a given
decision. The derived P* would describe an unimplementable gate.

## Decision

Per-role policy is declared **background configuration** the gate is
built with, not a per-decision observable input, and is therefore out of
Definition 1's candidacy -- the same way a fixed predicate threshold or
`SEED` is not itself a candidate property. Concretely:

- `domain.StateTuple` drops the three context fields; `CANDIDATE_
  PROPERTIES` is nine fields (action: actor_role, resource_class,
  order_value, day, workflow; evidence: grant_id; control_state:
  consumed_grant_ids, budget_remaining, frozen).
- `domain.role_policy()` still parses the three `declared_parameters`
  mappings from `loss-model.yaml`, but returns them as a lookup table,
  not tuple field values.
- The three policy-dependent predicates (`losses.py`) become
  **factories**: `make_order_value_beyond_entitlement(policy)` etc.
  close over the policy table and read `policy[t.actor_role][...]`
  internally. `load_loss_registry(loss_model)` builds the bound registry.
- `actor_role` is now a genuine, independently observable candidate
  property again, exactly as `role` already is in the imported
  baseline's own `specs/authority.yaml` predicates (`ctx.args.role`,
  compared against `ctx.args.allowed_roles`) -- the baseline never hits
  this coupling because it has no *per-role* table, only one flat
  scenario-wide cap and allow-list, so `role` and the fields it is
  checked against were never coupled to begin with. Paper 5's
  contribution (per-role entitlement, window, and class policy) is
  exactly the enrichment that first creates the coupling risk; ADR-002
  is the record of catching and correctly modeling it.

Re-running `derive.py` against the corrected design gives a P* that
includes `actor_role` directly (see `out/checkers/derivation_output.json`
once Phase 2 is complete) -- a gate that observes the nine P*-and-
coverage-partitioned fields plus the baked-in policy table can actually
evaluate all six losses.

## What this changes about the paper's claims

None of the six declared losses, none of CH-A1-CH-A4's decision rules,
and none of the paper's central definitions changed. Only the
*representation* of one input space changed, before any experiment
touched it. `prereg-p5-v1`'s original `pair-test-grid.yaml` (visible at
that tag, not rewritten) is left as an honest record of the initial,
flawed representation; `pair-test-grid.yaml` on the branch history after
this ADR is the corrected nine-property version every later phase
(including all CH-A1-CH-A4 results) actually uses.

## Threats to validity this ADR itself surfaces

This is exactly the "pair testing probes the representation, not the
loss model" caveat CH-A2 is pre-registered to name (`prereg/
hypotheses.md`) -- generalized one level up: *the participation
criterion itself probes whatever tuple representation it is handed*.
A badly chosen representation (fields structurally coupled to a field
the test holds fixed) can make Definition 1 under-report participation
in a way that is mathematically sound for that representation and
practically misleading about what a gate must observe. The paper's
limitations section states this explicitly rather than leaving it only
in this ADR: the derivation is only as trustworthy as the tuple design
it is run against, and choosing that design is a modeling judgment this
artifact does not itself derive or verify.

## Alternatives considered

- **Keep context fields, add a "coupled group" notion to Definition 1**
  (report groups of jointly-varying fields as participating, not just
  singletons). Rejected: the task brief's Definition 1 is stated in
  terms of a single differing property p; generalizing it to subsets is
  a materially different (and more complex) definition the brief does
  not ask for, and risks combinatorial blowup (checking all subsets, not
  just all singletons, of even nine candidates is no longer small).
- **Keep context fields, treat `actor_role` as non-candidate instead**
  (drop only `actor_role`, keep the three resolved fields as
  candidates). Rejected: this does not fix the underlying problem --
  the three resolved fields would still never vary (nothing else
  produces them), so P* would still lack any way to select the right
  threshold; it only relocates which name is missing.
