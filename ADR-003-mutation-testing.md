# ADR-003: Mutation Testing (Phase 2 / Verification, V5-equivalent gate)

**Status**: Accepted
**Date**: 2026-08-31

## Context

Verification requires mutation testing on `participation.py` and
`derive.py` to reach a kill score of at least 0.85, or that survivors be
individually justified here (task brief).

## Result

```
mutmut run, source_paths = [participation.py, derive.py]
Total mutants: 169
Killed:        146
Survived:        23
No tests:         0
Kill score = 146 / (146 + 23) = 0.8639 (86.4%)
```

Above the 0.85 threshold. Recorded in `mutants/mutmut-cicd-stats.json`.
Test selection: `test_participation.py`, `test_derive.py`
(`pyproject.toml`'s `[tool.mutmut].pytest_add_cli_args_test_selection`).

## First pass and the fixes it drove

The first run (173 total: 116 killed, 23 survived, 34 no-tests) scored
0.8345 -- below threshold -- and surfaced four real, distinct issues,
addressed directly rather than papered over:

1. **`derive.main()` had zero tests** (34 "no tests" mutants, the entire
   gap between the two runs' totals). Added
   `test_main_writes_the_output_file` (calls `main()` in a temp cwd via
   a symlinked `prereg/`, checks the written file's parsed content and
   specific stdout substrings) and `test_head_sha_matches_real_git_rev_
   parse` (checks `_head_sha()` against a direct `git rev-parse HEAD`
   call). Both are genuinely useful tests this module lacked, not
   written only to move the score.
2. **`find_witness`'s `continue`/`break` distinction was untested.** A
   mutant changing `continue` to `break` when skipping a singleton
   fingerprint group survived: with only two- and three-tuple reachable
   lists in the existing tests, no test had a *singleton group ordered
   before* the real witness-bearing group, so a `break`-mutated version
   that stops the whole search early produced the same (wrong-for-the-
   wrong-reason, but accidentally matching) result as the correct
   version on those inputs. `test_find_witness_does_not_stop_at_an_
   earlier_singleton_group` constructs exactly that ordering and kills it.
3. **`_serialize`'s frozenset branch was untested directly.** All
   existing witnesses happened to come from `Toy` (no frozenset field)
   or from the real `derive()` run's own witnesses, which the tests
   never inspected at the level of "is `consumed_grant_ids` actually a
   sorted list, not `None`". Added two direct unit tests on `_serialize`
   (nonempty and empty frozenset).
4. **Two lines of genuinely dead code were found and deleted, not
   justified.** `_serialize`'s `elif isinstance(v, tuple):` branch is
   unreachable: no field in the current nine-property `StateTuple`
   design is tuple-typed (the one that was, `role_window`, was removed
   by `ADR-002-participation-tuple-design.md`'s correction). `find_
   witness`'s `"unknown"` fallback for `differing_losses` being empty
   is unreachable by construction: entering that branch requires
   `v != base_verdict`, i.e. `bool(fired_a) != bool(fired_a_prime)`,
   which is only possible if the two sets differ, which is exactly what
   a nonempty symmetric difference means -- so `differing_losses` can
   never actually be empty there. Deleting unreachable code outright
   (per the project's own "complexity that does not pay rent deleted"
   standard) is preferred over writing a test that cannot exist for
   code that cannot run, or an ADR entry pretending the dead branch is
   a meaningful equivalence class.

## Survivor classes (second pass, 23 remaining)

Grouped by root cause, not enumerated mutant-by-mutant (reproducible via
`mutmut results` / `mutmut show <id>` against this ADR's commit).

### 1. `subprocess.run`'s `check=` parameter, unobservable on the success path (3 survivors, `_head_sha`)

`check=True` -> `check=None` / `check=False`. `check` only changes
behavior when the subprocess itself fails (raises `CalledProcessError`
vs. not); `test_head_sha_matches_real_git_rev_parse` runs `_head_sha()`
in this repository's own real, always-succeeding git checkout, so the
three values are behaviorally identical for every case the test suite
can construct without fabricating a broken git environment. Equivalent
under every call this test suite makes.

### 2. Whitespace-only AST mutation (1 survivor, `_head_sha`)

One mutant reformats the `subprocess.run(...).stdout.strip()` call
across a different line split with no token added, removed, or
reordered. Byte-different, semantically identical; unkillable by any
behavioral test because there is no behavior to differ.

### 3. Exception-fallback string, unreachable without mocking git failure (2 survivors, `_head_sha`)

`return "unknown"` in the `except Exception:` branch, case-mutated to
`"XXunknownXX"` / `"UNKNOWN"`. This branch is real and reachable in
production (no git installed, not a git checkout, etc.) but not by this
test suite, which deliberately tests `_head_sha()` against this
repository's own real git state rather than mocking `subprocess.run` to
fail. Accepted rather than added: a mocked-failure test would exercise
mutmut's counter, not this artifact's actual reliability, since the
real fallback value ("unknown" vs. any other string) has no downstream
consumer that branches on its exact text (`derivation_output.json`'s
`generated_at_head_sha` is documented as informational only, per
`checkers/_provenance.py`'s own freshness-is-`inputs_hash`-not-`head_
sha` design, carried into this repo's schema).

### 4. Explicit argument equals the callee's own default (1 survivor, `derive`)

`compute_p_star(reachable, registry, CANDIDATE_PROPERTIES)` ->
`compute_p_star(reachable, registry, )`. `participation.compute_p_star`
declares `candidate_properties: Tuple[str, ...] = CANDIDATE_PROPERTIES`
as its own default, so passing the identical value explicitly and
omitting it are the same call. Equivalent by construction; killing it
would require either removing the explicit argument (making the
dependency implicit, which this repo's style otherwise avoids for
exactly the traceability reason `derive.py` was written to make
explicit) or removing the shared default (which `participation.py`
legitimately wants for its own callers, e.g. `test_participation.py`'s
default-domain tests).

### 5. `main()`'s console-formatting mutations (16 survivors)

Mutations to `print()` call arguments (`print(None)` instead of
`print(json.dumps(...))`), `json.dumps`'s `indent=` value, and
`Path.mkdir`'s `exist_ok=True` -> `exist_ok=None` (falsy-equivalent to
`False`, but only observable on a *second* call against a directory
that already exists -- `test_main_writes_the_output_file` calls `main()`
once against a fresh temp directory, so the branch this would need to
diverge on is never reached). `test_main_writes_the_output_file`
deliberately checks the WRITTEN FILE's parsed content (what downstream
tooling -- `checkers/participation_check.py`, `paper_tables.py` --
actually consumes) and specific stdout substrings, not the exact
byte-for-byte formatting of every print statement or the double-call
idempotency of `mkdir`. Chasing full coverage of `main()`'s human-
readable console output and directory-creation idempotency, code with
no downstream consumer other than a person reading a terminal, is not
where this artifact's correctness risk lives; the file-content and
schema checks (`test_derive_output_matches_schema`) cover what matters.

## Decision

Accept the 0.864 kill score. The first pass's real gaps (main()
untested, the continue/break distinction, `_serialize`'s frozenset
branch) are closed with tests that have independent value beyond moving
the number, and two lines of dead code the first pass surfaced are
deleted rather than defended. The 23 remaining survivors are equivalence
under every case this suite constructs (classes 1, 2, 4), a real but
deliberately-not-mocked branch with no observable-content consequence
(class 3), or cosmetic console formatting with no downstream consumer
(class 5) -- not gaps in what this artifact actually needs to be correct
about.

## Reproducing

```
bash bootstrap.sh   # if not already done
rm -rf mutants .mutmut-cache && find . -name __pycache__ -exec rm -rf {} +  # required: stale mutants/ test copies confuse pytest's import collection on a second run
mutmut run
mutmut export-cicd-stats && cat mutants/mutmut-cicd-stats.json
mutmut results      # lists non-killed mutants
mutmut show <id>     # view a specific mutant's diff
```
