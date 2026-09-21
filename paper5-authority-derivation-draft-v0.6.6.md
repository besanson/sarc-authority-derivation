# Compiling Sufficient Governance Context from Declared Losses and Reachable States

**This title names this paper's own thesis** (**Definition 1** defines
observation contract and **Definition 4** defines sufficiency, below;
never asserted loosely of any specific contract without an instance
check).

### Exact Observation-Contract Synthesis with Cardinality and Cost Objectives

Gaston Besanson[^1]

[^1]: Universidad Torcuato Di Tella

Companion artifact: `sarc-authority-derivation`. Paper 5 of the SARC
series, built on the pinned `sarc-suite-one-pass` artifact (arXiv
[2608.18360](https://arxiv.org/abs/2608.18360), commit `782261e`) as a
read-only imported baseline (`ADR-001-foundation.md`).

**Status**: draft v0.6.6, revising the Acknowledgements to credit the
independent reproducer's full name and affiliation and to cover all
three recorded reproduction attempts, not only the successful third --
itself a revision recording the third independent reproduction attempt
succeeding (`besanson/sarc-authority-derivation#3`) and closing
`FINAL-AUDIT.md`'s own external-reproduction item (v0.6.5), a
two-residue wording revision of v0.6.3 (a wording-and-related-work
revision of v0.6.2, a citation-restoration revision of v0.6.1, a
claim-led revision of v0.6). v0.6.5 (and every version before it, v0.1
through v0.6.4) is frozen at its own commit and remains on disk, linked
from `README.md`'s History section, exactly as written -- nothing in it
is retracted, reworded, or deleted. This revision touches only the
Acknowledgements -- and changes no result, runs no new experiment, and
registers no new hypothesis. Every figure below arrives through a
generated slot, sourced solely from `out/checkers/*.json` /
`out/results/*.json` already on disk before this draft was written
(`paper_tables.py`/`populate_paper.py`).

## Abstract

We call the object this paper derives and certifies a **minimal
sufficient governance context**: given a finite reachable-state model,
a deterministic declared verdict, and a set of candidate observable
attributes, we compute sufficient observation sets, distinguish
attributes that are individually indispensable from contracts that are
jointly sufficient, and select among sufficient contracts under a
cardinality or a declared observation-cost objective. An **observation
contract** is a set of candidate attributes whose values determine the
declared verdict on every reachable state; an **authority contract** is
an observation contract selected under one of those objectives and
bound to a gate schema (Section 2). We do not declare an observation
contract and hope it is complete: we synthesize every inclusion-minimal
sufficient contract where exhaustive enumeration is affordable, and a
minimum-cardinality or minimum-cost sufficient contract by SAT/MaxSAT
encoding otherwise; for every selected contract reported in the
evaluation, we separately check sufficiency.

On a preregistered constructed code/cloud domain (not planted for this purpose),
the individually-indispensable core is
**[GENERATED: ch_b1_core_sufficient_status]** as an observation
contract ([GENERATED: ch_b1_core_cardinality] of
[GENERATED: ch_b1_candidate_property_count] candidates) and
[GENERATED: ch_b1_num_reducts] distinct
[GENERATED: ch_b1_min_reduct_cardinality]-attribute reducts exist; a
preregistered declared-cost model separates them exactly (CH-B2:
**[GENERATED: ch_b2_status]**, the cheaper contract costs
[GENERATED: ch_b2_min_cost_contract_total_cost] against
[GENERATED: ch_b2_other_reduct_cost] for the alternative, both
independently checked sufficient before cost is consulted). On a
second, independently structured,
[GENERATED: ch_c1_candidate_property_count]-property constructed
domain, preregistered before any core, reduct, or cost outcome was
computed, the same core-insufficiency pattern recurs (CH-C1:
**[GENERATED: ch_c1_status]**, a [GENERATED: ch_c1_core_cardinality]-
property core, a minimum-cardinality contract of
[GENERATED: ch_c1_min_cardinality] attributes, at least
[GENERATED: ch_c1_contracts_found_count] distinct minimum-cardinality
contracts) -- but the same domain's own cost model does not separate
them: CH-C2 is **[GENERATED: ch_c2_status]**, a fully explained cost
tie across every known minimum-cardinality contract at
[GENERATED: ch_c2_min_cost_contract_total_cost], reported as found. We
measure discernibility-family scaling on candidate-attribute universes
up to [GENERATED: v5_3_family_c_n] properties, where exhaustive
enumeration is expected and confirmed infeasible within a registered
[GENERATED: v5_3_exhaustive_budget_seconds]-second timeout under this
project's own measured setup, while SAT/MaxSAT synthesis solves in well
under a second on the same instances; MaxSAT showed no measured
cardinality advantage over plain SAT on these specific families
([GENERATED: v5_3_maxsat_advantage_any_family]). AuthorityBench compares
four baselines -- a declared-only manual policy, ABAC-mining
reimplemented from Xu and Stoller (2015), essential-variable analysis,
and exhaustive reduct enumeration -- across
[GENERATED: ab_domain_count] domains; the declared-only baseline is not
exactly sufficient on any of them
([GENERATED: ab_v2_manual_correct] / [GENERATED: ab_v4_manual_correct] /
[GENERATED: ab_dc_manual_correct]). Every selected contract is checked
for sufficiency, with a concrete counterexample returned on failure and
a check summary (a partition-cell count and a uniformity flag, not a
portable certificate) on success; this is the compiler-focused scope
of the two-scope table in Section 12 -- a separately coded, independently
specified end-to-end case study is registered follow-up work, not
claimed here. Results in full: [GENERATED: results_sentence_v06]

## 1. Introduction

**The decision problem.** A pre-action authority gate is exactly as
complete as whoever declared its observation set thought to be. This
artifact's own imported baseline (`sarc-suite-one-pass`'s
`specs/authority.yaml`) observes two things: whether the acting role is
on an allow-list, and whether a declared order value exceeds a single
scenario-wide cap. Acquiring every candidate field instead of choosing
is not free either: latency, privacy exposure, and availability each
carry a cost a gate pays on every decision. Between "declare an
observation set by hand and hope it is complete" and "observe
everything," this paper compiles the third option: derive, from a
declared loss model and a declared reachable-state model, the exact
observation contracts sufficient to reproduce that model's verdict, and
select among them by an explicit objective.

**Running example.** Section 6's own CH-B1 result gives the concrete
shape of the problem before any formalism: on a preregistered
constructed code/cloud execution-agent domain, the set of attributes
that are individually
indispensable (Section 2's core) is
**[GENERATED: ch_b1_core_sufficient_status]** as an observation
contract on its own, and there are exactly
[GENERATED: ch_b1_num_reducts] operationally different ways to close
the remaining gap -- the core plus `branch`
(`{`[GENERATED: ch_b1_reduct_branch_list]`}`), or the core plus
`environment` (`{`[GENERATED: ch_b1_reduct_environment_list]`}`), each
independently checked sufficient. Neither is more "correct" than the
other on cardinality alone; Section 6 shows a declared cost model can
break the tie. A gate builder choosing by hand has no way to know a
second, equally sufficient alternative exists, let alone which one a
declared cost model would prefer.

**Contribution statement.** This paper separates three things, and
claims no more for any of them than its own evidence supports: first, a
formulation of governance-context compilation as sufficient-set
synthesis over a declared loss model and a declared reachable-state
model (Section 2); second, an implemented pipeline -- discernibility
construction, SAT/MaxSAT synthesis, sufficiency checking -- exposed
through one packaged entry point (Section 3 and Section 4); and third,
a bounded evaluation across constructed domains, measuring semantic
correctness, contract multiplicity, cost separation, and solver scaling
(Section 5 through Section 7). Test counts, correction history, and
engineering-gate counts are not scientific contributions and are not
presented as such; they are
reported, where relevant, as evidence quality, in Section 11 and the
supplementary material (Section 14).

**Guarantee boundary, stated once here and held to throughout.**
Correctness in this paper is relative to a declared loss model, a
declared candidate-attribute representation, and a declared reachable-
state set -- never a general safety guarantee independent of those
three declarations. A domain missing a real hazard from its declared
loss model still produces a checked core or contract *for the declared
model*, silently uninformative about the hazard it does not model. What
is implemented and checked, and what remains downstream engineering
(gate-schema binding, enforcement, concurrent-agent safety), is stated
explicitly at the end of Section 4, not left for a reader to infer.

**Scope.** This is the compiler-focused paper of the two legitimate
scopes Section 12 distinguishes: formulation, implementation, and a
bounded evaluation against declared, constructed models, not an
end-to-end operational validation. A case study with domain-owner-
specified losses, an equal-information baseline comparison, and a
separately coded reference executor -- the stronger, operationally
validated scope -- is registered future work (Section 14), not
performed and not claimed here.

## 2. Problem Formulation and Guarantee Boundary

**Inputs.** A finite reachable set `R` of executable-reachable state
tuples over a declared set of candidate attributes `A`; a deterministic
declared verdict `v_M`, a boolean function of one reachable tuple (one
modeled safe-versus-unsafe distinction per loss predicate,
`domain.py`/`losses.py`); and, optionally, a strictly positive additive
declared observation cost `c(a)` per candidate attribute
(`costs_v7.py`/`costs_v8.py`). "Reachable" means executable-reachable
by this artifact's own declared construction (`domain.py`'s rank-0
union remediation-reachable set) -- a fact about the declared
construction, not a claim about every possible redesign; Proposition
0-general (`appendix-a-proofs.md`) establishes that, for a fixed
candidate representation and verdict function, the derivation depends
on the reachable set rather than on how an identical reachable set was
produced. It does not establish invariance to changing the candidate
representation itself.

**Representation assumption.** The full candidate-attribute projection
of a reachable tuple must determine `v_M`'s verdict on it -- two
reachable tuples agreeing on every declared candidate attribute cannot
disagree on their verdict, by construction of `v_M` as a function of
the declared candidates. This is a consistency requirement on the
declared model, not an assertion that observing every candidate
attribute suffices for an arbitrary malformed or incomplete input; a
tuple outside the declared reachable set, or missing a declared
attribute's value, is outside every guarantee below.

**Definition 1 (observation contract).** An observation contract is a
set `S` of candidate attributes. `S` is **sufficient** for `v_M` on `R`
(Definition 4 below) iff any two reachable tuples agreeing on every
attribute in `S` also agree on their `v_M` verdict -- `S` determines the
declared verdict, not merely correlates with it. A sufficient
observation contract selected under an explicit objective (minimum
cardinality or minimum declared cost, Section 3) and bound to a gate
schema is an **authority contract**: the runtime-facing object this
paper's implementation produces (Section 4). Every claim in this paper
about "sufficiency" is a claim about an observation contract; "authority
contract" names the same object once an objective and a binding have
been applied to it.

**Definition 2 (participation, the one-flip criterion).** Attribute `a`
is authority-bearing for `v_M` iff there exist reachable tuples `t`,
`t'` differing only in `a` -- a single flip, holding every other
candidate attribute fixed -- whose `v_M` verdicts differ
(`participation.py`, swept exhaustively over every candidate attribute
against every loss predicate, over the full enumerated reachable set,
not a sample). The same single-flip comparison, run independently by
hand against the imported baseline's own declared authority policy
rather than against this artifact's derivation, is the origin of this
pair-testing approach and reported four coverage boundaries of that
policy (Moona Intelligence, 2026).

**Definition 3 (the core).** The set of every attribute participating
by Definition 2. **Definition 4 (sufficiency, restated via
discernibility).** `S` is sufficient for `v_M` on `R` iff, for every
pair of reachable tuples whose verdicts differ (a cross-verdict pair),
`S` intersects that pair's *difference set* (the candidate attributes
on which the pair disagrees) -- machine-checked equivalent to the
direct partition test above, not merely assumed equivalent
(`checkers/discernibility_check.py`: [GENERATED: discernibility_check_model_count]
declared models checked, every one agreeing,
[GENERATED: discernibility_check_all_agree]; Skowron and Rauszer's own
discernibility-matrix device, 1992). **Definition 5 (a reduct).** An
inclusion-minimal sufficient observation contract: sufficient, and no
proper subset is. **Definition 6 (the core, restated as an
intersection).** The intersection of every reduct -- machine-checked
equal to Definition 3's own witness-search answer wherever both are
computed (`checkers/reduct_check.py`), not assumed equal from the two
definitions' own statement alone.

