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

## v0.3 update: `reduct.py` added, hard gate (B4, `prereg/v3-core-reduct-correction.md`)

`pyproject.toml`'s `[tool.mutmut]` target set extends to
`participation.py`, `derive.py`, `reduct.py` (Definitions 4-6,
Proposition 1'/Negative Proposition N's shared machinery); `test_reduct.py`
adds 7 fast, synthetic-model unit tests (no dependency on the real v2
model, mirroring `test_participation.py`'s own domain-agnostic style, so
mutation testing stays fast). `make mutate` is now a hard gate:
`mutmut run` (no `|| true` -- this mutmut version's own exit code does
not key off survivor count, so nothing was silently swallowed once the
literal `|| true` token was removed) is followed by `mutmut export-cicd-stats`
and `mutation_check.py`, which parses `mutants/mutmut-cicd-stats.json`
programmatically and fails (`SystemExit(1)`) if the kill score is below
0.85 or if any mutant recorded `no_tests` (a real coverage gap, not an
acceptable survivor class -- this repeats the first pass's own "34
no-tests mutants is a bug, not a score component" finding above as a
standing rule, not just a one-time fix).

```
Total mutants: 291
Killed:        265
Survived:        26
No tests:         0
Kill score = 265 / (265 + 26) = 0.9107 (91.1%)
```

Above threshold; `mutation_check.py` (invoked by `make mutate`) exits 0.
The 23 pre-existing `participation.py`/`derive.py` survivors are
unchanged in kind from the original pass above (classes 1-5, `also_copy`
and `pytest_add_cli_args_test_selection` untouched for those two files).
`reduct.py` contributes 3 new survivors, all genuine equivalent mutants,
verified by direct reasoning about `exact_reducts()`'s own loop
structure, not accepted on the score alone:

### 6. `range(0, n + 1)` reformatted / off-by-one at the upper bound (2 survivors, `exact_reducts`)

`range(0, n + 1)` -> `range(n + 1)` (Python's own default start is 0 --
byte-different, semantically identical) and `range(0, n + 1)` ->
`range(0, n + 2)` (tries `size = n + 1`, one more than the candidate
count; `itertools.combinations(candidates, n + 1)` returns no
combinations at all when the requested size exceeds the population,
per Python's own documented behavior, so the extra loop iteration
produces zero subsets and changes nothing observable). Both equivalent
under every input this suite -- or any input -- can construct.

### 7. `r <= s` narrowed to `r < s` in the pruning check (1 survivor, `exact_reducts`)

`any(r <= s for r in reducts)` -> `any(r < s for r in reducts)`. `<=`
and `<` differ only when some already-found reduct `r` equals the
candidate `s` being tested. `itertools.combinations` never yields two
equal sets at any single call, and `reducts` (at the moment `s` of a
given size is tested) only ever contains reducts found at *smaller*
sizes than `s` plus other reducts already tested at the *same* size in
the same inner loop -- both cases are necessarily different sets from
`s` (distinct combinations of the same or smaller size can never be set-
equal to `s`). `r == s` is therefore unreachable at this call site by
construction, making `<=` and `<` behaviorally identical here -- not
tested around, because there is no behavior to differ, the same
standard this ADR already applied to class 2 above. (The *analogous*
comparison in `verify_core_identity`'s own core-subset-of-every-reduct
check, `core_via_intersection <= r`, is a live boundary -- the core can
legitimately equal a reduct when there is exactly one, e.g. this
artifact's own v2 model -- and IS covered, by
`test_verify_core_identity_holds_when_core_is_the_unique_reduct`.)

## Decision (v0.3 update)

Accept the 0.9107 kill score with `reduct.py` included. Its 3 survivors
are equivalent mutants under class 1/2/4's own established reasoning,
verified directly rather than assumed; the boundary case that class 7
could have missed (core equal to a unique reduct) was caught during this
review and closed with a real test, not left as an unexplained gap.

## v0.4 / Milestone C update: `domain_v4.py`/`losses_v4.py` added

`pyproject.toml`'s `[tool.mutmut]` target set extends to include
`domain_v4.py`/`losses_v4.py` (the independent software-and-cloud domain,
`prereg/v4-realistic-domain.md`, tag `prereg-p5-v4`); `test_domain_v4.py`
and `test_losses_v4.py` are added to test selection.

First pass (117 new mutants from the two new files): 40 survived, score
dropped to 0.8382 (342/408) -- below threshold, correctly caught by the
hard gate rather than silently accepted. All 40 traced to a real,
specific gap, not accepted as equivalent: `test_domain_v4.py`'s original
tests only checked "at least one tuple satisfies each predicate" and
`has_recovery_path`/reachability's aggregate tuple COUNT, never each
predicate's own individual clauses or each field's actual per-tuple
VALUE. Two rounds of precise tests closed all 40:

