# Reproduction report: 4a96769 on Ubuntu 26.04 / Python 3.12.13

Technical result: bootstrap, quick reproduction, CH-B1 and CH-C1 passed. The exact wheel recipe failed because `build` was missing; after one recorded environment-only prerequisite installation, the unchanged wheel target and an additional wheel-only provenance check passed. One listed regenerated output, CH-C2, did not match the expected same-commit hash.

**Are you independent of this repository's development?**

Not an independent human reproducer. This is a separate Perplexity Computer verification session commissioned by the repository owner, not a session that implemented this checkout. Existing project context was available; no development artifacts or earlier execution results were used as substitutes for this run. Therefore this report must not, by itself, be counted as satisfying REPRODUCTION.md's independent-person requirement or closing FINAL-AUDIT item 11.

**Environment**

Isolated cloud Linux sandbox, hostname `space-sandbox`; the workspace initially contained only session context, memory and skills, with no repository or sibling checkout. The repository was freshly cloned into `/home/user/workspace/sarc-authority-derivation`. A new Python environment at `/home/user/workspace/reproduction-venv` was created with `python3.12 -m venv`; `PYTHONPATH` was unset. The exact wheel target created its own separate fresh `/tmp/sarc-p5-ac-smoke` environment and executed from `/tmp`; a further retained-wheel verification used a third fresh environment and confirmed every tested project import resolved to that environment's `site-packages`.

The initial empty workspace is observable, but platform/VM lifecycle attestation and physical-host history are not available. I cannot certify that the underlying machine/VM was never used in development. This is a qualification limitation, not a claimed compliance pass. The sandbox had 2 vCPUs (Intel Xeon @ 2.90 GHz), 7.8 GiB RAM, no swap, and roughly 11 GiB free disk initially. Environment evidence is in `03-environment.log` and `06-selected-python.log`.

**Commit sha you tested at**

`4a9676966aecb3d18cec6411decd5b9cfa8a7320` (detached HEAD, unchanged throughout).

Repository: https://github.com/besanson/sarc-authority-derivation

**Operating system**

Ubuntu 26.04 LTS (Resolute Raccoon), x86_64; kernel `6.1.155+`, `#1 SMP PREEMPT_DYNAMIC Thu Dec 18 15:17:16 UTC 2025`. Git 2.53.0. The run began on 2026-09-14 UTC and completed its technical verification on 2026-09-14 at 22:02:07 UTC (2026-09-15 00:02:07 CEST).

**Python version**

CPython **3.12.13**, within the documented 3.11/3.12 range. The machine default was Python 3.14.3, used only for initial inspection/recording before selecting 3.12.13; it was not used for reproduction targets. Initial pip: 25.0.1. Resolved dependencies included pytest 9.1.1, Hypothesis 6.168.0, mutmut 3.8.0, jsonschema 4.26.0, SciPy 1.17.1, python-sat 1.9.dev15, PyYAML 6.0.3 and NumPy 2.5.3; complete before/after package inventories are in `12-final-state.log` and `20-integrity.log`.

**Commands you ran**

- [x] `bash bootstrap.sh`
- [x] `make quick-reproduce`
- [ ] `make release-check` (optional; not run for this repository)
- [x] `make package-smoke-test` (failed initially; passed on unchanged-target retry)
- [ ] `authority-bench` (full benchmark not run; `--help` was exercised)
- [x] The code/cloud multi-reduct example, CH-B1 (REPRODUCTION.md section 6)
- [x] The large-domain core-insufficiency example, CH-C1 (REPRODUCTION.md section 6b)
- [x] Other: additional retained wheel build/install, neutral-directory import-path verification, hashes and source-integrity checks

The exact substantive sequence below was executed through an external recorder. Each command's working directory, start time in UTC, exit code, wall-clock duration, combined stdout/stderr and SHA-256 are retained in `commands.jsonl` and the per-command logs; `command-ledger.md` lists every recorded command in full. The CH-B1 heredoc was extracted verbatim from REPRODUCTION.md, not rewritten. Activation/unsetting were performed in the wrapper scripts included in the bundle.

```bash
# Fresh clone and pinned checkout
git clone https://github.com/besanson/sarc-authority-derivation.git
cd sarc-authority-derivation
git checkout --detach 4a96769
git rev-parse HEAD
git status --porcelain=v1

# Environment selection, outside repository
python3.12 -m venv /home/user/workspace/reproduction-venv
source /home/user/workspace/reproduction-venv/bin/activate
unset PYTHONPATH

# Repository-root commands, exact documented targets
bash bootstrap.sh
make quick-reproduce
make package-smoke-test
# Above failed with: No module named build

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

python3 -m checkers.ch_c1_check

# Explicit recovery, after preserving the initial failure
python3 -m pip install build
make package-smoke-test
```

