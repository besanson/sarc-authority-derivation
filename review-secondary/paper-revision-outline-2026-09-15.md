# Governance-Context Synthesis: Revised Paper Outline and Evidence Checklist

## Purpose and scope

This revision plan turns the existing work into one current, claim-led paper rather than an append-only development history. It separates what can be written from existing evidence, what needs a targeted verification, and what would require a new experiment.

**Evidence baseline:** repository commit `4a9676966aecb3d18cec6411decd5b9cfa8a7320`, its populated v0.5 draft, implementation, checker outputs, and the separate verification run documented in this conversation. This is a revision plan, not a rewritten manuscript, a new literature review, or a fresh certification of every result. No repository files were edited to produce it.

The user has indicated that reporting was already handled. This plan does not recheck the issue tracker or infer that an independent-human reproduction requirement has therefore been satisfied.

## Recommended positioning

### Working title

**Compiling Sufficient Governance Context from Declared Losses and Reachable States**

Optional subtitle: **Exact Observation-Contract Synthesis with Cardinality and Cost Objectives**

“Observation contract” should be defined before introducing “authority contract.” The object specifies information sufficient to determine an approved model’s verdict; it does not independently establish legitimate organizational authority, discover undeclared hazards, or implement a complete enforcement system.

### Central claim

> Given a finite reachable-state model, a deterministic declared verdict, and candidate observable attributes, we compute sufficient observation sets, distinguish indispensable attributes from jointly sufficient contracts, and select contracts under cardinality or declared observation-cost objectives.

This is the defensible center of the paper. Describe the contribution as the formulation, implementation, and evaluation of governance-context compilation; attribute inherited mathematical and solver techniques explicitly rather than treating their application as evidence of foundational novelty.

### Two legitimate publication scopes

| Scope | What the paper can aim to establish | Additional requirement |
|---|---|---|
| **Compiler-focused paper, recommended immediate revision** | Conditional sufficiency, contract alternatives, optimization behavior, bounded scaling and an executable artifact | Reconcile prose with actual outputs; tighten closest-prior-work positioning; complete targeted claim checks below |
| **Operationally validated compiler paper, stronger follow-up** | The above, plus useful observation savings and correct execution through a separate gate implementation | Independently specified case, fair expert baseline, measured costs and end-to-end validation |

Do not imply that every proposed operational experiment is necessary to present the existing bounded contribution. Conversely, do not borrow the stronger scope’s claims before its evidence exists.

## Revised manuscript outline

### Introduction: the decision problem and contribution

**Reader question:** Why derive an observation set rather than hand-select it or read everything?

- **Problem:** A gate may omit decision-relevant information, but acquiring every field can carry latency, privacy and availability costs.
- **Running example:** Introduce CH-B1’s two alternatives, core plus `branch` or core plus `environment`. Explain their operational difference before introducing the mathematical terminology.
- **Contribution statement:** Separate the governance-context formulation, implemented synthesis/checking pipeline, and bounded evaluation. Do not list test counts or corrections as scientific contributions.
- **Boundary:** Correctness is relative to declared losses, candidate representation and reachable states, not a general safety guarantee.

**Evidence anchors:** CH-B1; claims C1–C4 below. End the introduction with an explicit statement of what is implemented and what remains downstream engineering.

### Problem formulation and guarantee boundary

**Reader question:** Exactly what is being computed, under which assumptions?

Define:

- **Inputs:** Finite reachable set \(R\), candidate attributes \(A\), deterministic model verdict \(v_M\), and optional strictly positive additive observation costs \(c(a)\).
- **Sufficiency:** \(S \subseteq A\) is sufficient when agreement on \(S\) implies agreement in \(v_M\) throughout \(R\).
- **Core:** Attributes present in every inclusion-minimal sufficient set.
- **Reduct:** An inclusion-minimal sufficient set. Distinguish this from a minimum-cardinality set and a minimum-cost set.
- **Representation assumption:** The full candidate projection must determine the verdict. State the consistency requirement rather than asserting that full observation is sufficient for arbitrary malformed or incomplete inputs.
- **Cost boundary:** The current objective is a declared additive score with strictly positive weights, not necessarily monetary cost or a measured end-to-end latency function.

