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
"""Small shared JSON Schema validation helper (jsonschema, installed by
bootstrap.sh alongside pytest/hypothesis/mutmut, same toolchain as the
imported baseline)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import jsonschema


def validate_against_schema(instance: Dict[str, Any], schema_path: str) -> None:
    schema = json.loads(Path(schema_path).read_text())
    jsonschema.validate(instance=instance, schema=schema)