The supplemental retained build and verification commands are reproduced verbatim in `command-ledger.md` and `package-followup.sh`. The exact smoke target deletes its own wheel and environment on success; the additional build exists only to retain a hashable wheel and directly attest import paths. No repository code, Makefile, configuration or documentation was edited to obtain any result.

**Elapsed time**

Times below are external `time.monotonic()` wall-clock measurements of each recorded command, excluding subsequent log hashing/copying. Commands were run sequentially; short read-only monitoring/audit operations overlapped the long run. Hardware differs from the document's timing platform.

| Command/stage | Seconds | Elapsed | Exit |
|---|---:|---|---:|
| Bootstrap, including imported-baseline release check | 205.030 | 3m 25.030s | 0 |
| Quick reproduce | 3911.154 | 65m 11.154s | 0 |
| Exact wheel target, initial failure | 0.016 | 0m 0.016s | 2 |
| Exact CH-B1 section-6 snippet | 8.977 | 0m 8.977s | 0 |
| Standalone CH-C1 checker | 454.938 | 7m 34.938s | 0 |
| Environment-only build prerequisite | 0.670 | 0m 0.670s | 0 |
| Unchanged wheel target, retry | 6.199 | 0m 6.199s | 0 |
| Additional retained sdist and wheel build | 3.083 | 0m 3.083s | 0 |
| Additional fresh wheel-only environment/install | 2.919 | 0m 2.919s | 0 |
| Wheel import paths, exact smoke example and CLI help | 0.562 | 0m 0.562s | 0 |

Quick reproduction took **3911.15 seconds**, versus the documented 2,874.14 seconds: **1037.01 seconds (17.28 minutes; 36.1%) longer**. Bootstrap plus quick reproduction took 4116.18 seconds, versus the documented total of 3,053.27 seconds. The test suite itself reported 275.64 seconds. Standalone CH-C1 has no separately documented timing expectation. Timings for clone, setup, inspections and verification are in the complete command ledger.

**Output hashes you got**

Only actually regenerated outputs are claimed here; matching retained files are not counted as reproduced.

| File | Your sha256 | Comparison |
|---|---|---|
| `paper5-authority-derivation-draft-v0.5-populated.md` | `cd42bb15e194c4a93770f7b706d0d20b28d87d89686e19009b80e61e721bc881` | MATCH |
| `out/checkers/ch_b1_check.json` | `a5a884c0557cf1cb70c244a7fd9098d7285e07479c6fb911112a9c33d98b471a` | MATCH |
| `out/checkers/ch_c1_check.json` | `5fae64128807c8b0358a5423adc89ff9f46b0ebf8047022c0c090a0665d49b7d` | MATCH |
| `out/checkers/ch_c2_check.json` | `8a58658f11fb4fdb4a037f30177b0919fb89d4d4cd002c2f4c7b58e71b002935` | MISMATCH |
| `out/results/authority_bench_v6_1.json` | Not generated; retained committed file, not reproduction evidence | Not evaluated |
| `out/results/v8_exhaustive_attempt.json` | Not generated; retained committed file, not reproduction evidence | Not evaluated |

CH-B1 and CH-C1 also matched these hashes in the preserved first formal run. CH-C1's standalone rerun matched again; CH-C2's first-run and final values both had the same observed mismatching hash. For CH-C2 the documented expected SHA-256 is `750b42c192aab023439c462ec18b7fee09f74d15c72661f346295e4c10f3789f`.

Additional retained artifacts, with no reference hash specified by REPRODUCTION.md:

- `sarc_authority_derivation-0.6.1-py3-none-any.whl`: `df54943253e4879932dbe027b0df65c5da5f9e24eb1fe7c921bd24cf305ec4ab`
- `sarc_authority_derivation-0.6.1.tar.gz`: `00e0b513934c85577e28b65f8ded231f2a24ba8a77b7d13a0d172281534bd064`

These are from the supplemental build, not the artifact deleted by the exact smoke target. Build-byte identity between these two builds was not assessed. Every recorded command-output hash is in `commands.jsonl` and `command-ledger.md`; `SHA256SUMS` covers the report and evidence bundle contents.

**Test/mutation results**

