# Deriving Authority: A Machine-Checkable Derivation from a Declared Loss Model to the Minimal Property Set a Pre-Action Authority Gate Must Observe

Companion artifact: `sarc-authority-derivation`. Paper 5 of the SARC
series, built on the pinned `sarc-suite-one-pass` artifact (arXiv
[2608.18360](https://arxiv.org/abs/2608.18360), commit `782261e`) as a
read-only imported baseline (`ADR-001-foundation.md`).

**Status**: draft v0.1. Not submission-ready, not independently reviewed.
See the human checklist at the end of this document.

## Abstract

Prior work in this setting either declares which properties an
authority gate must observe (this artifact's own imported baseline,
`sarc-suite-one-pass`'s `specs/authority.yaml`: role plus a single value
cap) or derives safety constraints from losses as a human-driven analyst
methodology (the STPA lineage). We formalize a participation criterion
-- property p is authority-bearing for a declared loss model M iff two
executable-reachable actions differing only in p produce different
M-verdicts -- and a derivation procedure that computes the minimal
sound property set P\* and an honestly emitted coverage list of
excluded properties, in the remediation-coupled setting `sarc-suite-one-
pass` establishes, where a control's own remediation changes which
actions are reachable at all. We machine-check P\*'s soundness and
minimality exhaustively over the declared finite model, independently
recover it via a formalized pair-testing method (credited to an
independent replication of the imported baseline), and add a consumable
per-execution grant mechanism that binds one authorization to exactly
one sealed execution. Against the real imported simulation, 30 seeds,
both workflows: [GENERATED: abstract_results_sentence]

## 1. Introduction

Once a pre-action authority gate is permitted to observe only the
properties someone thought to declare, the gate is exactly as complete
as that person's foresight -- and no more. `sarc-suite-one-pass`'s own
imported baseline (`specs/authority.yaml`) observes two things: whether
the acting role is on an allow-list, and whether an order value exceeds
a single scenario-wide cap. Its own roadmap names the gap directly:
"Authority-completeness: deriving which properties must be
authority-bearing from a consequence model, rather than declaring them"
(`sarc-suite-one-pass`'s `README.md`), motivated by an independent
replication's coverage-boundary findings (`REPLICATIONS.md`; Section 4
below).

This paper closes that gap for one declared loss model. We do not derive
the loss model itself -- that stays a human, out-of-scope act of
judgment (Section 8) -- but given one, we derive, deterministically and
machine-checkably, the minimal property set an authority gate must
observe to correctly detect every loss the model declares, and we
honestly emit the properties it does not need, rather than silently
dropping them.

### 1.1 Novelty fence

STPA derives safety constraints from declared losses as an analyst
methodology; ABAC mining reconstructs policies from existing grants;
interference-style criteria detect dependence but do not derive. This
paper contributes a formal participation criterion over the
executable-reachable action set, a machine-checkable derivation from a
declared loss model to the minimal property set a pre-action authority
gate must observe, with the excluded residue emitted as a derived
coverage list, in a setting where remediation changes the reachable set.

(Verbatim from `NOVELTY.md`, Phase R. See Section 3 for the full
per-cluster novelty comparison this fence summarizes, and
`verified-citations.json` for every source's fetch-verification record.)

## 2. Setting

We inherit `sarc-suite-one-pass`'s retail simulation without editing it:
real UCI Online Retail data (CC BY 4.0, `data/PROVENANCE.md`), a
deterministic decision stream (`suite_sim.RetailSimulation`), two
workflows (W1 daily, W2 weekly commitment, `prereg/w2-workflow.md`
carried over by reference), and two remediation operators (evidence
substitution, resource downroute) whose composition paper 4 already
establishes is sound under `remediate_regate` (`composition.py`,
Theorem 1 there). This paper adds no new remediation logic; it asks a
different question of the same remediation-coupled setting: which
properties must the authority gate observe, given what remediation can
change about the reachable action set?

We declare six losses (`prereg/loss-model.yaml`, tagged `prereg-p5-v1`)
as machine-evaluable hazard predicates over an (action, context,
evidence, control_state) four-tuple: order value beyond a per-role
entitlement ceiling, procurement outside a per-role permitted temporal
window, action on a resource class the role is not entitled to, replayed
execution of a consumed authorization, spend against a depleted
resource-gate budget, and action on a control state marked frozen. Nine
per-decision fields are candidates for observation (`domain.py`'s
`CANDIDATE_PROPERTIES`); per-role policy itself (the entitlement
ceiling/window/allowed-class tables) is declared background
configuration the gate is built with, not a per-decision observable
input -- see `ADR-002-participation-tuple-design.md` for why an earlier
design that exposed resolved policy values as separate fields produced a
mathematically correct but practically unimplementable P\*.

## 3. Related work (novelty comparison)

One paragraph per neighbouring cluster, reproduced from `NOVELTY.md`
(Phase R; every source fetch-verified in `verified-citations.json`):

**STPA and its descendants.** Leveson and Thomas's STPA Handbook (2018)
establishes System-Theoretic Process Analysis: a structured but
human-driven analyst process. Young and Leveson's STPA-Sec (CACM 2014)
carries the same process into security; Rismani, Dobbe, and Moon's PHASE
(2024) and Mylius (2025) into AI governance and frontier-AI hazard
analysis; Qi et al.'s DeepSTPA (2023) into the ML development lifecycle.
In every case the output is human-authored, expert-reviewed constraints,
not a machine-checked minimal property set, and none formalize
soundness or minimality as machine-checkable claims over an enumerated
model.

**ABAC policy mining.** Xu and Stoller (TDSC 2015) establish the
problem of reconstructing which attributes already participate in an
*existing* deployed policy from grants and attribute data; Nobi et al.'s
2022 survey catalogues the ML extensions of that same reconstruction
problem. This paper derives forward, from a declared loss model to a
*new* gate's minimal property set, with a machine-checked soundness and
minimality guarantee mining has no ground truth to check itself against.

**Policy-language completeness.** Crampton and Morisset's PTaCL (POST
2012) and Crampton and Williams's canonical-completeness result (SACMAT
2016) establish what a policy *combination* language can express once
the participating attributes are already fixed. Neither asks which
attributes must be observed in the first place; this paper contributes
exactly that prior question.

**Non-interference.** Goguen and Meseguer (1982) define non-interference
as a semantic *check* of whether a dependence exists between two fixed
parties in a given system. This paper's Definition 1 borrows the
underlying comparison -- does changing X change the verdict? -- but
turns it into a derivation swept over every candidate property against
every loss predicate, with soundness and minimality verified
exhaustively, not a single dependence check.

**Counterfactual fairness.** Kusner et al. (NeurIPS 2017) evaluate one
pre-chosen sensitive attribute's counterfactual invariance, once. This
paper generalizes the same comparison to every candidate property
against a declared loss model, with an exhaustive minimality result the
fairness literature neither claims nor checks.

## 4. The Moona Intelligence replication and its method's origin

An independent replication of the imported baseline (Moona Intelligence,
published 28 August 2026 under the organisation's then-name, Belay
Intelligence; `REPLICATIONS.md`), beyond confirming a clean-clone
reproduction of `sarc-suite-one-pass`'s full release-check, ran eight
adversarial pair tests against the deployed `specs/authority.yaml` on a
separate branch with zero edits to existing code, and reported four
coverage boundaries: resource identity is present in the execution
context but not authority-bearing in the configured policy; the policy
is role-based rather than actor-specific; temporal context is recorded
but not authority-bearing; and, in finding A7,

> "nothing in the authority path exposes an authorization identifier,
> an approval identifier, a nonce, or any consume on use mechanism that
> would bind one authority verdict to exactly one execution"

(Moona Intelligence, 2026). This is the method's origin for CH-A2's
pair-testing formalization below, and finding A7 is this paper's direct
motivation for Section 6's grant mechanism. On the scope of the eight
tests themselves, the report is explicit about what it does and does not
claim:

> "I want to be plain about the framing here. Nothing below is a report
> of SARC breaking. It is a report of what SARC's own authority policy
> was configured to look at, produced by testing that policy directly
> rather than by editing it."

(Moona Intelligence, 2026). We take this framing seriously in Section 7
below: our own formalized pair-test checker inherits exactly this
scope limit, stated as a registered blind spot, not smoothed over.

## 5. Definitions

**Definition 1 (participation).** Property p is authority-bearing for
loss model M iff there exist executable-reachable tuples a, a′
differing only in p whose M-verdicts differ.

**Definition 2 (the minimal participation set P\*).**
P\* = {p in candidate_properties : p is authority-bearing for M}.

**Definition 3 (the derived coverage list).**
coverage_list = candidate_properties − P\*, emitted, not dropped.

"Executable-reachable" (task brief) includes post-remediation actions:
`prereg/pair-test-grid.yaml`'s reachability section characterizes what
the imported baseline's two remediation operators can produce (evidence
substitution: any other order-value point in the declared domain,
either direction; resource downroute, W2 only: strictly lower only),
and `domain.executable_reachable_tuples()` is the union of rank-0 and
remediation-reachable tuples.

