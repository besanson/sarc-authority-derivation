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
Milestone E, Step 6 (`prereg/v6.1-authoritybench-amendment.md`, tag
`prereg-p5-v6.1`, "Timed reproduction"): a canonical reproduction timed
from a genuinely bare clone -- `git clone` of this repository alone (not
the pinned siblings, which `bootstrap.sh` clones as its own timed phase)
through `bash bootstrap.sh && make release-check` finishing with `ALL
CHECKS PASS`, wall-clock, in a fresh temporary directory this script
deletes when it finishes.

Target "about five minutes" (task brief's own E4 language) is
descriptive, not a pass/fail gate -- registered here BEFORE this script
was ever run: `bootstrap.sh` clones three pinned engine siblings plus
`sarc-suite-one-pass` itself and then runs THAT repo's own `make
release-check` as its own imported-baseline verification step (`bash
"$ONE_PASS_DIR/bootstrap.sh"` and `make release-check` inside it,
`bootstrap.sh`'s own lines 82-94), so the real number is reported
honestly whatever it is, not massaged toward the five-minute figure.

Writes `out/reproduction_timing.json` (a sidecar `reproducibility_
report.py` reads and folds into `out/reproducibility-report.json`'s own
`reproduction_timing` field at that report's next regeneration -- this
script does not write into that report directly, since regenerating it
is `reproducibility_report.py`'s own job, called via `make
release-check`'s existing last step, not duplicated here).

**A real gotcha, found by running this exact script, not hypothesized in
advance**: `bootstrap.sh` (both this repo's own and, delegated,
`sarc-suite-one-pass`'s) installs the three engine siblings with `pip
install -e` -- EDITABLE installs, which record an absolute path to the
source tree in this (shared, non-virtualenv-isolated) environment's
global site-packages metadata, not a copy of the code. Run inside the
disposable temp clone this script creates, that editable install points
at the TEMP clone's own sibling directories; when the temp directory is
then deleted, every subsequent `import sarc_governance` (etc.) in the
PERMANENT working copy breaks with `ModuleNotFoundError`, because pip's
editable-install metadata is process-global, not scoped to any one
checkout. First observed directly: after this script's first real run,
`pip show sarc-governance` reported `Editable project location:
/tmp/sarc-p5-timed-repro-.../sarc-governance` -- a directory this
script's own cleanup had already removed -- and the permanent working
copy's own `make release-check` failed at test collection with exactly
that `ModuleNotFoundError`, not a hypothetical risk. Fixed by re-running
the PERMANENT repo's own `bootstrap.sh` (`_restore_host_environment`
below) unconditionally in `finally`, before the temp directory is
removed -- idempotent by `bootstrap.sh`'s own design (its own docstring:
"safe to re-run"), and cheap relative to the temp clone's own bootstrap
phase since every sibling is already checked out and pinned at
`/home/user`, so this restore step is not itself included in
`bootstrap_seconds`/`total_seconds` (it repairs host state; it is not
part of the reproduction being timed)."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict

OUTPUT_PATH = Path("out/reproduction_timing.json")
CLONE_URL = "https://github.com/besanson/sarc-authority-derivation"
PERMANENT_REPO_ROOT = Path(__file__).resolve().parent


def _restore_host_environment() -> bool:
    """Re-run THIS (permanent) repo's own bootstrap.sh so the engine
    siblings' editable pip installs point back at `/home/user/*`, not
    whatever temp clone this script's own timed run last bootstrapped.
    Returns whether the restore itself succeeded (checked, not
    assumed) -- a failure here is reported, not silently swallowed,
    since it would leave the host environment broken for every other
    script in this repo, not just this one."""
    print("=== Step 6: restoring host environment (re-running the permanent repo's own bootstrap.sh) ===", flush=True)
    rc = subprocess.run(["bash", "bootstrap.sh"], cwd=str(PERMANENT_REPO_ROOT)).returncode
    if rc != 0:
        print(f"=== Step 6: WARNING -- host environment restore FAILED (bootstrap.sh exit code {rc}) ===", flush=True)
    return rc == 0


def run() -> Dict[str, Any]:
    tmp_root = Path(tempfile.mkdtemp(prefix="sarc-p5-timed-repro-"))
    clone_dir = tmp_root / "sarc-authority-derivation"
    result: Dict[str, Any] = {"clone_url": CLONE_URL, "success": False}
    try:
        print(f"=== Step 6: git clone {CLONE_URL} -> {clone_dir} ===", flush=True)
        t0 = time.perf_counter()
        clone_rc = subprocess.run(["git", "clone", "--quiet", CLONE_URL, str(clone_dir)]).returncode
        result["clone_seconds"] = time.perf_counter() - t0
        if clone_rc != 0:
            result["failed_at"] = "git clone"
            return result

        result["cloned_commit_sha"] = subprocess.run(
            ["git", "-C", str(clone_dir), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()

        print("=== Step 6: bash bootstrap.sh ===", flush=True)
        t0 = time.perf_counter()
        bootstrap_rc = subprocess.run(["bash", "bootstrap.sh"], cwd=str(clone_dir)).returncode
        result["bootstrap_seconds"] = time.perf_counter() - t0
        if bootstrap_rc != 0:
            result["failed_at"] = "bootstrap.sh"
            return result

        print("=== Step 6: make release-check ===", flush=True)
        t0 = time.perf_counter()
        release_check_rc = subprocess.run(["make", "release-check"], cwd=str(clone_dir)).returncode
        result["release_check_seconds"] = time.perf_counter() - t0
        if release_check_rc != 0:
            result["failed_at"] = "make release-check"
            return result

        result["total_seconds"] = result["clone_seconds"] + result["bootstrap_seconds"] + result["release_check_seconds"]
        result["success"] = True
        return result
    finally:
        result["host_environment_restored"] = _restore_host_environment()
        shutil.rmtree(tmp_root, ignore_errors=True)


def main() -> None:
    result = run()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