State the verdict being preserved precisely. A single admit/deny verdict is not automatically equivalent to preserving the identity of every violated loss predicate.

**Evidence anchors:** `reduct.py`, `synthesis.py`, `losses.py`; C1–C4. Include one guarantee-boundary diagram: approved model inputs → compilation → selected observation set → separate downstream execution.

### Method: from discernibility to selected contracts

**Reader question:** What does the compiler do, and which parts are inherited?

Present a single algorithm:

1. Materialize or receive reachable tuples and evaluate the declared verdict.
2. Construct attribute-difference sets for verdict-disagreeing pairs.
3. Remove supersets that add no additional hitting-set constraint.
4. Encode sufficiency constraints for SAT/MaxSAT.
5. Select any sufficient set, a minimum-cardinality set, or a minimum-cost set, depending on the requested objective.
6. Check the returned set’s sufficiency; produce a counterexample when a tested set is insufficient.
7. Enumerate all reducts only where affordable; otherwise label a capped collection explicitly as a lower bound.

Separate three evidence objects: a sufficiency check, an inclusion-minimality/optimality justification, and a provenance record. One does not substitute for another.

**Evidence anchors:** `discernibility.py`, `synthesis.py`, `reduct.py`; C1, C3, C5. Report preprocessing complexity separately from solver complexity.

### Implementation and verification interface

**Reader question:** What can a caller actually import, inspect and verify?

- **Package:** Document the wheel API and one neutral-directory example.
- **Returned objects:** Explain the selected sets, core, bounded/all-enumeration status, counterexamples and change-analysis callable.
- **Current limitations:** The API’s `sufficiency_certificate` is computed for the core. The successful checker return is a partition count and uniformity flag, not the serialized partition itself.
- **Verification boundary:** Present the current implementation as executable checking. Do not describe it as a portable proof-carrying runtime contract without a matching artifact and consumer.

**Evidence anchors:** `src/authority_compiler/api.py`, `authority_compiler_smoke.py`; C5–C6. A compact interface table should distinguish implemented fields from proposed future interface changes.

### Evaluation design

**Reader question:** What would each experiment establish, and what would count against the thesis?

Organize the evaluation by questions, not development versions:

- **RQ1:** Do the selected contracts preserve verdicts on the declared finite models?
- **RQ2:** Does the core fail to suffice, and do alternative contracts exist?
- **RQ3:** Does a declared cost objective distinguish alternatives?
- **RQ4:** Where is compilation practical, including preprocessing?
- **RQ5, conditional extension:** Does the method improve on a competent manual or conservative alternative in an independently specified workflow?

Describe the domains as constructed executable models with stated provenance. Keep “non-planted,” “organizationally plausible,” “independently specified” and “live-deployment-derived” separate; none implies the others.

**Evidence anchors:** Existing preregistrations and C1–C8. Specify which measurements were rerun and which remain repository-reported results.

### Results: semantic correctness, alternatives and cost

Lead with one consolidated table:

| Domain/result | Candidate attributes | Reachable tuples | Core | Minimum contract | Multiplicity | Cost finding |
|---|---:|---:|---|---|---|---|
| Code/cloud, CH-B1/B2 | 10 | 15,120 | 6; insufficient | 7 attributes | Exactly two reducts | Declared scores approximately 6.124 versus 7.354 |
| Large constructed domain, CH-C1/C2 | 35 | 27,000 | 4; insufficient | 9 attributes | At least five minimum-cardinality reducts; search capped at five | Five returned alternatives tie at approximately 9.153; cost optimum agrees |

Explain the narrower CH-B2 conclusion: cost selects between two contracts of the same cardinality. It does **not** demonstrate that a larger contract is cheaper than every minimum-cardinality contract in that realistic domain.

Retain CH-C2’s negative cost-discrimination result. It limits the usefulness of the registered cost model without negating the core-insufficiency result.

Keep the procurement results as supporting evidence, not a second paper embedded inside the main text. Explain why comparisons to a restricted manual policy do not establish superiority to expert policy engineering.

**Evidence anchors:** C2–C4 and C8.

### Computational behavior and change analysis