1. `test_losses_v4.py` (new, mirroring `test_losses.py`'s own precision):
   one positive case and one "near-miss" negative case per AND-clause,
   per predicate -- e.g. `unauthorised_mutation`'s two clauses are each
   independently toggled back to safe and re-checked, not just the
   overall positive case asserted once. Closed 35 of the 40.
2. Two gaps remained after that pass, found by `mutmut show`, not
   guessed: (a) `secret_exposure`'s `operation in {"read", "write"}` was
   only exercised with `"read"` -- a case-mutated `"write"` variant
   survived untested; closed by adding a `"write"`-operation positive
   case. (b) Three `StateTupleV4` fields nothing predicate-level reads
   (`actor_identity`, `repository` was also implicated, `deployment_
   window`) had their tuple-construction silently mutated to `None` and
   nothing noticed, because no test checked a reachable tuple's fields
   actually carry their own loop variable's value rather than a
   placeholder -- closed by
   `test_rank0_reachable_every_field_takes_every_declared_value`, a
   single general test asserting every one of the ten fields' full
   declared domain actually appears somewhere in the reachable set.

```
Total mutants: 408
Killed:        382
Survived:        26
No tests:         0
Kill score = 382 / (382 + 26) = 0.9363 (93.6%)
```

Above threshold; all 26 survivors are the same pre-existing
`participation.py`/`derive.py`/`reduct.py` equivalence classes 1-5 and 7
documented above, unchanged in kind -- zero survivors in
`domain_v4.py`/`losses_v4.py` after the fixes above (confirmed directly
via `mutmut results | grep domain_v4`, not assumed from the aggregate
score alone).

## Decision (v0.4 / Milestone C update)

Accept the 0.9363 kill score. The first pass's real gap (predicate
clauses and field values checked only in aggregate, not individually)
is closed with tests that have independent value beyond moving the
number -- the same standard the original first pass held itself to for
`participation.py`/`derive.py`. No new equivalent-mutant class is
introduced by this milestone; the two new files' every mutant that survived
traced to an actual, closeable test gap.

## Milestone D update: `discernibility.py`/`synthesis.py` added

`pyproject.toml`'s `[tool.mutmut]` target set extends to
`discernibility.py`/`synthesis.py` (the discernibility IR and PySAT
SAT/MaxSAT backends, `prereg/v5-synthesis.md`, tag `prereg-p5-v5`);
`test_discernibility.py`/`test_synthesis.py` added to test selection.

First pass (132 new mutants): 7 survived. Five traced to real,
closeable gaps, closed the same way as every prior pass -- not accepted
on the aggregate score:

- `remove_redundant_supersets`'s `sorted(family, key=len)` mutated to
  drop the `key=len` entirely survived twice (two different AST
  mutations of the same drop) because every existing test's family
  happened to already sort correctly under Python's OWN default
  frozenset ordering (subset comparison) too -- not because size-order
  is inessential. `test_remove_redundant_supersets_requires_size_order_
  not_input_or_default_order` constructs a family
  (`[{a,b}, {c}, {a}]`) where the two orderings diverge and confirmed,
  by direct execution, that dropping `key=len` really does produce a
  wrong (non-minimal) result on it -- not merely asserted from reading
  the code.
