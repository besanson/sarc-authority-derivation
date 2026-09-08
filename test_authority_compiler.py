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
"""Tests for src/authority_compiler (Milestone E1, full signature --
prereg/v6.1-authoritybench-amendment.md) -- confirms the packaged entry
point returns exactly what its wrapped functions (reduct.compute_core,
reduct.sufficiency, reduct.exact_reducts, synthesis.
find_minimum_cardinality_contract, synthesis.find_minimum_cost_contract,
synthesis.contract_change_delta) return when called directly with the
same arguments, on small synthetic fixtures shared with test_reduct.py/
test_synthesis.py for direct comparability -- deliberately no real-domain
integration test here: this file feeds mutation testing (pyproject.toml),
and a real domain's discernibility-family build (tens of seconds,
benchmarks.py's own Makefile comment) run per mutant would make `make
mutate` prohibitive, the same reason test_reduct.py/test_synthesis.py
stay synthetic-only and real-domain checks live separately in
checkers/*.py instead."""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from reduct import compute_core, exact_reducts, sufficiency
from synthesis import find_minimum_cardinality_contract, find_minimum_cost_contract

from authority_compiler import AuthorityContract, derive_authority_contract
from authority_compiler.api import EXHAUSTIVE_REDUCT_SUBSET_LIMIT


@dataclass(frozen=True)
class Toy:
    x: int
    y: int
    z: str

    def with_property(self, name: str, value: Any) -> "Toy":
        return replace(self, **{name: value})


TWO_STATE = [Toy(x=0, y=0, z="a"), Toy(x=1, y=1, z="a")]


def two_state_registry():
    return {"is_one": lambda t: bool(t.x)}


def test_derive_authority_contract_matches_the_wrapped_functions_directly():
    """x alone determines the verdict (test_reduct.py's own unique-reduct
    fixture): core == {x}, sufficient, minimum-cardinality reduct == {x}
    too -- every field matches calling the wrapped functions directly
    with the same arguments, not just a plausible-looking value. `z`'s
    declared domain (a, b, c) is wider than what actually appears in
    `reachable_semantics` (only a, b) -- the one property this fixture
    registers as reachability-dependent."""
    reachable = [Toy(x=1, y=1, z="a"), Toy(x=9, y=1, z="a"), Toy(x=1, y=2, z="b")]
    registry = {"x_ge_5": lambda t: t.x >= 5}
    candidate_context = {"x": [1, 9], "y": [1, 2], "z": ["a", "b", "c"]}
    candidate_properties = ("x", "y", "z")

    result = derive_authority_contract(registry, reachable, candidate_context)
    assert isinstance(result, AuthorityContract)

    expected_core, expected_coverage, _ = compute_core(reachable, registry, candidate_properties)
    expected_sufficient, expected_certificate = sufficiency(tuple(sorted(expected_core)), reachable, registry)
    expected_reducts, _ = exact_reducts(candidate_properties, reachable, registry)
    expected_min_card = find_minimum_cardinality_contract(candidate_properties, reachable, registry)

    assert result.core_attributes == frozenset(expected_core) == frozenset({"x"})
    assert result.redundant_attributes == frozenset(expected_coverage) == frozenset({"y", "z"})
    assert result.sufficiency_certificate == expected_certificate
    assert result.counterexamples is None  # core IS sufficient here
    assert result.minimal_reducts == expected_reducts == [frozenset({"x"})]
    assert result.minimal_reducts_note is None
    assert result.minimum_cardinality_reduct == expected_min_card == frozenset({"x"})
    assert result.minimum_cost_reduct is None  # no observation_costs supplied
    assert result.reachability_dependencies == frozenset({"z"})
    assert result.candidate_property_count == 3
    assert result.reachable_tuple_count == 3
    assert expected_sufficient is True


def test_derive_authority_contract_reports_an_insufficient_empty_core_honestly():
    """Negative Proposition N's own registered counterexample
    (test_reduct.py's TWO_STATE): the core is EMPTY and NOT sufficient --
    `derive_authority_contract` must report a counterexample, not
    silently treat the empty core as though it were a valid answer, and
    minimum_cardinality_reduct must still be a genuine, nonempty,
    sufficient reduct (the packaged entry point's own honest fallback
    when the core alone does not suffice). Both singleton reducts tie on
    cardinality; declaring y strictly cheaper than x must make
    minimum_cost_reduct pick y specifically, independent of
    minimum_cardinality_reduct's own (unspecified-by-cost) tie-break."""
    registry = two_state_registry()
    candidate_context = {"x": [0, 1], "y": [0, 1]}

    result = derive_authority_contract(registry, TWO_STATE, candidate_context, observation_costs={"x": 5.0, "y": 1.0})

    assert result.core_attributes == frozenset()
    assert result.redundant_attributes == frozenset({"x", "y"})
    assert result.counterexamples is not None
    assert result.counterexamples["verdict_a"] != result.counterexamples["verdict_a_prime"]
    assert sorted(sorted(r) for r in result.minimal_reducts) == [["x"], ["y"]]
    assert result.minimum_cardinality_reduct in (frozenset({"x"}), frozenset({"y"}))
    is_suff, _ = sufficiency(tuple(sorted(result.minimum_cardinality_reduct)), TWO_STATE, registry)
    assert is_suff is True

    expected_min_cost = find_minimum_cost_contract(("x", "y"), TWO_STATE, registry, {"x": 5.0, "y": 1.0})
    assert result.minimum_cost_reduct == expected_min_cost == frozenset({"y"})
    assert result.reachability_dependencies == frozenset()  # both properties use their full declared 2-value domain


