# Minimal Sufficient Governance Context: Compiling Loss Models and Reachable Execution Semantics into Cost-Aware Runtime Authority Contracts for Autonomous Agents

**This title names the paper's own thesis** (**Definition 4** defines
sufficiency and **Definition 5** minimality precisely, below; never
asserted loosely of any specific core or P\* without an instance
certificate).

Gaston Besanson[^1]

[^1]: Universidad Torcuato Di Tella

Companion artifact: `sarc-authority-derivation`. Paper 5 of the SARC
series, built on the pinned `sarc-suite-one-pass` artifact (arXiv
[2608.18360](https://arxiv.org/abs/2608.18360), commit `782261e`) as a
read-only imported baseline (`ADR-001-foundation.md`).

**Status**: draft v0.6, the consolidated manuscript. This version
replaces v0.5 as the live paper (version-split convention,
`README.md`): v0.1 through v0.5 are each frozen at their own commit and
remain on disk, linked from `README.md`'s History section, exactly as
written -- nothing in them is retracted, reworded, or deleted. Earlier
versions kept the full v0.1-through-v0.4 procurement paper re-embedded
as an unedited Part II; this version does not re-embed it a second
time. The v2 procurement result is instead folded in as this paper's
own worked introduction (Section 2 and Section 3 below), and the reader who wants
the full historical procurement paper -- its own Introduction, related
work, empirical section, and Conclusion -- is pointed to the frozen
versions directly (Section 11). This is a consolidation from
already-committed results only: no new experiment, no new registration,
no new number. Every figure below arrives through a generated slot,
sourced solely from `out/checkers/*.json` / `out/results/*.json`
already on disk before this draft was written
(`paper_tables.py`/`populate_draft.py`).

## Abstract

Given a declared loss model and the states an autonomous system can
reach, we derive and certify the minimal, cost-aware sets of runtime
observations sufficient to make every modeled safe-versus-unsafe
authority distinction. We do not declare an observation set and hope it
is complete: we **synthesize** every minimal sufficient contract
(Definition 5's reduct, encoding this artifact's own discernibility
sets -- Skowron and Rauszer 1992 -- as CNF for SAT/MaxSAT solvers),
certify each one with a machine-checkable partition certificate, and
select among them by declared observation cost, not cardinality alone.
On a real code/cloud authority domain (not planted for this purpose),
the individually-indispensable core is
**[GENERATED: ch_b1_core_sufficient_status]** as a runtime contract
([GENERATED: ch_b1_core_cardinality] of
[GENERATED: ch_b1_candidate_property_count] candidates) and
[GENERATED: ch_b1_num_reducts] distinct
[GENERATED: ch_b1_min_reduct_cardinality]-attribute reducts exist; a
registered, preregistered cost model separates them exactly
(CH-B2: **[GENERATED: ch_b2_status]**, the cheaper contract costs
[GENERATED: ch_b2_min_cost_contract_total_cost] against
[GENERATED: ch_b2_other_reduct_cost] for the alternative, both
independently certified safety-equivalent). On a second, larger,
non-planted domain built independently of this question
([GENERATED: ch_c1_candidate_property_count] candidate properties), the
same core-is-not-a-reduct distinction recurs
(CH-C1: **[GENERATED: ch_c1_status]**, a
[GENERATED: ch_c1_core_cardinality]-property core, minimum reduct
cardinality [GENERATED: ch_c1_min_cardinality], at least
[GENERATED: ch_c1_contracts_found_count] distinct minimum-cardinality
contracts) -- but the same domain's own cost model does **not**
separate them: CH-C2 is **[GENERATED: ch_c2_status]**, a genuine,
fully explained cost tie across every known minimum-cardinality
contract at [GENERATED: ch_c2_min_cost_contract_total_cost], reported
as found, not reframed. We register and measure discernibility-family
scaling on candidate-attribute universes up to
[GENERATED: v5_3_family_c_n] properties, where exhaustive reduct
enumeration is expected and confirmed infeasible within a registered
[GENERATED: v5_3_exhaustive_budget_seconds]-second budget, while
SAT/MaxSAT synthesis solves in well under a second; MaxSAT showed no
measured cardinality advantage over plain SAT on these specific
registered families
([GENERATED: v5_3_maxsat_advantage_any_family]), a two-sided registered
question, not a claim tuned toward the outcome we expected.
AuthorityBench compares four baselines -- a declared-only manual
policy, ABAC-mining reimplemented from Xu and Stoller (2015),
essential-variable analysis, and exhaustive reduct enumeration --
across [GENERATED: ab_domain_count] domains; the declared-only baseline
is not exactly sufficient on any of them
([GENERATED: ab_v2_manual_correct] /
[GENERATED: ab_v4_manual_correct] / [GENERATED: ab_dc_manual_correct]).
Every synthesized contract is compiled with a sufficiency certificate
and, where the reachable set is enumerable, a counterexample when it is
not -- a runtime gate is meant to consume the certificate, not a claim.
Results in full: [GENERATED: results_sentence_v06]

## 1. Problem

A pre-action authority gate is exactly as complete as whoever declared
its observation set thought to be. `sarc-suite-one-pass`'s own imported
baseline (`specs/authority.yaml`) observes two things: whether the
acting role is on an allow-list, and whether an order value exceeds a
single scenario-wide cap -- and, on the real code/cloud domain below, a
**declared-only policy of this same shape is not exactly sufficient**
([GENERATED: ch_b1_core_sufficient_status] is a stronger, machine-checked
version of the same finding this artifact's own v2 baseline comparison
already made: CH-A1's declared-only baseline missed
[GENERATED: ch_a1_baseline_missed] of [GENERATED: ch_a1_true_violations]
declared violations across the sweep; the same shape of baseline is
also not exactly sufficient on AuthorityBench's other two registered
domains -- Section 7). This paper's claim: given one declared loss
model and one executable-reachable action set, *compile* -- do not
hand-author -- the exact, minimal, cost-aware runtime context a gate
must observe, with alternative contracts, certificates, and
counterexamples a downstream system can consume directly, not merely a
number a human reads once.

## 2. Formal Objects

Let a **reachable state** be one executable-reachable tuple over a
declared set of candidate properties (`domain.py`'s rank-0 union
remediation-reachable construction; Proposition 0, `appendix-a-proofs.md`,
establishes that remediation adds no tuples beyond rank-0 in this
artifact's v1 model specifically -- a fact about that one construction,
not assumed of every redesign, and v2's own redesign is built precisely
to test whether a different construction can differ). Let a **loss
model** M be a finite set of boolean predicates over a reachable
tuple, each declaring one way an action can be unsafe. Two reachable
tuples are a **cross-verdict pair** if M's verdict differs between
them.

**Definition 1 (participation, the one-flip criterion).** Property `p`
is authority-bearing for M iff there exist executable-reachable tuples
`a`, `a'` differing only in `p` -- a single flip, holding every other
candidate property fixed -- whose M-verdicts differ. This is the
criterion `participation.py` sweeps exhaustively: every candidate
property, against every loss predicate, over the full enumerated
reachable set, not a sample.

**Definition 2 (the core P\*).** P\* is the set of every property
participating by Definition 1. **Definition 3 (the derived coverage
list).** The candidate properties not in P\*. **Definition 4
(sufficiency).** A property set `S` is sufficient for M iff any two
reachable tuples agreeing on every property in `S` also agree on their
M-verdict -- equivalently (`discernibility.py`, restating Definition 4
via Skowron and Rauszer's own discernibility-matrix device, 1992): for
every cross-verdict pair, its *difference set* is the candidate
properties on which the pair disagrees, and `S` is sufficient iff `S`
hits (has nonempty intersection with) every difference set -- machine-
checked equivalent to the partition test, not merely assumed
equivalent (`checkers/discernibility_check.py`). **Definition 5 (a
reduct).** A minimal sufficient set: sufficient, and no proper subset
is. **Definition 6 (the core, restated as an intersection).** The
intersection of every reduct.

This discernibility restatement is what makes reduct synthesis
tractable past exhaustive enumeration (Section 6): a difference set
that is a proper superset of another already in the family adds no
separate hitting-set constraint
(`discernibility.remove_redundant_supersets`), and the pruned family
becomes one CNF clause per surviving difference set and one boolean
variable per candidate property -- a SAT or MaxSAT solver's own input,
not `exact_reducts()`'s `2^n` subset enumeration, which every backend
is still cross-checked against everywhere exhaustion stays affordable
(`checkers/synthesis_exactness_check.py`).

## 3. Core versus Reduct

Definition 2's P\* (individual indispensability, a singleton-
perturbation witness) and Definition 5's reduct (joint sufficiency,
Definition 4) are different properties. **Proposition 1' (replacing the
original, corrected Proposition 1; `appendix-a-proofs.md`,
`prereg/v3-core-reduct-correction.md`):** claim one, Definition 1's
witness search computes exactly the core, Definition 6; claim two, the
core is a subset of every reduct; claim three, *if* the core is
sufficient, *then* the core is the unique reduct -- claim three's
antecedent never assumed, always decided per instance by a sufficiency
certificate or a concrete counterexample. **Negative Proposition N (the core need not be
sufficient, in general):** the registered two-state counterexample
(`prereg/fixtures/negative-proposition-n-counterexample.json`,
candidate properties `x, y in {0, 1}`, reachable set
`{(x=0,y=0), (x=1,y=1)}`, verdict `M(x,y) = x`) has an **empty** core
(no reachable pair differs in exactly `x` or exactly `y` -- the set's
only two members differ in both at once) that is trivially **not
sufficient** (`M(0,0) != M(1,1)`, yet the empty set determines nothing)
-- with `{x}` and `{y}` each an independent singleton reduct, neither
equal to the core. This is the sharpest possible instance: a core that
is not merely non-maximal but *empty*, directly falsifying the general
claim Proposition 1 originally made (Section 11 records the correction
itself as a finding, not smoothed over).

