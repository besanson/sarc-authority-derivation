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
synthesis.py), unmodified."""
from __future__ import annotations

from authority_compiler.api import AuthorityContract, derive_authority_contract

__all__ = ["AuthorityContract", "derive_authority_contract"]
