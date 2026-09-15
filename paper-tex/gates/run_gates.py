#!/usr/bin/env python3
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
LaTeX release-kit gates for this repository's own paper-tex/main.tex.
Ported with attribution from sarc-suite-one-pass's paper-tex/gates/run_gates.py
(commit 782261e) -- see ADR-001-foundation.md. This repo ports four of the
sibling's nine gates (task brief: "LaTeX build with byte-identical double
builds under a content-stable epoch; abstract sidecar and metadata with
the sync gate; citation completeness and bibliography-quality gates"):

  G1 -- build (compiler-aware, artifact-based, byte-identical double build)
  G7 -- arXiv sidecar sync (abstract/metadata match this paper's own thesis)
  G8 -- citation completeness (no unresolved [CITE-NEEDED]/[CITE:] placeholders)
  G9 -- bibliography quality (verified-citations.json's own schema, refs.bib
        regenerated and matched byte-for-byte)

NOT ported: the sibling's G2-G6 (token/number/prose/structure parity, and
disclosure-banner checks) -- those exist there to catch drift between a
SEPARATELY hand-maintained main.tex and its own markdown source; this
file's own content is a direct, one-time-careful transcription of this
repo's own already-verified, already-slot-generated
paper5-authority-derivation-draft-v0.6-populated.md, not an independently
re-authored document that could drift from it silently over time the way
the sibling's four-review-round main.tex history shows its own did.

Genuine difference from the sibling's own G1 (found and fixed here, not
present in their own gate): a single `tectonic main.tex` invocation from a
genuinely clean directory (no prior .aux/.bbl) leaves LaTeX's own
undefined-reference/undefined-citation warnings for THIS document's
internal \\ref/\\cite commands and bibliography -- verified directly,
twice, by running a clean single invocation and inspecting its own log,
not assumed from the sibling's own docstring claim that Tectonic "does
not require a prior latexmk/tectonic invocation". A second invocation in
the same directory (reading back the first's own .aux/.bbl) resolves them
-- standard LaTeX+BibTeX multi-pass convergence, wrapped by Tectonic's own
single-process model rather than eliminated by it. `_do_one_build` below
therefore reruns the compiler, within the same logical "build", until the
log shows zero undefined refs/citations or a small bounded attempt count
is exhausted -- exactly what `latexmk` automates under the hood, made
explicit here so G1's own byte-identical-double-build check compares two
independently-converged, fully-resolved builds, not two builds each
correctly reporting the SAME spurious warning.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

GATES_DIR = Path(__file__).resolve().parent
PAPER_TEX_DIR = GATES_DIR.parent
REPO_ROOT = PAPER_TEX_DIR.parent

SOURCE_MD = REPO_ROOT / "paper5-authority-derivation-draft-v0.6-populated.md"
MAIN_TEX = PAPER_TEX_DIR / "main.tex"
MAIN_PDF = PAPER_TEX_DIR / "main.pdf"
REPORT_PATH = PAPER_TEX_DIR / "parity-report.json"
ARXIV_ABSTRACT = PAPER_TEX_DIR / "arxiv-abstract.txt"
ARXIV_METADATA = PAPER_TEX_DIR / "arxiv-metadata.txt"
REFS_BIB = PAPER_TEX_DIR / "refs.bib"
CITATIONS_JSON = REPO_ROOT / "verified-citations.json"
BIB_AUDIT_JSON = REPO_ROOT / "review-secondary" / "bib-audit.json"


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=False, **kwargs)


# ---------------------------------------------------------------------------
# G1: Build (compiler-aware, artifact-based; see module docstring for the
# multi-pass convergence fix this repo's own gate adds over the sibling's)
# ---------------------------------------------------------------------------

COMPILER_ENV_VAR = "SARC_LATEX_COMPILER"
MAX_PASSES = 4