Separate synthetic attribute-scaling families, tuple-scaling families and the non-planted constructed domain. Report tuple construction, verdict evaluation, discernibility construction/pruning, solver time, checking, total time and peak memory wherever measured.

Treat the 300-second exhaustive-search cutoff as a measured timeout under a specified setup, not a complexity lower bound. Do not equate a sub-second solver stage with sub-second compilation.

Include a bounded change-analysis subsection: the existing callable handles additional tuples under the same candidate schema and loss registry. Distinguish its monotone extension of a prior contract from unconstrained reoptimization.

**Evidence anchors:** C7–C8. If detailed timing decomposition is absent, label it as missing rather than reconstructing it from the quick-reproduction total.

### Related work and contribution boundary

Build the comparison around the closest potential substitutes, not a long list of adjacent topics. Review the paper’s acknowledged decision-reduct/discernibility lineage, feature selection under constraints, policy synthesis/mining, and relevant enforcement/synthesis work.

For each genuinely close method, compare its input, output, objective, guarantee, reachability treatment and verification interface. Verify individual sources before asserting a difference; the existing literature discussion should not be treated as independently revalidated by this plan.

End with one paragraph stating which elements are inherited and which combination, interface or evaluated behavior constitutes this paper’s contribution. Avoid “first,” “unique” and broad claims that neighboring fields cannot provide equivalent guarantees without direct support.

**Evidence anchors:** C9.

### Limitations, reproducibility and conclusion

Keep these sections concise and current:

- **Model validity:** Omitted hazards and unrepresented observations remain outside the guarantee.
- **Operational scope:** No claim of deployed runtime enforcement, concurrent-agent safety or temporal/probabilistic loss coverage.
- **Cost validity:** Declared scores require sensitivity analysis; correlated acquisition and shared lookup costs are not represented by an additive objective.
- **Reproduction:** Distinguish semantic agreement, within-environment byte identity, cross-environment byte identity and independent-person reproduction.
- **Conclusion:** State what is computed and demonstrated, not the history of how errors were corrected.

**Evidence anchors:** C5–C10. Close with the conditional contribution, not an unsupported universal safety claim.

### Supplementary material

Move historical manuscripts, correction chronology, full preregistrations, extended procurement experiments, complete proofs/checker details, mutation records and complete run logs here. Preserve traceability through a short correction notice and commit references; consolidation should not conceal prior overclaims.

## Claim-by-claim evidence checklist

### How to use the checklist

**Supported** means bounded evidence exists, not that novelty or generalization has been independently certified. **Partial** means some supporting implementation/evidence exists but the stronger wording is not yet licensed. **Proposed** means the work has not been completed in this plan.

For every headline claim, maintain a record containing: exact sentence, assumptions, generating code and command, frozen input identifiers, expected outcome, observed output, checking method, reproduction status, and permitted wording. A checked box below refers only to evidence inspected or obtained, not an entire future publication gate.

### C1: Sufficiency can be computed and checked on the declared finite model

**Permitted claim:** The selected observation set preserves the specified model verdict over the supplied reachable set.

**Current status:** Supported on checked finite instances, with a general mathematical argument requiring clear assumptions.

**Evidence:** `reduct.sufficiency`; `checkers/discernibility_check.py`; `checkers/synthesis_exactness_check.py`; corresponding outputs. These checkers ran within the completed quick reproduction.

- [x] Partition-based checking and a separate discernibility formulation exist.
- [x] Small-domain synthesis results are cross-checked against exhaustive enumeration.
- [ ] State determinism, representation consistency and verdict semantics explicitly.
- [ ] Ensure every selected contract used in a headline result has its own sufficiency check, rather than relying on the core’s status.
- [ ] Distinguish a mathematical proof, finite exhaustive checking and solver correctness assumptions.

**Acceptance test:** The paper makes no claim beyond \(R\) and \(M\); each selected set can be checked against those inputs, and an insufficient set yields a verdict-disagreeing pair.

### C2: The core may be insufficient and alternatives may be necessary

**Permitted claim:** CH-B1 and CH-C1 instantiate core insufficiency; CH-B1 has exactly two reducts, and CH-C1 exposes at least five minimum-cardinality reducts.