**The worked introduction: this artifact's own v2 procurement instance,
where claim 3's antecedent holds.** `prereg/pair-test-grid.yaml`'s
registered retail-procurement domain -- nine original candidate
properties plus `min_order_quantity`, a declared cross-field
reachability filter, and two characterized remediation mechanisms
(downroute, retry-delay) -- is not a counterexample to Proposition 1':
it is the case where the antecedent fires. CH-A8
(`checkers/sufficiency_check.py`) certifies the v2 core sufficient over
the full [GENERATED: ch_a8_reachable_swept]-tuple reachable set
([GENERATED: ch_a8_partition_cells] partition cells, uniform verdict
within every one); CH-A10 (`checkers/reduct_check.py`, exhaustive
enumeration of [GENERATED: ch_a10_subsets_considered] of
[GENERATED: ch_a10_power_set_size] candidate subsets) confirms the
core -- [GENERATED: ch_a10_candidate_property_count] properties -- is
the **unique reduct**, of minimum cardinality
[GENERATED: ch_a10_min_cardinality]
(`core_is_unique_reduct: [GENERATED: ch_a10_core_is_unique_reduct]`).
Proposition 1' claim 1's identity
([GENERATED: v3_identity_holds]) and claim 2's subset property
([GENERATED: v3_core_subset_holds]) are checked directly against this
model too, not only inferred from the intersection arithmetic. This is
this paper's simplest instance, worked first because it is the one
case in this whole artifact where core and reduct coincide -- every
domain in Section 4 below is chosen to test whether that coincidence
holds again, and mostly does not.

