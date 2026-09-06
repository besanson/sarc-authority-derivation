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

r"""
typed-numerals lint (v0.2.1 repair 2b): every numeral in the live paper
draft's own prose must come from a `[GENERATED: ...]` slot, not be
hand-typed, except for a declared, narrow allowlist -- so a future
hand-typed result number (the exact mistake repair 1 fixed for v2's
CH-A5-CH-A7 counts) is caught automatically rather than relying on
review to notice it. Scoped to the live draft
(paper5-authority-derivation-draft-v0.3.md) only: v0.1's own source is
frozen as of commit 37a2e7f and v0.2's at commit 7112031 (README.md's
version-split note), neither re-gated by a check invented after either
was written.

"Prose" excludes, stripped before any allowlist is applied: a
`[GENERATED: ...]` slot itself; inline code spans and fenced code
blocks (identifiers, formulas, file paths -- not claims in the author's
voice); double-quoted spans (a direct quotation, already governed by
citation_check.py's own verification gate, or -- as in Section 9's
"100% detection" -- a hypothetical reader's misreading, not this
paper's own assertion); and bare URLs.

The declared allowlist, applied to what remains:
1. Section numbers, broadened to every numbered structural element this
   document itself defines and cross-references by number -- Section,
   Definition(s), Proposition(s), Corollary, Theorem, Lemma, and the
   SARC series' own "paper N" convention -- plus a markdown heading's
   own leading number ("## 5. Definitions").
2. Years (bare, 1900-2099) and full dates (a day-of-month immediately
   before a month name and year, e.g. "28 August 2026", checked as one
   unit so the day-of-month is not flagged as a separate bare count).
3. Hypothesis/finding/identifier ids: this document's own short
   letter-prefix-plus-digit labels (CH-A1..CH-A7, the cited
   replication's own A7, review findings F0/F1, loss ids L1-L3,
   workflow names W1/W2) -- matched by shape (an optional "CH-" prefix
   plus 1-2 uppercase letters plus 1-2 digits), not an enumerated list,
   so a newly added id in the same house style (CH-A8, F2, ...) is
   still recognized without editing this file.
4. Tag/version names: prereg-p5-v1/v2's own naming shape
   (`v\d+(\.\d+){0,2}`), covering every "v0.1"/"v0.2"/"v0.1.2"/"v1"/"v2"
   mention in this document as one convention, and an arXiv identifier
   shape (already governed by citation_check.py's own gate).
5. A short, explicit, BY-VALUE list of declared parameter/technical-term
   constants that are not measured/computed results and have no
   generated slot to source from: agent-delegate's entitlement
   ceiling/window/budget-multiplier (prereg/loss-model.yaml), the
   retry-delay day constant (domain.RETRY_DELAY_DAY), the CC BY license
   version, the sha256 hash-algorithm name, and this artifact's own
   "rank-0"/"round-0" compound model terms. Listed by literal value, not
   a general pattern, so a DIFFERENT bare numeral is still caught.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Pattern

DRAFT_PATH = "paper5-authority-derivation-draft-v0.3.md"
OUTPUT_PATH = Path("out/checkers/typed_numerals_lint.json")

_MONTHS = (
    "January|February|March|April|May|June|July|"
    "August|September|October|November|December"
)

_STRIP_FIRST: List[Pattern] = [
    re.compile(r"\[GENERATED:[^\]]*\]"),
    re.compile(r"```.*?```", re.DOTALL),
    re.compile(r"`[^`]*`"),
    re.compile(r'"[^"]*"'),
    re.compile(r"https?://\S+"),
]

_ALLOWED: List[Pattern] = [
    # 1. Structural cross-references + markdown heading numbers. An
    # optional trailing prime (Proposition 1') marks a corrected/replacement
    # numbered claim, same referent, not a different count.
    re.compile(
        r"\b(?:Section|Definitions?|Propositions?|Corollary|Theorem|Lemma|Phase|[Pp]aper|[Cc]laims?)"
        r"\s+\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?'?\b"
    ),
    re.compile(r"^#+\s*\d+(?:\.\d+)?\.?\s", re.MULTILINE),
    # 2. Full dates, then bare years.
    re.compile(rf"\b\d{{1,2}}\s+(?:{_MONTHS})\s+(?:19|20)\d{{2}}\b"),
    re.compile(r"\b(?:19|20)\d{2}\b"),
    # 3. Hypothesis / finding / loss / workflow identifiers.
    re.compile(r"\b(?:CH-)?[A-Z]{1,2}\d{1,2}\b"),
    # 4. Version/tag names; arXiv identifiers.
    re.compile(r"\bv\d+(?:\.\d+){0,2}\b"),
    re.compile(r"\b\d{4}\.\d{4,5}\b"),
    # Footnote markers.
    re.compile(r"\[\^\d+\]:?"),
    # 5. Declared parameter/technical-term constants, by literal value.
    re.compile(r"\b800-value\b"),
    re.compile(r"\[100,\s*180\]"),
    re.compile(r"\b1\.15x\b"),
    re.compile(r"\bday-200\b"),
    re.compile(r"\bCC BY 4\.0\b"),
    re.compile(r"\bsha256\b"),
    re.compile(r"\brank-0\b"),
    re.compile(r"\bround-0\b"),
]


def _redact(text: str, patterns: List[Pattern]) -> str:
    """Blank out every matched span with same-length whitespace,
    preserving embedded newlines, so line numbers reported for whatever
    remains stay accurate against the original text."""
    for pattern in patterns:
        text = pattern.sub(lambda m: "".join(c if c == "\n" else " " for c in m.group(0)), text)
    return text


def find_violations(text: str) -> List[Dict[str, Any]]:
    redacted = _redact(text, _STRIP_FIRST)
    redacted = _redact(redacted, _ALLOWED)

    violations = []
    for m in re.finditer(r"\S*\d\S*", redacted):
        line_start = redacted.rfind("\n", 0, m.start()) + 1
        line_end = redacted.find("\n", m.start())
        if line_end == -1:
            line_end = len(text)
        line_no = redacted.count("\n", 0, m.start()) + 1
        violations.append({
            "line": line_no,
            "token": text[m.start():m.end()],
            "context": text[line_start:line_end].strip(),
        })
    return violations


def run(draft_path: str = DRAFT_PATH) -> Dict[str, Any]:
    text = Path(draft_path).read_text()
    violations = find_violations(text)
    return {
        "draft_path": draft_path,
        "violation_count": len(violations),
        "violations": violations,
        "clean": len(violations) == 0,
    }


def main() -> None:
    result = run()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["clean"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
