---
name: Reproduction report
about: Report an independent attempt to reproduce this artifact's own results (REPRODUCTION.md)
title: "Reproduction report: "
labels: reproduction
assignees: ''
---

<!--
Thank you for attempting to reproduce this artifact's own results.
This template follows REPRODUCTION.md's own eight-point reproduction
standard -- fill in what you can; leaving a field blank is fine if it
does not apply to what you ran. Only reports filed here move
FINAL-AUDIT.md's own item 11 out of PENDING.
-->

**Are you independent of this repository's development?**
<!-- Not the author, and not an AI session that did the development
     work on this repository. Yes/No. -->

**Environment**
<!-- Confirm this was not a directory, container, or VM previously
     used to develop this repository -- e.g. "fresh Ubuntu 24.04 VM,
     never cloned this repo before". -->

**Commit sha you tested at**
<!-- git rev-parse HEAD, or the sha in the URL you cloned/downloaded -->

**Operating system**
<!-- e.g. Ubuntu 24.04, macOS 15, Windows 11 + WSL2 -->

**Python version**
<!-- python3 --version -->

**Commands you ran** (check all that apply, or list your own --
`make release-check` is optional given its ~63-minute cost; a report
covering only some of the items below is still a complete one)

- [ ] `bash bootstrap.sh`
- [ ] `make quick-reproduce`
- [ ] `make release-check` (optional, see above)
- [ ] `make package-smoke-test` (wheel install + black-box `authority_compiler` example)
- [ ] `authority-bench`
- [ ] The code/cloud multi-reduct example, CH-B1 (REPRODUCTION.md section 6)
- [ ] The large-domain core-insufficiency example, CH-C1 (REPRODUCTION.md section 6b)
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

**Deviations from REPRODUCTION.md's own expectations**
<!-- Anything that differed: a different hash on the SAME commit sha,
     a different test count, a step that failed, a much longer/shorter
     elapsed time than expected. "None" is a fine answer -- a different
     hash on the SAME commit sha is the single most useful kind of
     report. -->

**Anything else worth noting**
