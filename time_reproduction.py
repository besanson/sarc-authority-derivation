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

**Repair-3 addition (tooling, not a registered result -- no prereg
needed)**: this script also accepts an optional `make` target argument,
`python3 time_reproduction.py quick-reproduce`, to time `git clone` +
`bootstrap.sh` + `make quick-reproduce` instead of `make release-check`
-- the exact same clone+bootstrap+restore harness, so the two figures
are measured under identical bare-clone conditions and are genuinely
comparable side by side, not one with-clone number set against one
without. `make quick-reproduce` is release-check's own recipe minus the
mutation-testing gate (see Makefile's comment on that target): mutation
is release-check's dominant cost, so this reports the number a
contributor doing a fast local check, not a release, actually wants.
Writes `out/reproduction_timing_quick.json` in that mode (folded into
`out/reproducibility-report.json`'s own `quick_reproduce_timing` field,
alongside `reproduction_timing`). No argument defaults to
`release-check`, preserving the original Step 6 invocation and output
path unchanged.

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

OUTPUT_PATHS = {
    "release-check": Path("out/reproduction_timing.json"),
    "quick-reproduce": Path("out/reproduction_timing_quick.json"),
}
STEP_KEYS = {
    "release-check": "release_check_seconds",
    "quick-reproduce": "quick_reproduce_seconds",
}
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


def run(make_target: str = "release-check") -> Dict[str, Any]:
    """Time `git clone` + `bootstrap.sh` + `make <make_target>` end to end
    in a disposable temp clone. `make_target` is "release-check" (Step
    6's original figure, mutation gate included) or "quick-reproduce"
    (the repair-3 addition: the same recipe minus the mutation gate).
    Both share this one clone+bootstrap+restore harness so the two
    numbers are measured under identical bare-clone conditions."""
    step_key = STEP_KEYS[make_target]
    tmp_root = Path(tempfile.mkdtemp(prefix="sarc-p5-timed-repro-"))
    clone_dir = tmp_root / "sarc-authority-derivation"
    result: Dict[str, Any] = {"clone_url": CLONE_URL, "make_target": make_target, "success": False}
    try:
        print(f"=== Timed reproduction ({make_target}): git clone {CLONE_URL} -> {clone_dir} ===", flush=True)
        t0 = time.perf_counter()
        clone_rc = subprocess.run(["git", "clone", "--quiet", CLONE_URL, str(clone_dir)]).returncode
        result["clone_seconds"] = time.perf_counter() - t0
        if clone_rc != 0:
            result["failed_at"] = "git clone"
            return result

        result["cloned_commit_sha"] = subprocess.run(
            ["git", "-C", str(clone_dir), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()

        print(f"=== Timed reproduction ({make_target}): bash bootstrap.sh ===", flush=True)
        t0 = time.perf_counter()
        bootstrap_rc = subprocess.run(["bash", "bootstrap.sh"], cwd=str(clone_dir)).returncode
        result["bootstrap_seconds"] = time.perf_counter() - t0
        if bootstrap_rc != 0:
            result["failed_at"] = "bootstrap.sh"
            return result

        print(f"=== Timed reproduction ({make_target}): make {make_target} ===", flush=True)
        t0 = time.perf_counter()
        make_rc = subprocess.run(["make", make_target], cwd=str(clone_dir)).returncode
        result[step_key] = time.perf_counter() - t0
        if make_rc != 0:
            result["failed_at"] = f"make {make_target}"
            return result

        result["total_seconds"] = result["clone_seconds"] + result["bootstrap_seconds"] + result[step_key]
        result["success"] = True
        return result
    finally:
        result["host_environment_restored"] = _restore_host_environment()
        shutil.rmtree(tmp_root, ignore_errors=True)


def main() -> None:
    make_target = sys.argv[1] if len(sys.argv) > 1 else "release-check"
    if make_target not in STEP_KEYS:
        print(f"usage: time_reproduction.py [{'|'.join(STEP_KEYS)}]", file=sys.stderr)
        sys.exit(2)
    result = run(make_target)
    output_path = OUTPUT_PATHS[make_target]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