**Current status:** Supported; CH-B1 and CH-C1 values and expected output hashes reproduced in this session.

**Evidence:** `checkers/ch_b1_check.py`, `checkers/ch_c1_check.py`, their JSON outputs, and the exact section-6/6b reproduction runs.

- [x] Include core cardinality, a counterexample, selected-set cardinality and enumeration status.
- [x] Preserve CH-C1’s cap and lower-bound qualifier.
- [ ] Replace “redundant” with “non-core” wherever it means `candidate_properties - core`.
- [ ] State that an attribute outside the core can still be needed in a chosen contract; do not drop all non-core attributes.

**Acceptance test:** The reader can explain why removing both `branch` and `environment` from the CH-B1 core-plus-alternative design is not justified by their non-core status.

### C3: Cardinality and cost objectives are correctly distinguished

**Permitted claim:** The implementation selects minimum-cardinality or minimum-declared-cost sufficient sets using different objectives, under stated assumptions.

**Current status:** Supported by implementation and bounded exactness checks; larger-instance optimality relies on the solver/encoding boundary.

**Evidence:** `synthesis.find_minimum_cardinality_contract`, `find_minimum_cost_contract`, `test_synthesis.py`, `checkers/synthesis_exactness_check.py`.

- [x] The code uses distinct cardinality and weighted objectives.
- [x] Missing and non-positive declared costs are explicitly rejected.
- [ ] Explain why strictly positive additive costs support inclusion minimality.
- [ ] Separate sufficiency checking from optimality evidence.
- [ ] Do not call a partition-uniformity result an independently checkable optimality proof.

**Acceptance test:** Each “minimal,” “minimum,” and “optimal” occurrence names its objective and evidence basis. If independently verified optimality is claimed at scale, add a suitable proof artifact/checker or lower-bound verification.

### C4: Cost differentiation occurs in one domain and not in another

**Permitted claim:** CH-B2 selects the cheaper of two equally small sufficient contracts under its registered cost model; CH-C2’s returned alternatives tie under its registered model.

**Current status:** Supported as a model-relative finding. Both checkers ran during quick reproduction; floating-point serialization differs from committed outputs.

**Evidence:** `costs_v7.py`, `costs_v8.py`, `checkers/ch_b2_check.py`, `checkers/ch_c2_check.py`, v7/v8 preregistrations.

- [x] Report both CH-B2’s separation and CH-C2’s negative result.
- [x] Label values as declared composite scores, not measured business savings.
- [ ] Remove the obsolete statement that the code/cloud cost experiment is future work.
- [ ] Add sensitivity analysis before making robustness claims about the chosen contract.
- [ ] Keep any larger-but-cheaper constructed example separate from CH-B2.

**Acceptance test:** No sentence converts a score difference into demonstrated latency, financial or organizational benefit without measurements supporting that conversion.

### C5: Verification evidence accompanies the intended selected contract

**Permitted claim now:** The implementation can execute a sufficiency check and return a summary or concrete counterexample.

**Current status:** Partial. Stronger portable-certificate and runtime-consumption wording exceeds what the inspected interface establishes.

**Evidence:** `reduct.sufficiency` returns `partition_cell_count` and `uniform_verdict_within_every_cell` on success. `derive_authority_contract` assigns its `sufficiency_certificate` from a check of `core_attributes`, not automatically the chosen minimum-cardinality or minimum-cost set.

- [x] Identify and disclose which attribute set each check actually concerns.
- [ ] Remove “the partition itself” unless the output is changed to contain it.
- [ ] For the compiler-focused paper, describe recomputable checking accurately.
- [ ] For a stronger certificate claim, bind evidence to model/input versions and the selected set; define a consumer that rechecks evidence and rejects altered or stale bindings.
- [ ] Treat runtime consumption as proposed until implemented and tested.

**Acceptance test:** A reader cannot mistake a core-insufficiency counterexample for evidence that the selected sufficient contract failed, or mistake a success flag for a self-contained proof.

### C6: The compiler is usable outside its repository

**Permitted claim:** The built wheel supports the tested black-box example from a fresh environment without source-tree imports.

**Current status:** Supported after a documented environment-only prerequisite fix.