- **Bootstrap:** PASS, including the imported `sarc-suite-one-pass` baseline's release check; all four sibling SHAs matched their locks.
- **Quick reproduce:** `252 passed in 275.64s`; 0 failures, 0 errors, 0 skipped. `formal double-run byte-identical: OK`; `populated draft byte-identical to freshly regenerated: OK`; citation, typed-numerals, terminology and proof-status gates completed; final target message `quick-reproduce: ALL CHECKS PASS`.
- **Mutation:** this repository's mutation gate was deliberately not run. No reproduction claim is made for the documented 1229/1261 mutation score, even if a generated/retained report contains historical mutation information.
- **Wheel black box:** after the recorded prerequisite fix, exact target emitted `IMPORT_OK`, `DERIVE_OK ['a', 'b']` and `package-smoke-test: PASS`; `authority-bench --help` exited successfully. The supplementary check verified `authority_compiler`, its API and all enumerated local dependency modules were imported exclusively from the wheel-only environment's `site-packages`, with cwd `/tmp` and no `PYTHONPATH`.
- **CH-B1:** 15,120 reachable tuples; 6-of-10 core; `core sufficient: False`; exactly two 7-property reducts (core plus `branch` or `environment`); 1,014 subsets considered; `supported: true`. The section-6 snippet printed precisely those two reducts.
- **CH-C1:** 27,000 reachable tuples; 35 candidates; core cardinality 4; `is_core_sufficient: false`; `supported: true`; minimum cardinality 9; five contracts found under the cap of five. This is a bounded lower-bound enumeration, not a claim of exhaustive multiplicity. CH-B1 and CH-C1 used direct source imports as instructed, not the wheel API.

**Deviations from REPRODUCTION.md's own expectations**

1. **Missing wheel-build prerequisite (observed failure).** The unmodified `make package-smoke-test` failed immediately with `/home/user/workspace/reproduction-venv/bin/python3: No module named build` and make exit 2. `bootstrap.sh` does not install `build`; the CI package job does. Installing `build` in the external reproduction environment and retrying the unchanged target succeeded. Thus the documented bare-clone sequence was not fully self-sufficient. The failed and recovered runs are both retained.
2. **Same-commit CH-C2 hash mismatch (observed).** Six cost fields serialized as `9.153` instead of `9.152999999999999`; the exact diff is in `generated-output-diff.patch`. This is a byte-level failure of the documented expected hash, despite no substantive CH-C2 result-field change: it remains the registered `negative_tie`, with `supported: false`. The double-run gate compares the two new runs with each other, not their hashes against the committed hash table, so it passed without resolving this discrepancy. No source fix or output normalization was applied.
3. **Additional generated-file differences.** CH-B2 serialized two costs as `6.1240000000000006` rather than `6.124`; `derivation_output.json` and `derivation_output_v2.json` updated `generated_at_head_sha` from `63ec6034b488566684c24dcbb974fdb5f0772b5c` to the tested commit. These four tracked JSON files, including CH-C2, were the only tracked-file changes. They are command-generated outputs, not manual edits, and were deliberately not restored or hidden.
4. **Elapsed time differs.** Quick reproduction was 17.28 minutes slower than the stated measurement. Timing variability is permitted by the document, but the difference is recorded explicitly.
5. **Expected-hash coverage is overstated in the document.** Its claim that every listed file is regenerated and part of the formal double-run does not match the Makefile. Quick reproduction regenerates the populated draft separately and regenerates the three listed checker files via `formal`, but does not run AuthorityBench or the v8 exhaustive attempt. Those two files remained committed inputs and their hashes are not claimed as fresh reproduction. No exhaustive attempt was run, consistent with the document's warning and the user's requested scope.
6. **“Pinned toolchain” is incomplete.** SciPy is pinned and siblings are commit-pinned, but bootstrap leaves several tools and runtime dependencies unpinned. The actual resolved versions are recorded; they were not manually changed to chase expected hashes.
7. **Independence and filing remain unfulfilled.** This run is not an independent person's attestation, machine-history independence is unverified, and this report has not been filed as a GitHub issue. No change to FINAL-AUDIT item 11 is asserted.

**Anything else worth noting**

The user requested no repository modification. No manual repository edits, commits, restores, patches or pushes were performed; the prescribed commands necessarily rewrote generated outputs and created ignored build/test artifacts. A direct `git diff --exit-code -- . ':(exclude)out'` returned success. The four generated tracked-output differences above remain visible; it would be inaccurate to call the working tree wholly unchanged.

The retained report from `quick-reproduce` contains a paper-freshness description referring to a `make release-check` run even though the actual executed target was `quick-reproduce`. Its wording is not evidence that the optional authority-derivation release/mutation gate ran. This report's claims are based on the command ledger and actual logs instead.

The evidence bundle contains the original procedure/template/Makefile snapshots in the inspection logs, complete target output, exact wrapper scripts, first-formal-run output, stage snapshots, package inventories, retained wheel/sdist, generated-output diff, expected-hash verification and SHA-256 manifest. Preliminary discovery and status-polling shell calls are separately transcribed in `tool-command-transcript.md`; unlike substantive commands, they were not all independently stopwatch-timed. A harmless `printf` heading error in evidence-copy command 13 is retained; hashing, copying and test-count extraction still succeeded. An initial ordinary `nohup` launch did not persist and executed no recorded reproduction stage; the successful run used a separate process session via `setsid`.

**Disposition:** technical reproduction with documented deviations and a recovered packaging prerequisite, not certification of a fully independent reproduction. This is an issue-template-formatted draft, not a submitted issue.
