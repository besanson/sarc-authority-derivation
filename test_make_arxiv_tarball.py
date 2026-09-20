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

"""Tests for paper-tex/make_arxiv_tarball.py: two independent builds of
the same inputs must be byte-identical -- the property the sibling's own
shell `tar --sort=name --mtime=... --owner=0 --group=0` invocation
provides, but only under GNU tar (besanson/sarc-authority-derivation#2
found the default macOS BSD tar silently rejects --sort=name); this
repository's own packaging uses the tarfile module instead of shelling
out to any tar binary, so it cannot depend on which variant is on PATH."""
from __future__ import annotations

import importlib.util
import tarfile
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
PAPER_TEX_DIR = REPO_ROOT / "paper-tex"


def _load_module():
    # paper-tex/ is not a package (hyphen in the name, no __init__.py) --
    # same load-by-path pattern paper-tex/gates/run_gates.py's own
    # _load_generate_refs_bib_module already uses for a sibling script in
    # the same directory.
    spec = importlib.util.spec_from_file_location(
        "make_arxiv_tarball", str(PAPER_TEX_DIR / "make_arxiv_tarball.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


mat = _load_module()


def test_two_builds_are_byte_identical():
    with tempfile.TemporaryDirectory() as tmp:
        out1 = Path(tmp) / "one.tar.gz"
        out2 = Path(tmp) / "two.tar.gz"
        mat.build_arxiv_tarball(out1)
        mat.build_arxiv_tarball(out2)
        assert out1.read_bytes() == out2.read_bytes()


def test_deterministic_metadata_and_contents():
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "arxiv.tar.gz"
        mat.build_arxiv_tarball(out)
        with tarfile.open(out, mode="r:gz") as tf:
            members = tf.getmembers()
        names = [m.name for m in members]
        assert names == sorted(names)
        assert set(names) == {"main.tex", "refs.bib"}
        for m in members:
            assert m.mtime == mat.SOURCE_DATE_EPOCH
            assert m.uid == 0
            assert m.gid == 0