**Core versus reduct, stated once, without chronology.** Definition 3's
core (individual indispensability, a singleton-perturbation witness)
and Definition 5's reduct (joint sufficiency, Definition 4) are
different properties in general: the core is always a subset of every
reduct, but need not itself be sufficient. The registered two-state
counterexample makes this precisely (`prereg/fixtures/negative-
proposition-n-counterexample.json`; candidate attributes `x, y in {0,
1}`, reachable set `{(x=0,y=0), (x=1,y=1)}`, verdict `v_M(x,y) = x`):
the core is **empty** (no reachable pair differs in exactly `x` or
exactly `y` alone -- the set's only two members differ in both at
once), trivially not sufficient, while `{x}` and `{y}` are each an
independent singleton reduct. *If* the core happens to be sufficient,
*then* it is the unique reduct -- an antecedent never assumed, always
decided per instance by a sufficiency check or a concrete
counterexample (`appendix-a-proofs.md`'s Proposition 1', claims one
through three; Section 13's Corrections records how this was
established). Section 6's own two constructed domains are chosen
specifically to test whether core and reduct coincide on a domain not
designed around the question; mostly, they do not.

**Cost boundary.** Where a declared observation cost is used (Section
6), it is a declared additive score with strictly positive per-
attribute weights (`costs_v7.py`/`costs_v8.py`) -- not necessarily a
monetary cost, and not a measured end-to-end acquisition latency.
Strict positivity is what makes a minimum-cost sufficient contract a
reduct, not merely sufficient: a proper sufficient subset would have
strictly lower total cost, contradicting minimality (`synthesis.
find_minimum_cost_contract` enforces this by construction, raising on a
non-positive declared cost rather than silently accepting one).

**What this section does not claim.** A single admit/deny verdict
preserved exactly is not automatically equivalent to preserving the
identity of every individually violated loss predicate -- this paper's
own `v_M` is the declared boolean verdict function each domain's own
`losses.py`/`losses_v4.py`/`losses_v8.py` defines, and every
`v_M`-preservation claim below is relative to that exact function,
stated once here rather than re-qualified at every occurrence.

## 3. Method: From Discernibility to Selected Contracts

**One algorithm, three families of instantiation.** Given `R`, `A`,
`v_M`, and (optionally) `c`:

1. Materialize or receive the reachable tuple set and evaluate `v_M` on
   every tuple.
2. Construct the difference set for every cross-verdict pair.
3. Remove any difference set that is a proper superset of another
   already in the family -- it adds no separate hitting-set constraint
   (`discernibility.remove_redundant_supersets`).
