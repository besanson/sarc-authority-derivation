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
Definitions 1-3 (task brief Phase 2).

Definition 1 (participation): property p is authority-bearing for loss
model M iff there exist executable-reachable tuples a, a' differing only
in p whose M-verdicts differ.

Definition 2 (the minimal participation set P*): P* = {p in
candidate_properties : p is authority-bearing for M}.

Definition 3 (the derived coverage list): candidate_properties - P*, the
declared residue -- properties this derivation found no reachable
evidence for, emitted honestly rather than silently dropped.

Soundness/minimality of P* as defined here are structural consequences
of Definition 1 (see appendix-a-proofs.md's Proposition 1): a gate that
observes exactly P* can always compute M's true verdict on any reachable
tuple (soundness), and no proper subset of P* has this property
(minimality), PROVIDED M's per-tuple verdict is a well-defined function
of the tuple -- which losses.m_verdict is, by construction (a pure
function of one StateTuple). checkers/participation_check.py verifies
this by independent re-derivation, not by re-asserting the proposition.

SEED = 26313 (not applicable directly -- this module operates on the
finite abstract model, not the seeded simulation; seeded only via
whatever ordering domain.py's enumeration functions produce, which is
itself deterministic and seed-independent)
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from typing import Any, Callable, Dict, List, Optional, Tuple

from domain import CANDIDATE_PROPERTIES, StateTuple, field_names
from losses import m_verdict


def _fingerprint(t: StateTuple, exclude: str) -> Tuple[Any, ...]:
    return tuple(getattr(t, name) for name in field_names() if name != exclude)


def find_witness(
    property_name: str,
    reachable: List[StateTuple],
    registry: Dict[str, Callable[[StateTuple], bool]],
) -> Optional[Dict[str, Any]]:
    """Search reachable for a pair (a, a') differing only in
    property_name whose M-verdicts differ. Groups by the fingerprint of
    every OTHER field so a witness pair is found in O(n) rather than
    O(n^2) pairwise comparison; returns the first witness found (by
    reachable's own iteration order, which domain.py makes deterministic)
    plus which loss(es) disagreed, or None if no witness exists."""
    groups: Dict[Tuple[Any, ...], List[StateTuple]] = defaultdict(list)
    for t in reachable:
        groups[_fingerprint(t, property_name)].append(t)

    for group in groups.values():
        if len(group) < 2:
            continue
        verdicts = [(t, m_verdict(t, registry)) for t in group]
        base_verdict = verdicts[0][1]
        for t, v in verdicts[1:]:
            if v != base_verdict:
                a, a_prime = verdicts[0][0], t
                fired_a = {lid: pred(a) for lid, pred in registry.items() if pred(a)}
                fired_a_prime = {lid: pred(a_prime) for lid, pred in registry.items() if pred(a_prime)}
                differing_losses = sorted(set(fired_a) ^ set(fired_a_prime))
                loss_id = differing_losses[0] if differing_losses else "unknown"
                return {
                    "loss_id": loss_id,
                    "tuple_a": _serialize(a),
                    "tuple_a_prime": _serialize(a_prime),
                    "verdict_a": base_verdict,
                    "verdict_a_prime": v,
                }
    return None


def _serialize(t: StateTuple) -> Dict[str, Any]:
    d = asdict(t)
    for k, v in d.items():
        if isinstance(v, frozenset):
            d[k] = sorted(v)
        elif isinstance(v, tuple):
            d[k] = list(v)
    return d


def compute_p_star(
    reachable: List[StateTuple],
    registry: Dict[str, Callable[[StateTuple], bool]],
    candidate_properties: Tuple[str, ...] = CANDIDATE_PROPERTIES,
) -> Tuple[List[str], List[str], Dict[str, List[Dict[str, Any]]]]:
    """Definition 2 + 3. Returns (P*, coverage_list, witnesses) where
    witnesses maps each P* member to a one-element list containing its
    witness (schemas/derivation_output.schema.json allows more than one;
    this derivation records exactly the first found, deterministically)."""
    p_star: List[str] = []
    coverage: List[str] = []
    witnesses: Dict[str, List[Dict[str, Any]]] = {}
    for prop in candidate_properties:
        witness = find_witness(prop, reachable, registry)
        if witness is not None:
            p_star.append(prop)
            witnesses[prop] = [witness]
        else:
            coverage.append(prop)
    return sorted(p_star), sorted(coverage), witnesses