## 4. Realistic Evidence: The Empirical Centre

Section 3's abstract distinction (core need not be a reduct) and its
one worked coincidence (v2, where it happens to be one) leave open
whether either shape is typical on a domain not designed around the
question. Four hypotheses, on two independently-built domains neither
planted to exhibit core-versus-reduct or cost separation, are this
paper's own empirical centre.

**CH-B1 (`domain_v4.py`, Milestone C, `prereg/v4-realistic-domain.md`,
tag `prereg-p5-v4`): a software-and-cloud execution-agent domain.**
PROOF-STATUS: machine-checked (`checkers/ch_b1_check.py`,
[GENERATED: ch_b1_reachable_swept] reachable tuples swept, all
[GENERATED: ch_b1_power_set_size] candidate subsets of
[GENERATED: ch_b1_candidate_property_count] candidates considered,
subset-pruned). The core
([GENERATED: ch_b1_core_cardinality] properties:
[GENERATED: ch_b1_core_list]) is
**[GENERATED: ch_b1_core_sufficient_status]** as a contract --
individually indispensable, not jointly enough (Definition 6 versus
Definition 5) -- and [GENERATED: ch_b1_num_reducts] distinct minimum
reducts exist, both of cardinality
[GENERATED: ch_b1_min_reduct_cardinality], each the core plus exactly
one more property: `{`[GENERATED: ch_b1_reduct_branch_list]`}` or
`{`[GENERATED: ch_b1_reduct_environment_list]`}` -- two operationally
different, equally sufficient ways to close the same coverage gap, a
genuine multiplicity Negative Proposition N's own abstract
counterexample does not by itself demonstrate has a real instance.

**CH-B2 (`prereg/v7-cost-sensitive-contracts.md`, tag `prereg-p5-v7`):
does a preregistered observation-cost model separate CH-B1's own two
reducts?** PROOF-STATUS: machine-checked
(`checkers/ch_b2_check.py`, [GENERATED: ch_b2_reachable_swept]
reachable tuples swept, [GENERATED: ch_b2_subsets_considered] subsets
considered). **[GENERATED: ch_b2_status]** --
`[GENERATED: ch_b2_outcome_subcase]`: the minimum-cost contract
(`{`[GENERATED: ch_b2_min_cost_contract_list]`}`, cost
[GENERATED: ch_b2_min_cost_contract_total_cost]) is strictly cheaper
than the other minimum-cardinality reduct (cost
[GENERATED: ch_b2_other_reduct_cost], delta
[GENERATED: ch_b2_cost_delta]) -- both independently certified safety-
equivalent (`all_alternatives_safety_equivalent:
[GENERATED: ch_b2_all_safety_equivalent]`) before cost is consulted at
all, so cost breaks a tie between two contracts already known
interchangeable for safety, not a shortcut around safety. This answers
the open question Section 5 below registers: on at least one realistic
domain, minimum cardinality and minimum declared cost pick *different*
contracts, not merely differ on a hand-built proof-of-mechanism domain.