- `existing <= candidate` narrowed to `existing < candidate` (the same
  boundary-comparison shape ADR-003's own v0.3 update already treated
  once, `verify_core_identity`'s core-subset check): survives whenever
  no two sets in a test's family are ever exactly equal.
  `test_remove_redundant_supersets_drops_an_exact_duplicate` supplies a
  literal duplicate, the one case `<=` and `<` disagree on.
- `find_minimum_cost_contract`'s two `ValueError` messages, both
  mutated to `ValueError(None)`: `pytest.raises(ValueError)` alone does
  not inspect the message, so a wrong or missing message survives even
  though the exception TYPE and the rejection behavior are both already
  correctly tested. Closed by adding `match=` to both existing
  `pytest.raises` calls -- a small precision fix, not a new test.

Two survivors are genuine equivalent mutants, verified by direct
execution against the actual installed PySAT, not assumed from reading
the diff:

### 8. Uniform SAT-variable renumbering (1 survivor, `_property_variables`)

`i + 1` -> `i + 2` (every property's variable number shifts by the same
constant). `_hard_clauses` builds clauses from `var[p]` and
`_included_from_model` decodes the model through that SAME `var` dict,
so a uniform shift changes which INTEGER labels the solver sees but
never changes which PROPERTIES end up included -- confirmed directly:
re-solving the two-state counterexample's own CNF under both the `+1`
and `+2` numbering schemes returns the identical included set (`{x}`)
in both cases. Equivalent under any input, the same standard class 2
already applied to a byte-different, semantically-identical AST
reformatting.

### 9. Uniform MaxSAT soft-clause weight scaling (1 survivor, `find_minimum_cardinality_contract`)

`weight=1` -> `weight=2` on every one of the per-property soft clauses
uniformly. RC2 minimizes TOTAL weighted cost subject to the hard
clauses; scaling every soft clause's weight by the same positive
constant scales the reported total cost by that constant but cannot
change which assignment achieves the minimum (the argmin of a sum is
invariant to a uniform positive rescaling) -- confirmed directly:
re-solving a representative WCNF at weight 1, 2, and 5 returns the
identical model in all three cases, only `rc2.cost` itself changes
(1/2/5), a value this function does not even return. Equivalent under
any input, by the same "internal number with no downstream consumer"
reasoning class 4 already established for `derive.py`'s own explicit-
default-argument case -- here the invariant one is a scalar factor on a
MaxSAT weight, not a keyword argument's value, but the underlying shape
(a change that cannot reach an externally observable outcome) is the
same.

```
Total mutants: 540
Killed:        512
Survived:        28
No tests:         0
Kill score = 512 / (512 + 28) = 0.9481 (94.8%)
```

Above threshold; the 26 pre-existing survivors (classes 1-5, 7) are
unchanged in kind. `discernibility.py`/`synthesis.py` contribute exactly
the 2 new equivalence classes above -- zero other survivors in either
file after the fixes.

## Decision (Milestone D update)

Accept the 0.9481 kill score. Five of the first pass's seven survivors
were real, closeable gaps and are closed with tests that have
independent value (an order-dependent correctness bug in
`remove_redundant_supersets` that a less deliberately-constructed family
would have missed entirely, not merely a coverage-number fix); the
remaining two are genuine equivalent mutants, each verified by directly
executing both variants against the real, installed PySAT rather than
reasoned about from the diff alone.

## Milestone D5 update: `contract_change_delta` added to `synthesis.py`

`contract_change_delta` (`prereg/v5-synthesis.md`'s own D5 registration,
`synthesis.py`, no `pyproject.toml` change needed -- the file was already
a mutation target) adds 76 new mutants (540 -> 616 total). First pass: 10
survived, none accepted on the score alone:

- **8 dict-key-name mutations** (`"base_contract"` case-mutated to
  `"XXbase_contractXX"`/`"BASE_CONTRACT"`, and the same shape for
  `new_tuple_count`, `updated_contract_cardinality`, and
  `full_recomputation_cardinality`): a real, specific gap --
  `test_contract_change_delta_extends_a_broken_contract_and_keeps_the_
  pinned_property` and its siblings checked `was_still_sufficient`,
  `updated_contract`, `incremental_is_sufficient`, and
  `full_recomputation_contract`/`full_recomputation_cardinality_gap`,
  but never read these four other keys of the same returned dict.
  Closed by `test_contract_change_delta_reports_every_declared_field`,
  which asserts all four directly, not a broader test rewrite.
- **One real behavioral gap** (`if p not in base_contract:` mutated to
  `if p in base_contract:`, dropping every soft "prefer excluded" clause
  from non-base properties entirely while adding a no-op always-violated
  one to already-hard-pinned base properties): investigated by direct
  execution, not accepted as an obvious variant of classes 8/9 -- three
  probe fixtures were built to determine whether this changes observable
  output. A fully free variable (appearing in no discernibility clause)
  was confirmed to stay excluded either way, and a "forced-singleton
  plus absorbed OR-clause" construction collapsed to the same case once
  `remove_redundant_supersets` absorbed the redundant clause -- neither
  distinguished the mutation. A THIRD construction did: a colliding pair
  differing in two DIFFERENT non-base properties simultaneously, with no
  other clause a subset of `{y, z}` (so absorption cannot collapse it),
  leaves a genuine, unabsorbed two-way choice in the CNF. Under the
  correct code, the soft clauses make this tie cost-minimal (repeatably
  resolved to `{x, z}` across 5 direct runs through
  `contract_change_delta` itself); under the mutation, with no soft
  clauses left on `y` or `z` at all, the same fixture repeatably resolves
  to `{x, y}` instead (8 runs) -- both are valid same-cardinality
  answers (the mutation was never observed to add an UNNECESSARY third
  property in any of the three constructions), but WHICH valid answer is
  returned demonstrably changes, which is exactly what `pytest.raises`-
  style "any minimal answer accepted" testing would paper over. Closed
  by `test_contract_change_delta_picks_a_minimum_cardinality_extension_
  on_a_genuine_two_way_tie`, which pins the correct code's own
  deterministic resolution of this specific tie.
- **One new instance of the already-established class 9 pattern**
  (`weight=1` -> `weight=2` on `contract_change_delta`'s own non-base
  soft clauses, the identical shape class 9 already documents for
  `find_minimum_cardinality_contract`'s soft clauses, in a different
  function): re-verified directly rather than assumed identical by
  family resemblance -- re-solving the tie-fixture's WCNF at weight 1,
  2, 5, and 100 returns the identical `{x, z}` result at every weight.
  Equivalent under class 9's own established reasoning (uniform positive
  rescaling cannot change an argmin); not a new class, an additional
  survivor within the same one.

