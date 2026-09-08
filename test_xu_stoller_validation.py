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
"""Tests for xu_stoller_validation.py (Milestone E Step 3,
prereg/v6.1-authoritybench-amendment.md) -- the decisive checks are the
transcription oracle (|UP|==51, Fig. 5's own published number) and the
formulation-A/formulation-B agreement, since together they are what make
the downstream mining-soundness tier meaningful evidence about
`mining_baseline.py` rather than evidence about a mistranscription."""
from __future__ import annotations

from xu_stoller_validation import (
    _USERS,
    _RESOURCES,
    _grant_flat,
    _grant_raw,
    build_reachable_and_registry,
    run,
    structurally_valid_triples,
)


def test_case_study_size_matches_figure_5():
    """|A_u|=6 (position, ward, specialties, teams, agentFor, uid),
    |A_r|=7 (type, patient, treatingTeam, ward, author, topics, rid),
    |U|=21, |R|=16 -- the health care row of Fig. 5, confirmed directly
    against the transcribed data, not merely asserted."""
    assert len(_USERS) == 21
    assert len(_RESOURCES) == 16
    assert len({r.type for r in _RESOURCES}) == 2
    assert sum(1 for r in _RESOURCES if r.type == "HR") == 4
    assert sum(1 for r in _RESOURCES if r.type == "HRitem") == 12


def test_structurally_valid_triples_count_is_420():
    """21 users x (4 HR x 2 ops + 12 HRitem x 1 op) = 21 x 20 = 420."""
    assert len(structurally_valid_triples()) == 420


def test_transcription_oracle_reproduces_the_published_up_count_of_51():
    """Fig. 5's health care row: |UP|=51. The single most decisive check
    in this file -- if this fails, the 9 rules or the 21/16 attribute
    transcriptions have a bug, found here before any mining code runs
    against them."""
    triples = structurally_valid_triples()
    granted = sum(1 for u, r, op in triples if _grant_raw(u, r, op))
    assert granted == 51


def test_formulation_a_and_b_agree_on_every_structurally_valid_triple():
    """The flattened 11-boolean/categorical encoding (`_grant_flat`) must
    decide identically to the raw-attribute interpreter (`_grant_raw`) on
    every one of the 420 triples, not merely on the aggregate count --
    two formulations could theoretically disagree on some triples while
    agreeing on the total by coincidence; this checks per-triple."""
    from xu_stoller_validation import _flatten

    triples = structurally_valid_triples()
    for u, r, op in triples:
        assert _grant_raw(u, r, op) == _grant_flat(_flatten(u, r, op)), (u.uid, r.rid, op)


def test_build_reachable_and_registry_matches_grant_flat():
    """The registry predicate `mine_policy` actually consumes must agree
    with `_grant_flat` (denied == not granted), the m_verdict polarity
    convention this whole project uses elsewhere."""
    import dataclasses

    from losses import m_verdict

    candidate_properties, reachable, registry = build_reachable_and_registry()
    assert len(reachable) == 420
    assert set(candidate_properties) == {f.name for f in dataclasses.fields(reachable[0])}
    for t in reachable:
        assert m_verdict(t, registry) == (not _grant_flat(t))


def test_run_reports_a_well_formed_result_with_all_four_tiers():
    result = run()
    assert result["tier_1_transcription_oracle"]["computed_up_count"] == 51
    assert result["tier_1_transcription_oracle"]["pass"] is True
    assert result["tier_2_formulation_agreement"]["disagreement_count"] == 0
    assert result["tier_2_formulation_agreement"]["pass"] is True
    assert result["disposition"] in ("VALIDATED", "EXCLUDED: UNVALIDATED")
    assert result["validated"] == (
        result["tier_1_transcription_oracle"]["pass"]
        and result["tier_2_formulation_agreement"]["pass"]
        and result["tier_3_mining_soundness"]["pass"]
        and result["tier_4_rule_count_tolerance"]["pass"]
    )
