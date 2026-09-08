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
"""Tests for domain_datacomms.py -- mirrors test_domain_v4.py's own
precision (exact reachable size, every declared field value actually
appears, the one reachability rule's own boundary)."""
from __future__ import annotations

from domain_datacomms import (
    CANDIDATE_PROPERTIES_DATACOMMS,
    PROPERTY_DOMAINS_DATACOMMS,
    StateTupleDataComms,
    executable_reachable_tuples_datacomms,
    rank0_reachable_tuples_datacomms,
)


def test_candidate_properties_match_state_tuple_fields():
    from dataclasses import fields

    assert set(CANDIDATE_PROPERTIES_DATACOMMS) == {f.name for f in fields(StateTupleDataComms)}


def test_property_domains_matches_candidate_properties_exactly():
    assert set(PROPERTY_DOMAINS_DATACOMMS.keys()) == set(CANDIDATE_PROPERTIES_DATACOMMS)


def test_rank0_reachable_exact_size_after_reachability_rule():
    """4x5x9x2x2x3x4 = 8,640 -- the reachability rule narrows recipient_
    type x destination_region from 12 pairs to 9 (internal_only pairs
    only with eea)."""
    reachable = rank0_reachable_tuples_datacomms()
    assert len(reachable) == 8640


def test_executable_reachable_equals_rank0():
    """No remediation operator is declared for this domain -- same
    choice v4's own domain already made, verified directly rather than
    assumed."""
    assert executable_reachable_tuples_datacomms() == rank0_reachable_tuples_datacomms()


def test_internal_only_never_reaches_a_non_eea_region():
    reachable = rank0_reachable_tuples_datacomms()
    for t in reachable:
        if t.recipient_type == "internal_only":
            assert t.destination_region == "eea"


def test_non_internal_only_reaches_every_declared_region():
    """The reachability rule narrows ONLY internal_only -- the other two
    recipient types must still reach all four declared regions, not
    accidentally narrowed too."""
    reachable = rank0_reachable_tuples_datacomms()
    for recipient in ("processor_under_contract", "third_party_controller"):
        regions_reached = {t.destination_region for t in reachable if t.recipient_type == recipient}
        assert regions_reached == set(PROPERTY_DOMAINS_DATACOMMS["destination_region"])


def test_rank0_reachable_every_field_takes_every_declared_value():
    """Every one of the eight fields' full declared domain actually
    appears somewhere in the reachable set -- the Milestone C mutation-
    testing lesson (a field silently mutated to a constant/None would
    otherwise go unnoticed by aggregate-count tests alone)."""
    reachable = rank0_reachable_tuples_datacomms()
    for field, declared_domain in PROPERTY_DOMAINS_DATACOMMS.items():
        observed = {getattr(t, field) for t in reachable}
        assert observed == set(declared_domain), f"{field}: observed {observed} != declared {set(declared_domain)}"


def test_with_property_changes_exactly_one_field():
    t = rank0_reachable_tuples_datacomms()[0]
    t2 = t.with_property("data_category", "public")
    assert t2.data_category == "public"
    for f in CANDIDATE_PROPERTIES_DATACOMMS:
        if f != "data_category":
            assert getattr(t2, f) == getattr(t, f)


def test_state_tuple_is_hashable_and_usable_in_sets():
    t = rank0_reachable_tuples_datacomms()[0]
    {t}  # must not raise