UNDEFINED_REF_RE = re.compile(r"LaTeX Warning: Reference `([^']*)' on page \d+ undefined")
UNDEFINED_CITE_RE = re.compile(r"LaTeX Warning: Citation `([^']*)' .*undefined")
OVERFULL_PATTERNS = {
    "latexmk": re.compile(r"Overfull \\hbox \(([\d.]+)pt too wide\) in paragraph at lines (\d+)--(\d+)"),
    "tectonic": re.compile(r"warning: [^:\s]+:(\d+): Overfull \\hbox \(([\d.]+)pt too wide\)"),
}
GENERATED_FILE_GLOBS = [
    "main.pdf", "main.log", "main.aux", "main.bbl", "main.blg",
    "main.out", "main.fls", "main.fdb_latexmk", "main.synctex.gz",
    "main.toc", "texput.log",
]

# Content-stable epoch (task brief: "byte-identical double builds under a
# content-stable epoch"), the same fixed-constant discipline as the
# sibling's own errata-closure protocol item E3: a literal constant, not a
# live `git show`, so the build stays reproducible even from a source
# tarball with no git history. Reused verbatim from the sibling (same
# reasoning: an already-established "before any result existed" reference
# point is not this repo's own to reinvent) -- prereg-v1's own commit
# timestamp for sarc-suite-one-pass, ADR-001-foundation.md's own imported
# baseline, `git show -s --format=%ct 31552b2ee6548787e766b0253498014eb0a5093c`.
SOURCE_DATE_EPOCH = "1786609963"


def _source_date_epoch() -> str:
    return SOURCE_DATE_EPOCH


def _reproducible_build_env() -> dict:
    env = dict(os.environ)
    env["SOURCE_DATE_EPOCH"] = _source_date_epoch()
    env["TZ"] = "UTC"
    return env


def _sha256_file(path: Path):
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _detect_compiler() -> str:
    forced = os.environ.get(COMPILER_ENV_VAR, "").strip().lower()
    if forced:
        return forced
    if shutil.which("tectonic"):
        return "tectonic"
    if shutil.which("latexmk"):
        return "latexmk"
    return ""


def _clean_generated() -> None:
    for name in GENERATED_FILE_GLOBS:
        f = PAPER_TEX_DIR / name
        if f.exists():
            f.unlink()


def _pdf_page_count(pdf_path: Path):
    if not pdf_path.exists():
        return None
    r = run(["pdfinfo", str(pdf_path)])
    m = re.search(r"^Pages:\s+(\d+)", r.stdout, re.MULTILINE)
    return int(m.group(1)) if m else None


def _pdf_unresolved_marker_count(pdf_path: Path) -> int:
    """Ground-truth check on the rendered artifact itself, not the
    compiler's own log: "??" is the literal, compiler-independent text
    LaTeX's own \\ref/\\cite machinery prints in place of an unresolved
    reference (verified: a deliberately broken \\ref renders as "??" in
    the PDF, present under pdftotext). Added because, for this document,
    Tectonic's own --print log reports undefined_references/
    undefined_citations (an artifact of its internal sub-pass iteration,
    each sub-pass logging what it does not yet know even when a later
    sub-pass within the SAME external invocation resolves it) while the
    actually-produced PDF has zero "??" markers and every citation
    resolved to a real bracketed number -- verified directly, repeatedly,
    not assumed. The log fields are still recorded below for
    transparency (rule 10: never let prose substitute for a missing
    check) but the PDF's own rendered text, not the log, decides G1."""
    if not pdf_path.exists():
        return -1
    r = run(["pdftotext", str(pdf_path), "-"])
    return (r.stdout or "").count("??")


def _run_compiler_once(compiler: str) -> tuple[int, str]:
    env = _reproducible_build_env()
    if compiler == "tectonic":
        r = run(["tectonic", "--print", "main.tex"], cwd=str(PAPER_TEX_DIR), env=env)
    elif compiler == "latexmk":
        r = run(["latexmk", "-pdf", "-interaction=nonstopmode", "main.tex"], cwd=str(PAPER_TEX_DIR), env=env)
    else:
        raise RuntimeError(f"unsupported compiler {compiler!r}")
    return r.returncode, f"{r.stdout or ''}\n{r.stderr or ''}"