**CH-C1 (`domain_v8.py`, Package D, `prereg/v8-large-realistic-domain.md`,
tag `prereg-p5-v8`): does core-versus-reduct recur on a second,
independently-built, much larger domain?** A
[GENERATED: ch_c1_candidate_property_count]-property enterprise
access-governance domain -- seven properties from each of five
families, six reachability drivers, twenty-nine derivation rules --
whose reachability and derivation structure were fixed for
organisational plausibility *before* any core, reduct, or cost outcome
was computed (only the reachable-tuple *count*, a pure combinatorial
feasibility check, was verified first; `domain_v8.py`'s own docstring).
PROOF-STATUS: machine-checked
(`checkers/ch_c1_check.py`, [GENERATED: ch_c1_reachable_swept]
reachable tuples swept). **[GENERATED: ch_c1_status]**: the core
([GENERATED: ch_c1_core_cardinality] properties:
[GENERATED: ch_c1_core_list]) is
**[GENERATED: ch_c1_core_sufficient_status]**, minimum contract
cardinality is [GENERATED: ch_c1_min_cardinality], and at least
[GENERATED: ch_c1_contracts_found_count] distinct minimum-cardinality
contracts exist -- a genuine lower bound, via blocking-clause
enumeration capped at [GENERATED: ch_c1_multiplicity_cap]
(`synthesis.find_up_to_k_minimum_cardinality_contracts`), never claimed
exhaustive (Section 10). Exhaustive `reduct.exact_reducts()` was
separately attempted, registered budget
[GENERATED: v8_exhaustive_budget_seconds] seconds, and confirmed
infeasible (`out/results/v8_exhaustive_attempt.json`:
`feasible: [GENERATED: v8_exhaustive_feasible]`, wall time
[GENERATED: v8_exhaustive_wall_time_seconds]s, against
[GENERATED: v8_exhaustive_size7_subset_count] size-seven subsets alone)
-- Section 6's own symbolic-versus-exhaustive gap, demonstrated
empirically on this exact domain, not only claimed of it in the
abstract.

**CH-C2 (same prereg/tag): does a preregistered cost model separate
CH-C1's own minimum-cardinality contracts?** PROOF-STATUS: machine-
checked (`checkers/ch_c2_check.py`,
[GENERATED: ch_c2_reachable_swept] reachable tuples swept, same domain
as CH-C1). **[GENERATED: ch_c2_status]** --
`[GENERATED: ch_c2_outcome_subcase]`: every one of the
[GENERATED: ch_c2_num_tied_contracts] known minimum-cardinality
contracts costs exactly
[GENERATED: ch_c2_min_cost_contract_total_cost] under this domain's own
seven-tier cost model -- a genuine, fully explained tie, retained and
reported, not reframed as a partial success. Explanation, not smoothed
over: the tied contracts substitute properties from the *same* declared
cost tier for one another (the domain's own tier structure groups
several role/context/environment observations at identical declared
cost), so a cost model built at this granularity cannot discriminate
between them -- weighted optimisation over declared cost is
**conditional** on the cost model actually separating the substitute
properties in play; CH-B2 shows a domain where it does, CH-C2 shows one
where, at the granularity actually declared, it does not. Neither
result generalizes to the other domain; both are kept, cited, and
neither is treated as more representative than the other.

## 5. Synthesis: SAT, MaxSAT, and Weighted Contracts

`synthesis.py` (Milestone D2, `prereg/v5-synthesis.md`) encodes
Section 2's discernibility family as CNF and exposes three backends:
`find_any_sufficient_contract` (plain SAT -- any sufficient contract,
not necessarily minimal), `find_minimum_cardinality_contract`
(cardinality MaxSAT -- a soft unit clause per property, weight one),
and `find_minimum_cost_contract` (weighted MaxSAT -- the same
construction with each property's declared observation cost as its own
soft-clause weight); `find_up_to_k_minimum_cardinality_contracts`
(Section 4's own blocking-clause multiplicity method, added for CH-C1)
repeatedly re-solves the same objective, excluding each prior model
with one added hard clause, stopping as soon as an iteration's optimum
exceeds the first -- a genuine lower bound on multiplicity, never
`2^n` enumeration. `checkers/synthesis_exactness_check.py` holds every
backend to `reduct.exact_reducts()`'s own from-first-principles answer
everywhere exhaustion is affordable (this artifact's v1/v2/v4 models) --
a real regression would be caught by comparison, not assumed away by
trusting a solver.

Cost-aware synthesis' mechanism was proved first on a small, hand-
derived domain before it was asked of a realistic one
(`benchmarks.py`'s XOR-bijection construction, `exploratory_v5_0`'s own
`experiment_2_cost_aware`, `prereg/v5-synthesis.md`): a boolean
`[GENERATED: v50_xor_min_card_contract]` and a bijected pair
`[GENERATED: v50_xor_min_cost_contract]` where minimum cardinality
(`{`[GENERATED: v50_xor_min_card_contract]`}`, cost
[GENERATED: v50_xor_min_card_cost]) and minimum declared cost
(`{`[GENERATED: v50_xor_min_cost_contract]`}`, cost
[GENERATED: v50_xor_min_cost_cost], delta
[GENERATED: v50_xor_cost_delta]) disagree by construction -- proof the
mechanism *can* select a strictly cheaper sufficient contract over a
smaller one, not yet evidence a realistic domain does the same. This
artifact's own v1/v2/v4 domains showed no divergence at the time
(uniform declared cost floor,
[GENERATED: v50_real_domains_cost_delta_uniform] that every one of
their own cost deltas was exactly zero) -- the operational-value
question this left open is exactly what CH-B2 and CH-C2 above now
answer, on two realistic domains, in both directions.

`contract_change_delta` (D5's own worked illustration, not a registered
pass/fail experiment): on a small model where a new transition collides
with an existing tuple under the base contract's own projection
(base `{`[GENERATED: ccd_base_contract]`}`), sufficiency drops
(`was_still_sufficient: [GENERATED: ccd_was_still_sufficient]`), the
incremental update (`{`[GENERATED: ccd_updated_contract]`}`) is
independently confirmed sufficient and matches free-choice full
recomputation exactly in this illustration (cardinality gap
[GENERATED: ccd_full_recomputation_cardinality_gap]) -- not a general
guarantee: `test_synthesis.py`'s own unit tests separately construct a
case with a genuinely nonzero gap, the honest "price of incrementality"
the function's own docstring registers rather than hides.

## 6. Scale: Symbolic Synthesis Beyond Exhaustive Search

Three registered scaling results, kept as three separate, still-valid
questions, none superseding another:

**Exploratory (v5.0, kept, degeneracy disclosed; `prereg/v5-synthesis.md`,
tag `prereg-p5-v5`).** `experiment_1_scaling` (planted-reduct scaling)
grew the *candidate-property count* alone -- `n` = [GENERATED: v50_n_values] --
while deliberately holding the reachable set fixed at
[GENERATED: v50_reachable_tuple_count] tuples (a planted reduct of
cardinality [GENERATED: v50_planted_reduct_size] is unique by
construction on a reachable set this small). `all_exact:
[GENERATED: v50_all_exact]` at every size, wall time staying between
[GENERATED: v50_wall_time_min]s and [GENERATED: v50_wall_time_max]s
with no distinguishable growth trend -- a real, valid answer to the
question it was built for, but a **degenerate** one for scale in
general: the `n`-minus-planted-size noise properties never appear in
any discernibility-family clause, costing the solver nothing beyond one
extra boolean variable each, which is exactly why cost stayed flat
regardless of `n`. Relabelled `exploratory_v5_0` and superseded as the
primary scaling claim by the two results below, not deleted --
`out/results/synthesis_benchmarks.json` is unchanged since.

**The tuple-scaling result (v5.1, kept; `prereg/v5.1-discernibility-scaling.md`,
tag `prereg-p5-v5.1`).** Holding the candidate-property count small
enough to stay exhaustible, a planted two-reduct family grows the
*reachable set itself* to [GENERATED: v5_1_max_reachable_tuples]
tuples: the discernibility family still reduces, after superset
removal, to exactly [GENERATED: v5_1_family_size_after_pruning] set,
and all [GENERATED: v5_1_num_reducts] planted reducts are recovered
exactly by every backend -- answering whether the construction scales
as the reachable set grows, the question v5.0 above did not ask.

**The primary scaling table (v5.3): combinatorial hardness
(`prereg/v5.3-combinatorial-hardness-scaling.md`, tag
`prereg-p5-v5.3`).** Three families pair a planted minimum-reduct size
with a *large* candidate-attribute universe, far past exhaustive-
enumeration tractability, and a *diverse* discernibility structure
(hundreds of distinct minimal difference sets, not one):

| Family | Candidate properties (n) | Minimum reduct size (k) | Discernibility family after pruning | Exhaustive reduct enumeration |
|---|---|---|---|---|
| A | [GENERATED: v5_3_family_a_n] | [GENERATED: v5_3_family_a_k] | [GENERATED: v5_3_family_a_pruned_family_size] sets | infeasible, [GENERATED: v5_3_exhaustive_budget_seconds]s budget |
| B | [GENERATED: v5_3_family_b_n] | [GENERATED: v5_3_family_b_k] | [GENERATED: v5_3_family_b_pruned_family_size] sets | infeasible, [GENERATED: v5_3_exhaustive_budget_seconds]s budget |
| C | [GENERATED: v5_3_family_c_n] | [GENERATED: v5_3_family_c_k] | [GENERATED: v5_3_family_c_pruned_family_size] sets | infeasible, [GENERATED: v5_3_exhaustive_budget_seconds]s budget |

Exhaustive cross-check was registered as *expected*, not assumed,
infeasible at every family, and the real, measured attempt bore that
out on all three, each consuming its full registered budget before
being abandoned. Cardinality- and cost-MaxSAT both found the exact,
hand-proved minimum reduct at every family regardless, in well under a
second per family -- families that are hard for exhaustive enumeration
are not automatically hard for the solvers synthesizing over their own
discernibility family (Section 10). **Two-sided, reported as
measured**: does MaxSAT provide a meaningful cardinality advantage over
plain SAT here? [GENERATED: v5_3_maxsat_advantage_any_family] -- this
registration pre-committed to accept and report a uniformly-absent
advantage as a legitimate outcome, not a benchmark failure, and that is
what was found.

## 7. AuthorityBench

AuthorityBench (Milestone E, `prereg/v6.1-authoritybench-amendment.md`,
tag `prereg-p5-v6.1`) runs four baselines -- **manual least-privilege**
(the declared-only shape), **ABAC policy mining** (reimplemented from
Xu and Stoller, TDSC 2015, independently validated against the
published "Health Care Sample Policy" case study before being trusted
here, `xu_stoller_validation.py`:
[GENERATED: ab_xu_stoller_mining_validated]), **essential-variable
analysis**, and **exhaustive reduct enumeration** -- across
[GENERATED: ab_domain_count] domains this artifact independently
registered (procurement, code/cloud, data-and-communications), six
metrics each:

| Domain | Candidate properties | Reachable tuples | Manual baseline exactly sufficient | Mining-baseline contract size |
|---|---|---|---|---|
| Procurement (v2) | [GENERATED: ab_v2_candidate_property_count] | [GENERATED: ab_v2_reachable_tuple_count] | [GENERATED: ab_v2_manual_correct] | [GENERATED: ab_v2_mining_size] |
| Code/cloud (v4) | [GENERATED: ab_v4_candidate_property_count] | [GENERATED: ab_v4_reachable_tuple_count] | [GENERATED: ab_v4_manual_correct] | [GENERATED: ab_v4_mining_size] |
| Data-and-communications | [GENERATED: ab_dc_candidate_property_count] | [GENERATED: ab_dc_reachable_tuple_count] | [GENERATED: ab_dc_manual_correct] | [GENERATED: ab_dc_mining_size] |

The declared-only manual baseline is not exactly sufficient
(Definition 4) on any of the three -- Section 1's opening claim,
measured across every registered domain this artifact has, not
asserted from one. Mining agrees with `derive_authority_contract`'s own
minimum-cardinality answer on the procurement and code/cloud-core
instances and lands on the *other* known minimum reduct (the
`environment` variant of CH-B1's own two) on the code/cloud domain --
investigated, not left an anomaly: both are genuine, independently-
verified minimum reducts of the identical model, a tie-break divergence
between two independently-computed global minima, not a disagreement
about which properties matter. Decision: **INCONCLUSIVE** by the
registered rule applied honestly to what was measured (two domains
equal, one a benign tie, never a strict-superset case on any domain) --
a registered non-result for whether mining tends to be avoidably
non-minimal, reported as such rather than reframed as a win.

Two further registered results share this domain portfolio.
**The budget-binding scenario (v5.2, `prereg/v5.2-budget-binding-scenario.md`,
tag `prereg-p5-v5.2`)**: a procurement scenario constructed so the
budget loss predicate actually fires -- it did, in every one of
[GENERATED: v52_cells_with_fire] of [GENERATED: v52_n_cells] cells
([GENERATED: v52_total_fire_count] firings total) -- and CH-A1's own
derived-zero-miss guarantee held on every one of them
(**[GENERATED: v52_status]**; derived misses
[GENERATED: v52_derived_missed_ci] against a declared-only baseline
missing [GENERATED: v52_baseline_missed_ci]). **The isolated-arm
re-measurement (v0.4, `prereg/v3.1-isolated-arms.md`, tag
`prereg-p5-v3.1`)**: direct code inspection found the baseline,
derived, and over-inclusive experiment arms sharing one budget and one
grant ledger, a real internal-validity threat found by this paper's own
inspection, registered before any fix was written. The isolation
hypothesis itself was **NOT SUPPORTED**: all thirty registered seeds
across both workflows, re-run under the corrected, isolated `ArmState`
design, reproduce the prior shared-state result's own means, confidence
intervals, and booleans byte-for-byte -- a direct diagnostic confirmed
the one loss predicate the bug could have corrupted fired zero times
in any cell, so the bug, while real, was never load-bearing for this
declared parameter set. The corrected design is kept regardless of the
null result -- structurally correct independent of today's numbers,
guarding a future declared parameter set where budget genuinely binds
tightly enough to matter.

## 8. Runtime Implication

`src/authority_compiler` (Milestone E1, packaged and made installable
under Package A) packages this paper's own machinery behind one call,
`derive_authority_contract`, returning a compiled `AuthorityContract`:
the core, every reduct where exhaustion is affordable (explicitly
`None` with a stated reason otherwise, never silently truncated), the
minimum-cardinality and minimum-cost reducts, the redundant-attribute
list, a `sufficiency_certificate` (the partition itself, not a bare
boolean), `counterexamples` when the core is not sufficient, and a
bound `contract_change_delta` callable reporting whether a newly
reachable set of tuples still leaves a prior contract sufficient before
resynthesizing anything. A runtime pre-action gate is meant to consume
this compiled contract and its certificate directly -- gate schema and
enforcement code are downstream engineering this paper does not
implement, the same scoping this artifact's own grant mechanism already
observes for capability-system binding (Section 9).

## 9. Related Work and the Novelty Fence

Nine neighbouring literature clusters, each fetch-verified
(`verified-citations.json`): what each established, and what this
paper adds.

**STPA and its descendants** (Leveson and Thomas's STPA Handbook 2018;
Young and Leveson's STPA-Sec, CACM 2014; Rismani, Dobbe, and Moon's
PHASE 2024; Mylius 2025; Qi et al.'s DeepSTPA 2023). STPA establishes a
structured but human-driven analyst process: an engineer enumerates
losses and hazards and writes safety constraints by hand, checked by
expert review. In every one of these five sources the output is a set
of constraints produced and reviewed by a person; none derive, in
general, a machine-checked *minimal* property set for a runtime gate,
and none formalize soundness or minimality as machine-checkable claims
over an enumerated model. This paper's derivation is inspired by STPA's
loss-to-constraint direction of travel but replaces the analyst step
with a deterministic, exhaustively-verified derivation.

**ABAC policy mining** (Xu and Stoller, TDSC 2015; Nobi et al.'s 2022
survey). Mining starts from an *existing* lower-level policy plus
attribute data and reconstructs which attributes already participate.
This paper runs the derivation in the opposite direction, from a
declared loss model forward to the minimal property set a *new* gate
must observe, with a machine-checked soundness and minimality guarantee
that mining, in general, has no ground-truth policy to verify against
and so cannot provide -- Section 7's own AuthorityBench comparison
reimplements Xu and Stoller's method faithfully rather than merely
citing it, and finds it independent evidence for, not against, this
artifact's own core-versus-reduct results.

**Policy-language completeness** (Crampton and Morisset's PTaCL, POST
2012; Crampton and Williams's canonical-completeness result, SACMAT
2016). Both establish what a policy *combination* language can express
once the participating attributes and base decisions are already
fixed; neither asks which attributes must be observed in the first
place. This paper contributes exactly the question both assume already
answered.

**Non-interference** (Goguen and Meseguer 1982). A semantic criterion
for whether one party's actions can affect what another observes -- a
*check* of dependence between two fixed parties, in general neither a
derivation procedure nor a minimality guarantee. Definition 1 borrows
the underlying comparison (does changing X change the observable
verdict?) but turns it into a derivation swept over every candidate
property against every loss predicate, with soundness and minimality
verified exhaustively, not a single designated-pair check.

**Counterfactual fairness** (Kusner, Loftus, Russell, and Silva 2017).
Structurally the same comparison Definition 1 uses -- does changing one
property change the verdict? -- applied once, to a single pre-chosen
sensitive attribute, against a fairness objective. This paper
generalizes the comparison to every candidate property against a
declared loss model and adds an exhaustive, machine-checked minimality
result that, in general, the counterfactual-fairness literature neither
claims nor checks.

**Shield synthesis** (Bloem, Bettina Könighofer, Robert Könighofer, and
Wang, TACAS 2015). Given a reactive system and an omega-regular safety
specification, synthesizes a runtime monitor correcting violating
outputs over the system's *already-declared* interface signals. This
paper solves the strictly prior problem -- which properties an
enforcement point must observe at all, in general, with a machine-
checked minimality guarantee -- upstream of the corrective strategy
shield synthesis solves for.

**Runtime enforcement and edit automata** (Schneider, TISSEC 2000;
Ligatti, Bauer, and Walker 2005). Schneider characterizes execution
monitoring's own enforceable policy class (safety properties); Ligatti
et al. extend the monitor's corrective repertoire to insertion and
suppression over the identical, already-fixed target-action alphabet.
Neither asks which of a decision's available properties must be part
of that alphabet in the first place -- the antecedent question this
paper answers in general, with a minimality guarantee neither work
needs for its own narrower question.

**Controller synthesis** (Ramadge and Wonham 1987; Pnueli and Rosner,
POPL 1989). Both presuppose the plant's or module's own observable/
controllable alphabet and synthesize a control law *within* it.
In general, Ramadge and Wonham's own minimality result is about the
supervisor's behaviour given that alphabet, not the alphabet itself.
This paper derives the alphabet a controller (here, a pre-action
authority gate) must observe, before any supervisor or reactive module
is synthesized over it.

**Capability systems** (Dennis and Van Horn 1966). Establishes the
capability as an unforgeable reference carrying authority, propagated
by controlled copying -- *how* authority, once a decision to grant it
is made, is represented and delegated, not which conditions must be
checked before it is minted. This artifact's own execution-grant
mechanism (Section 8) is engineering informed by this lineage's modern
descendants (Macaroons, UCAN, Biscuit -- already cited there for the
grant's own bearer-token design), not a novelty claim in its own right;
this paper's derivation is upstream of the capability question in the
same way it is upstream of shield synthesis, runtime enforcement, and
controller synthesis: it derives what a gate must observe before that
decision, not how the resulting authority is represented once made.

**The fence, stated once.** In general, none of the nine clusters above
derive, from a declared loss model, a machine-checked *minimal*
property set for a runtime authority gate, with soundness and
minimality verified exhaustively over an enumerated model and
certificates a downstream system consumes directly. This paper's
contribution sits upstream of all nine, answering a question each of
them assumes already settled.

## 10. Limitations

- **Declared loss-model completeness** is assumed, not verified: a
  declared model missing a real hazard still produces a certified core
  or reduct *for the declared model*, silently uninformative about the
  missing one -- true identically of the procurement, code/cloud, and
  data-and-communications domains, and of the larger Section 4 domain.
- **Reachability-model validity**: every result above is exact *given*
  its own declared reachable set, transcribed from its own prereg, not
  measured from a live deployment -- a different or richer reachability
  model could change which properties participate.
- **Partial observability** is not modeled: every synthesis backend
  assumes the candidate properties it is given are the ones a gate
  *could* observe; a property outside that declared set cannot be
  discovered as missing by this machinery.
- **Temporal and probabilistic losses** are out of scope: every loss
  predicate here is a boolean function of one reachable tuple, not a
  sequence or a probability distribution over outcomes.
- **External validation**: the reproduction packet (`REPRODUCTION.md`,
  Package D) is this artifact's own attempt to make independent
  reproduction possible; per its own eight-point standard, it is not
  itself independent evidence until someone who did not build this
  artifact runs it and reports back (`FINAL-AUDIT.md`'s own external-
  reproduction item: **PENDING**, infrastructure ready, no reproduction
  report filed as of this draft).
- **Families hard for exhaustive enumeration are not automatically hard
  for the solvers synthesizing over their own discernibility family**:
  Section 6's own v5.3 families are registered-infeasible to enumerate
  and solve in well under a second regardless -- a fact about this
  specific discernibility-family construction on these specific
  families, not a general claim that no synthesis instance can be hard.
- **Reduct multiplicity in the Section 4 large domain (CH-C1) is a
  lower bound, not an exhaustive count**: blocking-clause enumeration
  capped at [GENERATED: ch_c1_multiplicity_cap] found
  [GENERATED: ch_c1_contracts_found_count] distinct minimum-cardinality
  contracts; whether more exist above the cap is open, and every place
  this number appears (`checkers/ch_c1_check.py`'s own output field
  names, this document) states it as "at least," never rounded up.

## 11. Corrections and Historical Foundation

Append-only, per this project's own discipline: nothing below is
retracted or reworded; each correction is recorded alongside its
original claim, not in place of it.

**The v1 singleton-sufficiency overclaim (corrected v0.3,
`prereg/v3-core-reduct-correction.md`).** The original Proposition 1
(frozen, `appendix-a-proofs.md`, preserved with its correction attached
rather than deleted) asserted that observing exactly P\* lets a gate
"always compute M's true verdict on any executable-reachable tuple" --
conflating individual indispensability (what Definition 1's singleton-
perturbation witness search actually certifies) with joint sufficiency
(Definition 4, a property no per-property witness search establishes).
A commissioned external, AI-assisted research review
(`review-secondary/external-research-review-2026-09-06.pdf`, sha256
`b205faf65fe84d773260d1ed514b20f5b04e420380d3136c23bff1cde4506b0b`)
identified the mischaracterization; per this project's own discipline
the finding was not applied directly -- it was adjudicated against this
artifact's own definitions, and Negative Proposition N's counterexample
was re-derived from first principles, not copied from the review's
prose (`prereg/v3-core-reduct-correction.md` records the adjudication).
Proposition 1 is superseded by Proposition 1' (Section 3), not deleted;
its PROOF-STATUS is narrowed to `checked-scope-only` with the
correction attached directly to it in `appendix-a-proofs.md`.

**The v5.0 degenerate scaling benchmark (disclosed v5.1,
`prereg/v5.1-discernibility-scaling.md`).** Section 6's own exploratory
benchmark scaled candidate-property count while holding the reachable
set fixed at [GENERATED: v50_reachable_tuple_count] tuples -- a valid
answer to the question it was built for, but one where the added
"noise" properties cost the solver nothing beyond one boolean variable
each, a structural reason (not a bug) that its own flat wall-time curve
cannot be read as evidence of scaling in general. Relabelled
`exploratory_v5_0` from v5.1 forward, superseded as the primary
scaling claim by v5.1 and v5.3 -- kept, cited, its degeneracy stated
plainly rather than quietly dropped.

**The entangled v0.3 experiment arms and their null delta (found and
corrected v0.4, `prereg/v3.1-isolated-arms.md`).** Section 7's own
budget/ledger-sharing defect, found by this paper's own code
inspection rather than an external review, registered two-sided before
any fix was written: isolating the three experiment arms' state
produced a result byte-identical to the prior shared-state measurement
across all thirty seeds and both workflows -- **NOT SUPPORTED**, with
the mechanism explaining why (the one vulnerable loss predicate never
fired under this declared parameter set) rather than left unexplained.
The corrected, isolated design is kept regardless of the null result.

**The two commissioned external review rounds, and this project's own
adjudication discipline.** Round one
(`review-secondary/external-research-review-2026-09-06.pdf`) produced
the core-versus-reduct correction above. Round two
(`review-secondary/final-gap-plan-9.5-2026-09-09.pdf`, sha256
`0d1d0ca1e9672b893f97fd0dd4289574dba7b84775ae060f7830e3c2f2b82bc9`)
produced the broadened contribution this paper's own front matter names
-- the code/cloud flagship promoted from a buried result to the
empirical centre, the packaging and CI-smoke-test gates, symbolic
scaling and AuthorityBench framing, and the large non-planted domain
(Section 4) this draft adds. Both rounds were committed unedited under
`review-secondary/`, and neither round's finding was ever applied as a
direct patch: every finding this paper's own results reflect was
independently re-derived and machine-checked against this artifact's
own definitions and data before being accepted, the same discipline
`prereg/v3-core-reduct-correction.md`'s own adjudication records for
round one specifically.

**Where the full historical procurement paper lives.** v0.1 (commit
`37a2e7f`), v0.2 (commit `7112031`), v0.3 (commit `382be13`), v0.4, and
v0.5 are each frozen at their own commit, unedited since, and linked
from `README.md`'s History section -- the complete v1-through-v4
Introduction, novelty fence, replication, Definitions 1-6, derivation
procedure, grant mechanism, pair testing, empirical section (CH-A1
through CH-A10), and their own Threats to validity, Limitations, and
Conclusion are preserved there in full, not reproduced a second time in
this consolidated manuscript.

## 12. Threats to Validity, Claims, and Proof Status

**Threats to validity, written adversarially.** First, every
"realistic" domain in Section 4 is still a declared model, not a live
deployment -- a domain built by the same author to be plausible is not
independent evidence that real deployments share its structure;
AuthorityBench's own three domains and Section 4's own two were each
registered before their own core/reduct outcome was computed, which
bounds researcher degrees of freedom but does not eliminate a shared
blind spot across all of them. Second, CH-C1's own multiplicity count
is a lower bound capped at [GENERATED: ch_c1_multiplicity_cap] by
construction -- a reader could reasonably suspect the true count is far
larger, which would weaken (not strengthen) any claim resting on "few"
alternatives. Third, CH-C2's cost tie could be read as this paper
quietly avoiding a result that would have been more impressive (cost
separation everywhere) -- the tie is reported at face value, with the
mechanism that produces it (same-tier substitution) stated explicitly,
precisely so a reader can judge whether a finer-grained cost model
would break it, rather than being left to assume the result is more
favorable than measured. Fourth, AuthorityBench's mining comparison is
INCONCLUSIVE by its own registered rule; a reader could reasonably ask
why an inconclusive baseline comparison is reported at all -- it is
reported because the registration committed to reporting whatever was
measured, not only a clean win.

**Claims versus non-claims.**

| This paper claims | This paper does not claim |
|---|---|
| On two independently-built, non-planted domains, the core is not always a reduct (CH-B1, CH-C1). | That the core is never a reduct -- v2's own worked instance (Section 3) is a real counterexample to that stronger claim. |
| On one of those two domains, declared cost strictly separates the minimum-cardinality alternatives (CH-B2). | That declared cost always separates them -- CH-C2, on the other domain, is a genuine tie. |
| Exhaustive reduct enumeration is registered-infeasible on the Section 6 hardness families and the Section 4 large domain, and SAT/MaxSAT synthesis solves them regardless. | That every hard-to-enumerate instance is easy for these solvers, or that this artifact has found the general boundary between the two. |
| MaxSAT showed no measured cardinality advantage over plain SAT on the specific registered v5.3 families. | That MaxSAT never has a cardinality advantage over SAT in general. |
| The declared-only manual baseline is not exactly sufficient on any of AuthorityBench's three registered domains. | That no declared-only policy could ever be sufficient -- v2's own core happens to be sufficient (Section 3); "manual" here means the specific declared-only shape AuthorityBench registered, not every possible hand-written policy. |
| `REPRODUCTION.md` gives a complete, working reproduction infrastructure, checked against an eight-point standard. | That this artifact has been independently reproduced -- `FINAL-AUDIT.md`'s own external-reproduction item is PENDING, checked directly against the issue tracker, not assumed. |

**Proof status.** Every numbered formal claim (Section 2's Definitions,
Section 3's Propositions) carries a `PROOF-STATUS` tag in
`appendix-a-proofs.md`: `machine-checked` (an executable
`checkers/*.py` module verifies the claim over an explicitly enumerated
finite domain), `checked-scope-only` (the certified scope is narrower
than the general prose, stated exactly), or `pending-human-review`
(asserted, not yet machine-verified) -- `proven` is never written,
enforced on every build by `checkers/proof_status_lint.py`. Every
Section 4 hypothesis (CH-B1, CH-B2, CH-C1, CH-C2) carries the same
discipline inline, naming its own checker and enumerated domain rather
than asserting a bare result. `pending_human_review_tag_count` in this
document's own build: [GENERATED: pending_human_review_tag_count]
(`appendix-a-proofs.md`'s coupling-generalization remark, unchanged
since v0.2).

**Results, restated once, in full**: [GENERATED: results_sentence_v06]

**Acknowledgements.** Drafting, engineering, formal derivation, and
citation verification were AI-assisted (Claude); the author is solely
responsible for all claims.

#### References

See `verified-citations.json` for the complete fetch-verified record
(url, title, first author, year, and how each was verified) of every
source cited above, and `sarc-suite-one-pass/verified-citations.json`
(pinned sibling, commit `782261e`) for the imported baseline's own
citations, referenced here by pointer rather than re-verified, since
this paper edits none of that artifact.

#### Human checklist

- [ ] Novelty fence (Section 9) reviewed by the author against
      `NOVELTY.md`'s sources.
- [ ] Corrections section (Section 11) reviewed by the author against
      `prereg/v3-core-reduct-correction.md`, `prereg/v3.1-isolated-arms.md`,
      and the two external reviews it credits.
- [ ] `pending-human-review` tags counted and individually assessed:
      [GENERATED: pending_human_review_tag_count]
      (`appendix-a-proofs.md`'s coupling-generalization remark).
- [ ] Push and any review chain are the author's decision, not
      automated by this pipeline.

**Not submission-ready. Not independently reviewed. Not claimed
complete against any loss model other than the ones declared in this
artifact's own `prereg/` files.**
