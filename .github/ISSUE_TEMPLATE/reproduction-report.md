---
name: Reproduction report
about: Report an independent attempt to reproduce this artifact's own results (REPRODUCTION.md)
title: "Reproduction report: "
labels: reproduction
assignees: ''
---

<!--
Thank you for attempting to reproduce this artifact's own results.
This template asks for exactly what REPRODUCTION.md needs to compare
your run against the committed expectations -- fill in what you can;
leaving a field blank is fine if it does not apply to what you ran.
-->

**Commit sha you tested at**
<!-- git rev-parse HEAD, or the sha in the URL you cloned/downloaded -->

**Operating system**
<!-- e.g. Ubuntu 24.04, macOS 15, Windows 11 + WSL2 -->

**Python version**
<!-- python3 --version -->

**Commands you ran** (check all that apply, or list your own)

- [ ] `bash bootstrap.sh`
- [ ] `make quick-reproduce`
- [ ] `make release-check`
- [ ] `make package-smoke-test`
- [ ] `authority-bench`
- [ ] The code/cloud multi-reduct example (REPRODUCTION.md section 6)
- [ ] Other:

**Elapsed time**
<!-- Wall-clock time for whichever command(s) above took the longest;
     note which command each time is for if you ran more than one. -->

**Output hashes you got**
<!-- sha256sum on whichever of these files your run produced; only
     fill in the ones you generated -->

| File | Your sha256 |
|---|---|
| `paper5-authority-derivation-draft-v0.5-populated.md` | |
| `out/checkers/ch_b1_check.json` | |
| `out/checkers/ch_c1_check.json` | |
| `out/checkers/ch_c2_check.json` | |
| `out/results/authority_bench_v6_1.json` | |
| `out/results/v8_exhaustive_attempt.json` | |

**Test/mutation results** (if you ran `make quick-reproduce` or `make release-check`)
<!-- test count and pass/fail; mutation score if you ran release-check -->

**Did everything match REPRODUCTION.md's own expectations?**
<!-- Yes / No -- if no, describe exactly what differed (a different
     hash on the SAME commit sha is the most useful kind of report) -->

**Anything else worth noting**