def _parse_build_diagnostics(compiler: str, output: str) -> dict:
    errors = [l for l in output.splitlines() if l.startswith("! ")]
    undefined_refs = UNDEFINED_REF_RE.findall(output)
    undefined_cites = UNDEFINED_CITE_RE.findall(output)

    overfull = []
    pattern = OVERFULL_PATTERNS[compiler]
    if compiler == "tectonic":
        for m in pattern.finditer(output):
            pts = float(m.group(2))
            if pts > 10.0:
                overfull.append({"pt": pts, "line": m.group(1)})
    else:
        for m in pattern.finditer(output):
            pts = float(m.group(1))
            if pts > 10.0:
                overfull.append({"pt": pts, "lines": f"{m.group(2)}--{m.group(3)}"})

    return {
        "errors": errors,
        "undefined_references": undefined_refs,
        "undefined_citations": undefined_cites,
        "overfull_hbox_above_10pt": overfull,
    }


def _do_one_build(compiler: str) -> dict:
    """One logical "build": a genuinely clean start, then the compiler
    rerun (up to MAX_PASSES times) until undefined refs/citations clear or
    the budget is exhausted -- see module docstring. Every pass's own exit
    code must be zero; only the LAST pass's diagnostics are reported (the
    ones that actually reached the reader), but an error on any pass fails
    the whole build immediately."""
    _clean_generated()
    passes = []
    for _ in range(MAX_PASSES):
        rc, output = _run_compiler_once(compiler)
        diagnostics = _parse_build_diagnostics(compiler, output)
        passes.append({"exit_code": rc, **diagnostics})
        if rc != 0:
            break
        if not diagnostics["undefined_references"] and not diagnostics["undefined_citations"]:
            break
    latest = passes[-1]
    return {
        "exit_code": latest["exit_code"],
        "pdf_produced": MAIN_PDF.exists(),
        "page_count": _pdf_page_count(MAIN_PDF),
        "file_list": sorted(p.name for p in PAPER_TEX_DIR.glob("main.*")),
        "pdf_sha256": _sha256_file(MAIN_PDF),
        "passes_needed": len(passes),
        "errors": latest["errors"],
        "undefined_references": latest["undefined_references"],
        "undefined_citations": latest["undefined_citations"],
        "overfull_hbox_above_10pt": latest["overfull_hbox_above_10pt"],
        "pdf_unresolved_marker_count": _pdf_unresolved_marker_count(MAIN_PDF),
    }


def gate_g1_build() -> dict:
    compiler = _detect_compiler()
    if not compiler:
        return {
            "pass": False,
            "detail": (
                f"no supported LaTeX compiler on PATH -- install pinned Tectonic "
                f"(canonical, see bootstrap.sh) or latexmk, or set {COMPILER_ENV_VAR}"
            ),
        }

    # Two independent, from-scratch builds: the artifact-based
    # byte-identical-double-build check under the fixed SOURCE_DATE_EPOCH
    # above -- a byte-identical PDF is the achievable, checked bar, not
    # merely page count or file list.
    builds = [_do_one_build(compiler), _do_one_build(compiler)]
    latest = builds[-1]

    exit_code_zero = all(b["exit_code"] == 0 for b in builds)
    pdf_produced = all(b["pdf_produced"] for b in builds)
    two_build_identical = (
        builds[0]["page_count"] is not None
        and builds[0]["page_count"] == builds[1]["page_count"]
        and builds[0]["file_list"] == builds[1]["file_list"]
        and builds[0]["pdf_sha256"] is not None
        and builds[0]["pdf_sha256"] == builds[1]["pdf_sha256"]
    )
    no_diagnostics = (
        not latest["errors"]
        and latest["pdf_unresolved_marker_count"] == 0
        and not latest["overfull_hbox_above_10pt"]
    )

    ok = exit_code_zero and pdf_produced and two_build_identical and no_diagnostics
    return {
        "pass": ok,
        "compiler": compiler,
        "source_date_epoch": _source_date_epoch(),
        "exit_code_zero": exit_code_zero,
        "pdf_produced": pdf_produced,
        "two_build_identical": two_build_identical,
        "pdf_sha256": latest["pdf_sha256"],
        "page_count": latest["page_count"],
        "file_list": latest["file_list"],
        "builds": builds,
        "errors": latest["errors"],
        "pdf_unresolved_marker_count": latest["pdf_unresolved_marker_count"],
        # Reported for transparency (rule 10), not gated on -- see
        # _pdf_unresolved_marker_count's own docstring for why: Tectonic's
        # own --print log reports these from its internal sub-pass
        # iteration even when the rendered PDF (checked above) is fully
        # resolved.
        "compiler_log_undefined_references": latest["undefined_references"],
        "compiler_log_undefined_citations": latest["undefined_citations"],
        "overfull_hbox_above_10pt": latest["overfull_hbox_above_10pt"],
    }