## 6. The derivation procedure and the grant mechanism

`derive.py` wires the declared loss model (`losses.load_loss_registry`)
against the executable-reachable set (`domain.py`) through
`participation.compute_p_star`, which finds a witness for each candidate
property by grouping reachable tuples on every OTHER field and checking
for a verdict difference within each group -- an O(n) sweep, not O(n²).
The result, `out/checkers/derivation_output.json`
(`schemas/derivation_output.schema.json`):

- P\* ([GENERATED: p_star_count] of [GENERATED: candidate_property_count]
  candidates): [GENERATED: p_star_list]
- Coverage list ([GENERATED: coverage_count]): [GENERATED: coverage_list]
- Executable-reachable tuples enumerated: [GENERATED: grid_size_reachable]

Every participating property carries a recorded witness pair, checked
independently (not re-asserted) by `checkers/participation_check.py`
(Proposition 1, `appendix-a-proofs.md`).

**Grant binding.** Directly motivated by finding A7 above,
`grant.GrantLedger` binds one consumable execution-grant id to the
content hash (sha256, canonical JSON) of one sealed post-remediation
action. Issuance and every consumption attempt -- admitted or rejected
-- append a new entry; nothing is mutated in place, mirroring the
imported baseline's own governed-buffer write-history design. The
single-use invariant is machine-checked exhaustively over 85 sequences
(`checkers/grant_check.py`, Proposition 3).

