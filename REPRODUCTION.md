# Reproduction

Package D (`prereg/v8-large-realistic-domain.md`, tag `prereg-p5-v8`)
registers this document. It gives exact commands, expected output
hashes, and expected elapsed times for reproducing this artifact's own
claims from a bare clone -- nothing here invites or recruits anyone to
do so. **The author recruits the reproducer; this pipeline does not.**
An issue template for reporting an independent reproduction attempt is
at the bottom.

**What a complete reproduction report needs** (the reviewer's own
eight-point standard this document and the issue template are aligned
to; `FINAL-AUDIT.md`'s own item 11 tracks whether one has actually been
filed against this repository, not just whether the infrastructure
below exists):

1. An independent person -- not the author, and not this development
   pipeline timing its own bare clone (see the note below).
2. An environment not used in this project's own development -- a
   separate machine, or a genuinely fresh container/VM, never a
   directory that ever held a development checkout of this repo.
3. A wheel install (step 4 below).
4. A black-box `authority_compiler` example: imported from the
   installed wheel alone, outside this repository's own source tree
   (step 4 -- its own example is a deliberately trivial, hand-verifiable
   packaging check, not a domain result; see point 5).
5. At least one substantive result, CH-B1 or CH-C1 preferred: step 6
   reproduces CH-B1 (the v4 flagship) via direct source import; step
   6b points at CH-C1's own checker for the v8 large-domain result.
   Neither runs through the installed wheel -- the black-box path
   (point 4) and the substantive-result path (point 5) are two
   separate steps below, not one combined step.
6. OS, Python version, exact commands, output hashes, and any
   deviations from what this document expects, all recorded -- the
   issue template's own fields.
7. `make release-check`'s own mutation gate is optional, given its
   ~63-minute cost: steps 1, 2 or 4, plus one substantive result (step
   6 or 6b), already make a complete, countable report; step 3 is
   offered for whoever wants the full gate too, not required for one.
8. The result filed as a reproduction-report issue on this repository
   (the template at the bottom) -- a run that is never reported does
   not move item 11.

Every command below is run from a fresh `git clone` on a machine with
Python 3.11 or 3.12 and no prior state from this repository. The
elapsed times in steps 2 and 3 were measured by this development
pipeline itself, timing its own bare clone on its own CI-equivalent
hardware (`time_reproduction.py`, a genuinely bare clone + bootstrap +
`make <target>` in a disposable temp directory, not a warm cache) --
this establishes the expected numbers and confirms the commands run
from nothing, but it is a self-timed dry run, not an independent
reproduction under points 1-2 above, and `FINAL-AUDIT.md` does not
treat it as one. Elapsed times will vary with hardware; the
reachable-tuple counts, test counts, mutation score, and file hashes
below do not.

## 1. Bootstrap

```bash
git clone https://github.com/besanson/sarc-authority-derivation.git
cd sarc-authority-derivation
bash bootstrap.sh
```

