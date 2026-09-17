I reviewed `ba742b3` as a **manuscript audit only**, keeping the repository score unchanged. I checked the manuscript claims against the committed outputs and then re-ran the novelty question against the adjacent literature.

My conclusion is: **the evidence discipline is strong, but I would not submit v0.6.2 unchanged.** I found several wording-level claim mismatches that are straightforward to fix, and Section 9 needs one material expansion of the prior-art fence. None of these findings invalidates the results.

## 1. C1–C10 evidence audit

The core empirical results are accurately represented. CH-B1 really has a six-attribute insufficient core and exactly two seven-attribute reducts over 15,120 reachable states.  CH-B2 really separates those two contracts at 6.124 versus 7.354 while both remain sufficient.  CH-C1 really has 35 candidates, a four-attribute insufficient core, minimum cardinality nine, and **at least** five certified alternatives over 27,000 states.  CH-C2 really is a retained negative tie at 9.153.  The SAT/MaxSAT implementation also matches exhaustive answers on all three models where exhaustive comparison is feasible.

My claim-level assessment is:

| Claim | Assessment                                                   | Comment                                                                                               |
| ----- | ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------- |
| C1    | **Supported as bounded**                                     | Correctly limited to declared finite models.                                                          |
| C2    | **Supported**                                                | "Exactly 2" for B1 and "at least 5" for C1 are both licensed.                                         |
| C3    | **Supported with stated solver boundary**                    | Good distinction between bounded cross-check and larger solver-only cases.                            |
| C4    | **Supported**                                                | Both the positive v7 result and negative v8 tie match committed output.                               |
| C5    | **Correctly Partial**                                        | Excellent that the paper calls the returned object a check summary, not a portable proof certificate. |
| C6    | **Supported**                                                | Current HEAD CI is green and the package path is exercised.                                           |
| C7    | **Supported as implementation evidence**                     | Correctly does not claim operational validation.                                                      |
| C8    | **Needs wording correction**                                 | Current wording contradicts Section 7.                                                                |
| C9    | **Correctly Partial, but novelty fence needs strengthening** | This is the main remaining manuscript issue.                                                          |
| C10   | **Supported with qualifications**                            | Excellent separation of automated reproduction from independent-person reproduction.                  |

The commissioned reproduction is now described correctly: it reproduced substantive results, found real packaging/serialization issues, and explicitly disclaims independent-human status. The current manuscript does not misuse that evidence.

### Five manuscript changes I would make before submission

First, **C8 contains a direct internal contradiction**. It currently says computational behavior is reported while "comparing equivalent workloads." But Section 7 correctly says that exhaustive enumeration finds **every reduct**, whereas SAT/MaxSAT find **one objective-selected contract**, so these are explicitly different workloads.  The scaling JSON confirms exactly those different tasks.

Change C8 to something like:

> **C8.** Measured computational behavior is reported for the specific constructed families and domains tested; non-equivalent workloads are labeled as such, and the paper does not interpret all-reduct exhaustive enumeration versus one-contract SAT/MaxSAT optimization as an apples-to-apples speed comparison.

Second, I would remove **"real code/cloud authority domain"** from the abstract. The manuscript itself correctly says all evaluation domains are **constructed**, not live deployments.  Use **"preregistered constructed code/cloud domain"** or **"realistic constructed code/cloud domain."**

Third, the phrase describing v8 as **"built independently of this question"** overstates its provenance. The v8 preregistration explicitly says the package was created to ask whether the same core/reduct distinctions survive at 30–50 attributes. What was protected from outcome-fitting was the **structure and parameterization**: they were fixed before any core/reduct/cost outcome was computed.  I would write:

> "a second, independently structured 35-property constructed domain, preregistered before any core/reduct/cost outcome was computed"

That is stronger scientifically because it says exactly what independence you established.

