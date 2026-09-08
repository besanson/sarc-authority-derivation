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
Milestone E1 (task brief; prereg/v6-authority-bench.md, tag
prereg-p5-v6, registers what E4 will point this package at):
packages this artifact's own already-verified derivation machinery
(participation.py's Definition 1/2, reduct.py's Definitions 4-6,
synthesis.py's SAT/MaxSAT backend) behind one call. No new derivation
semantics: `derive_authority_contract` computes every field by calling
straight through to an existing, already-tested function of the same
name -- `reduct.compute_core` (itself `participation.compute_p_star`
unmodified, per reduct.py's own docstring), `reduct.sufficiency`, and
`synthesis.find_minimum_cardinality_contract` (exact-verified against
exhaustive enumeration wherever exhaustion is affordable,
`checkers/synthesis_exactness_check.py`). This module's own new
behavior is the packaging itself (one dataclass, one dispatch
function, argument-order normalization across the three wrapped
functions' own differing signatures) -- not the mathematics, which
stays exactly where it was verified.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, FrozenSet, List, Tuple

from reduct import compute_core, sufficiency
from synthesis import find_minimum_cardinality_contract


@dataclass(frozen=True)
class AuthorityContract:
    """The packaged result of one `derive_authority_contract` call.

    `core`: Definition 2's P* -- individually-indispensable properties
    (each has its own singleton-perturbation witness, Definition 1).
    `coverage_list`: Definition 3 -- `candidate_properties - core`.
    `core_is_sufficient`: Definition 4, checked directly (Proposition 1'
    already establishes core is not *always* sufficient -- Negative
    Proposition N's own counterexample -- so this is a per-call fact,
    not assumed true from `core` alone).
    `minimum_cardinality_contract`: Definition 5, a reduct of minimum
    cardinality (via `synthesis.py`'s SAT/MaxSAT backend) -- always
    well-defined and returned, whether or not `core` itself turns out
    to be sufficient.
    """

    core: FrozenSet[str]
    coverage_list: FrozenSet[str]
    core_is_sufficient: bool
    minimum_cardinality_contract: FrozenSet[str]
    candidate_property_count: int
    reachable_tuple_count: int


def derive_authority_contract(
    candidate_properties: Tuple[str, ...],
    reachable: List[Any],
    registry: Dict[str, Callable[[Any], bool]],
) -> AuthorityContract:
    """The packaged entry point: candidate properties + the executable-
    reachable tuples + a declared loss registry in, one `AuthorityContract`
    out. Equivalent, field for field, to calling `reduct.compute_core`,
    `reduct.sufficiency`, and `synthesis.find_minimum_cardinality_contract`
    directly with the same three arguments -- this function's only
    contribution is bundling their three results into one returned value
    with one consistent argument order (the three wrapped functions
    declare `candidate_properties`/`reachable`/`registry` in three
    different orders among themselves; this package's own public
    signature fixes one, `synthesis.py`'s own convention, throughout)."""
    core, coverage, _witnesses = compute_core(reachable, registry, candidate_properties)
    core_sufficient, _ = sufficiency(tuple(sorted(core)), reachable, registry)
    min_card = find_minimum_cardinality_contract(candidate_properties, reachable, registry)
    return AuthorityContract(
        core=frozenset(core),
        coverage_list=frozenset(coverage),
        core_is_sufficient=core_sufficient,
        minimum_cardinality_contract=min_card,
        candidate_property_count=len(candidate_properties),
        reachable_tuple_count=len(reachable),
    )
