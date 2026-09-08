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
echo "Installing this repo's own toolchain (pytest, hypothesis, mutmut, jsonschema, scipy, python-sat)..."
pip install -q pytest hypothesis mutmut jsonschema "scipy==1.17.1" python-sat

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