**Evidence:** `authority_compiler_smoke.py`; `make package-smoke-test`; retained wheel/import-provenance logs in the reproduction evidence.

- [x] Build and install the wheel in a fresh virtual environment.
- [x] Execute from `/tmp`; verify relevant project imports resolve to installed `site-packages`.
- [x] Preserve the initial `No module named build` failure and successful retry.
- [ ] Correct or explicitly document the missing build prerequisite on any future revised commit.
- [ ] Add a substantive wheel-only domain example if claiming that the packaged API reproduces the flagship domain result end to end.

**Acceptance test:** Packaging evidence is not conflated with substantive source-import evidence. The trivial wheel example proves packaging behavior, not enterprise applicability.

### C7: Existing contracts can be rechecked after reachable-set expansion

**Permitted claim:** For additional tuples under the same schema and loss registry, the implementation checks prior sufficiency and can extend a contract while preserving existing observations.

**Current status:** Implemented with supporting tests; a dedicated operational change study remains proposed.

**Evidence:** `synthesis.contract_change_delta`; the bound callable in the compiler API; relevant `test_synthesis.py` coverage.

- [x] The code compares the combined reachable set with the prior contract.
- [x] It distinguishes a pinned-contract extension from full cardinality reoptimization.
- [ ] Make the same-registry, same-schema, additional-tuples boundary explicit.
- [ ] Present a named benign expansion and a named expansion that invalidates the contract.
- [ ] Treat changed loss predicates, removed states, schema changes and automatic drift detection as separate extensions, not current guarantees.
- [ ] Do not portray `reachability_dependencies` as full dependency inference: the inspected implementation detects reduced marginal value sets, not every cross-field constraint.

**Acceptance test:** A reader can tell exactly which changes the existing function handles and which require a different validation procedure.

### C8: Synthesis has a bounded computational and comparative advantage

**Permitted claim:** Report measured behavior for specified constructed families and domains; compare equivalent tasks and separate compilation stages.

**Current status:** Partial for stronger performance claims. Repository scaling/AuthorityBench outputs exist, but the full benchmark and exhaustive-attempt commands were not rerun in this session.

**Evidence:** `discernibility_scaling_benchmark.py`, `authority_bench.py`, `out/results/authority_bench_v6_1.json`, `out/results/v8_exhaustive_attempt.json`; formal-run and quick-reproduction logs.

- [x] Label planted, non-planted constructed and live-derived evidence separately.
- [x] Record the actual 65m 11s quick-run duration without presenting it as a single compilation time.
- [ ] Rerun headline benchmark measurements at the selected release commit.
- [ ] Report preprocessing, solver, checking and end-to-end time with hardware, repetitions and memory.
- [ ] Compare finding one solution with finding one solution; do not use all-reduct enumeration time as an unqualified baseline for a one-contract task.
- [ ] Report retained historical files as retained, not freshly reproduced.

**Acceptance test:** Every speedup compares explicit workloads; a timeout means “not completed within this budget,” not proof that the problem is inherently infeasible.

### C9: The contribution differs meaningfully from the closest prior work

**Permitted claim:** A precise, source-supported account of the paper’s formulation, interface or demonstrated application beyond inherited techniques.

**Current status:** Requires focused literature adjudication; not settled by successful reproduction.

**Evidence starting points:** The manuscript’s references, `NOVELTY.md`, and its existing citation records. These are starting points, not fresh independent verification.

- [ ] Identify the closest substitutes, including decision-reduct/discernibility methods.
- [ ] Directly check the relevant primary sources and compare equivalent problem statements.
- [ ] Build an input/output/objective/guarantee comparison matrix.
- [ ] Name what is inherited and what is contributed in one paragraph.
- [ ] Test the practical addition against a simpler syntactic-read-set or conservative-observation baseline.

**Acceptance test:** The novelty paragraph survives the objection “this is a standard reduction under new terminology” without relying on test volume or unsupported claims about neighboring fields.

### C10: The artifact’s reproduction claims are accurate and scoped

**Permitted claim:** State the exact computational checks completed, their deviations and the identity/scope of the reproduction evidence.

**Current status:** Supported with qualifications for this session’s technical run; current external issue/reproducer status is not reassessed here.

