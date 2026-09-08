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
Reproducibility report (Milestone A3, review-secondary/improvement-
plan-9.5-2026-09-06.pdf's reimplemented findings): `make release-check`'s
own final artifact, out/reproducibility-report.json -- one self-contained
snapshot of what this run actually checked.

Placement matters: the Makefile runs this script LAST in `make
release-check`, after the pytest run, the formal double-run + diff, and
the mutation gate have all already either passed or aborted the whole
`make` invocation (Make's own documented semantics: any nonzero recipe
line stops the target). `tests_passed`, `formal_checks_passed`, and
`paper_freshness_status` below are therefore correctly inferred from
reaching this point, not re-run a second time -- but every field that
does NOT follow from mere pipeline position (dependency/sibling shas,
the mutation score, artifact hashes, the individual formal-checker
booleans in `formal_check_summary`) is independently re-read or
re-hashed here, not asserted. This script must never be treated as a
standalone freshness/test oracle outside that exact release-check
position.

"Formal checks passed" means every checker with genuine correctness
semantics (soundness/minimality of the witness search, exact-recovery
match, single-use holds, the core/reduct identity, PROOF-STATUS and
terminology-lint cleanliness) came back true -- NOT that every
registered hypothesis came back SUPPORTED. CH-A9's registered NOT
SUPPORTED result is an honest scientific finding, not a checker failure,
and must never make this report look red.
"""
from __future__ import annotations

import importlib.metadata
import json
import platform
import subprocess
from pathlib import Path
from typing import Any, Dict

from checkers._provenance import head_sha
from checkers.proof_status_lint import lint as _lint_proof_status
from checkers.terminology_lint import lint as _lint_terminology
from checkers.typed_numerals_lint import run as _lint_typed_numerals
from mutation_check import run as _mutation_run

OUTPUT_PATH = Path("out/reproducibility-report.json")
ENGINES_LOCK = Path("engines.lock")

DEPENDENCY_NAMES = ["pytest", "hypothesis", "mutmut", "jsonschema", "scipy", "python-sat", "pyyaml"]

ARTIFACT_PATHS = [
    "paper5-authority-derivation-draft-v0.4-populated.md",
    "appendix-a-proofs.md",
    "NOVELTY.md",
    "review-secondary/external-research-review-2026-09-06.pdf",
]


def _dependency_versions() -> Dict[str, str]:
    versions = {}
    for name in DEPENDENCY_NAMES:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return versions


def _parse_engines_lock(path: Path) -> Dict[str, Dict[str, str]]:
    pins = {}
    for line in path.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        name, url, sha = line.split()
        pins[name] = {"url": url, "pinned_sha": sha}
    return pins


def _sibling_shas() -> Dict[str, Dict[str, Any]]:
    repo_root = Path(__file__).resolve().parent
    parent_dir = repo_root.parent
    pins = _parse_engines_lock(repo_root / ENGINES_LOCK)
    result = {}
    for name, pin in pins.items():
        sibling_dir = parent_dir / name
        entry = {"pinned_sha": pin["pinned_sha"], "url": pin["url"]}
        if (sibling_dir / ".git").exists():
            actual = subprocess.run(
                ["git", "-C", str(sibling_dir), "rev-parse", "HEAD"],
                capture_output=True, text=True, check=True,
            ).stdout.strip()
            entry["on_disk_sha"] = actual
            entry["on_disk_matches_pinned"] = actual == pin["pinned_sha"]
        else:
            entry["on_disk_sha"] = None
            entry["on_disk_matches_pinned"] = None
        result[name] = entry
    return result


def _artifact_hashes() -> Dict[str, str]:
    import hashlib
    hashes = {}
    for rel_path in ARTIFACT_PATHS:
        p = Path(rel_path)
        if p.exists():
            hashes[rel_path] = hashlib.sha256(p.read_bytes()).hexdigest()
    return hashes


def _pytest_junit_summary(junit_path: Path) -> Dict[str, Any]:
    if not junit_path.exists():
        return {"available": False}
    import xml.etree.ElementTree as ET
    root = ET.parse(junit_path).getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    attrib = suite.attrib
    failures = int(attrib.get("failures", 0))
    errors = int(attrib.get("errors", 0))
    return {
        "available": True,
        "tests": int(attrib.get("tests", 0)),
        "failures": failures,
        "errors": errors,
        "skipped": int(attrib.get("skipped", 0)),
        "all_passed": failures == 0 and errors == 0,
    }


def _formal_check_summary() -> Dict[str, Any]:
    def _load(name: str) -> Dict[str, Any]:
        p = Path(f"out/checkers/{name}.json")
        return json.loads(p.read_text()) if p.exists() else {}

    pcheck = _load("participation_check")
    pcheck_v2 = _load("participation_check_v2")
    ptcheck = _load("pairtest_check")
    ptcheck_v2 = _load("pairtest_check_v2")
    gcheck = _load("grant_check")
    reduct = _load("reduct_check")
    proof_status = _lint_proof_status()
    terminology = _lint_terminology()
    typed_numerals = _lint_typed_numerals()

    summary = {
        "v1_sound_and_minimal": pcheck.get("sound_and_minimal"),
        "v2_sound_and_minimal": pcheck_v2.get("sound_and_minimal"),
        "v1_pairtest_exact_recovery": ptcheck.get("ch_a2_exact_recovery"),
        "v2_pairtest_ch_a6_exact_recovery": ptcheck_v2.get("ch_a6_exact_recovery"),
        "grant_single_use_holds_exhaustively": gcheck.get("single_use_holds_exhaustively"),
        "reduct_identity_holds": reduct.get("proposition_1_prime_claim_1_identity_holds"),
        "reduct_core_subset_of_every_reduct": reduct.get("proposition_1_prime_claim_2_core_subset_of_every_reduct"),
        "proof_status_lint_clean": proof_status.get("all_clean"),
        "terminology_lint_clean": terminology.get("all_clean"),
        "typed_numerals_lint_clean": typed_numerals.get("clean"),
    }
    summary["all_true"] = all(v is True for v in summary.values())
    return summary


def build_report() -> Dict[str, Any]:
    junit = _pytest_junit_summary(Path("out/pytest-junit.xml"))
    formal_summary = _formal_check_summary()
    mutation = _mutation_run()

    return {
        "head_sha": head_sha(),
        "python_version": platform.python_version(),
        "os": platform.platform(),
        "dependency_versions": _dependency_versions(),
        "sibling_shas": _sibling_shas(),
        "tests": junit,
        "tests_passed": bool(junit.get("all_passed")),
        "formal_check_summary": formal_summary,
        "formal_checks_passed": bool(formal_summary.get("all_true")),
        "mutation": mutation,
        "artifact_hashes": _artifact_hashes(),
        "paper_freshness_status": "verified byte-identical earlier in this same "
                                   "`make release-check` run (populated-draft "
                                   "freshness gate) -- see note in this module's docstring",
        "note": (
            "tests_passed/formal_checks_passed/paper_freshness_status reflect "
            "gates that already ran and either passed or aborted `make "
            "release-check` before this report was written (Make's own "
            "abort-on-nonzero semantics), not a second independent run "
            "performed by this script."
        ),
    }


def main() -> None:
    report = build_report()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True))
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