Fourth, Section 6 says the manual baseline failure was measured across **"every registered domain this artifact has."** That is too broad. AuthorityBench has three domains; v8 is also a registered domain but is deliberately not part of AuthorityBench.  Change it to **"all three AuthorityBench domains."**

Fifth, Section 2 currently suggests Proposition 0-general means the result does not depend on **"one particular encoding choice."** That is too strong and conflicts with your own guarantee boundary, which explicitly makes correctness relative to the candidate representation. Proposition 0-general establishes invariance when the **same reachable set** is obtained through different construction/provenance routes; it does not establish representation invariance if candidate attributes are split, merged, or reparameterized. The appendix itself states the narrower set-theoretic result.

I would replace that sentence with:

> "Proposition 0-general establishes that, for a fixed candidate representation and verdict function, the derivation depends on the reachable set rather than on how an identical reachable set was produced. It does not establish invariance to changing the candidate representation itself."

One final small ambiguity: the abstract says you select contracts while **"checking each one's sufficiency directly."** The evaluation does this for the contracts reported in the paper, but the public `AuthorityContract.sufficiency_certificate` field is specifically computed for the **core**, not automatically for whichever min-cardinality/min-cost contract a caller selects.  I would say **"for every selected contract reported in the evaluation, we separately check sufficiency"** rather than making that sound like a universal API behavior.

Those are the claim-side corrections. I do **not** see an empirical result that needs to be withdrawn.

---

# 2. Section 9 novelty fence

Here I think v0.6.2 is **directionally correct but not yet fully defensible**.

The key problem is not that the contribution disappears. The problem is that two very close prior-art families are currently understated: **decision/attribute reducts with costs**, and **minimum sensor/observation selection in supervisory control**.

## Decision reducts need their own explicit paragraph

This is the most important addition.

Classical rough-set reducts are already defined around the same fundamental structure: attributes are **jointly sufficient and individually necessary**. Discernibility matrices/functions are classical machinery for deriving those reducts. ([ScienceDirect][1])

More importantly, **minimum-cost reducts are also established prior art**. Test-cost-sensitive attribute reduction explicitly formulates the problem of finding sufficient reducts with minimum observation/test cost. ([ScienceDirect][2])

Therefore I would not leave rough-set prior art buried only in the final "what is inherited" paragraph.

The defensible fence is:

> Decision-reduct theory supplies the mathematical notions of joint sufficiency, inclusion-minimal reducts, cores, discernibility functions, and cost-sensitive attribute reduction. We do not claim those notions or their SAT/hitting-set realization as new. The contribution here is to construct the decision system itself from **declared governance losses plus executable reachability**, interpret reducts as runtime authority-observation contracts, expose that derivation through an executable compiler interface, and evaluate its behavior on autonomous-system governance domains.

That makes the paper **less vulnerable and more interesting**.

Your novelty is not "we invented minimum reducts."

It is:

**loss semantics + reachability → decision table/discernibility structure → runtime governance contract.**

That is the research bridge.

---

## Controller synthesis paragraph needs material revision

The current wording says controller synthesis starts with an already-fixed observable alphabet and your paper derives that alphabet. That is not true of the whole literature.

There is established supervisory-control work specifically on selecting a **minimum-cardinality or minimum-cost sensor set** that permits controller synthesis. Rohloff, Khuller and Kortsarz directly formulate minimal sensor selection for supervisory control. ([Research with Rutgers][3]) A 2026 paper explicitly studies supervisory control with **minimal event observation**. ([MDPI][4])

So a formal-methods/control reviewer could legitimately challenge the present paragraph.

I would replace it with approximately:

> **Observation/sensor selection in supervisory control.** Classical supervisory-control formulations often assume an observation structure, but a separate literature explicitly studies minimum-cardinality and minimum-cost sensor/event observation sufficient for supervisor synthesis. We therefore do not claim to originate minimum-observation synthesis. The distinction here is the object and semantics being compiled: candidate per-decision governance attributes, a declared loss-derived verdict, and an executable reachable-state relation, rather than event sensors for preserving supervisory controllability or a temporal control specification. The output is a sufficient authority-observation contract, not a synthesized controller.