Installs pinned toolchain dependencies (`pytest`, `hypothesis`,
`mutmut`, `jsonschema`, `scipy`, `python-sat`, `pyyaml`, `build` --
versions pinned in `constraints.txt`, used by both `bootstrap.sh` and
CI, `.github/workflows/ci.yml`) and clones the three pinned sibling
engine repositories `engines.lock` names (used by
`reproducibility_report.py`'s own sibling-sha cross-check; not required
for anything else below). `build` (needed by step 4's `make
package-smoke-test`) is installed here precisely so that step runs
unmodified straight after a bare bootstrap -- its absence from
`bootstrap.sh` was itself a finding of the 2026-09-14 commissioned
reproduction (`review-secondary/reproductions/2026-09-14-perplexity-
computer/`, deviation 1), now fixed.

## 2. Quick reproduce (release-check's own recipe, minus the mutation gate)

```bash
make quick-reproduce
```

Runs the full test suite, the formal double-run byte-identity check
(`make formal` twice, diffed), and the populated-draft freshness check
-- skips only the mutation-testing hard gate (see step 3). Expected:
**252 tests pass**, both double-run diffs report byte-identical, the
populated draft regenerates byte-identical to the committed copy.
Expected elapsed time: **~48 minutes** (`quick_reproduce_seconds:
2874.14`, `total_seconds` including bootstrap: `3053.27`, measured
2026-09-10 via a genuine bare `git clone` + `bash bootstrap.sh` + `make
quick-reproduce` in a disposable temp directory, `out/reproduction_
timing_quick.json`; dominated by `checkers/ch_c1_check.py`'s/
`checkers/ch_c2_check.py`'s own discernibility-family construction over
v8's 27,000-tuple reachable set, `~O(reachable^2)`,
`discernibility.py`'s own documented complexity, paid twice via the
formal double-run -- about 15 minutes less than full release-check,
roughly the mutation gate's own share of the difference).

## 3. Full release-check (adds the mutation hard gate)

**Optional** for a countable reproduction report (point 7 above),
given its cost -- steps 1-2 or 1+4, plus one substantive result (step
6 or 6b), already make a complete report; run this one too if you
want the full gate as well.

```bash
make release-check
```

Everything in step 2, plus `make mutate` (hard gate: mutation score
`>= 0.85`; ADR-003-mutation-testing.md), plus the citation, typed-
numerals, terminology, and PROOF-STATUS lints, plus
`reproducibility_report.py`'s own final snapshot
(`out/reproducibility-report.json`). Expected: **release-check: ALL
CHECKS PASS**, mutation score **1229/1261 = 0.9746233148295004** (32
pre-existing survivors in `derive.py`/`reduct.py`/`synthesis.py`/
`losses_datacomms.py`, none newer than Package C; one is this
package's own `find_up_to_k_minimum_cardinality_contracts`, a genuine
equivalent mutant -- see `NOVELTY.md`'s Fourteenth amendment and the
`D2` commit message for why it cannot be killed by any black-box
test). Expected elapsed time: **~63 minutes** (`release_check_seconds:
3793.52`, `total_seconds` including bootstrap: `3981.94`, measured
2026-09-10 via a genuine bare `git clone` + `bash bootstrap.sh` + `make
release-check` in a disposable temp directory, `out/reproduction_
timing.json`; dominated by `make mutate`'s own mutation run, ~1,261
mutants, plus `checkers/ch_c1_check.py`'s/`checkers/ch_c2_check.py`'s
own discernibility-family construction over v8's 27,000-tuple
reachable set, paid twice via the formal double-run).

Do not run `make v8-exhaustive-attempt` expecting it to complete: it is
a registered 300-second complexity data point (`reduct.exact_reducts()`
attempted and confirmed infeasible on v8's 35 properties,
`C(35,7) = 6,724,520` size-7 subsets alone), not a correctness gate,
and is deliberately excluded from both targets above.

## 4. Wheel install (black-box, outside this repository's own source tree)

Satisfies points 3 and 4 of the standard above.

```bash
make package-smoke-test
```

Builds an sdist+wheel (`python3 -m build`), installs the wheel into a
fresh virtual environment, then -- from `/tmp`, not this repository,
fed via stdin so no accidental repo-root/pythonpath fallback is
possible (`authority_compiler_smoke.py`'s own docstring) -- imports
`authority_compiler`, derives one contract (a deliberately trivial,
hand-verifiable two-property example -- a packaging check, not a
domain result; see steps 6/6b for a substantive result), and runs
`authority-bench --help`. Expected: `package-smoke-test: PASS`. CI
(`.github/workflows/ci.yml`, `package` job) runs this exact target on
both Python 3.11 and 3.12 at every push.

## 5. One AuthorityBench domain

```bash
authority-bench          # after `pip install .` or the wheel from step 4
python3 -c "
import json
result = json.load(open('out/results/authority_bench_v6_1.json'))
v4 = next(d for d in result['domains'] if d['domain'] == 'v4')
print(json.dumps(v4['summary'], indent=2, sort_keys=True))
"
```

Prints the `v4` (code/cloud) domain's own summary: which of the three
single-contract baselines (manual least-privilege, Xu-Stoller mining,
essential-variable analysis) are sufficient, and the smallest/cheapest
among them -- `out/results/authority_bench_v6_1.json`'s own committed
copy has sha256 `ad61f92158d64dcf84b5ff89cc3c68bb5263cf72240e3f986c60b8c84816de5b`. AuthorityBench packages
three domains (`v2`, `v4`, `data-and-communications`); v8 is
deliberately not a fourth (`NOVELTY.md`'s Fourteenth amendment,
`D2` commit message: `authority_bench.py`'s own `exhaustive_reduct`
baseline has no size guard and would never finish on v8's registered-
infeasible domain).

## 6. Code/cloud multi-reduct example (the flagship result, README's own snippet)

Satisfies point 5 of the standard above (CH-B1). Direct source import,
run from the repository root -- not the black-box wheel path (that is
step 4).

```bash
python3 <<'EOF'
from domain_v4 import CANDIDATE_PROPERTIES_V4, executable_reachable_tuples_v4
from losses_v4 import load_loss_registry_v4
from reduct import compute_core, exact_reducts, sufficiency

reachable = executable_reachable_tuples_v4()
registry = load_loss_registry_v4()

core, redundant, _witnesses = compute_core(reachable, registry, CANDIDATE_PROPERTIES_V4)
print(f"core ({len(core)} of {len(CANDIDATE_PROPERTIES_V4)} candidates):", sorted(core))

is_sufficient, _certificate = sufficiency(tuple(sorted(core)), reachable, registry)
print("core sufficient:", is_sufficient)

reducts, subsets_considered = exact_reducts(CANDIDATE_PROPERTIES_V4, reachable, registry)
print(f"reducts ({subsets_considered} subsets tested after pruning):")
for r in sorted(sorted(r) for r in reducts):
    print(" ", r)
EOF
```

Expected: a 6-of-10-property core, `core sufficient: False`, and
exactly two 7-property reducts (core plus `branch`, or core plus
`environment`) -- `out/checkers/ch_b1_check.json`'s own committed copy
has sha256 `a5a884c0557cf1cb70c244a7fd9098d7285e07479c6fb911112a9c33d98b471a`.

## 6b. Large-domain core-insufficiency example (CH-C1, v8)

Satisfies point 5 of the standard above as an alternative to CH-B1.
Also a direct import, run from the repository root; the checker itself
(not a hand-copied snippet) is the reproduction recipe.

```bash
python3 -m checkers.ch_c1_check
```

Expected: `core_cardinality: 4` (of 35 candidates), `is_core_sufficient:
false`, `supported: true` (CH-C1: the core is not sufficient), and
`minimum_cardinality: 9` with `minimum_cardinality_contracts_found_count`
at least 1 and at most 5 (a registered lower bound via blocking-clause
enumeration, never claimed exhaustive) -- `out/checkers/ch_c1_check.json`'s
own committed copy has sha256
`5fae64128807c8b0358a5423adc89ff9f46b0ebf8047022c0c090a0665d49b7d`
(also in the table below). No elapsed time is separately measured for
this checker alone; it is part of quick-reproduce's own measured
~48-minute total (step 2), which already accounts for both this
checker's and `ch_c2_check`'s own discernibility-family construction
over v8's 27,000-tuple reachable set.

## Expected output hashes (as of this commit; unrelated future commits change unrelated files, not these)

**Corrected (2026-09-14 commissioned reproduction, deviation 5): not
every file below is regenerated by the same mechanism, and two of them
are not regenerated by anything in this document at all** -- the table
previously claimed otherwise. Matched here against the Makefile
exactly, not asserted:

| File | sha256 | Regenerated by |
|---|---|---|
| `paper5-authority-derivation-draft-v0.6-populated.md` | `65d633c86b70f48b11d755a062138ff913605ae7a8a14eab814f78fe0122e17e` | `populate_paper.py`, diffed against the committed copy -- a separate freshness gate, not the formal double-run below (step 2/3) |
| `out/checkers/ch_b1_check.json` | `a5a884c0557cf1cb70c244a7fd9098d7285e07479c6fb911112a9c33d98b471a` | `make formal` (step 2/3's own formal-double-run byte-identity gate: two consecutive `make formal` runs, diffed) |
| `out/checkers/ch_c1_check.json` | `5fae64128807c8b0358a5423adc89ff9f46b0ebf8047022c0c090a0665d49b7d` | `make formal`, same gate |
| `out/checkers/ch_c2_check.json` | `8a58658f11fb4fdb4a037f30177b0919fb89d4d4cd002c2f4c7b58e71b002935` | `make formal`, same gate -- value changed this commit, see Corrections below |
| `out/results/authority_bench_v6_1.json` | `ad61f92158d64dcf84b5ff89cc3c68bb5263cf72240e3f986c60b8c84816de5b` | **Not regenerated by anything above.** A committed, frozen input step 5 reads directly; this hash confirms your copy matches this repository's, not that your own run reproduced it. |
| `out/results/v8_exhaustive_attempt.json` | `ee8724d31c71f5c4f7076a93fe9295731669bfa5420464f3efd96cfac445d0cc` | **Not regenerated by anything above** (only by `make v8-exhaustive-attempt`, which step 3 above says explicitly not to run expecting completion). Same caveat as the row above. |

Only the three `out/checkers/` rows are part of `make release-check`'s/
`make quick-reproduce`'s own formal-double-run byte-identity gate --
matching hashes at the same commit is expected there, not coincidental,
and a mismatch on the SAME commit sha for one of those three is itself
a reportable finding (see the issue template below). The populated
draft is regenerated too, automatically, on every `quick-reproduce`/
`release-check` run, but by a different, separate gate
(`populate_paper.py`'s own freshness diff) -- still expected to match,
just not by the same double-run mechanism as the three checker files.
The two `out/results/` rows are committed, historical artifacts this
document never asks you to regenerate; list them only so a reader
comparing bytes has the expected values, not as a reproduction claim.
A mismatch on a DIFFERENT commit is expected whenever that commit's own
diff touches the underlying source, for any row.

## Corrections

Append-only, per this project's own discipline: nothing below is
retracted or reworded; each correction is recorded alongside its
original claim, not in place of it.

**Cross-environment float-serialization non-determinism (found
2026-09-14, commissioned automated reproduction, `review-secondary/
reproductions/2026-09-14-perplexity-computer/`).** A same-commit hash
mismatch on `out/checkers/ch_c2_check.json` (six cost fields serialized
as `9.153` by the reproduction's Python 3.12.13 run, versus this
repository's own Python-3.11-generated `9.152999999999999`) was traced,
not assumed: confirmed directly, side by side on python3.11/3.12/3.13,
that `sum()` over the identical sorted sequence of costs
(`checkers/ch_b2_check.py`'s/`ch_c2_check.py`'s own summation) returns a
different last-bit float on Python 3.11 than on 3.12/3.13 alone --
`checkers/ch_b2_check.py`'s own prior comment had already diagnosed and
partially fixed a same-process, hash-randomization-driven version of
this (sorting before summing), but that fix could not, and did not,
address a difference between interpreter versions on the identical
sorted input. `synthesis.py`'s new `total_cost` helper (`math.fsum`
over sorted input, rounded to a declared precision,
`synthesis.COST_SERIALIZATION_DECIMALS`) is confirmed identical across
all three tested interpreters and is now the only path every cost-
summing call site in this repository uses
(`checkers/ch_b2_check.py`/`ch_c2_check.py`, `authority_bench.py`,
`benchmarks.py`, `discernibility_scaling_benchmark.py`) --
`test_synthesis.py`'s own `test_total_cost_shuffled_order_serializes_
identically` pins this directly. No registered result changed: CH-B2 is
still **SUPPORTED** (the cheaper contract still costs `6.124` against
`7.354`), CH-C2 is still **NOT SUPPORTED** (the same exact tie, now
`9.153` on every tested interpreter rather than disagreeing by roughly
one unit in the last place of a 64-bit double, about 1 part in 10^15)
-- only a spurious difference far past any digit this repository's own
prose reads or relies on is affected. The expected-
hash table above is updated to the post-fix value; a hash recorded
before this correction (`750b42c192aab023439c462ec18b7fee09f74d15c72661f346295e4c10f3789f`,
this file's own prior committed copy) is superseded, not silently
dropped -- kept here as the historical value a pre-fix checkout would
still produce.

## Reporting an independent reproduction

Point 8 of the standard above. Use the issue template at
[`.github/ISSUE_TEMPLATE/reproduction-report.md`](.github/ISSUE_TEMPLATE/reproduction-report.md)
(select "Reproduction report" when opening a new issue on this
repository). It asks for exactly the fields needed to compare your run
against this document: whether you are independent of this project's
own development, your environment, commit sha, OS, Python version, the
commands you ran, elapsed time, the output hashes you got, and any
deviations from what this document expects. This project does not
solicit reproduction attempts or track who has or hasn't reproduced it
-- the template exists so that whoever the author recruits has a
precise, low-friction way to report back, and so that `FINAL-AUDIT.md`
has something concrete to check for.
