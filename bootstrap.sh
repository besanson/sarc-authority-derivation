#!/usr/bin/env bash
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
#
# Ported with attribution from sarc-suite-one-pass's bootstrap.sh (commit
# 782261e) -- see ADR-001. Adapted: this repo's engines.lock pins
# sarc-suite-one-pass itself (as a read-only imported baseline) alongside
# the three engines, and this script verifies that baseline's own
# release-check passes before declaring bootstrap complete (task brief
# Phase 0: "it must pass before you build anything").
#
# Clone sarc-suite-one-pass + the three governance engines as pinned
# siblings of this repo (engines.lock), delegate engine installs and the
# LaTeX toolchain to sarc-suite-one-pass's own bootstrap.sh, install this
# repo's own toolchain, and verify the imported baseline. Idempotent: safe
# to re-run.
#
# SEED = 26313 (inherited baseline seed; this repo's own seeds are
# registered separately in prereg/seeds.json, Phase 1)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR"
PARENT_DIR="$(dirname "$REPO_ROOT")"
LOCKFILE="$REPO_ROOT/engines.lock"

# Preflight, before cloning anything: every external executable this
# repo's own paper-tex/gates/run_gates.py (pdfinfo, pdftotext) and the
# pinned sarc-suite-one-pass sibling's own release-check (pdftotext,
# pandoc) need. The first independent reproduction attempt
# (besanson/sarc-authority-derivation#1) found both pandoc and pdftotext
# missing on macOS, discovered late -- a FileNotFoundError five tests
# into the delegated sibling release-check this script runs near the
# bottom, not a clear message up front (REPRODUCTION.md's own
# Corrections note). Do not silently skip the baseline: a missing tool
# here must stop this script before it clones or builds anything, not
# be discovered minutes later inside someone else's test suite.
MISSING=""
for tool in pdfinfo pdftotext pandoc; do
    command -v "$tool" >/dev/null 2>&1 || MISSING="$MISSING $tool"
done
if [ -n "$MISSING" ]; then
    echo "Missing required external tool(s):$MISSING" >&2
    echo "(pdfinfo, pdftotext: this repo's own paper-tex/gates/run_gates.py; pdftotext, pandoc: the pinned sarc-suite-one-pass sibling's own release-check)" >&2
    echo >&2
    echo "Install on macOS (Homebrew):" >&2
    echo "  brew install poppler pandoc" >&2
    echo >&2
    echo "Install on Debian/Ubuntu (apt):" >&2
    echo "  sudo apt-get install poppler-utils pandoc" >&2
    exit 1
fi
echo "Preflight OK: pdfinfo, pdftotext, pandoc all found on PATH."
echo

if [ ! -f "$LOCKFILE" ]; then
    echo "engines.lock not found at $LOCKFILE" >&2
    exit 1
fi

clone_or_checkout() {
    local name="$1" url="$2" sha="$3"
    local dest="$PARENT_DIR/$name"
    if [ -d "$dest/.git" ]; then
        echo "[$name] already cloned at $dest; fetching and checking out pinned commit..."
        git -C "$dest" fetch origin "$sha" --depth 1 2>/dev/null || git -C "$dest" fetch origin
        git -C "$dest" checkout --quiet "$sha"
    else
        echo "[$name] cloning $url at $sha..."
        git clone --quiet "$url" "$dest"
        git -C "$dest" checkout --quiet "$sha"
    fi
    local actual
    actual="$(git -C "$dest" rev-parse HEAD)"
    if [ "$actual" != "$sha" ]; then
        echo "[$name] FAILED to pin: expected $sha, got $actual" >&2
        exit 1
    fi
    echo "[$name] pinned at $actual"
}

# Parse engines.lock (simple "name url sha" lines, '#' comments allowed).
while IFS= read -r line; do
    line="${line%%#*}"
    line="$(echo "$line" | xargs || true)"
    [ -z "$line" ] && continue
    name=$(echo "$line" | awk '{print $1}')
    url=$(echo "$line" | awk '{print $2}')
    sha=$(echo "$line" | awk '{print $3}')
    clone_or_checkout "$name" "$url" "$sha"
done < "$LOCKFILE"

ONE_PASS_DIR="$PARENT_DIR/sarc-suite-one-pass"
if [ ! -d "$ONE_PASS_DIR" ]; then
    echo "sarc-suite-one-pass not found as a pinned sibling at $ONE_PASS_DIR" >&2
    exit 1
fi

echo
echo "Delegating engine installs + LaTeX toolchain to sarc-suite-one-pass's own bootstrap.sh..."
bash "$ONE_PASS_DIR/bootstrap.sh"

echo
echo "Installing this repo's own toolchain (pytest, hypothesis, mutmut, jsonschema, scipy, python-sat, pyyaml, build), pinned by constraints.txt..."
pip install -q -c "$REPO_ROOT/constraints.txt" pytest hypothesis mutmut jsonschema scipy python-sat pyyaml build

echo
echo "=== Verifying the imported baseline: sarc-suite-one-pass's own release-check ==="
echo "(task brief Phase 0: this must pass before anything in this repo is built)"
( cd "$ONE_PASS_DIR" && make release-check )
echo
echo "Imported baseline release-check: PASS"

echo
echo "Bootstrap complete."
echo "Sibling commits:"
for name in sarc-suite-one-pass dqSarc sarc-governance Greensarc; do
    echo "  $name: $(git -C "$PARENT_DIR/$name" rev-parse HEAD)"
done