4. Encode the pruned family as CNF: one boolean variable per candidate
   attribute, one hard clause per surviving difference set ("at least
   one of these attributes is included").
5. Select a satisfying assignment: any one (plain SAT,
   `find_any_sufficient_contract`), a minimum-cardinality one (a unit
   soft clause per attribute, weight one, cardinality MaxSAT,
   `find_minimum_cardinality_contract`), or a minimum-cost one (the same
   construction with each attribute's declared cost as its own soft-
   clause weight, weighted MaxSAT, `find_minimum_cost_contract`).
6. Check the returned observation contract's sufficiency directly
   (Definition 4's own partition test); on a positive result this is a
   check summary (a partition-cell count and a uniformity flag,
   `reduct.sufficiency`'s own success return -- not the serialized
   partition), on a negative result a concrete counterexample pair.
7. Where exhaustive enumeration over `2^|A|` subsets is affordable,
   enumerate every reduct (`reduct.exact_reducts`); otherwise, a
   repeated-resolve blocking-clause method
   (`find_up_to_k_minimum_cardinality_contracts`) finds a capped,
   explicitly labeled lower bound on minimum-cardinality-contract
   multiplicity, never presented as an exhaustive count.

**Three separate evidence objects, never substituted for one another.**
A sufficiency check (step 6) establishes that one specific observation
contract determines `v_M`'s verdict. An inclusion-minimality or
cardinality/cost-optimality result (step 5, cross-checked against step
7 wherever exhaustion is affordable) establishes that the same contract
cannot be made smaller, or cheaper, without losing sufficiency. A
provenance record (which prereg, which commit, which committed JSON)
establishes that a given number in this paper traces to a specific,
reproducible run. None of these three is evidence for either of the
others.

**Correctness of the encoding, checked, not assumed.** Every backend
above is held to `reduct.exact_reducts()`'s own from-first-principles
answer everywhere exhaustion is affordable
(`checkers/synthesis_exactness_check.py`:
[GENERATED: synthesis_exactness_model_count] declared models checked,
every one exact,
[GENERATED: synthesis_exactness_all_exact]) -- a real encoding
regression would be caught by this comparison, not assumed away by
trusting the solver. This is a bounded-instance exactness check, not a
general proof that the encoding is correct for every possible loss
model; Section 7 reports where exhaustive cross-checking itself stops
being affordable, and what evidence remains once it does.

**Why minimum-cardinality and minimum-cost selections are also
reducts.** If a proper subset of a minimum-cardinality sufficient
contract were itself sufficient, it would have strictly smaller
cardinality, contradicting minimality -- so a minimum-cardinality
selection cannot properly contain a smaller sufficient set, exactly
Definition 5's own minimality clause. The same argument holds for
minimum-cost selection under the strictly-positive cost boundary
Section 2 states.

## 4. Implementation and Verification Interface

**Package.** `src/authority_compiler` (installable: `pip install .` or
a built wheel, `python -m build`, verified in a fresh virtual
environment with no repository root, pythonpath, editable install, or
sibling directory present, `make package-smoke-test`) packages this
paper's own machinery behind one call, `derive_authority_contract
(loss_model, reachable_semantics, candidate_context, observation_costs)`,
returning a compiled `AuthorityContract`.

**Returned fields, and what each one currently is.** The core
attributes (Definition 3); every reduct where `len(candidate_context)`
stays within an explicit, documented exhaustion limit (`None` with a
stated reason otherwise, never silently truncated or sampled); the
minimum-cardinality and minimum-cost reducts; the non-core attributes
(`candidate_properties` minus the core); a `sufficiency_certificate`
field that is, currently, the same check-summary shape Section 3 step 6
describes -- computed for the **core attributes specifically**, not
automatically for whichever contract a caller ultimately selects;
`counterexamples`, populated when the core is not sufficient; a
`reachability_dependencies` field naming candidate attributes whose
observed value set in `reachable_semantics` is a strict subset of their
declared domain in `candidate_context` -- detected directly by
comparing the two, a genuine but narrow signal (which attributes SOME
reachability constraint restricts), not full cross-attribute dependency
inference; and a bound `contract_change_delta` callable (Section 7).

**Verification boundary, stated plainly.** The current implementation
is executable checking: a caller can re-run `reduct.sufficiency` on any
returned contract and get the same check summary or counterexample this
paper reports. It is not yet a portable, proof-carrying runtime
artifact: nothing in `sufficiency_certificate`'s current shape lets a
separate consumer verify a contract's sufficiency without re-running
this artifact's own code against the same reachable set and loss model.
Describing it as a portable certificate a downstream gate consumes
without recomputation would exceed what the inspected interface
establishes; this paper does not do so (Section 8, C5).

**What remains downstream engineering.** Gate-schema binding and
enforcement code are not implemented by this package. The artifact's
own execution-grant mechanism (single-use, machine-checked,
`grant.py`/`checkers/grant_check.py`) is a worked example of the
capability-representation layer downstream of contract selection, not
part of the derivation this paper claims, and is informed by, not a
novelty claim against, the capability-systems lineage Section 9 cites.

## 5. Evaluation Design

**Questions, not development versions.** Five questions organize the
evidence, matching Section 6's own results and Section 8's own claims
table:

- **RQ1.** Do selected observation contracts preserve `v_M`'s verdict on
  their declared finite models?
- **RQ2.** Does the core fail to suffice, and do genuinely alternative
  sufficient contracts exist?
- **RQ3.** Does a declared cost objective distinguish among alternative
  minimum-cardinality contracts?
- **RQ4.** Where is compilation practical, including the preprocessing
  a solver's own reported time does not include?
- **RQ5** (conditional, not attempted here). Does synthesis improve on a
  competent manual or conservative alternative in an independently
  specified operational workflow?

**Domain provenance, kept separate.** Every domain this paper reports
on is a declared, **constructed** executable model
(`domain.py`/`domain_v4.py`/`domain_v8.py`/`domain_datacomms.py`),
never a live deployment or live production system. "Non-planted"
(reachability rules and derivation logic fixed for organisational
plausibility before any core/reduct/cost outcome was computed, verified
structurally, `domain_v8.py`'s own docstring for the Section 6 large
domain), "organisationally plausible" (the constructed domain's own
declared rationale), and "independently specified" (a domain-owner-
authored loss model, not attempted here) are three separate properties;
none of this paper's domains claims the third, and none implies
another.

**AuthorityBench.** Four baselines -- manual least-privilege (the
declared-only shape), ABAC policy mining (reimplemented from Xu and
Stoller, TDSC 2015, independently validated against the published
"Health Care Sample Policy" case study before being trusted here,
`xu_stoller_validation.py`: [GENERATED: ab_xu_stoller_mining_validated]),
essential-variable analysis, and exhaustive reduct enumeration -- across
[GENERATED: ab_domain_count] constructed domains (procurement,
code/cloud, data-and-communications), six metrics each (correctness,
contract size, declared cost, runtime, peak memory, counterexamples).

**What was rerun for this revision, and what was not.** This revision
changes no result: it reruns no benchmark, no scaling family, and no
AuthorityBench domain. `make formal`'s own checkers (Section 6's and
Section 8's evidence anchors) run on every `make release-check`/`make
quick-reproduce` invocation, including the one gating this commit; the
scaling and AuthorityBench results in Section 6 and Section 7 are read
from their own already-committed `out/results/*.json`, generated on the
runs their own prereg names, and are labeled as retained where that is
what they are.

## 6. Results: Semantic Correctness, Alternatives, and Cost

**Consolidated table.**

| Domain/result | Candidate attributes | Reachable tuples | Core | Minimum-cardinality contract | Multiplicity | Cost finding |
|---|---:|---:|---|---|---|---|
| Code/cloud, CH-B1/CH-B2 | [GENERATED: ch_b1_candidate_property_count] | [GENERATED: ch_b1_reachable_swept] | [GENERATED: ch_b1_core_cardinality]; [GENERATED: ch_b1_core_sufficient_status] as a contract | [GENERATED: ch_b1_min_reduct_cardinality] attributes | Exactly [GENERATED: ch_b1_num_reducts] reducts | Declared scores [GENERATED: ch_b2_min_cost_contract_total_cost] versus [GENERATED: ch_b2_other_reduct_cost] |
| Large constructed domain, CH-C1/CH-C2 | [GENERATED: ch_c1_candidate_property_count] | [GENERATED: ch_c1_reachable_swept] | [GENERATED: ch_c1_core_cardinality]; [GENERATED: ch_c1_core_sufficient_status] as a contract | [GENERATED: ch_c1_min_cardinality] attributes | At least [GENERATED: ch_c1_contracts_found_count] contracts, capped at [GENERATED: ch_c1_multiplicity_cap] | All [GENERATED: ch_c2_num_tied_contracts] returned alternatives tie at [GENERATED: ch_c2_min_cost_contract_total_cost] |

**RQ1/RQ2: semantic correctness and alternatives.** CH-B1
(`domain_v4.py`, [GENERATED: ch_b1_power_set_size] candidate subsets of
[GENERATED: ch_b1_candidate_property_count] considered, subset-pruned)
and CH-C1 (`domain_v8.py`) each instantiate a core that is
**[GENERATED: ch_b1_core_sufficient_status]** /
**[GENERATED: ch_c1_core_sufficient_status]** as an observation
contract on its own, with genuinely alternative minimum-cardinality
contracts: CH-B1's own two,
`{`[GENERATED: ch_b1_reduct_branch_list]`}` or
`{`[GENERATED: ch_b1_reduct_environment_list]`}`, each independently
checked sufficient (Definition 4); CH-C1's own
[GENERATED: ch_c1_contracts_found_count], a genuine lower bound via the
blocking-clause method (Section 3, step 7), never rounded up to an
exact count. Removing every attribute outside the core is not justified
by that attribute's non-core status alone: `branch` and `environment`
are each non-core in CH-B1, and each is still required by one of its
two minimum-cardinality contracts.

**RQ3: cost separation, in one domain and not in the other.** CH-B2
(`checkers/ch_b2_check.py`, [GENERATED: ch_b2_reachable_swept] reachable
tuples, [GENERATED: ch_b2_subsets_considered] subsets considered) is
**[GENERATED: ch_b2_status]** -- `[GENERATED: ch_b2_outcome_subcase]`:
the minimum-cost contract
(`{`[GENERATED: ch_b2_min_cost_contract_list]`}`, cost
[GENERATED: ch_b2_min_cost_contract_total_cost]) is strictly cheaper
than CH-B1's other minimum-cardinality reduct (cost
[GENERATED: ch_b2_other_reduct_cost], delta
[GENERATED: ch_b2_cost_delta]), both independently checked sufficient
(`all_alternatives_safety_equivalent:
[GENERATED: ch_b2_all_safety_equivalent]`) before cost is consulted.
This is a narrower finding than "cost separates alternatives in
general": CH-B2 selects between two contracts of the *same* minimum
cardinality; it does not show that a larger, non-minimum-cardinality
contract is ever cheaper than every minimum-cardinality contract in
this domain, and no claim to that effect is made. CH-C2 (same domain
family, `checkers/ch_c2_check.py`,
[GENERATED: ch_c2_reachable_swept] reachable tuples) is the retained
negative counterpart: **[GENERATED: ch_c2_status]** --
`[GENERATED: ch_c2_outcome_subcase]`, every one of
[GENERATED: ch_c2_num_tied_contracts] known minimum-cardinality
contracts costing exactly [GENERATED: ch_c2_min_cost_contract_total_cost]
under this domain's own seven-tier declared cost model. The mechanism,
not smoothed over: the tied contracts substitute attributes from the
*same* declared cost tier for one another, so a cost model built at
this tier granularity cannot discriminate between them. Declared-cost
selection is conditional on the cost model separating the substitutes
actually in play; CH-B2 and CH-C2 are two constructed domains where it
does and does not, respectively, and neither generalizes to the other.

**AuthorityBench: the declared-only baseline.** The manual least-
privilege baseline is not exactly sufficient (Definition 4) on any of
AuthorityBench's [GENERATED: ab_domain_count] domains
([GENERATED: ab_v2_manual_correct] / [GENERATED: ab_v4_manual_correct] /
[GENERATED: ab_dc_manual_correct]) -- Section 1's opening claim,
measured across all three AuthorityBench domains, not
asserted from one. Mining agrees with the packaged minimum-cardinality
answer on the procurement and code/cloud-core instances, and lands on
the *other* known minimum-cardinality contract (the `environment`
variant of CH-B1's own two) on the code/cloud domain -- both
independently verified minimum-cardinality contracts of the identical
model, a tie-break divergence between two correct global optima, not a
disagreement about which attributes matter. By the registered decision
rule applied to what was actually measured (two domains equal, one a
benign tie, no strict-superset case on any domain), this comparison is
**inconclusive**: reported as such, not reframed as a win, per the
registration's own commitment to report whatever was measured.

**Two further registered results.** The budget-binding scenario (v5.2)
constructs a procurement scenario where the budget loss predicate
actually fires -- in [GENERATED: v52_cells_with_fire] of
[GENERATED: v52_n_cells] cells ([GENERATED: v52_total_fire_count]
firings total) -- and the derived-zero-miss guarantee held on every one
(**[GENERATED: v52_status]**; derived misses
[GENERATED: v52_derived_missed_ci] against a declared-only baseline
missing [GENERATED: v52_baseline_missed_ci]). The isolated-arm
re-measurement (v3.1) found a real internal-validity defect (the
baseline, derived, and over-inclusive experiment arms sharing one
budget and one grant ledger) by this project's own code inspection,
registered before any fix was written; the isolation hypothesis itself
was **[GENERATED: v4_isolation_status]** -- all thirty registered seeds,
re-run under an isolated `ArmState` design, reproduce the prior shared-
state result's own means, confidence intervals, and booleans exactly, a
direct diagnostic confirming the one loss predicate the defect could
have corrupted never fired under this declared parameter set. The
corrected, isolated design is kept regardless of the null result.

## 7. Computational Behaviour and Change Analysis

**What is, and is not, separately measured.** Three registered scaling
results exist, at three different granularities, none superseding
another. None of them, and none of CH-B1/CH-C1/CH-B2/CH-C2's own
checkers, separately records tuple-construction time, verdict-
evaluation time, and discernibility-family-construction time as
distinct numbers from solving time -- checked directly against their
own committed JSON before writing this paragraph, not assumed present.
Where a number below is a per-backend wall-clock time, it is the
backend's own total call (discernibility-family construction plus
solving together); this is stated here once, honestly, as a measurement
granularity limit, per the revision outline's own instruction, rather
than reconstructed from an end-to-end total that was never designed to
decompose this way.

**The exploratory result (v5.0, kept, degeneracy disclosed).** Scaling
candidate-attribute count alone (`n` =
[GENERATED: v50_n_values]) while holding the reachable set fixed at
[GENERATED: v50_reachable_tuple_count] tuples produced
`all_exact: [GENERATED: v50_all_exact]` at every size, wall time
between [GENERATED: v50_wall_time_min]s and
[GENERATED: v50_wall_time_max]s with no distinguishable growth trend --
a real, valid answer to the narrow question it was built for, and a
**degenerate** one for scaling in general: the added attributes never
appear in any discernibility-family clause, costing the solver nothing
beyond one extra boolean variable each. Superseded as the primary
scaling claim by the two results below, kept and cited, not deleted.

**Tuple scaling (v5.1, kept).** Holding candidate-attribute count small
enough to stay exhaustible, a planted two-reduct family grows the
*reachable set itself* to [GENERATED: v5_1_max_reachable_tuples]
tuples: the discernibility family still reduces, after pruning, to
exactly [GENERATED: v5_1_family_size_after_pruning] set, and all
[GENERATED: v5_1_num_reducts] planted reducts are recovered exactly by
every backend.

**The primary scaling table (v5.3): combinatorial hardness.** Three
constructed families pair a planted minimum-cardinality reduct size
with a large candidate-attribute universe and a diverse discernibility
structure:

| Family | Candidate attributes (n) | Reduct size (k) | Discernibility family after pruning | Exhaustive enumeration |
|---|---|---|---|---|
| A | [GENERATED: v5_3_family_a_n] | [GENERATED: v5_3_family_a_k] | [GENERATED: v5_3_family_a_pruned_family_size] sets | Timed out, [GENERATED: v5_3_exhaustive_budget_seconds]s |
| B | [GENERATED: v5_3_family_b_n] | [GENERATED: v5_3_family_b_k] | [GENERATED: v5_3_family_b_pruned_family_size] sets | Timed out, [GENERATED: v5_3_exhaustive_budget_seconds]s |
| C | [GENERATED: v5_3_family_c_n] | [GENERATED: v5_3_family_c_k] | [GENERATED: v5_3_family_c_pruned_family_size] sets | Timed out, [GENERATED: v5_3_exhaustive_budget_seconds]s |

The [GENERATED: v5_3_exhaustive_budget_seconds]-second figure is a
measured timeout under this project's own recorded hardware and setup,
registered as *expected* infeasible and confirmed so on all three
families -- not a complexity lower bound, and not a claim that no
faster exhaustive method exists in general. Cardinality- and cost-
MaxSAT both found the hand-proved minimum-cardinality reduct at every
family regardless, each backend's own solve call completing in well
under a
second; the same discernibility-family construction that defeats
exhaustive enumeration on a family does not, on these three families,
defeat the solvers synthesizing over it. This is a comparison of two
different workloads (find every reduct versus find one reduct under an
objective), not one workload measured twice, and is stated as such --
a sub-second solver stage is not, by itself, evidence of superiority
over exhaustive enumeration on the same task, since the two never
attempt the same task. Two-sided, reported as measured: does MaxSAT
give a meaningful cardinality advantage over plain SAT here?
[GENERATED: v5_3_maxsat_advantage_any_family] -- registered to accept
and report a uniformly-absent advantage as a legitimate outcome, which
is what was found.

**The large domain (CH-C1/CH-C2).** Exhaustive `reduct.exact_reducts()`
was separately attempted on the Section 6 large domain, registered
budget [GENERATED: v8_exhaustive_budget_seconds] seconds, and confirmed
infeasible (`feasible: [GENERATED: v8_exhaustive_feasible]`, measured
wall time [GENERATED: v8_exhaustive_wall_time_seconds]s, against
[GENERATED: v8_exhaustive_size7_subset_count] size-seven subsets alone)
-- the same registered-timeout-versus-solver-success pattern as the
v5.3 families, demonstrated on a domain built for realism rather than
hardness.

**Change analysis: monotone extension only.** `contract_change_delta`
handles exactly one class of change: additional tuples reachable under
the SAME declared candidate schema and the SAME declared loss registry
-- a base contract already known sufficient on the prior reachable set,
checked directly against the combined set, and, if no longer
sufficient, extended by the fewest additional attributes needed while
every attribute the base contract already relied on stays pinned. A
change to the loss registry itself, a change to the candidate schema, a
removed reachable tuple, or automatic drift detection are each a
different kind of change this function does not handle and this paper
does not claim it handles; `reachability_dependencies` (Section 4)
detects a narrower signal (which attributes some reachability
constraint currently restricts), not general cross-attribute
dependency inference. On one small worked illustration (base contract
`{`[GENERATED: ccd_base_contract]`}`), a new tuple collides with an
existing one under the base contract's own projection, sufficiency
drops (`was_still_sufficient:
[GENERATED: ccd_was_still_sufficient]`), and the incremental update
(`{`[GENERATED: ccd_updated_contract]`}`) is independently checked
sufficient and matches free-choice full recomputation exactly in this
illustration (cardinality gap
[GENERATED: ccd_full_recomputation_cardinality_gap]) -- one worked
example, not a general guarantee; `test_synthesis.py`'s own unit tests
separately construct a case with a genuinely nonzero gap, the honest
price of pinning a prior contract rather than reoptimizing freely.

## 8. Claim-by-Claim Evidence

Every headline claim in this paper maps to one of the ten claims a
commissioned revision outline registered
(`review-secondary/paper-revision-outline-2026-09-15.md`, section
"Claim-by-claim evidence checklist"), adjudicated against this
artifact's own current committed state rather than copied from the
outline's own point-in-time observations. **Supported** means bounded
evidence exists on checked finite instances, not that novelty or
generalization is independently certified; **Partial** means an
implementation and some evidence exist, but a stronger wording is not
yet licensed by what is checked; **Proposed** means the work described
has not been performed in this artifact.

| Claim | Permitted claim | Status |
|---|---|---|
| C1 | The selected observation contract preserves `v_M`'s verdict over the supplied reachable set. | Supported on checked finite instances ([GENERATED: discernibility_check_model_count] models cross-checked, [GENERATED: discernibility_check_all_agree]); the general argument (Section 2) requires the stated representation assumption. |
| C2 | CH-B1 and CH-C1 instantiate core insufficiency; CH-B1 has exactly [GENERATED: ch_b1_num_reducts] reducts, CH-C1 exposes at least [GENERATED: ch_c1_contracts_found_count] minimum-cardinality contracts. | Supported; both checkers ran as part of this commit's own `make formal`. |
| C3 | The implementation selects minimum-cardinality or minimum-cost sufficient contracts, the latter under a declared-cost objective, using distinct objectives (Section 2's cost boundary). | Supported by implementation and bounded exactness checks ([GENERATED: synthesis_exactness_model_count] models, [GENERATED: synthesis_exactness_all_exact]); optimality beyond exhaustible instances relies on the solver/encoding boundary Section 3 states. |
| C4 | CH-B2 selects the cheaper of two equal-cardinality sufficient contracts; CH-C2's returned alternatives tie. | Supported as a model-relative finding on both domains. A same-commit floating-point serialization non-determinism the outline's own commissioned reproduction found (`out/checkers/ch_c2_check.json`, cross-Python-version summation) is fixed as of this lineage's own reproduction-repair commit (`synthesis.total_cost`, `REPRODUCTION.md`'s own Corrections note) -- not an open caveat of this draft. |
| C5 | The implementation executes a sufficiency check and returns a check summary on success or a concrete counterexample on failure. | Partial by design, not by gap: Section 4 states plainly that `sufficiency_certificate` is a check summary bound to the core attributes, not a portable, independently-verifiable certificate -- the stronger wording this claim could otherwise support is deliberately not used (Section 4). |
| C6 | The built wheel supports the documented black-box example from a fresh environment, outside this repository's own source tree. | Supported; the missing `build` prerequisite the outline's own commissioned reproduction found is now installed directly by `bootstrap.sh` (this lineage's own reproduction-repair commit), not merely documented as a one-off environment fix. |
| C7 | For additional reachable tuples under the same declared schema and loss registry, the implementation checks prior sufficiency and can extend a contract while preserving its existing attributes. | Implemented with supporting tests (Section 7); a dedicated, independently specified operational change study is registered future work, not performed. |
| C8 | Measured computational behaviour is reported for the specific constructed families and domains tested; all-reduct exhaustive enumeration and one-contract SAT/MaxSAT optimisation are labelled as non-equivalent workloads, never interpreted as an apples-to-apples speed comparison. | Supported: Section 7 states this comparison is two different workloads (find every reduct versus find one reduct under an objective), not one workload measured twice; the scaling and AuthorityBench measurements in Section 6 and Section 7 are retained from their own registered runs, not rerun for this revision (Section 5). |
| C9 | This paper's formulation, interface, or demonstrated application differs from the closest prior work in a specific, source-supported way. | Partial: Section 9 compares against the closest clusters fetch-verified in `verified-citations.json`, expanded in this revision with two additional prior-art clusters (decision/test-cost-sensitive reducts, supervisory-control sensor/observation selection) per a commissioned manuscript audit (`review-secondary/manuscript-audit-2026-09-17.md`); a fresh, independently re-verified comparison-matrix exercise beyond that existing record was not newly performed (zero new experiments). |
| C10 | This artifact's reproduction claims state exactly which computational checks were completed, their deviations, and the scope of the reproduction evidence behind them. | Supported: `REPRODUCTION.md`, `FINAL-AUDIT.md`'s own external-reproduction item, and the commissioned reproduction evidence (`review-secondary/reproductions/2026-09-14-perplexity-computer/`) together distinguish semantic agreement, within-run byte identity, cross-environment byte identity, and independent-person reproduction; that item is now MET, an independent reproducer having run and reported CH-B1 matching this repository's own committed hash (`besanson/sarc-authority-derivation#3`, Section 11). |

## 9. Related Work and Contribution Boundary

Eleven neighbouring literature clusters, each fetch-verified
(`verified-citations.json`), compared on what each establishes as
input, output, objective, guarantee, and verification interface,
against what this paper contributes.

**Decision reducts and test-cost-sensitive attribute reduction**
(Pawlak 1982; Skowron and Rauszer 1992; Min, He, Qian, and Zhu 2011).
Decision-reduct theory supplies the mathematical notions this paper's
own Section 2 uses: joint sufficiency, inclusion-minimal reducts,
cores, and discernibility functions (Skowron and Rauszer 1992,
restating Definition 4) -- and, once a declared per-attribute cost is
introduced, test-cost-sensitive attribute reduction formulates the
problem of a sufficient reduct at minimum observation/test cost (Min,
He, Qian, and Zhu 2011). This paper does not claim those notions, or
their SAT/hitting-set realization, as new. The contribution here is to
construct the decision system itself from declared governance losses
plus executable reachability, interpret reducts as runtime
authority-observation contracts, expose that derivation through an
executable compiler interface, and evaluate its behaviour on
autonomous-system governance domains.

**STPA and its descendants** (Leveson and Thomas's STPA Handbook 2018;
Young and Leveson's STPA-Sec, CACM 2014). Classical STPA is an
analyst-led hazard-analysis methodology that derives unsafe control
actions and safety constraints from a system control structure,
reviewed by a person rather than machine-checked. This paper borrows
STPA's loss-to-constraint orientation, but solves a different finite
synthesis problem: selecting a sufficient and minimal (Definition 4,
Definition 5) observation subset for an already-declared, exhaustively
checked executable verdict relation. Automated and formal STPA extensions (Rismani, Dobbe, and
Moon's PHASE 2024; Mylius 2025; Qi et al.'s DeepSTPA 2023) remain
adjacent to this classical picture rather than characterized here as
purely manual.

**ABAC policy mining** (Xu and Stoller, TDSC 2015; Nobi et al.'s 2022
survey). Input: an extant authorization relation or policy plus
attribute data. Output: a generalized ABAC rule set intended to
reproduce or compactly generalize that extant authorization relation
under a policy-quality objective. This paper instead starts from an
independently declared loss model forward to the observation contract
a *new* gate must observe, with a checked sufficiency and minimality
result (Definition 4, Definition 5) mining cannot provide without one;
Section 6's own AuthorityBench comparison reimplements Xu and Stoller's
method rather than only citing it, and reports it inconclusive rather
than beaten.

**Policy-language completeness** (Crampton and Morisset's PTaCL, POST
2012; Crampton and Williams's canonical-completeness result, SACMAT
2016). Input/output: a fixed set of participating attributes and base
decisions, combined by a policy-combination language. Guarantee:
expressiveness of the combination language itself. Neither asks which
attributes must be observed in the first place -- the question this
paper answers upstream of theirs.

**Non-interference** (Goguen and Meseguer 1982). A semantic *check* of
dependence between two fixed parties -- in general, neither a derivation
procedure nor a minimality guarantee. A conceptually related invariance
under changes to selected inputs, not the same formal operation as
Definition 2: this paper sweeps a per-attribute comparison over every
candidate attribute against every loss predicate, with a sufficiency
and minimality result checked exhaustively over the declared reachable
set, not one designated-pair check.

**Counterfactual fairness** (Kusner, Loftus, Russell, and Silva 2017).
A conceptually related invariance under changes to selected inputs,
defined via counterfactual interventions in a causal model and applied
once, to one pre-chosen sensitive attribute, against a fairness
objective -- not the same formal operation as Definition 2. This paper
applies a per-attribute comparison to every candidate attribute against
a declared loss model and adds a checked minimality result (Definition
5) neither claimed nor checked by that literature.

**Shield synthesis** (Bloem, Bettina Könighofer, Robert Könighofer, and
Wang, TACAS 2015). Input: a reactive system and an omega-regular safety
specification, over an *already-declared* interface. Output: a runtime
monitor correcting violating outputs. This paper solves an orthogonal
upstream problem in this artifact of which attributes an enforcement
point must observe at all, with a checked minimality guarantee
(Definition 5), an orthogonal upstream problem in this artifact
relative to the corrective strategy shield synthesis solves for.

**Runtime enforcement and edit automata** (Schneider, TISSEC 2000;
Ligatti, Bauer, and Walker 2005). Input/output: a fixed, already-
declared target-action alphabet and a monitor's own corrective
repertoire over it. Minimal selection of per-decision observation
attributes is not the central problem those works formulate -- the
antecedent question this paper answers, with a minimality guarantee
(Definition 5) neither work needs for its own narrower question.

**Controller synthesis** (Ramadge and Wonham 1987; Pnueli and Rosner,
POPL 1989). Input: a plant's or module's own already-fixed observable/
controllable alphabet. Output: a control law within it. This paper
derives the alphabet a controller (here, a pre-action authority gate)
must observe, before any supervisor or reactive module is synthesized
over it.

**Observation/sensor selection in supervisory control** (Rohloff,
Khuller, and Kortsarz 2006; Hu and Chen 2026). Classical
supervisory-control formulations (Ramadge and Wonham 1987; Pnueli and
Rosner 1989, above) often assume an observation structure is already
fixed, but a separate literature explicitly studies minimum-cardinality
and minimum-cost sensor or event observation sufficient for supervisor
synthesis: Rohloff, Khuller, and Kortsarz formulate minimal sensor
selection for supervisory control as a graph-cut problem with
approximation guarantees, and Hu and Chen minimize the observation
alphabet a supervisor needs while preserving control equivalence with
the original supremal supervisor. This paper does not claim to
originate minimum-observation synthesis. The distinction is the object
and semantics being compiled: candidate per-decision governance
attributes, a declared loss-derived verdict, and an executable
reachable-state relation, rather than event sensors preserving
supervisory controllability or a temporal control specification. The
output is a sufficient, checked-minimal (Definition 4, Definition 5)
authority-observation contract, not a synthesized controller.

**Capability systems** (Dennis and Van Horn 1966). Capability systems
provide mechanisms for representing, attenuating, delegating, and
verifying authority -- an unforgeable reference, propagated by
controlled copying, and, in this lineage's modern descendants
(Macaroons, UCAN, Biscuit, already cited in Section 4 for the grant's
own bearer-token design), contextual caveats or conditions evaluated at
delegation or invocation. This paper does not claim novelty in those
mechanisms; its distinct question is how, from declared losses and
reachable execution states, to synthesize a sufficient/minimal set of
candidate observations that could inform such authorization conditions.

**Contribution boundary.** This paper does not introduce reduct theory,
discernibility functions, minimum-cardinality or minimum-cost attribute
selection, SAT/MaxSAT optimization, runtime enforcement, capability
attenuation, or minimum-observation supervisory control. Its
contribution is the governance-specific compilation problem and
evaluated system: derive the decision relation from declared loss
semantics and executable reachability, synthesize sufficient runtime
observation contracts over that relation, expose cardinality- and
cost-optimal contracts with explicit sufficiency/counterexample checks,
and evaluate that formulation across constructed autonomous-system
governance domains. This is a combination and an evaluated behaviour,
not a claim that no neighbouring field could in principle provide an
equivalent guarantee; no such broader claim is made.

## 10. Limitations

- **Declared loss-model completeness** is assumed, not verified: a
  declared model missing a real hazard still produces a checked core or
  contract *for the declared model*, silently uninformative about the
  missing one.
- **Reachability-model validity**: every result above is exact *given*
  its own declared reachable set, transcribed from its own prereg, not
  measured from a live deployment.
- **Partial observability** is not modeled: every synthesis backend
  assumes the candidate attributes it is given are the ones a gate
  *could* observe; an attribute outside that declared set cannot be
  discovered as missing by this machinery.
- **Temporal and probabilistic losses** are out of scope: every loss
  predicate here is a boolean function of one reachable tuple, not a
  sequence or a probability distribution over outcomes.
- **Declared-cost validity**: the cost objective (Section 2) is a
  declared additive score with strictly positive weights, not
  necessarily monetary cost or measured latency; correlated acquisition
  costs and shared lookups are not represented by an additive model, and
  no sensitivity analysis on the declared weights is performed here.
- **Families that defeat exhaustive enumeration are not automatically
  hard for the solvers synthesizing over their own discernibility
  family** (Section 7) -- a fact about this specific construction on
  these specific families, not a general claim that no synthesis
  instance can be hard.
- **Contract multiplicity in the large constructed domain (CH-C1) is a
  lower bound**, capped at [GENERATED: ch_c1_multiplicity_cap] by the
  blocking-clause method; whether more minimum-cardinality contracts
  exist above the cap is open, and every occurrence of this number
  states it as "at least," never rounded up.
- **External validation**: the reproduction packet (`REPRODUCTION.md`)
  is this artifact's own attempt to make independent reproduction
  possible; a reproducer who did not build this artifact has since run
  it and reported back (Section 11; `FINAL-AUDIT.md`'s own external-
  reproduction item: MET).

## 11. Reproducibility

Four distinct properties, kept separate rather than collapsed into one
word "reproducible" (the revision outline's own C10 acceptance test):
**semantic agreement** (a rerun produces the same core, reducts, and
booleans -- checked on every `make formal` run, this commit's own
included); **within-environment byte identity** (two consecutive `make
formal` runs in the same process produce byte-identical
`out/checkers/*.json` -- `release-check`'s/`quick-reproduce`'s own
formal-double-run gate); **cross-environment byte identity** (the same
committed inputs produce byte-identical serialized output on a
different machine and Python interpreter -- the property a same-commit
hash mismatch in `out/checkers/ch_c2_check.json` exposed as failing
between `python3.11` and `python3.12`/`python3.13`, traced to `sum()`'s
own version-dependent float summation and fixed by `synthesis.
total_cost`'s declared-precision `math.fsum`, `REPRODUCTION.md`'s own
Corrections note); and **independent-person reproduction** (an
environment and a person not involved in this artifact's own
development, running the documented commands and reporting back). A
commissioned automated reproduction
(`review-secondary/reproductions/2026-09-14-perplexity-computer/`)
satisfies the first three at the commit it ran against and exercised
the fourth's own infrastructure without itself being one -- its own
report states this explicitly, not reinterpreted here as more than it
claims. The fourth property is now independently satisfied: a third
reproduction attempt, by a reproducer with no role in this artifact's
own development, ran `bash bootstrap.sh` (including the delegated
upstream release-check), `make package-smoke-test`, and the CH-B1
direct example from a clean, detached-HEAD clone at commit
`34cf82f05151971874f249e193543c2d6cf88b50`, and reported back a
matching `out/checkers/ch_b1_check.json` hash
(`besanson/sarc-authority-derivation#3`). `FINAL-AUDIT.md`'s own
external-reproduction item is now **MET**.

## 12. Conclusion

Given a declared loss model, a declared reachable-state model, and a
set of candidate attributes, this paper compiles sufficient observation
contracts rather than asking a gate builder to declare one by hand: it
distinguishes attributes that are individually indispensable from
contracts that are jointly sufficient, and it selects among sufficient
contracts by an explicit cardinality or declared-cost objective,
checking each selection directly (`reduct.sufficiency`) rather than
assuming it from construction. On two independently constructed domains
(CH-B1/CH-C1, `checkers/ch_b1_check.py`/`checkers/ch_c1_check.py`), the
individually-indispensable core is not itself a sufficient contract,
and genuinely alternative minimum-cardinality contracts exist; a
declared cost model (CH-B2/CH-C2) separates those alternatives on one
domain and does not on the other, both reported as found. Symbolic
synthesis remains practical on discernibility families where exhaustive
enumeration times out under this project's own measured setup.

This is the compiler-focused paper of the two scopes Section 1 and
Section 8's own claims table distinguish: a formulation, an
implementation with a stated verification boundary, and a bounded
evaluation against declared, constructed models -- not an end-to-end
operational validation. Section 14 registers, as a plan rather than a
result, what the stronger, operationally validated scope would require:
an independently specified case, equal-information baselines, and a
separately coded reference executor. No claim in this paper depends on
that plan being carried out, and none of its content is presented as
already having been.

## 13. Corrections

Append-only, per this project's own discipline: nothing below is
retracted or reworded; each correction is recorded alongside its
original claim, not in place of it. Historical propositions and the
full correction chronology live here and in Section 14, not
re-narrated in the sections above.

**The v1 singleton-sufficiency overclaim (corrected v0.3,
`prereg/v3-core-reduct-correction.md`).** The original Proposition 1
(frozen, `appendix-a-proofs.md`, preserved with its correction attached
rather than deleted) asserted that observing exactly the core lets a
gate always compute the declared verdict on any reachable tuple --
conflating individual indispensability (Definition 2's witness search)
with joint sufficiency (Definition 4). A commissioned external,
AI-assisted research review identified the mischaracterization
(`review-secondary/external-research-review-2026-09-06.pdf`, sha256
`b205faf65fe84d773260d1ed514b20f5b04e420380d3136c23bff1cde4506b0b`);
per this project's own discipline the finding was adjudicated against
this artifact's own definitions and re-derived from first principles,
not applied as a direct patch (`prereg/v3-core-reduct-correction.md`
records the adjudication). Proposition 1 is superseded by Proposition
1' (`appendix-a-proofs.md`, restated without chronology in Section 2
above), not deleted; its PROOF-STATUS is narrowed to
`checked-scope-only`.

**The v5.0 degenerate scaling benchmark (disclosed v5.1,
`prereg/v5.1-discernibility-scaling.md`).** Section 7's own exploratory
benchmark held the reachable set fixed while scaling candidate-attribute
count -- a valid answer to the question it was built for, but one where
the added attributes cost the solver nothing beyond one boolean
variable each, a structural reason its own flat wall-time curve cannot
be read as evidence of scaling in general. Relabelled `exploratory_v5_0`
from v5.1 forward, superseded as the primary scaling claim, kept and
cited.

**The entangled v0.3 experiment arms and their null delta (found and
corrected v0.4, `prereg/v3.1-isolated-arms.md`).** A budget/ledger-
sharing defect across three experiment arms, found by this project's
own code inspection, registered two-sided before any fix was written:
isolating the arms' state produced a result byte-identical to the prior
shared-state measurement across all thirty seeds and both workflows --
**NOT SUPPORTED**, with the mechanism explaining why (the one
vulnerable loss predicate never fired under this declared parameter
set) rather than left unexplained. The corrected, isolated design is
kept regardless of the null result.

**Cross-environment float-serialization non-determinism (found
`2026-09-14`, commissioned automated reproduction).** A same-commit hash
mismatch on `out/checkers/ch_c2_check.json`, traced directly (not
assumed) to Python's own built-in `sum()` returning a different last-bit
float for the identical sorted cost sequence between `python3.11` and
`python3.12`/`python3.13`. Fixed by `synthesis.total_cost` (`math.fsum` over sorted
input, rounded to a declared precision), confirmed identical across all
three tested interpreters; no registered result changed (CH-B2 remains
[GENERATED: ch_b2_status], CH-C2 remains [GENERATED: ch_c2_status]),
only spurious trailing digits no prose in this artifact ever read to
that precision. Full account: `REPRODUCTION.md`'s own Corrections
section.

**This revision (v0.6.1, `review-secondary/paper-revision-outline-
2026-09-15.md`).** A commissioned revision outline, committed unedited
and attested as not applied directly, identified terminology conflated
across `minimal`/`minimum`, `certificate`/`summary`, `constructed`/
`live`, and `core`/`non-core`, an append-only structure that had grown
chronological rather than claim-led, and several claims (the
observation-contract-before-authority-contract definition, the
compiler-focused scope statement, the change-analysis boundary) that
needed to be stated explicitly rather than left implicit. Every finding
was adjudicated against this artifact's own current committed state
(Section 8), not applied as a direct patch: `checkers/terminology_lint.py`
now enforces the four term-pair distinctions on this draft going
forward (`check_term_pairs`), and this section, Section 8, and
`REPRODUCTION.md`'s own Corrections note are where a reader can check
what changed and why. No result changed; no new experiment was run.

**This revision (v0.6.2).** Restores one citation the v0.6.1 rewrite
dropped: where the one-flip comparison is introduced (Definition 2),
the replication report is cited again as the source of that probe and
of its four coverage-boundary observations. Nothing else changes: no
new prose beyond that one sentence, no acknowledgement change, no
result changed, no new experiment run.

**This revision (v0.6.3).** A commissioned manuscript audit
(`review-secondary/manuscript-audit-2026-09-17.md`) found the evidence
discipline strong but identified wording-level claim mismatches and an
understated novelty fence. Corrected: C8's own wording (no longer reads
as comparing equivalent workloads, when Section 7 already says
otherwise); the Abstract's own domain description (previously calling
it "real" rather than constructed) and v8's own provenance description;
Section 6's own baseline-coverage claim; Section 2's Proposition
0-general summary (representation invariance, not claimed); and the
Abstract's own sufficiency-checking sentence. Section 9's novelty fence
gained two clusters (decision/test-cost-sensitive reducts;
supervisory-control sensor/observation selection; three new
fetch-verified citations) and tightened wording in the ABAC, STPA,
shield-synthesis, runtime-enforcement, capability-systems,
non-interference, and counterfactual-fairness paragraphs; the
Contribution boundary paragraph now carries the audit's own proposed
novelty statement verbatim. `checkers/terminology_lint.py` gained a
fifth term-pair check (constructed vs. real) alongside this correction.
No result changed; no new experiment was run.

**This revision (v0.6.4).** Two residues from the same manuscript audit,
wording only. First, the Introduction's own Running example still
called its domain "real" rather than constructed, missed by v0.6.3's
own version of the constructed-vs-real check: that check suppressed the
violation on finding a negation anywhere in the same paragraph (matching
`constructed vs live`'s own logic), and this paragraph's own unrelated
"a gate builder ... has no way to know" supplied one. The check now
requires the negation to be local to the match, a short window
immediately before it, re-run over the live manuscript to confirm
nothing else was hiding the same way. Second, the shield-synthesis
paragraph's closing "upstream of the corrective strategy shield
synthesis solves for" is restated as "an orthogonal upstream problem in
this artifact relative to the corrective strategy shield synthesis
solves for," so the paragraph's own closing comparison no longer risks
the same ordering-claim reading Definition 5's own upstream framing was
corrected against in v0.6.3. No result changed; no new experiment was
run.

**This revision (v0.6.5).** A third independent reproduction attempt
(`besanson/sarc-authority-derivation#3`) ran `bash bootstrap.sh`
(including the delegated upstream release-check), `make
package-smoke-test`, and the CH-B1 direct example at commit
`34cf82f05151971874f249e193543c2d6cf88b50` and reported back a matching
`out/checkers/ch_b1_check.json` hash -- `FINAL-AUDIT.md`'s own
external-reproduction item (Section 11's own fourth reproducibility
property) is now **MET**, not merely infrastructure-ready. Section 8's
C10 row, Section 10's own external-validation limitation bullet, and
Section 11 are updated accordingly; the Acknowledgements below credit
the reproducer by name. No result changed; no new experiment was run.

**This revision (v0.6.6).** The Acknowledgements are revised to credit
the independent reproducer's full name and affiliation, `Eduardo Arana
(Arananet)`, and to cover all three recorded reproduction attempts
(`#1`, `#2`, `#3`), not only the successful third -- attempts one and
two are corrections to the reproduction path (undeclared prerequisites;
the GNU-tar-only arXiv packaging invocation), both this reproducer's
own findings, credited here alongside the successful attempt rather
than only the one that closed `FINAL-AUDIT.md`'s own
external-reproduction item. No contact detail is added anywhere in
this repository. No result changed; no new experiment was run.

**The two commissioned external review rounds preceding this one, and
this project's own adjudication discipline.** Round one
(`review-secondary/external-research-review-2026-09-06.pdf`) produced
the core-versus-reduct correction above. Round two
(`review-secondary/final-gap-plan-9.5-2026-09-09.pdf`, sha256
`0d1d0ca1e9672b893f97fd0dd4289574dba7b84775ae060f7830e3c2f2b82bc9`)
produced the broadened contribution v0.6's own front matter named --
the code/cloud flagship, packaging and CI-smoke-test gates, symbolic
scaling and AuthorityBench framing, and the large constructed domain.
All three rounds were committed unedited under `review-secondary/`, and
none was ever applied as a direct patch: every finding this artifact's
own results reflect was independently re-derived and machine-checked
against its own definitions and data before being accepted.

## 14. Supplementary Material

**Historical manuscripts.** v0.1 (commit `37a2e7f`), v0.2 (commit
`7112031`), v0.3 (commit `382be13`), v0.4, v0.5, v0.6, v0.6.1, v0.6.2,
v0.6.3, v0.6.4, and v0.6.5 are each frozen at their own commit, unedited
since, and linked from `README.md`'s History section. v0.1 through v0.4
preserve the complete original procurement-domain Introduction, related
work, empirical section (CH-A1 through CH-A10), and Conclusion; v0.5
and v0.6 preserve the append-only, chronologically-structured
manuscript v0.6.1 restructures; v0.6.1 preserves the claim-led
structure v0.6.2 and v0.6.3 carry forward, v0.6.2 preserves that
structure with one restored citation, v0.6.3 preserves the
wording-and-related-work-corrected manuscript v0.6.4 closes two
residues in, v0.6.4 preserves that twice-corrected manuscript before
v0.6.5's own external-reproduction update, and v0.6.5 preserves that
update before this revision's own Acknowledgements-only correction.
None is retracted, reworded, or deleted; this revision consolidates
their content under a claim-led structure without hiding what any of them
originally claimed.

**Extended procurement evidence.** The v2 procurement domain's own
worked instance, where core and reduct coincide, is preserved in full
in v0.4/v0.5/v0.6 (`prereg/pair-test-grid.yaml`; CH-A8/CH-A10,
[GENERATED: ch_a10_candidate_property_count] properties,
`core_is_unique_reduct: [GENERATED: ch_a10_core_is_unique_reduct]`,
[GENERATED: ch_a10_subsets_considered] of
[GENERATED: ch_a10_power_set_size] subsets exhaustively checked); the
declared loss model swept [GENERATED: v1_loss_count] v1 losses and
[GENERATED: v2_loss_count] total v1+v2 losses across
[GENERATED: grid_size_reachable] reachable tuples. Full statistical
sweep results (CH-A1 through CH-A4, thirty seeds, two workflows,
confidence intervals): v0.4 through v0.6.

**Proofs and checker detail.** Every numbered Definition and
Proposition carries a `PROOF-STATUS` tag in `appendix-a-proofs.md`
(`machine-checked`, `checked-scope-only`, or `pending-human-review`,
never `proven`, enforced by `checkers/proof_status_lint.py`);
[GENERATED: pending_human_review_tag_count] tags in this artifact's own
build are `pending-human-review` (`appendix-a-proofs.md`'s coupling-
generalization remark, unchanged since v0.2). Full checker source is
under `checkers/`; `NOVELTY.md` records the complete, dated novelty-
fence history this paper's Section 9 restates without its own
chronology.

**Mutation and reproduction records.** Mutation testing (hard gate,
`>= 0.85`, `ADR-003-mutation-testing.md`) and the full command ledger,
output hashes, and elapsed times for a bare-clone reproduction are in
`REPRODUCTION.md` and the commissioned reproduction evidence bundle
(`review-secondary/reproductions/2026-09-14-perplexity-computer/`), not
repeated here.

**Registered follow-up work: the operationally validated scope.** The
stronger scope Section 1 and Section 8's own claims table decline to
claim: one bounded operational workflow, with domain owners
independently specifying or reviewing losses, constraints, and costs
before seeing a synthesized answer; equal-information baselines (an
expert-authored contract, the loss-predicate syntactic read set, every
candidate attribute, and the synthesized contract, all given the same
declared problem); a separately coded reference decision procedure,
not the same registry called twice; measured verdict disagreement,
observation count, acquisition latency where available, and
declared-cost score reported separately from any of them; one change
case that keeps the prior contract's own coverage of `v_M` and one
that invalidates it; and predeclared decision rules requiring zero
verdict
disagreement, a pre-agreed cost/latency threshold, and every baseline
reported including one that ties or beats the synthesized contract.
This protocol is registered as a plan, not preregistered as an
experiment; no comparative outcome under it currently exists, and none
is claimed.

**Acknowledgements.** Drafting, engineering, formal derivation, and
citation verification were AI-assisted (Claude); the author is solely
responsible for all claims. Eduardo Arana (Arananet) independently
reproduced the package installation and CH-B1 result from a clean
clone (issue `#3`), after two recorded attempts (`#1`, `#2`) whose
findings corrected the reproduction path; no other external
contribution to this artifact's own claims is acknowledged.

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
- [ ] Corrections section (Section 13) reviewed by the author against
      `prereg/v3-core-reduct-correction.md`, `prereg/v3.1-isolated-arms.md`,
      `REPRODUCTION.md`'s own Corrections note, and the three external
      reviews it credits.
- [ ] Claim-by-claim table (Section 8) reviewed by the author against
      `review-secondary/paper-revision-outline-2026-09-15.md`'s own
      checklist, claim by claim.
- [ ] `pending-human-review` tags counted and individually assessed:
      [GENERATED: pending_human_review_tag_count]
      (`appendix-a-proofs.md`'s coupling-generalization remark).
- [ ] Push and any review chain are the author's decision, not
      automated by this pipeline.

**Not submission-ready. Not independently reviewed. Not claimed
complete against any loss model other than the ones declared in this
artifact's own `prereg/` files.**