That is a much more robust fence.

---

## ABAC mining needs more accurate characterization

The current text says ABAC mining outputs **"which attributes already participate in that policy."** That understates Xu and Stoller.

Their method takes an existing user-permission relation/ACL or RBAC policy plus attribute data and synthesizes **generalized ABAC rules**, including rule construction, generalization, merging, simplification, and selection. ([Stony Brook University][5])

I would change the description to:

> Input: an extant authorization relation or policy plus attribute data. Output: a generalized ABAC rule set intended to reproduce or compactly generalize that extant authorization relation under a policy-quality objective.

Then your distinction is clean:

> This paper instead starts from an independently declared loss/verdict model over reachable states and asks which observations are sufficient to determine that verdict.

I would also drop **"Guarantee: none against a ground truth"**. It is broader than necessary and invites argument. Your own AuthorityBench already does the better thing: it compares the methods and reports the result **inconclusive**, rather than claiming policy mining is theoretically inferior.

---

## STPA should be softened, not removed

The conceptual comparison is good: STPA moves from losses/hazards toward unsafe control actions and safety constraints. The official handbook indeed describes a structured hazard-analysis process involving losses, hazards, control structures and unsafe control actions. ([PSAS][6])

But saying **"STPA and its descendants"** produce constraints "written and reviewed by a person" with only "expert-review confidence" is too categorical. There are tools and more automated/formal variants.

I would fence only the classical method:

> Classical STPA is an analyst-led hazard-analysis methodology that derives unsafe control actions and safety constraints from a system control structure. This paper borrows its loss-to-constraint orientation, but solves a different finite synthesis problem: selecting a sufficient/minimal observation subset for an already-declared executable verdict relation. Automated/formal STPA extensions remain adjacent rather than being characterized here as purely manual.

That is enough.

---

## Shield synthesis and runtime enforcement are mostly defensible

Shield synthesis genuinely synthesizes a runtime mechanism that monitors an already-defined input/output interface and corrects erroneous outputs relative to safety properties. ([arXiv][7])

Your distinction is sound, but I would replace **"strictly prior problem"** with **"orthogonal upstream problem in this artifact."**

"Strictly prior" sounds like a universal theoretical ordering. In your architecture, observation selection happens upstream of a shield; that does not mean all shield-synthesis settings require your problem to be solved first.

Similarly, Schneider-style execution monitoring and edit automata principally characterize what policies can be enforced by monitoring/intervening on execution traces. Edit automata examine and transform streams of program actions. ([Princeton University][8])

I would change **"Neither asks which..."** to:

> "Minimal selection of per-decision observation attributes is not the central problem those works formulate."

That avoids universal negative claims.

---

## Capability systems need a substantive wording correction

The current paragraph says capability systems represent/delegate authority but not **"which conditions must be checked before it is minted."**

That is too simple.

Macaroons explicitly embed contextual caveats that constrain **when, where, by whom, and for what purpose** authorization should succeed. ([Google Research][9]) UCAN likewise supports attenuated capabilities and conditions evaluated as part of delegation/invocation. ([GitHub][10])

The clean boundary is:

> Capability systems provide mechanisms for representing, attenuating, delegating and verifying authority, including contextual caveats or conditions. This paper does not claim novelty in those mechanisms. Its distinct question is how, from declared losses and reachable execution states, to synthesize a sufficient/minimal set of candidate observations that could inform such authorization conditions.

That is stronger than pretending capabilities lack contextual conditions.

---

## Two smaller related-work cleanups

I would also revise the **non-interference** and **counterfactual-fairness** paragraphs even though they were not central to your question.

Calling non-interference the same underlying **"single-flip comparison"** is too loose: non-interference is a semantic independence property over information flows/executions, not simply one-coordinate perturbation.

