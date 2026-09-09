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
"""Package A (review-secondary/final-gap-plan-9.5-2026-09-09.pdf's own
mandatory CI smoke test): `authority-bench --help` previously had no
argument parsing at all, so it silently ran the full four-baseline/
three-domain benchmark instead of printing usage and exiting. Confirms
the fix directly, without paying for a real `run()` call (monkeypatched
out and asserted never invoked) -- the full benchmark itself is exercised
by `make authority-bench`, not by this file."""
from __future__ import annotations

import pytest

import authority_bench


def test_help_prints_usage_and_exits_zero_without_running_the_benchmark(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["authority-bench", "--help"])
    called = []
    monkeypatch.setattr(authority_bench, "run", lambda: called.append(True))

    with pytest.raises(SystemExit) as exc_info:
        authority_bench.main()

    assert exc_info.value.code == 0
    assert called == []
    assert "authority-bench" in capsys.readouterr().out


def test_no_arguments_still_runs_the_benchmark(monkeypatch, tmp_path):
    monkeypatch.setattr("sys.argv", ["authority-bench"])
    monkeypatch.setattr(authority_bench, "OUTPUT_PATH", tmp_path / "authority_bench_v6_1.json")
    called = []
    monkeypatch.setattr(authority_bench, "run", lambda: called.append(True) or {})

    authority_bench.main()

    assert called == [True]