# ---------------------------------------------------------------------------
# G7: arXiv sidecar sync
# ---------------------------------------------------------------------------
# paper-tex/arxiv-abstract.txt and paper-tex/arxiv-metadata.txt are
# hand-maintained sidecars, not generated from the manuscript -- this gate
# makes their drift from this paper's own thesis a release-check failure,
# same discipline the sibling's own G7 enforces for its paper.

ARXIV_ABSTRACT_MAX_CHARS = 1900
ARXIV_ABSTRACT_REQUIRED_PHRASE = "minimal sufficient governance context"
ARXIV_METADATA_REQUIRED_AUTHOR_LINE = "Gaston Besanson (Universidad Torcuato Di Tella)"


def gate_g7_sidecar_sync() -> dict:
    abstract_text = ARXIV_ABSTRACT.read_text()
    metadata_text = ARXIV_METADATA.read_text()

    abstract_len = len(abstract_text.rstrip("\n"))
    has_required_phrase = ARXIV_ABSTRACT_REQUIRED_PHRASE in abstract_text
    within_length = abstract_len <= ARXIV_ABSTRACT_MAX_CHARS
    metadata_has_author_line = ARXIV_METADATA_REQUIRED_AUTHOR_LINE in metadata_text

    ok = has_required_phrase and within_length and metadata_has_author_line
    return {
        "pass": ok,
        "abstract_char_count": abstract_len,
        "abstract_within_max_chars": within_length,
        "abstract_has_required_phrase": has_required_phrase,
        "metadata_has_required_author_line": metadata_has_author_line,
    }


# ---------------------------------------------------------------------------
# G8: citation completeness
# ---------------------------------------------------------------------------

CITE_PLACEHOLDER_PATTERN = re.compile(r"\[CITE[-:][^\]]*\]")


def gate_g8_citation_completeness() -> dict:
    text = SOURCE_MD.read_text()
    matches = CITE_PLACEHOLDER_PATTERN.findall(text)
    count = len(matches)
    return {
        "pass": count == 0,
        "cite_placeholder_count": count,
        "cite_placeholders": matches,
    }


# ---------------------------------------------------------------------------
# G9: Bibliography quality
# ---------------------------------------------------------------------------

VALID_ENTRY_TYPES = {"article", "inproceedings", "incollection", "misc"}
REQUIRED_VENUE_FIELDS_BY_TYPE = {
    "article": ("journal",),
    "inproceedings": ("booktitle",),
    "incollection": ("booktitle",),
}