**Evidence:** The delivered reproduction report, command ledger, output snapshots, wheel and hash manifest.

- [x] Record Python 3.12.13, OS, commands, timings and output hashes.
- [x] Separate the optional mutation gate from completed quick reproduction.
- [x] Preserve the CH-C2 byte mismatch despite passing within-run byte identity.
- [x] Distinguish source integrity from generated-output changes.
- [ ] If claiming independently reproduced results, identify the actual report and verify that its person/environment/scope support that wording.
- [ ] On any future fixed release, regenerate expected hashes under an explicit serialization policy rather than retroactively normalizing this run’s evidence.

**Acceptance test:** A reviewer can distinguish semantic agreement, repeated-run determinism, cross-environment byte agreement and independent-person reproduction.

## Proposed operational evidence extension

This extension supports a stronger practical-value claim; it is not completed evidence. Freeze its protocol before computing comparative outcomes and retain ties or negative findings.

### Design

- **Case and separation:** Select one bounded workflow. Have domain owners independently specify or review losses, constraints and costs before seeing the synthesized answer; preserve their rationale and freeze the evaluation version.
- **Equal-information baselines:** Compare an expert-authored observation contract, the loss-predicate syntactic read set, all available candidate attributes, and the synthesized contract. All approaches receive the same declared problem; record development effort and any tuning.
- **Separate evaluator:** For an end-to-end claim, implement a gate that uses only the selected observations and an explicit decision mapping. An independently coded reference decision procedure should evaluate the same approved semantics; simply calling the same registry on both sides establishes only limited integration evidence.
- **Measurements:** Verdict disagreement on the complete bounded model; observation count; measured acquisition latency/requests where available; declared privacy/cost score reported separately; total compilation time; model-authoring and integration effort.
- **Change cases:** Test one additional reachable-state set that preserves sufficiency and one that invalidates the old contract. Test changed losses separately as a proposed broader capability, not as evidence for the current additional-tuples API.
- **Unmodeled inputs:** Include missing, stale or unknown observations only with an explicitly specified gate policy and tests. Rejecting such inputs may be a sound engineering choice, but is not automatically supplied by the compiler.

### Predeclared decision rules

- [ ] Require zero verdict disagreement for the declared finite-domain correctness claim; report every counterexample.
- [ ] Define the practical cost/latency improvement threshold with the domain owner before evaluation.
- [ ] Report all baselines, including a manual contract that ties or beats the synthesized one.
- [ ] Separate model-relative correctness from evidence that the approved model reflects the real process.
- [ ] Limit conclusions to the case unless further independent cases support generalization.

**Stronger claim unlocked only after completion:** In this specified workflow, the compiler produced a checked observation contract with a measured advantage over named alternatives while preserving the approved decisions.

## Revision sequence and release checklist

### Manuscript-only changes first

- [ ] Replace the historical main-text structure with the outline above.
- [ ] Integrate CH-B2 and CH-C1/C2; remove stale future-work statements.
- [ ] Correct core/non-core, minimal/minimum, certificate/summary and constructed/live terminology.
- [ ] State the exact verdict and conditional guarantee.
- [ ] Map every abstract and conclusion claim to C1–C10.
- [ ] Move development history to supplements without hiding prior corrections.

### Targeted verification second

- [ ] Resolve certificate-to-selected-contract wording or implement and test the stronger interface.
- [ ] Validate closer baseline comparisons and equivalent computational workloads.
- [ ] Reproduce only the benchmark measurements the revised paper will headline.
- [ ] Complete the closest-prior-work comparison before strengthening novelty wording.
- [ ] Resolve reproducibility prerequisites and serialization policy on a separate, explicitly revised commit if changes are authorized.

### New operational evidence last

- [ ] Decide whether to keep the compiler-only scope or undertake the proposed case study.
- [ ] Preregister the case, baselines, measurements and negative-result rules if proceeding.
- [ ] Add practical-value and runtime claims only after their evidence is available.

**Submission decision:** The compiler-focused paper should stand on a precise contribution and bounded verified results without claiming deployment-level validation. The operationally validated version should add independently specified, end-to-end evidence rather than more variations of internally constructed demonstrations.