def test_derive_authority_contract_skips_exhaustive_enumeration_past_the_limit():
    """A candidate_context larger than EXHAUSTIVE_REDUCT_SUBSET_LIMIT
    must report minimal_reducts=None with a stated reason, not silently
    truncate or sample -- exercised by monkeypatching the module-level
    limit down to something a tiny fixture can exceed, rather than
    building a genuinely huge candidate set just to test this branch."""
    import authority_compiler.api as api_module

    original_limit = api_module.EXHAUSTIVE_REDUCT_SUBSET_LIMIT
    try:
        api_module.EXHAUSTIVE_REDUCT_SUBSET_LIMIT = 2
        registry = {"x_ge_5": lambda t: t.x >= 5}
        reachable = [Toy(x=1, y=1, z="a"), Toy(x=9, y=1, z="a"), Toy(x=1, y=2, z="b")]
        candidate_context = {"x": [1, 9], "y": [1, 2], "z": ["a", "b"]}  # 3 properties > patched limit of 2

        result = api_module.derive_authority_contract(registry, reachable, candidate_context)
        assert result.minimal_reducts is None
        assert result.minimal_reducts_note is not None
        assert "3" in result.minimal_reducts_note
        assert result.minimum_cardinality_reduct == frozenset({"x"})  # still computed via the SAT backend, unaffected
    finally:
        api_module.EXHAUSTIVE_REDUCT_SUBSET_LIMIT = original_limit


def test_derive_authority_contract_attempts_exhaustion_exactly_at_the_limit():
    """The boundary the above test does not reach: candidate count EQUAL
    to EXHAUSTIVE_REDUCT_SUBSET_LIMIT must still attempt exhaustive
    enumeration (the registered threshold is `<=`, not `<`) -- patches
    the limit to exactly this fixture's own 3-property count."""
    import authority_compiler.api as api_module

    original_limit = api_module.EXHAUSTIVE_REDUCT_SUBSET_LIMIT
    try:
        api_module.EXHAUSTIVE_REDUCT_SUBSET_LIMIT = 3
        registry = {"x_ge_5": lambda t: t.x >= 5}
        reachable = [Toy(x=1, y=1, z="a"), Toy(x=9, y=1, z="a"), Toy(x=1, y=2, z="b")]
        candidate_context = {"x": [1, 9], "y": [1, 2], "z": ["a", "b"]}  # 3 properties == patched limit of 3

        result = api_module.derive_authority_contract(registry, reachable, candidate_context)
        assert result.minimal_reducts == [frozenset({"x"})]
        assert result.minimal_reducts_note is None
    finally:
        api_module.EXHAUSTIVE_REDUCT_SUBSET_LIMIT = original_limit


def test_contract_change_delta_field_is_bound_to_this_calls_own_arguments():
    """The returned `contract_change_delta` is a callable closing over
    this call's OWN minimum_cardinality_reduct/candidate_properties/
    reachable_semantics/loss_model -- calling it with new_tuples alone
    must match calling synthesis.contract_change_delta directly with
    those same bound arguments plus the same new_tuples."""
    from synthesis import contract_change_delta as raw_contract_change_delta

    reachable = [Toy(x=1, y=1, z="a"), Toy(x=9, y=1, z="a"), Toy(x=1, y=2, z="b")]
    registry = {"x_ge_5": lambda t: t.x >= 5, "z_is_dangerous": lambda t: t.z == "c"}
    candidate_context = {"x": [1, 9], "y": [1, 2], "z": ["a", "b", "c"]}
    new_tuples = [Toy(x=1, y=1, z="c")]

    result = derive_authority_contract(registry, reachable, candidate_context)
    bound_delta = result.contract_change_delta(new_tuples)

    expected_delta = raw_contract_change_delta(
        result.minimum_cardinality_reduct, ("x", "y", "z"), reachable, new_tuples, registry
    )
    assert bound_delta == expected_delta
    assert bound_delta["was_still_sufficient"] is False
    assert bound_delta["updated_contract"] == ["x", "z"]