Similarly, counterfactual fairness is defined via counterfactual interventions in a causal model; it is not literally "the same comparison Definition 2 uses."

Use **"conceptually related invariance under changes to selected inputs"** instead of asserting that the formal operation is the same.

---

# The novelty statement I would submit

After those fixes, I think the fence becomes defensible and appropriately ambitious:

> **This paper does not introduce reduct theory, discernibility functions, minimum-cardinality or minimum-cost attribute selection, SAT/MaxSAT optimization, runtime enforcement, capability attenuation, or minimum-observation supervisory control. Its contribution is the governance-specific compilation problem and evaluated system: derive the decision relation from declared loss semantics and executable reachability, synthesize sufficient runtime observation contracts over that relation, expose cardinality- and cost-optimal contracts with explicit sufficiency/counterexample checks, and evaluate that formulation across constructed autonomous-system governance domains.**

That is neither timid nor inflated.

In fact, I think it is a **better contribution statement** than claiming novelty in the mathematics. It identifies the real intellectual move:

**governance intent → executable state semantics → minimal sufficient runtime context.**

## Submission judgment

I would characterize v0.6.2 as **very close on evidence discipline, but not yet clean enough on novelty fencing for submission unchanged**.

The result/evidence side needs mostly surgical edits: C8, the "real/built independently" wording, the "every registered domain" sentence, representation-invariance wording, and the API/check wording.

Section 9 needs a more meaningful change: add **decision/test-cost reducts** explicitly, add **minimum-observation supervisory control**, and tighten ABAC/STPA/capability descriptions.

Once those changes are made, I do **not** see a claim-evidence problem that would force another experiment before manuscript submission. Human reproduction remains an external-validation item, exactly as the paper currently says; it should stay pending rather than being promoted or hidden.

[1]: https://www.sciencedirect.com/science/article/pii/S0020025508001540?utm_source=chatgpt.com "Attribute reduction in decision-theoretic rough set models - ScienceDirect"
[2]: https://www.sciencedirect.com/science/article/abs/pii/S0020025511003410?utm_source=chatgpt.com "Test-cost-sensitive attribute reduction - ScienceDirect"
[3]: https://www.researchwithrutgers.com/en/publications/approximating-the-minimal-sensor-selection-for-supervisory-contro/?utm_source=chatgpt.com "Approximating the minimal sensor selection for supervisory control - Rutgers, The State University of New Jersey"
[4]: https://www.mdpi.com/2227-7390/14/6/1058?utm_source=chatgpt.com "Supervisor Design for Minimal Event Observation in Discrete Event Systems: A Linear Programming Approach | MDPI"
[5]: https://researchconnect.stonybrook.edu/en/publications/mining-attribute-based-access-control-policies/?utm_source=chatgpt.com "Mining Attribute-Based Access Control Policies - Stony Brook University"
[6]: https://psas.scripts.mit.edu/home/books-and-handbooks/?utm_source=chatgpt.com "Books and Handbooks | MIT Partnership for Systems Approaches to Safety and Security (PSASS)"
[7]: https://arxiv.org/abs/1501.02573?utm_source=chatgpt.com "Shield Synthesis: Runtime Enforcement for Reactive Systems"
[8]: https://collaborate.princeton.edu/en/publications/edit-automata-enforcement-mechanisms-for-run-time-security-polici/?utm_source=chatgpt.com "Edit automata: Enforcement mechanisms for run-time security policies - Princeton University"
[9]: https://research.google/pubs/macaroons-cookies-with-contextual-caveats-for-decentralized-authorization-in-the-cloud/?utm_source=chatgpt.com "Macaroons: Cookies with Contextual Caveats for Decentralized Authorization in the Cloud"
[10]: https://github.com/ucan-wg/delegation?utm_source=chatgpt.com "GitHub - ucan-wg/delegation · GitHub"
