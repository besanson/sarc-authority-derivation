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
"""Phase 5 driver: populate_draft.py + paper_tables.py, wired together.

v0.5 is the live draft (README.md's version-split note, Package B,
review-secondary/final-gap-plan-9.5-2026-09-09.pdf): v0.1's own
source/populated pair is frozen at commit 37a2e7f, v0.2's at commit
7112031, v0.3's at commit 382be13, and v0.4's at the commit Package B's
own version-split makes; none of the four is read or written by this
module."""
from paper_tables import build_slots
from populate_draft import populate_draft

DRAFT_PATH = "paper5-authority-derivation-draft-v0.5.md"
OUTPUT_PATH = "paper5-authority-derivation-draft-v0.5-populated.md"

if __name__ == "__main__":
    slots = build_slots()
    unfilled = populate_draft(DRAFT_PATH, slots, OUTPUT_PATH)
    if unfilled:
        raise SystemExit(f"unfilled slots: {unfilled}")