## 7. Pair testing, formalized (CH-A2)

`checkers/pairtest_check.py` formalizes the eight-test method Section 4
credits, generalized from eight hand-picked cases to a full sweep of the
declared grid: for every reachable tuple as a baseline and every
candidate property, swap in every other declared domain value for that
property alone and check for a verdict change -- a one-factor-at-a-time
sweep, algorithmically independent of Definition 1's own
fingerprint-grouped search. Result: [GENERATED: ch_a2_pairtest_reachable_tuples]
tuples swept; missed participants: [GENERATED: ch_a2_missed_participants];
false participants: [GENERATED: ch_a2_false_participants]. **CH-A2:
[GENERATED: ch_a2_status]**.

**Registered blind spot**, in the same spirit as Section 4's quoted
framing: pair testing probes the representation -- `pair-test-grid.yaml`'s
declared finite domain values -- not the loss model. It cannot detect a
hazard whose true threshold falls strictly between two declared values,
or a property never represented in the grid at all. This is a structural
limit of the method, not a defect in this run; `checkers/pairtest_check.py`
emits the note in its own machine output, not only here.

## 8. Empirical section (CH-A1, CH-A3, CH-A4, and the overderivation ablation)

`experiments.py` runs the real imported decision stream (real UCI data,
real per-class defect injection, real `sarc_governance` evaluation of
the imported `specs/authority.yaml` for the baseline arm) through three
policies per decision -- baseline declared-only, derived-P\*, and an
over-inclusive ablation that adds one spurious rule (escalate whenever
`workflow == W2`, the one derived-non-participating candidate) -- plus a
grant-binding on/off ablation with an injected replay rate, across all
30 registered seeds (`prereg/seeds.json`) and both workflows.

**CH-A1** (derived coverage strictly exceeds the baseline). The
declared-only baseline missed [GENERATED: ch_a1_baseline_missed] of
[GENERATED: ch_a1_true_violations] declared loss-violations across the
sweep. The derived-P\* policy's own admission decision is computed
directly from the same loss registry the ground truth is defined by, so
zero missed violations (`derived_missed`, [GENERATED: ch_a1_derived_zero_every_cell]
on every seed x workflow cell) is a checked structural consequence of
that construction, not an independent empirical claim -- stated plainly,
not oversold; the genuine empirical content is the baseline comparison.
**CH-A1: [GENERATED: ch_a1_status]**.

**CH-A3** (grant binding eliminates replay admissions). Across the
sweep, [GENERATED: ch_a3_replay_probe_count] replayed-presentation
probes were injected per cell on average. With grant binding on,
replay admissions were zero on every cell
([GENERATED: ch_a3_on_zero_every_cell]). With grant binding off (a
policy that never consults ledger state), replay admissions averaged
[GENERATED: ch_a3_off_admissions] -- nonzero on at least one cell
([GENERATED: ch_a3_off_nonzero_at_least_one_cell]), the positive control
confirming the hazard is real and reachable absent the mechanism, not
just theoretically stated. Escalation overhead is reported, not
registered (magnitude not pre-committed, per `prereg/hypotheses.md`):
[GENERATED: ch_a3_escalation_overhead] decisions per cell on average
needed a fresh grant-issuance round trip after a correctly-rejected
replay attempt before they could be admitted at all. **CH-A3:
[GENERATED: ch_a3_status]**.