## Correction to class 8 (discovered while closing the gap above)

Closing the two-way-tie gap above required directly executing both the
correct and the `_property_variables` `i+1`/`i+2`-renumbered code on the
SAME tie fixture (the standard this ADR already holds itself to for every
equivalence claim). Doing so surfaced that the new test, run against a
literal copy of `synthesis.py` with class 8's own mutation re-applied
(`i + 1` -> `i + 2` in `_property_variables`, `mutmut show
synthesis.x__property_variables__mutmut_2`), FAILS: the renumbered code
resolves the identical two-way tie to `{x, y}`, not `{x, z}` --
observably different, not equivalent, on this input. Class 8's original
"Equivalent under any input" claim (Milestone D update, above) was
verified only against that section's own two-state counterexample
fixture, which -- despite itself documenting a tie
(`test_find_minimum_cardinality_contract_is_a_singleton_reduct` already
accepts `contract in ({"x"}, {"y"})` there) -- did not happen to expose
numbering-sensitivity in its own tie-break. The corrected, narrower claim,
verified directly rather than reasoned from the general shape of "a
uniform relabeling": a uniform SAT-variable renumbering cannot change
SUFFICIENCY or the CARDINALITY of the returned contract (both are
properties of the clause structure, invariant to variable labels by
construction), and cannot change the returned set when the optimal
solution is UNIQUE -- but when several equally-optimal solutions exist (a
genuine tie), WHICH one the underlying SAT solver's own tie-breaking
resolves to can depend on the absolute variable numbers, because the
solver's internal decision heuristics are keyed by variable ID, not only
by clause structure. `synthesis.x__property_variables__mutmut_2` is
correspondingly re-classified: no longer an accepted equivalent mutant --
`test_contract_change_delta_picks_a_minimum_cardinality_extension_on_a_
genuine_two_way_tie` (added for the gap above) kills it too, incidentally
closing a Milestone D survivor this milestone did not set out to touch.
v0.1-v4's own committed mutation results stay frozen and cited as prior
iterations; Milestone D's own reported 0.9481 score and 28-survivor count
are not retroactively edited -- they are what that milestone's own test
suite actually achieved at the time, correct for the tests that existed
then; this section records what changed and why, not a rewrite of that
history.

```
Total mutants: 616
Killed:        588
Survived:        28
No tests:         0
Kill score = 588 / (588 + 28) = 0.9545 (95.5%)
```

Above threshold. Of the 28 survivors: 23 `derive.py` + 3 `reduct.py`
(classes 1-5, 7, unchanged), 1 `find_minimum_cardinality_contract`
(class 9's original instance, unchanged), and 1
`contract_change_delta` (class 9's new instance, above) -- confirmed
directly via `mutmut results` diffed against the pre-D5 list (`comm -23`/
`comm -13` against the two runs' survivor sets), not assumed from the
aggregate score. Zero survivors in `discernibility.py`; zero OTHER
survivors in `synthesis.py` beyond the two class-9 instances --
`_property_variables`'s own class 8 survivor is gone, per the correction
above.

## Decision (Milestone D5 update)

Accept the 0.9545 kill score. Nine of the first pass's ten new survivors
were real, closeable gaps (eight field-assertion gaps closed with direct
key checks, one genuine tie-numbering-sensitivity bug closed with a
fixture specifically constructed to expose it after two other
constructions failed to); the tenth is a new instance of the
already-established class 9 equivalence, re-verified rather than assumed
from family resemblance. Closing the tie-numbering gap surfaced that
Milestone D's own class 8 claim was overstated -- corrected here, in the
open, rather than left standing on a verification that turned out to
cover less than it claimed.
