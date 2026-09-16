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
Terminology lint (Milestone A4, review-secondary/improvement-plan-9.5-
2026-09-06.pdf's reimplemented findings -- reimplemented from the plan,
never applied as a patch, per this repo's own external-review
discipline).

Live prose -- the v0.6.2 paper draft and README.md; this repository ships
no separate RESEARCH-GUIDE.md (the Makefile's own `help` target names
one that was never created), so "guide" resolves to README.md, the only
guide-equivalent document actually present -- must never assert that a
core or P* is sufficient, minimal, or sound FOR THE MODEL in general
without scope: the exact shape of v0.1/v0.2's own corrected overclaim
(Proposition 1 -> Proposition 1', appendix-a-proofs.md).

Every occurrence of P*, sufficient/sufficiency, minimal/minimality, and
sound/soundness -- plus, tracked but never fail-triggering on their own
since they name data structures rather than assert a property,
`participating_properties` and `coverage_list` -- is classified
paragraph-scoped (blank-line delimited, mirroring
proof_status_lint.py's own paragraph-scope convention) into exactly one
of five buckets:

  historical         -- framed as a past/superseded claim (a Corrections
                         section, "originally", "v0.1"/"v0.2", "now
                         corrected", "superseded", "overclaim").
  instance-certified -- grounded by a nearby checkers/*.py reference, a
                         CH-A hypothesis id, a [GENERATED: ...] slot, a
                         PROOF-STATUS tag, "certificate", or
                         "counterexample".
  general-theorem    -- holds for ANY model, not this one instance (a
                         defining "Definition N (...)" statement, an
                         "iff", "for any"/"in general"/"by construction"
                         proof shape, a negated claim ("need not be
                         sufficient"), or the Pawlak/Skowron-Rauszer
                         prior-art citations that shape is positioned
                         against).
  core               -- tied explicitly to Definition 6 / "the core".
  reduct             -- tied explicitly to Definition 5 / "the reduct".

A P*/sufficient/minimal/sound occurrence matching none of the five is a
VIOLATION: an unscoped, uncertified claim -- the overclaim shape this
checker exists to catch.

**Term-pair misuse (v0.6.1, `review-secondary/paper-revision-outline-
2026-09-15.md`, sha256 `9011e9e5d358d6fc50650ec5812f0c18905c21a165eb2a
317626eea1de6c6374`, section A6 of the commissioned amendment applying
it): four additional, independent checks** -- not the P*/sufficient/
minimal/sound bucket system above, a separate MISUSE detector for four
term pairs the outline's own claim checklist (C2, C3, C5, C8) flags as
conflated in the pre-revision draft:

  minimal vs. minimum   -- "minimal" names Definition 5's inclusion-
                            minimality (a reduct: sufficient, no proper
                            subset is); "minimum" names an optimum under
                            an explicit objective (cardinality or cost)
                            and must always be paired with that
                            objective's name. "minimal cardinality"/
                            "minimal cost" (using minimal where the
                            objective-optimal claim minimum names is
                            meant) and a bare "minimum" with no
                            cardinality/cost paired to it are both
                            VIOLATIONS.
  certificate vs summary -- `reduct.sufficiency`'s own success return is
                            a partition-cell COUNT and a uniformity
                            FLAG (verified directly against its source,
                            not assumed) -- not the serialized partition
                            a "certificate" implies. Prose "certificate"
                            outside a code identifier is a VIOLATION
                            unless the same paragraph also says
                            "summary", the pairing this file's own
                            C5 wording (populate_paper.py-adjacent
                            prose) uses to stay accurate about what the
                            field actually contains.
  constructed vs live    -- every domain this artifact reports on is a
                            declared, constructed model (`prereg/`),
                            never a live deployment. "live" describing a
                            deployment/domain/data/process/system is a
                            VIOLATION unless the same paragraph also
                            negates it (the honest shape: "not... live",
                            "never... live", "no live...").
  core vs non-core        -- "redundant" for `candidate_properties -
                            core` is imprecise (redundant relative to
                            WHAT is never stated); "non-core" names the
                            same set exactly. Prose "redundant" outside
                            a code identifier (`redundant_attributes`,
                            `remove_redundant_supersets`, the `redundant`
                            local variable README's own worked example
                            unpacks `compute_core`'s return tuple into)
                            is always a VIOLATION.

Each check strips fenced AND inline code (`` `identifier` ``) before
matching, so a code reference or a worked example's own variable names
are never mistaken for a prose claim -- the same discipline
`_strip_fenced_code` already applies to the bucket system above,
extended here to single backticks specifically because these four
checks care about a WORD (certificate, redundant) that is also a
legitimate Python identifier fragment (`sufficiency_certificate`,
`redundant_attributes`) this checker must not flag.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

DEFAULT_TARGETS = ["paper5-authority-derivation-draft-v0.6.2.md", "README.md"]
OUTPUT_PATH = Path("out/checkers/terminology_lint.json")

CLAIM_TERMS: Dict[str, re.Pattern] = {
    "P*": re.compile(r"P\\?\*"),
    "sufficient": re.compile(r"\bsufficien(?:t|cy)\b", re.IGNORECASE),
    "minimal": re.compile(r"\bminimal(?:ity)?\b", re.IGNORECASE),
    "sound": re.compile(r"\bsound(?:ness)?\b", re.IGNORECASE),
}
STRUCTURAL_TERMS: Dict[str, re.Pattern] = {
    "participating_properties": re.compile(r"participating_properties"),
    "coverage_list": re.compile(r"coverage_list"),
}
BUCKETS = ["historical", "instance-certified", "general-theorem", "core", "reduct"]

_FENCED_CODE = re.compile(r"```.*?```", re.DOTALL)

_NEGATED_BEFORE = re.compile(r"\b(?:not|never|n't|need not|cannot|no longer)\b[\w\s]{0,25}$", re.IGNORECASE)
_HISTORICAL = re.compile(
    r"\bCorrections?\b|\boriginally\b|\bv0\.1\b|\bv0\.2\b|\bnow corrected\b|\bsuperseded\b|\boverclaim(?:ed)?\b"
    r"|\bADR-\d|\ban earlier design\b",
    re.IGNORECASE,
)
_CERTIFICATE = re.compile(
    r"checkers/[A-Za-z0-9_]+\.py|\bCH-A\d{1,2}\b|\[GENERATED:|\bPROOF-STATUS\b|\bcertificate\b|\bcounterexample\b"
)
_GENERAL_THEOREM = re.compile(
    r"\bfor any\b|\bin general\b|\bby construction\b|\bevery reduct\b|\bPawlak\b|\bSkowron\b"
    r"|Proposition 1'|\*\*Definition\s+\d|\biff\b",
    re.IGNORECASE,
)
_CORE = re.compile(r"\bDefinition 6\b|\bthe core\b|\bcore attribute", re.IGNORECASE)
_REDUCT = re.compile(r"\bDefinition 5\b|\bthe (?:unique )?reduct\b|\ba reduct\b", re.IGNORECASE)

# Term-pair misuse (A6 of the commissioned amendment -- module docstring).
_INLINE_CODE = re.compile(r"`[^`\n]+`")
_MINIMAL_MISUSED_FOR_MINIMUM = re.compile(r"\bminimal\b\s+(?:cardinality|cost)\b", re.IGNORECASE)
_BARE_MINIMUM = re.compile(r"\bminimum\b(?!-?\s*(?:cardinality|cost|declared\s+cost))", re.IGNORECASE)
_CERTIFICATE_TERM = re.compile(r"\bcertificates?\b", re.IGNORECASE)
_SUMMARY_TERM = re.compile(r"\bsummary\b", re.IGNORECASE)
_LIVE_DOMAIN = re.compile(r"\blive\b\s+(?:deployment|domain|data|process|system)", re.IGNORECASE)
_NEGATION_ANYWHERE = re.compile(r"\bnot\b|\bnever\b|\bno\b|n't\b|\bwithout\b", re.IGNORECASE)
_REDUNDANT_TERM = re.compile(r"\bredundant\b", re.IGNORECASE)


def _strip_fenced_code(text: str) -> str:
    """Blank fenced code blocks (same-length whitespace, newlines kept)
    so a code sample's own identifiers (e.g. README's 60-second example
    calling `sufficiency(...)`) are never mistaken for a prose claim --
    line numbers into the original text stay accurate."""
    return _FENCED_CODE.sub(lambda m: "".join(c if c == "\n" else " " for c in m.group(0)), text)


def _strip_inline_code(text: str) -> str:
    """Same technique as `_strip_fenced_code`, for single-backtick inline
    code -- the term-pair checks below (`check_term_pairs`) care about
    words (`certificate`, `redundant`) that are also legitimate Python
    identifier fragments (`` `sufficiency_certificate` ``,
    `` `redundant_attributes` ``); blanking preserves line numbers and
    leaves the rest of the paragraph's own prose intact."""
    return _INLINE_CODE.sub(lambda m: "".join(c if c == "\n" else " " for c in m.group(0)), text)


def check_term_pairs(text: str) -> List[Dict[str, Any]]:
    """A6's four term-pair misuse checks, paragraph-scoped like
    `find_occurrences` above but independent of its five-bucket
    classification -- see the module docstring for what each of the four
    checks does and why."""
    stripped = _strip_inline_code(_strip_fenced_code(text))
    spans = _paragraph_spans(stripped)
    violations: List[Dict[str, Any]] = []

    def _line_of(offset: int) -> int:
        return stripped.count("\n", 0, offset) + 1

    for start, end in spans:
        para = stripped[start:end]
        if not para.strip():
            continue
        for m in _MINIMAL_MISUSED_FOR_MINIMUM.finditer(para):
            violations.append({
                "pair": "minimal-vs-minimum", "issue": "minimal used where minimum (an objective optimum) was meant",
                "line": _line_of(start + m.start()), "excerpt": " ".join(para.strip().split())[:220],
            })
        for m in _BARE_MINIMUM.finditer(para):
            violations.append({
                "pair": "minimal-vs-minimum", "issue": "minimum not paired with its objective (cardinality/cost)",
                "line": _line_of(start + m.start()), "excerpt": " ".join(para.strip().split())[:220],
            })
        if _CERTIFICATE_TERM.search(para) and not _SUMMARY_TERM.search(para):
            m = _CERTIFICATE_TERM.search(para)
            violations.append({
                "pair": "certificate-vs-summary", "issue": "certificate claimed without a summary qualifier in the same paragraph",
                "line": _line_of(start + m.start()), "excerpt": " ".join(para.strip().split())[:220],
            })
        for m in _LIVE_DOMAIN.finditer(para):
            if not _NEGATION_ANYWHERE.search(para):
                violations.append({
                    "pair": "constructed-vs-live", "issue": "live deployment/domain/data claimed without negation in the same paragraph",
                    "line": _line_of(start + m.start()), "excerpt": " ".join(para.strip().split())[:220],
                })
        for m in _REDUNDANT_TERM.finditer(para):
            violations.append({
                "pair": "core-vs-non-core", "issue": "redundant used where non-core (candidate_properties - core) was meant",
                "line": _line_of(start + m.start()), "excerpt": " ".join(para.strip().split())[:220],
            })
    return violations


def _paragraph_spans(text: str) -> List[Tuple[int, int]]:
    spans = []
    start = 0
    for m in re.finditer(r"\n[ \t]*\n", text):
        spans.append((start, m.start()))
        start = m.end()
    spans.append((start, len(text)))
    return spans


def classify(paragraph: str, match_start: int) -> str:
    if _NEGATED_BEFORE.search(paragraph[max(0, match_start - 30):match_start]):
        return "general-theorem"
    if _HISTORICAL.search(paragraph):
        return "historical"
    if _CERTIFICATE.search(paragraph):
        return "instance-certified"
    if _GENERAL_THEOREM.search(paragraph):
        return "general-theorem"
    if _CORE.search(paragraph):
        return "core"
    if _REDUCT.search(paragraph):
        return "reduct"
    return "unclassified"


def find_occurrences(text: str) -> List[Dict[str, Any]]:
    """Paragraph-scoped, with one narrow exception: a paragraph that
    itself classifies as unclassified is re-tried against the paragraph
    immediately following it. This covers a caveat placed in the very
    next paragraph rather than repeated inline -- the shape of a
    verbatim-preserved historical quote (Section 1.1's NOVELTY.md fence)
    followed by its own correction note -- without widening to a whole
    section, which would risk one unrelated certificate mention
    masking a genuinely unscoped claim elsewhere in the same section."""
    stripped = _strip_fenced_code(text)
    spans = _paragraph_spans(stripped)
    paras = [stripped[s:e] for s, e in spans]
    occurrences = []
    for i, (start, end) in enumerate(spans):
        para = paras[i]
        if not para.strip():
            continue
        for term, pattern in {**CLAIM_TERMS, **STRUCTURAL_TERMS}.items():
            for m in pattern.finditer(para):
                line_no = stripped.count("\n", 0, start + m.start()) + 1
                bucket = classify(para, m.start())
                if bucket == "unclassified" and i + 1 < len(paras) and paras[i + 1].strip():
                    next_bucket = classify(paras[i + 1], 0)
                    if next_bucket != "unclassified":
                        bucket = next_bucket
                occurrences.append({
                    "term": term,
                    "is_claim_term": term in CLAIM_TERMS,
                    "bucket": bucket,
                    "line": line_no,
                    "excerpt": " ".join(para.strip().split())[:220],
                })
    return occurrences


def lint_file(path: str) -> Dict[str, Any]:
    text = Path(path).read_text()
    occurrences = find_occurrences(text)
    violations = [o for o in occurrences if o["is_claim_term"] and o["bucket"] == "unclassified"]
    counts = {b: 0 for b in BUCKETS + ["unclassified"]}
    for o in occurrences:
        counts[o["bucket"]] += 1
    term_pair_violations = check_term_pairs(text)
    return {
        "path": path,
        "occurrence_count": len(occurrences),
        "classification_counts": counts,
        "violations": violations,
        "term_pair_violations": term_pair_violations,
        "clean": len(violations) == 0 and len(term_pair_violations) == 0,
    }


def lint(paths: List[str] = None) -> Dict[str, Any]:
    paths = paths if paths is not None else DEFAULT_TARGETS
    results = [lint_file(p) for p in paths if Path(p).exists()]
    return {
        "files": results,
        "total_occurrences": sum(r["occurrence_count"] for r in results),
        "all_clean": all(r["clean"] for r in results),
    }


def main() -> None:
    result = lint()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["all_clean"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