**Overderivation ablation (spurious escalation cost).** The
over-inclusive policy's one extra rule spuriously escalated
[GENERATED: spurious_escalations_overinclusive] genuinely safe decisions
per cell on average -- the measured cost of defensively treating a
non-participating candidate as though it mattered, instead of deriving
the minimal set. This number is definitionally tied to how large a
share of decisions carry the one excluded candidate's non-default value
(`workflow == "W2"`) in this declared model and this simulation's own
W1/W2 mix; it is reported as exactly what it is -- the cost of not
deriving minimality on this declared model -- not generalized beyond it.

**CH-A4** (robustness). CH-A1 and CH-A3's conclusions (not magnitudes)
held across all [GENERATED: n_seeds] seeds and [GENERATED: workflows]
workflows ([GENERATED: n_cells] seed x workflow cells); CH-A2 is
formal-track, evaluated once, not per seed. **CH-A4: [GENERATED: ch_a4_status]**.

### Claims and evidence

| Claim | Evidence | PROOF-STATUS / decision rule |
|---|---|---|
| P\* is sound and minimal | `checkers/participation_check.py`, [GENERATED: grid_size_reachable] tuples | machine-checked |
| CH-A2 (pair testing recovers P\* exactly) | `checkers/pairtest_check.py` | machine-checked |
| Grant mechanism is single-use | `checkers/grant_check.py`, [GENERATED: grant_check_sequences] sequences | machine-checked |
| CH-A1 (baseline misses what derived-P\* does not) | `sweep.py` / `out/results/sweep_summary.json` | [GENERATED: ch_a1_status], decision rule per `prereg/hypotheses.md` |
| CH-A3 (grant binding eliminates replay admissions) | `sweep.py` / `out/results/sweep_summary.json` | [GENERATED: ch_a3_status], decision rule per `prereg/hypotheses.md` |
| CH-A4 (robustness) | `sweep.py` / `out/results/sweep_summary.json` | [GENERATED: ch_a4_status] |

## 9. Threats to validity (written against this paper's own results)

- **CH-A1's derived-zero result is circular by construction, and we say
  so rather than let it read as a surprise finding.** The ground truth
  and the derived policy's admission rule share one registry
  (`losses.m_verdict`). The only non-tautological empirical content in
  CH-A1 is the baseline comparison; a reader who takes "100% detection"
  as an independent empirical triumph has misread the claim, and this
  section exists so they cannot reasonably do so.