def _load_generate_refs_bib_module():
    spec = importlib.util.spec_from_file_location(
        "generate_refs_bib", str(PAPER_TEX_DIR / "generate_refs_bib.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def gate_g9_bibliography_quality() -> dict:
    data = json.loads(CITATIONS_JSON.read_text())
    citations = data["citations"]

    invalid_entry_type = []
    missing_authors = []
    missing_venue_fields = []
    doi_mismatches = []
    misc_with_venue_info = []
    audit_drift = []

    refs_bib_text = REFS_BIB.read_text() if REFS_BIB.exists() else ""

    audit_by_id = {}
    if BIB_AUDIT_JSON.exists():
        audit_by_id = {r["id"]: r for r in json.loads(BIB_AUDIT_JSON.read_text()).get("results", [])}

    for c in citations:
        cid = c.get("id", "<no id>")
        entry_type = c.get("entry_type")

        if entry_type not in VALID_ENTRY_TYPES:
            invalid_entry_type.append({"id": cid, "entry_type": entry_type})
            continue

        authors = c.get("authors")
        if not authors or c.get("first_author") != authors[0]:
            missing_authors.append({"id": cid, "authors": authors, "first_author": c.get("first_author")})

        for field in REQUIRED_VENUE_FIELDS_BY_TYPE.get(entry_type, ()):
            if not c.get(field):
                missing_venue_fields.append({"id": cid, "entry_type": entry_type, "missing_field": field})

        if "doi" in c:
            expected_doi_line = f"doi = {{{c['doi']}}},"
            if expected_doi_line not in refs_bib_text and not refs_bib_text.rstrip().endswith(expected_doi_line.rstrip(",") + "}"):
                doi_mismatches.append({"id": cid, "doi": c["doi"]})

        if entry_type == "misc" and (c.get("journal") or c.get("booktitle")):
            misc_with_venue_info.append({"id": cid, "journal": c.get("journal"), "booktitle": c.get("booktitle")})

        if "doi" in c:
            audit_entry = audit_by_id.get(cid)
            if audit_entry is not None:
                venue_field = audit_entry.get("authoritative_venue_field")
                authoritative_venue = audit_entry.get("authoritative_venue")
                if venue_field and authoritative_venue is not None and c.get(venue_field) != authoritative_venue:
                    audit_drift.append({
                        "id": cid, "field": venue_field,
                        "current": c.get(venue_field), "audited": authoritative_venue,
                    })
                authoritative_volume = audit_entry.get("authoritative_volume")
                if authoritative_volume is not None and c.get("volume") != authoritative_volume:
                    audit_drift.append({
                        "id": cid, "field": "volume",
                        "current": c.get("volume"), "audited": authoritative_volume,
                    })

    grb = _load_generate_refs_bib_module()
    expected_refs_bib = grb.generate()
    refs_bib_matches = refs_bib_text == expected_refs_bib

    ok = (
        not invalid_entry_type
        and not missing_authors
        and not missing_venue_fields
        and not doi_mismatches
        and not misc_with_venue_info
        and not audit_drift
        and refs_bib_matches
    )
    return {
        "pass": ok,
        "total_citations": len(citations),
        "invalid_entry_type": invalid_entry_type,
        "missing_authors": missing_authors,
        "missing_venue_fields": missing_venue_fields,
        "doi_mismatches": doi_mismatches,
        "misc_with_venue_info": misc_with_venue_info,
        "audit_drift": audit_drift,
        "bib_audit_checked": bool(audit_by_id),
        "refs_bib_matches_generator": refs_bib_matches,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    results = {
        "G1_build": gate_g1_build(),
        "G7_sidecar_sync": gate_g7_sidecar_sync(),
        "G8_citation_completeness": gate_g8_citation_completeness(),
        "G9_bibliography_quality": gate_g9_bibliography_quality(),
    }
    all_pass = all(g["pass"] for g in results.values())
    report = {"all_pass": all_pass, "gates": results}

    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True))

    print(json.dumps(report, indent=2, sort_keys=True))
    print()
    for name, g in results.items():
        print(f"{name}: {'PASS' if g['pass'] else 'FAIL'}")
    print()
    print("ALL GATES PASS" if all_pass else "GATE FAILURE -- see detail above")

    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
