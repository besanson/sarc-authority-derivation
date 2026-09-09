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
Package A (review-secondary/final-gap-plan-9.5-2026-09-09.pdf's own
mandatory CI smoke test): a true black-box check that a BUILT WHEEL --
not this repository's own source tree -- actually contains a working
`authority_compiler`. Run via `make package-smoke-test` (locally) or the
`package` CI job (both Python 3.11 and 3.12): build sdist+wheel, install
the wheel alone into a fresh, disposable virtual environment, then feed
THIS file's own contents to that venv's `python` on STDIN (`python - <
authority_compiler_smoke.py`), never as `python authority_compiler_smoke.py` -- the two are
not equivalent: running a script BY PATH puts that script's own
directory (this repository's root) at `sys.path[0]`, which would let
`import reduct`/`import domain`/etc. silently resolve against THIS
repo's own source files even if the wheel's packaging were broken,
defeating the entire point of a black-box test. Reading from stdin
instead (and invoking from a neutral working directory, e.g. /tmp, not
this repo) sets `sys.path[0]` to that neutral cwd, so every import below
can only be satisfied by what pip actually installed from the wheel.

The example itself is deliberately trivial and hand-verifiable (two
boolean properties, verdict = both set) -- this is a packaging check,
not a correctness check (that is every other test file's own job); it
exists to prove the installed package runs end to end, not to test
`derive_authority_contract`'s logic again.
"""
from __future__ import annotations

from dataclasses import make_dataclass

from authority_compiler import AuthorityContract, derive_authority_contract

CandidateTuple = make_dataclass("CandidateTuple", [("a", int), ("b", int)], frozen=True)
reachable = [CandidateTuple(1, 1), CandidateTuple(0, 1), CandidateTuple(1, 0), CandidateTuple(0, 0)]
loss_model = {"needs_both": lambda t: t.a == 1 and t.b == 1}
candidate_context = {"a": [0, 1], "b": [0, 1]}

contract = derive_authority_contract(loss_model, reachable, candidate_context)
assert isinstance(contract, AuthorityContract), type(contract)
assert contract.minimum_cardinality_reduct == frozenset({"a", "b"}), sorted(contract.minimum_cardinality_reduct)
assert contract.core_attributes == frozenset({"a", "b"}), sorted(contract.core_attributes)

print("IMPORT_OK")
print("DERIVE_OK", sorted(contract.minimum_cardinality_reduct))
