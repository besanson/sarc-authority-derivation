# Novelty

Phase R output (task brief R2). One paragraph per neighbouring literature
cluster: what it established, and what this paper adds. Every source cited
below is fetch-verified in `verified-citations.json`.

## STPA and its descendants (STPA Handbook; STPA-Sec; PHASE; Mylius 2025;
## DeepSTPA)

Leveson and Thomas's STPA Handbook (2018) establishes System-Theoretic
Process Analysis: a structured but human-driven analyst process in which
an engineer enumerates losses and hazards, models a system as a hierarchy
of controllers, and writes safety constraints and unsafe-control-action
requirements by hand, checked by expert review. Young and Leveson's
STPA-Sec (CACM 2014) carries the same analyst process into security.
Rismani, Dobbe, and Moon's PHASE (2024) and Mylius (2025) carry it into AI
governance and frontier-AI hazard analysis respectively; Qi et al.'s
DeepSTPA (2023) extends STPA's control-loop model to the stages of the ML
development lifecycle. In every one of these five sources, the output is
a set of natural-language or semi-structured constraints produced and
reviewed by a person; none of them derive, from a declared loss model, a
machine-checked *minimal* property set for a runtime authorization gate,
and none formalize soundness or minimality as machine-checkable claims
over an enumerated model. This paper's derivation procedure is inspired
by STPA's loss-to-constraint direction of travel but replaces the analyst
step with a deterministic, exhaustively-verified derivation.

## ABAC policy mining (Xu and Stoller 2014-2015; Nobi et al. 2022 survey)

Xu and Stoller (TDSC 2015) establish the ABAC policy-mining problem:
given an *existing* lower-level policy (an ACL or RBAC policy) plus
attribute data, algorithmically reconstruct which attributes already
participate in the deployed access decisions. Nobi et al.'s 2022
taxonomy and survey catalogue the many machine-learning extensions of
that same reconstruction problem published since. Both directions of
work start from grants that already exist and infer structure backward
from them. This paper runs the derivation in the opposite direction and
from a different starting point: not from existing grants, but from a
declared loss model, forward to the minimal property set a *new* gate
must observe -- with a machine-checked soundness and minimality
guarantee that mining, which has no ground-truth "correct" policy to
verify against, cannot by construction provide.

## Policy-language completeness (PTaCL; SACMAT 2016 canonical completeness)

Crampton and Morisset's PTaCL (POST 2012) and Crampton and Williams's
canonical-completeness result (SACMAT 2016) establish what a policy
*combination* language can express once the participating attributes and
base decisions are already fixed -- completeness is a property of the
combinator algebra over a given attribute set. Neither work asks which
attributes must be observed by the gate in the first place; both assume
that question already answered. This paper contributes exactly the
question PTaCL and the SACMAT 2016 result assume away: which properties
a gate must observe at all, derived from a declared loss model, before
any question of how to combine decisions over them arises.

## Non-interference (Goguen and Meseguer 1982)

Goguen and Meseguer define non-interference as a semantic criterion for
whether one user's or domain's actions can affect what another observes
-- a *check* of whether a dependence exists between two fixed parties in
a given system. It is not a procedure for deriving, from a declared loss
model, the complete set of properties a decision must consult, and it
does not produce a minimality guarantee over that set. This paper's
Definition 1 (participation) borrows non-interference's underlying
comparison -- does changing X change the observable verdict? -- but
turns it into a derivation swept over every candidate property against
every loss predicate, with soundness and minimality verified
exhaustively over the enumerated model, rather than a single
dependence check between two designated parties.

## Counterfactual fairness (Kusner et al. 2017)

Kusner, Loftus, Russell, and Silva define counterfactual fairness as
invariance of a decision to a counterfactual change in one designated
protected attribute, with the causal graph over the remaining variables
held fixed. This is structurally the same comparison this paper's
Definition 1 uses -- does changing one property change the verdict? --
but Kusner et al. apply it to evaluate a single pre-chosen sensitive
attribute against a fairness objective, once. This paper generalizes the
comparison to sweep every candidate property in the
(action, context, evidence, control-state) space against a declared loss
model, and adds an exhaustive, machine-checked minimality result -- that
the recovered set is both sufficient and irreducible -- which the
counterfactual-fairness literature neither claims nor checks.

## The fence

STPA derives safety constraints from declared losses as an analyst
methodology; ABAC mining reconstructs policies from existing grants;
interference-style criteria detect dependence but do not derive. This
paper contributes a formal participation criterion over the
executable-reachable action set, a machine-checkable derivation from a
declared loss model to the minimal property set a pre-action authority
gate must observe, with the excluded residue emitted as a derived
coverage list, in a setting where remediation changes the reachable set.

## Kill-criteria check (task brief R3)

Searched explicitly, across all five literature clusters above, for
prior work that derives a runtime authorization property set from a
loss or hazard model *with machine-checked minimality*. Found: none.
STPA and its descendants derive constraints as an analyst methodology,
not a machine-checked derivation, and do not claim or check minimality.
ABAC mining reconstructs from existing grants, not from a declared loss
model, and has no minimality claim (or ground truth to check one
against). PTaCL/SACMAT completeness is a property of a combinator
algebra over an already-fixed attribute set, not a derivation of that
set. Non-interference and counterfactual fairness are both single
dependence/invariance *checks*, not derivations, and carry no
minimality result. Kill criteria not triggered. Proceeding to Phase 0.
