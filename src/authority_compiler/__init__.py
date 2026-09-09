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
"""Milestone E1: this artifact's own derivation machinery, packaged
behind one call. See `authority_compiler.api` for the implementation --
every field `derive_authority_contract` returns is computed by an
existing, already-verified top-level module (participation.py, reduct.py,
synthesis.py), unmodified.

**Public API stability statement (Package A, review-secondary/
final-gap-plan-9.5-2026-09-09.pdf):** `derive_authority_contract` and
`AuthorityContract` (this module's `__all__`, in full) are this
package's stable public surface -- their names, parameter order, and
`AuthorityContract`'s own field set do not change without a version
bump and a NOVELTY.md amendment explaining why. `authority_compiler.api`
is an implementation module: importable, but not itself part of the
stability contract -- import from `authority_compiler` directly, not
`authority_compiler.api`, to stay on the stable surface. `__version__`
tracks this distribution's own release (`importlib.metadata`, falling
back to a sentinel when not installed -- e.g. `pythonpath` test-mode,
`reproducibility_report.py`'s own `_dependency_versions` uses the same
fallback pattern for the same reason: an uninstalled, path-injected
import must not crash on a metadata lookup that has nothing to find)."""
from __future__ import annotations

import importlib.metadata

from authority_compiler.api import AuthorityContract, derive_authority_contract

try:
    __version__ = importlib.metadata.version("sarc-authority-derivation")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0+unknown"

__all__ = ["AuthorityContract", "derive_authority_contract", "__version__"]