- **The candidate-property representation is a modeling choice, and a
  different one gives a different P\*.** `ADR-002-participation-
  tuple-design.md` documents a design that exposed per-role policy as
  separate fields and derived actor_role itself as non-participating --
  mathematically correct for that representation, practically
  unimplementable. The corrected design avoids that specific failure by
  construction, not by a general proof; the general claim ("a candidate
  coupled to an always-held-fixed field can never be derived as
  participating") is tagged `pending-human-review` in
  `appendix-a-proofs.md`, not machine-checked, because we have not swept
  an exhaustive space of coupling configurations to confirm no other
  failure mode of the same shape survives in the current nine-field
  design.
- **The role/entitlement/window/class-set declared values are this
  paper's own design choices, not measurements.** `agent-delegate`'s
  800-value ceiling, [100, 180] window, and single-class entitlement
  were chosen to make L1-L3 each independently exercisable against the
  role structure (see `prereg/loss-model.yaml`'s comments) -- they are
  not calibrated from any real organizational policy, unlike the
  imported baseline's own scenario budgets, which paper 4 calibrates
  from real order-value/cost/carbon distributions. A different set of
  declared values would change CH-A1's baseline-missed count and the
  overderivation ablation's spurious-escalation count in magnitude,
  though not CH-A2's exact-recovery claim or Proposition 1's structural
  guarantee.
- **The overderivation ablation's one added rule (escalate on
  `workflow == W2`) targets exactly the one property Phase 2 already
  found excluded.** This is not circular -- the point of the ablation is
  precisely to cost out treating a known-irrelevant candidate as
  relevant -- but it does mean the reported spurious-escalation count is
  a direct function of how large the W2 population is in this
  simulation's own daily/weekly decision mix, not a general estimate of
  "the cost of overderivation" applicable beyond this declared model and
  this simulation.
- **The budget-depletion loss (`spend_against_depleted_delegated_budget`)
  uses a period budget calibrated from this run's own median per-period
  demand (`experiments.calibrate_period_budget`), deliberately tuned to
  bind on above-median periods.** This is a declared modeling choice
  (documented in the function's own docstring), not a measurement of any
  real resource-gate policy; a materially looser or tighter multiplier
  than the declared 1.15x would shift true_violations and, through it,
  every downstream count in this section, without changing which
  properties Phase 2 derives as participating (a fact about the loss
  predicates' structure, not about how often they fire).
- **The pair-test checker and Definition 1's own checker share the same
  declared finite domain (`pair-test-grid.yaml`).** CH-A2's exact-
  recovery claim demonstrates the two ALGORITHMS agree, not that either
  is complete against the true (much larger, partly continuous) action
  space -- Section 7's registered blind spot applies to both, not only
  to the one named "pair testing."

## 10. Limitations

- **Deriving the loss model itself is out of scope.** This paper starts
  from `prereg/loss-model.yaml` as given and derives the minimal
  observation set a gate needs to check it; it does not derive, verify,
  or validate that these six losses are the right or complete set of
  things an organization should declare. A declared loss model with a
  missing loss produces a P\* that is minimal and sound *for the
  declared model*, silently uninformative about the missing one.
- **Multi-agent settings, the evidence-integrity layer, and any
  runtime LLM involvement are out of scope** (task brief). The grant
  mechanism assumes a single sealing/execution path per decision, not
  concurrent or adversarial multi-agent claims on the same grant.
- **The finite enumerated model is a deliberate abstraction for
  exhaustive checking**, not the full (in principle continuous)
  action space the real simulation draws order values, days, and
  budgets from. Section 7's blind spot is the general statement of what
  this abstraction cannot see.
- **This is a mechanism demonstration on open payload data with a
  declared synthetic metadata layer** (role tiers, resource-class
  assignment, temporal windows) layered on the real UCI Online Retail
  data, following the imported baseline's own precedent and disclosure
  style (`sarc-suite-one-pass README.md`'s Artifact scope section) --
  not a live deployment, not a prevalence study, not the proprietary
  Suite.

## Coverage-honesty banner

**Six declared losses, nine candidate properties, one derived coverage
list. `workflow` is derived non-participating for this declared loss
model and is reported as such, not omitted. The overderivation
ablation's spurious-escalation count is specific to this simulation's
own workflow mix and declared parameter values, not a general estimate.
CH-A1's zero-miss result for the derived policy is a checked structural
consequence of sharing one registry with the ground truth, disclosed as
such in Section 9, not an independent empirical claim.**

## 11. Conclusion

Given a declared loss model, this paper derives -- not declares -- the
minimal property set a pre-action authority gate must observe,
machine-checks that set's soundness and minimality exhaustively,
independently recovers it via a formalized version of the method an
outside replication used by hand, and closes the specific coverage
boundary (execution-specific grant binding) that replication's finding
A7 named, with a machine-checked single-use guarantee. The declared-only
baseline this paper compares against is not a straw man: it is the
actual imported artifact's own shipped policy. What the derivation adds
is not more caution, but the right amount, honestly accounted for in
both directions -- the coverage list names what a gate need not check,
and the overderivation ablation prices out what it costs to guess wrong
about that in the direction of "everything, just in case."

## Acknowledgements

Drafting, engineering, formal derivation, and citation verification were
AI-assisted (Claude); the author is solely responsible for all claims.

## References

See `verified-citations.json` for the complete fetch-verified record
(url, title, first author, year, and how each was verified) of every
source cited above, and `sarc-suite-one-pass/verified-citations.json`
(pinned sibling, commit `782261e`) for the imported baseline's own
citations (the SARC, Green SARC, and sarc-dq engine papers; the UCI
Online Retail dataset; and the composition-theory literature paper 4
cites), referenced here by pointer rather than re-verified, since this
paper edits none of that artifact.

## Human checklist

- [ ] Novelty fence reviewed by the author against `NOVELTY.md`'s
      sources.
- [ ] `pending-human-review` tags counted and individually assessed:
      1 (`appendix-a-proofs.md`'s coupling-generalization remark).
- [ ] Push and any review chain are the author's decision, not
      automated by this pipeline.

**Not submission-ready. Not independently reviewed. Not claimed
complete against any loss model other than the one declared in
`prereg/loss-model.yaml`.**
