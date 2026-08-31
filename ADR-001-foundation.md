# ADR-001: Foundation — Imported Baseline and Ported Infrastructure

**Status**: Accepted
**Date**: 2026-08-31
**Author**: SARC Suite Demo (paper 5, sarc-authority-derivation)

## Context

Paper 5 derives, from a declared loss model, the minimal set of
properties a pre-action authority gate must observe, in the
remediation-coupled setting sarc-suite-one-pass (arXiv 2608.18360,
commit 782261e) already established. The task brief requires this
artifact to (a) treat sarc-suite-one-pass and its three composed engines
as a pinned, read-only imported baseline that must itself pass its own
release-check before any new code is built, and (b) reuse
sarc-suite-one-pass's gated-pipeline machinery rather than reinvent it,
"as libraries or copied-with-attribution modules recorded in an ADR."

sarc-suite-one-pass exposes no installable package for its own
demo-repo scripts (only the three engines it composes are packaged;
see its `pyproject.toml` comment: "This repo has no packaging config of
its own"). A library-import boundary is therefore only available for the
three engines themselves; the five named pipeline components (release-
check pattern, citation pipeline, slots pipeline, sweep/CI machinery,
PROOF-STATUS linter) are plain scripts run in place, not distributed
modules. This ADR records the resulting per-component decision.

## Decision

### Sibling layout and the imported-baseline gate

`engines.lock` pins four siblings: `sarc-suite-one-pass` at 782261e (the
paper 4 artifact itself, not just its three engines) plus `dqSarc`,
`sarc-governance`, and `Greensarc` at the exact commits
sarc-suite-one-pass's own `engines.lock` names. `bootstrap.sh` clones all
four, delegates engine installs and the LaTeX toolchain to
sarc-suite-one-pass's own `bootstrap.sh` (avoiding a second, divergent
copy of that install logic), then runs `make release-check` inside the
pinned sarc-suite-one-pass sibling and fails loudly if it does not print
`release-check: ALL CHECKS PASS`. This repo's own bootstrap is not
considered complete until that baseline is verified — task brief Phase
0: "it must pass before you build anything."

**Boundary**: this repo never edits sarc-suite-one-pass or the three
engines (task brief, Out of scope). New code imports `sarc_governance`
directly, the same way sarc-suite-one-pass's own `composition.py` does,
and registers its own new predicates into that engine's own predicate
registry (Phase 2: the derived-P* policy's predicates and the
consumable execution-grant predicate) rather than modifying the engine
or the demo repo to add them.

### Per-component porting decision

| Component | Source | Decision | Rationale |
|---|---|---|---|
| Release-check gate pattern | `Makefile`'s `release-check` target | Copied-with-attribution (Makefile target rewritten for this repo's own file names, same structure: full test suite, formal double-run byte-identity, then this paper's own build gate) | Not a distributable script — a Makefile recipe |
| Citation pipeline | `citation_check.py` | Copied-with-attribution, near-verbatim (only the default CLI target filename changed) | Already fully generic (parametrized by paper path + whitelist path); no engine-specific logic to strip |
| Slots pipeline | `populate_draft.py` | Copied-with-attribution, verbatim | Already fully generic (`[GENERATED: key]` substitution + slot-only-diff verification has no domain-specific content) |
| PROOF-STATUS linter | `checkers/proof_status_lint.py`, `checkers/_provenance.py` | Copied-with-attribution, verbatim | Already fully generic (regex over `PROOF-STATUS:` tags and `checkers/*.py` references; `DEFAULT_TARGETS` still resolves correctly since this repo also names its proofs file `appendix-a-proofs.md`) |
| Sweep and CI machinery | `sweep.py`'s structure (seed loop, per-seed checkpointing, `mean_ci95`'s order-stable t-based CI), `.github/workflows/ci.yml` | Pattern ported, not copied verbatim — the loop shape, checkpoint-to-`out/results/sweep/seed_<seed>.json` convention, and `math.fsum`-over-sorted-inputs CI helper are reused, but the scenario/metric bodies are rewritten from scratch in Phase 3 against this paper's own baseline/derived-P*/over-inclusive policies, since sarc-suite-one-pass's CH1-CH8 metrics do not exist in this paper's domain | The statistical/checkpointing scaffolding is domain-independent; the metrics it wraps are not |
| Engines (dqSarc, sarc-governance, Greensarc) | Published Apache-2.0 packages | Library import (`pip install -e`, unchanged) | Already packaged and versioned; this is what "library" means for the three components that actually are libraries |

### What is not ported

`composition.py`'s two-phase remediate-regate protocol, `runner.py`'s
scenario harness, and `suite_sim.py`'s retail simulation are **imported
and called**, not copied: Phase 3 experiments run against the pinned
sarc-suite-one-pass sibling's own modules (added to `PYTHONPATH` at
experiment-run time, read-only) exactly as this repo's own code imports
`sarc_governance`, rather than duplicating simulation logic this repo
would then have to keep in sync by hand.

## Consequences

- A `pip install -e` boundary exists only for the three engines;
  everything ported from sarc-suite-one-pass itself is a copied file
  with an attribution header pointing back to commit 782261e, editable
  independently of upstream from this point on (upstream is frozen at
  a pinned commit in any case).
- If sarc-suite-one-pass's own pipeline scripts change upstream, this
  repo's copies do not pick up the change automatically — acceptable
  because the imported baseline itself is pinned by `engines.lock`, so
  "drift" is not possible without a deliberate re-pin.
- Reusing `sweep.py`'s checkpoint-per-seed convention and `mean_ci95`
  helper (rather than inventing a new statistical convention) keeps
  Phase 3's 30-seed sweep directly comparable in method, if not in
  metric, to paper 4's.

## Alternatives considered

- **Vendor sarc-suite-one-pass's scripts via a git submodule instead of
  copying.** Rejected: the task brief's "libraries or copied-with-
  attribution modules recorded in an ADR" language anticipates exactly
  the copy-with-attribution path taken here, and a submodule would still
  need this same attribution/ADR treatment while adding tooling
  overhead (submodule init/update) the brief does not ask for.
- **Reimplement the pipeline components from scratch instead of
  porting.** Rejected: the brief explicitly asks for porting, and the
  five components above are already generic and gate-tested in
  sarc-suite-one-pass across four review rounds; reimplementing would
  reintroduce risk the existing, reviewed implementation already
  retired.
