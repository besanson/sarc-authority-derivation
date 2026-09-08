# Copyright 2026 SARC Suite Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Milestone E, Step 3 (`prereg/v6.1-authoritybench-amendment.md`, tag
`prereg-p5-v6.1`): the Xu-and-Stoller validation gate registered under
"The four baselines", item 2 -- "before this baseline [`mining_baseline.
py`] is used in Step 4's comparison, its own output is checked against at
least one independently-verifiable, published quantity from Xu and
Stoller's own paper... specifically, whether this scoped reimplementation,
run on a small worked example constructed to match a case their paper
describes..., lands within a registered, generous tolerance of their
reported number... This is a real gate, not a formality."

**What was located** (investigated here, honestly, not assumed in
advance): the paper's own text (arXiv:1306.2401 / TDSC 2015, citation id
`xu-stoller-abac-mining`) states, page 7: "All of the code and data is
available at http://www.cs.sunysb.edu/~stoller/". That address 503s (the
domain moved); the author's current homepage
(https://www3.cs.stonybrook.edu/~stoller/) links a "Software" page
(https://www3.cs.stonybrook.edu/~stoller/software/index.html) listing
`ABAC-Mining.zip` -- "an implementation of the policy mining algorithms
described in our 2015 IEEE TDSC paper", updated 16 August 2014 -- fetched
2026-09-08 (sha256 of the zip and of the specific file transcribed below
are recorded in `verified-citations.json`'s
`xu-stoller-healthcare-case-study-data` entry). That archive's
`ABACMining/case-studies/healthcare.abac` is the paper's own hand-authored
"Health Care Sample Policy" (Section 5's evaluation, Fig. 5's `health
care` row) -- NOT a reconstruction, the authors' own original input file.
Its GPLv3 `COPYING` file means the CODE is not vendored here (nor would
"reimplemented from Xu and Stoller" call for vendoring it); the FACTS
below (attribute values, rule semantics) are transcribed by hand into
fresh Python, the same transcription discipline this project already
applies to cited legal text (`losses_datacomms.py`) and prereg tables
(`domain_v4.py`) -- data, not their expression, and independently
re-derived, not copied.

**Cross-checked against Fig. 5 (health care, "man" row) before any
mining code below was written**: |Rules|=9, |A_u|=6 (position, ward,
specialties, teams, agentFor, plus the distinguished `uid`), |A_r|=7
(type, patient, treatingTeam, ward, author, topics, plus the
distinguished `rid`), |Op|=3, |U|=21, |R|=16, |UP|=51, average per-rule
coverage |[[rho]]|=6.7 -- every one of these falls out of the transcribed
data below by direct count/computation (`test_xu_stoller_validation.py`
asserts |UP|==51 exactly), not asserted from the paper alone. Section
5.1's own prose (page 7): "If no attributes are declared unremovable,
the generated [mined] policy is the same as the original ABAC policy
except that the RAE conjunct 'type=HRitem' is eliminated from four
rules... If resource type is declared unremovable, the generated policy
is identical to the original ABAC policy" -- i.e. Xu and Stoller's own
algorithm mines exactly 9 rules on this input, matching the original
rule count. That "9" is the "published number" this gate's tolerance
band (below) is measured against.

**Validation criteria (registered here, in this docstring, BEFORE
`run()` below was ever executed -- "registered semantics never retuned
to chase a result")**, three tiers, most decisive first:

1. **Transcription oracle (exact, not a tolerance)**: the raw-attribute
   rule interpreter (`_grant_raw`, formulation A, a direct transcription
   of the 9 `rule(...)` lines against the 9 English comments that
   accompany each in the source file -- both checked against each
   other while transcribing) must produce exactly `|UP| = 51` over the
   420 structurally-valid (user, resource, op) triples (21 users x (4
   HR resources x {addItem, addNote} + 12 HRitem resources x {read})).
   A mismatch here is a transcription bug to hunt down and fix before
   anything downstream is trusted -- ordinary debugging against a
   known-answer test, not a criterion to loosen.
2. **Cross-formulation agreement (exact)**: formulation B (`_grant_flat`,
   the same 9 clauses restated over 11 flattened boolean/categorical
   candidate properties so `mining_baseline.py`'s equality-based
   generalizer can operate on them at all -- relational tests like
   "treatingTeam in teams" or "topics <= specialties" are precomputed
   into flat booleans for exactly this reason, not because the original
   relation is hard to state) must agree with formulation A on all 420
   triples individually, not merely on the aggregate count.
3. **Mining validation (decisive, exact pass/fail, no tolerance)**:
   `mining_baseline.mine_policy` run on the 420 flattened triples,
   followed by `verify_soundness`, must report `sound=True,
   mismatch_count=0` -- reproducing Xu and Stoller's own reported
   noise-free result (their Section 5.3: mined policies match the
   original when no noise is injected).
4. **Rule-count corroboration (generous tolerance, registered in
   advance)**: `rule_count_after_simplify` must land in `[3, 27]` --
   a factor of 3 either side of the published 9. Chosen this wide
   deliberately even though this project's flattened encoding already
   resolves the main structural gap (relational facts are precomputed
   booleans, so a close count is *expected*, not merely hoped for):
   `mine_policy`'s seed order and its single-pass simplify step are
   still cruder than Xu and Stoller's WSC-guided merge, and a factor of
   3 absorbs that without being wide enough to pass a badly broken
   reimplementation.

Overall verdict: **VALIDATED** iff tiers 1-4 all pass. Otherwise
**EXCLUDED: UNVALIDATED**, exactly the registered contingency -- Step 4
does not use `mining_baseline.py` as a benchmarked baseline in that case,
and reports it excluded, not silently omitted.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Tuple

from mining_baseline import mine_policy, verify_soundness

OUTPUT_PATH = Path("out/results/xu_stoller_validation.json")
PUBLISHED_RULE_COUNT = 9
PUBLISHED_UP_COUNT = 51
PUBLISHED_AVERAGE_RULE_COVERAGE = 6.7
RULE_COUNT_TOLERANCE_BAND = (3, 27)  # factor of 3 either side of 9, registered above


# -- Formulation A: the case study's own raw user/resource attributes ------

@dataclass(frozen=True)
class _RawUser:
    uid: str
    position: str | None = None
    ward: str | None = None
    specialties: FrozenSet[str] = field(default_factory=frozenset)
    teams: FrozenSet[str] = field(default_factory=frozenset)
    agentFor: FrozenSet[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class _RawResource:
    rid: str
    type: str
    patient: str
    treatingTeam: str
    ward: str
    author: str | None = None
    topics: FrozenSet[str] = field(default_factory=frozenset)


# Transcribed verbatim from ABACMining/case-studies/healthcare.abac's
# `userAttrib(...)` block (sha256-pinned in verified-citations.json).
_USERS: Tuple[_RawUser, ...] = (
    _RawUser(uid="oncNurse1", position="nurse", ward="oncWard"),
    _RawUser(uid="oncNurse2", position="nurse", ward="oncWard"),
    _RawUser(uid="carNurse1", position="nurse", ward="carWard"),
    _RawUser(uid="carNurse2", position="nurse", ward="carWard"),
    _RawUser(uid="oncDoc1", position="doctor", specialties=frozenset({"oncology"}), teams=frozenset({"oncTeam1", "oncTeam2"})),
    _RawUser(uid="oncDoc2", position="doctor", specialties=frozenset({"oncology"}), teams=frozenset({"oncTeam1"})),
    _RawUser(uid="oncDoc3", position="doctor", specialties=frozenset({"oncology"}), teams=frozenset({"oncTeam2"})),
    _RawUser(uid="oncDoc4", position="doctor", specialties=frozenset({"oncology"}), teams=frozenset({"oncTeam2"})),
    _RawUser(uid="carDoc1", position="doctor", specialties=frozenset({"cardiology"}), teams=frozenset({"carTeam1"})),
    _RawUser(uid="carDoc2", position="doctor", specialties=frozenset({"cardiology"}), teams=frozenset({"carTeam2"})),
    _RawUser(uid="anesDoc1", position="doctor", specialties=frozenset({"anesthesiology"}), teams=frozenset({"oncTeam1", "carTeam1"})),
    _RawUser(uid="doc1", position="doctor", specialties=frozenset({"oncology", "pediatrics"})),
    _RawUser(uid="doc2", position="doctor", specialties=frozenset({"cardiology", "neurology"})),
    _RawUser(uid="oncPat1", ward="oncWard"),
    _RawUser(uid="oncPat2", ward="oncWard"),
    _RawUser(uid="carPat1", ward="carWard"),
    _RawUser(uid="carPat2", ward="carWard"),
    _RawUser(uid="oncAgent1", agentFor=frozenset({"oncPat2"})),
    _RawUser(uid="oncAgent2", agentFor=frozenset({"oncPat2"})),
    _RawUser(uid="carAgent1", agentFor=frozenset({"carPat2"})),
    _RawUser(uid="carAgent2", agentFor=frozenset({"carPat2"})),
)

# Transcribed verbatim from the same file's `resourceAttrib(...)` block.
_RESOURCES: Tuple[_RawResource, ...] = (
    _RawResource(rid="oncPat1oncItem", type="HRitem", author="oncDoc1", patient="oncPat1", topics=frozenset({"oncology"}), treatingTeam="oncTeam1", ward="oncWard"),
    _RawResource(rid="oncPat1nursingItem", type="HRitem", author="oncNurse2", patient="oncPat1", topics=frozenset({"nursing"}), treatingTeam="oncTeam1", ward="oncWard"),
    _RawResource(rid="oncPat1noteItem", type="HRitem", author="oncPat1", patient="oncPat1", topics=frozenset({"note"}), treatingTeam="oncTeam1", ward="oncWard"),
    _RawResource(rid="oncPat1HR", type="HR", patient="oncPat1", treatingTeam="oncTeam1", ward="oncWard"),
    _RawResource(rid="oncPat2oncItem", type="HRitem", author="doc1", patient="oncPat2", topics=frozenset({"oncology"}), treatingTeam="oncTeam2", ward="oncWard"),
    _RawResource(rid="oncPat2nursingItem", type="HRitem", author="oncNurse1", patient="oncPat2", topics=frozenset({"nursing"}), treatingTeam="oncTeam2", ward="oncWard"),
    _RawResource(rid="oncPat2noteItem", type="HRitem", author="oncAgent1", patient="oncPat2", topics=frozenset({"note"}), treatingTeam="oncTeam2", ward="oncWard"),
    _RawResource(rid="oncPat2HR", type="HR", patient="oncPat2", treatingTeam="oncTeam2", ward="oncWard"),
    _RawResource(rid="carPat1carItem", type="HRitem", author="carDoc2", patient="carPat1", topics=frozenset({"cardiology"}), treatingTeam="carTeam1", ward="carWard"),
    _RawResource(rid="carPat1nursingItem", type="HRitem", author="carNurse1", patient="carPat1", topics=frozenset({"nursing"}), treatingTeam="carTeam1", ward="carWard"),
    _RawResource(rid="carPat1noteItem", type="HRitem", author="carPat1", patient="carPat1", topics=frozenset({"note"}), treatingTeam="carTeam1", ward="carWard"),
    _RawResource(rid="carPat1HR", type="HR", patient="carPat1", treatingTeam="carTeam1", ward="carWard"),
    _RawResource(rid="carPat2carItem", type="HRitem", author="doc2", patient="carPat2", topics=frozenset({"cardiology"}), treatingTeam="carTeam2", ward="carWard"),
    _RawResource(rid="carPat2nursingItem", type="HRitem", author="carNurse2", patient="carPat2", topics=frozenset({"nursing"}), treatingTeam="carTeam2", ward="carWard"),
    _RawResource(rid="carPat2noteItem", type="HRitem", author="carAgent1", patient="carPat2", topics=frozenset({"note"}), treatingTeam="carTeam2", ward="carWard"),
    _RawResource(rid="carPat2HR", type="HR", patient="carPat2", treatingTeam="carTeam2", ward="carWard"),
)

_OPS_BY_RESOURCE_TYPE: Dict[str, Tuple[str, ...]] = {
    "HR": ("addItem", "addNote"),
    "HRitem": ("read",),
}


def structurally_valid_triples() -> List[Tuple[_RawUser, _RawResource, str]]:
    """The 420 (user, resource, op) triples this validation sweeps: every
    user paired with every resource, restricted to the op(s) that
    resource's own `type` supports -- addItem/addNote apply only to
    type=HR (the whole record), read only to type=HRitem (an entry in
    it), mirroring the case study's own two rule blocks ("rules for
    health records" vs. "rules for health record items")."""
    return [(u, r, op) for u in _USERS for r in _RESOURCES for op in _OPS_BY_RESOURCE_TYPE[r.type]]


def _grant_raw(user: _RawUser, resource: _RawResource, op: str) -> bool:
    """Formulation A: the 9 `rule(...)` lines transcribed directly,
    each checked against both the DSL text and the file's own English
    comment for that rule while transcribing."""
    if op == "addItem" and resource.type == "HR" and user.position == "nurse" and user.ward == resource.ward:
        return True  # "a nurse can add an item in a HR for a patient in the ward in which he/she works"
    if op == "addItem" and resource.type == "HR" and resource.treatingTeam in user.teams:
        return True  # "a user can add an item in a HR for a patient treated by one of the teams of which he/she is a member"
    if op == "addNote" and resource.type == "HR" and user.uid == resource.patient:
        return True  # "a user can add an item with topic note in his/her own HR"
    if op == "addNote" and resource.type == "HR" and resource.patient in user.agentFor:
        return True  # "...in the HR of a patient for which he/she is an agent"
    if op == "read" and resource.type == "HRitem" and user.uid == resource.author:
        return True  # "the author of an item can read it"
    if op == "read" and resource.type == "HRitem" and user.position == "nurse" and "nursing" in resource.topics and user.ward == resource.ward:
        return True  # "a nurse can read an item with topic nursing...in the ward in which he/she works"
    if op == "read" and resource.type == "HRitem" and resource.topics <= user.specialties and resource.treatingTeam in user.teams:
        return True  # "...if the topics of the item are among his/her specialties" + on the treating team
    if op == "read" and resource.type == "HRitem" and "note" in resource.topics and user.uid == resource.patient:
        return True  # "a user can read an item with topic note in his/her own HR"
    if op == "read" and resource.type == "HRitem" and "note" in resource.topics and resource.patient in user.agentFor:
        return True  # "an agent can read an item with topic note...for which he/she is an agent"
    return False


def _rule_hits(user: _RawUser, resource: _RawResource, op: str) -> List[int]:
    """Which of the 9 original rules (1-indexed, source order) this
    triple satisfies -- used only for the |[[rho]]| corroboration
    (Fig. 5's average per-rule coverage, 6.7), never for the grant
    verdict itself (that stays `_grant_raw`, independent of this)."""
    hits = []
    if op == "addItem" and resource.type == "HR" and user.position == "nurse" and user.ward == resource.ward:
        hits.append(1)
    if op == "addItem" and resource.type == "HR" and resource.treatingTeam in user.teams:
        hits.append(2)
    if op == "addNote" and resource.type == "HR" and user.uid == resource.patient:
        hits.append(3)
    if op == "addNote" and resource.type == "HR" and resource.patient in user.agentFor:
        hits.append(4)
    if op == "read" and resource.type == "HRitem" and user.uid == resource.author:
        hits.append(5)
    if op == "read" and resource.type == "HRitem" and user.position == "nurse" and "nursing" in resource.topics and user.ward == resource.ward:
        hits.append(6)
    if op == "read" and resource.type == "HRitem" and resource.topics <= user.specialties and resource.treatingTeam in user.teams:
        hits.append(7)
    if op == "read" and resource.type == "HRitem" and "note" in resource.topics and user.uid == resource.patient:
        hits.append(8)
    if op == "read" and resource.type == "HRitem" and "note" in resource.topics and resource.patient in user.agentFor:
        hits.append(9)
    return hits


# -- Formulation B: the same 9 rules, flattened for mining_baseline.py -----

CANDIDATE_PROPERTIES: Tuple[str, ...] = (
    "position",
    "resource_type",
    "op",
    "wards_match",
    "is_author",
    "is_patient",
    "is_agent_for_patient",
    "on_treating_team",
    "specialties_cover_topics",
    "topic_is_nursing",
    "topic_is_note",
)


@dataclass(frozen=True)
class FlatTuple:
    position: str | None
    resource_type: str
    op: str
    wards_match: bool
    is_author: bool
    is_patient: bool
    is_agent_for_patient: bool
    on_treating_team: bool
    specialties_cover_topics: bool
    topic_is_nursing: bool
    topic_is_note: bool


def _flatten(user: _RawUser, resource: _RawResource, op: str) -> FlatTuple:
    """The 11 candidate properties `mining_baseline.py`'s equality-based
    generalizer can actually operate on -- relational tests over the raw
    attributes (e.g. `resource.treatingTeam in user.teams`) are
    precomputed into flat booleans HERE, once, so the mining algorithm
    sees the same relational facts the original 9 rules test, not a
    weaker approximation of them."""
    return FlatTuple(
        position=user.position,
        resource_type=resource.type,
        op=op,
        wards_match=(user.ward == resource.ward),
        is_author=(user.uid == resource.author),
        is_patient=(user.uid == resource.patient),
        is_agent_for_patient=(resource.patient in user.agentFor),
        on_treating_team=(resource.treatingTeam in user.teams),
        specialties_cover_topics=(resource.topics <= user.specialties),
        topic_is_nursing=("nursing" in resource.topics),
        topic_is_note=("note" in resource.topics),
    )


def _grant_flat(t: FlatTuple) -> bool:
    """Formulation B: the identical 9 clauses, restated over `FlatTuple`'s
    own fields -- must agree with `_grant_raw` on every structurally
    valid triple (tier 2 of the registered validation criteria above)."""
    if t.op == "addItem" and t.resource_type == "HR" and t.position == "nurse" and t.wards_match:
        return True
    if t.op == "addItem" and t.resource_type == "HR" and t.on_treating_team:
        return True
    if t.op == "addNote" and t.resource_type == "HR" and t.is_patient:
        return True
    if t.op == "addNote" and t.resource_type == "HR" and t.is_agent_for_patient:
        return True
    if t.op == "read" and t.resource_type == "HRitem" and t.is_author:
        return True
    if t.op == "read" and t.resource_type == "HRitem" and t.position == "nurse" and t.topic_is_nursing and t.wards_match:
        return True
    if t.op == "read" and t.resource_type == "HRitem" and t.specialties_cover_topics and t.on_treating_team:
        return True
    if t.op == "read" and t.resource_type == "HRitem" and t.topic_is_note and t.is_patient:
        return True
    if t.op == "read" and t.resource_type == "HRitem" and t.topic_is_note and t.is_agent_for_patient:
        return True
    return False


def build_reachable_and_registry() -> Tuple[Tuple[str, ...], List[FlatTuple], Dict[str, Any]]:
    reachable = [_flatten(u, r, op) for u, r, op in structurally_valid_triples()]
    registry = {"denied_by_original_healthcare_policy": lambda t: not _grant_flat(t)}
    return CANDIDATE_PROPERTIES, reachable, registry


def run() -> Dict[str, Any]:
    triples = structurally_valid_triples()

    # Tier 1: transcription oracle -- |UP| must be exactly 51 (Fig. 5).
    true_grants = [_grant_raw(u, r, op) for u, r, op in triples]
    up_count = sum(true_grants)
    tier1_pass = up_count == PUBLISHED_UP_COUNT

    hit_lists = [_rule_hits(u, r, op) for u, r, op, in triples]
    per_rule_counts = [sum(1 for hits in hit_lists if rule_no in hits) for rule_no in range(1, 10)]
    average_rule_coverage = sum(per_rule_counts) / len(per_rule_counts)

    # Tier 2: formulation agreement, per triple, not just aggregate.
    candidate_properties, reachable, registry = build_reachable_and_registry()
    flat_grants = [_grant_flat(t) for t in reachable]
    disagreements = [i for i, (a, b) in enumerate(zip(true_grants, flat_grants)) if a != b]
    tier2_pass = not disagreements

    # Tier 3: mining_baseline.py, run on the flattened case study.
    mining_result = mine_policy(candidate_properties, reachable, registry)
    soundness = verify_soundness(candidate_properties, reachable, registry, mining_result["rules"])
    tier3_pass = bool(soundness["sound"]) and soundness["mismatch_count"] == 0

    # Tier 4: rule-count corroboration, generous pre-registered tolerance.
    rule_count = mining_result["rule_count_after_simplify"]
    tier4_pass = RULE_COUNT_TOLERANCE_BAND[0] <= rule_count <= RULE_COUNT_TOLERANCE_BAND[1]

    validated = tier1_pass and tier2_pass and tier3_pass and tier4_pass

    return {
        "source": "https://www3.cs.stonybrook.edu/~stoller/software/ABAC-Mining.zip (ABACMining/case-studies/healthcare.abac), retrieved 2026-09-08",
        "citation_id": "xu-stoller-healthcare-case-study-data",
        "tier_1_transcription_oracle": {
            "pass": tier1_pass,
            "computed_up_count": up_count,
            "published_up_count": PUBLISHED_UP_COUNT,
            "computed_average_rule_coverage": average_rule_coverage,
            "published_average_rule_coverage": PUBLISHED_AVERAGE_RULE_COVERAGE,
            "per_original_rule_coverage": per_rule_counts,
        },
        "tier_2_formulation_agreement": {
            "pass": tier2_pass,
            "triples_checked": len(triples),
            "disagreement_count": len(disagreements),
            "first_disagreements": disagreements[:5],
        },
        "tier_3_mining_soundness": {
            "pass": tier3_pass,
            "sound": soundness["sound"],
            "mismatch_count": soundness["mismatch_count"],
            "tractable": mining_result["tractable"],
            "elapsed_seconds": mining_result["elapsed_seconds"],
        },
        "tier_4_rule_count_tolerance": {
            "pass": tier4_pass,
            "rule_count_after_simplify": rule_count,
            "rule_count_before_simplify": mining_result["rule_count_before_simplify"],
            "published_rule_count": PUBLISHED_RULE_COUNT,
            "tolerance_band": list(RULE_COUNT_TOLERANCE_BAND),
        },
        "validated": validated,
        "disposition": "VALIDATED" if validated else "EXCLUDED: UNVALIDATED",
    }


def main() -> None:
    result = run()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"\nXu-Stoller validation gate: {result['disposition']} "
          f"(tiers: 1={result['tier_1_transcription_oracle']['pass']}, "
          f"2={result['tier_2_formulation_agreement']['pass']}, "
          f"3={result['tier_3_mining_soundness']['pass']}, "
          f"4={result['tier_4_rule_count_tolerance']['pass']})")


if __name__ == "__main__":
    main()
