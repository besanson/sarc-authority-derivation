.PHONY: bootstrap test formal derive derive_v2 experiments sweep paper release-check mutate benchmarks discernibility-scaling authority-bench authority-bench-domains xu-stoller-validation time-reproduction time-quick-reproduce quick-reproduce ci-local clean help

# Paper 5: Deriving Authority (sarc-authority-derivation)
# Apache License 2.0
# Release-check pattern ported with attribution from sarc-suite-one-pass
# (commit 782261e) -- see ADR-001-foundation.md.

bootstrap:
	@echo "Bootstrapping pinned siblings (sarc-suite-one-pass + 3 engines) + toolchain + imported-baseline check..."
	bash bootstrap.sh

ci-local: bootstrap test formal
	@echo "ci-local: bootstrap + test + formal all green."

test:
	@echo "Running test suite..."
	python3 -m pytest -v

# Phase 2 / V2 gate: exhaustive checkers over the enumerated finite model.
# v2 additions (tag prereg-p5-v2: Proposition 0-general + CH-A5/CH-A6/CH-A7),
# v3 additions (tag prereg-p5-v3: Proposition 1'/N + CH-A8/CH-A9/CH-A10), and
# v4's independent domain (tag prereg-p5-v4: CH-B1) run alongside v1's own
# gate below, never in place of it -- CH-B1 needs no `derive`/`derive_v2`
# prerequisite (domain_v4.py is entirely self-contained).
formal: derive derive_v2
	@echo "V2 gate: exhaustive checkers (reachability measurement, participation soundness+minimality, pair-test recovery, grant single-use) + proof lint..."
	python3 -m checkers.reachability_check
	python3 -m checkers.participation_check
	python3 -m checkers.pairtest_check
	python3 -m checkers.grant_check
	python3 -m checkers.general_reachability_check
	python3 -m checkers.ch_a5_check
	python3 -m checkers.participation_check_v2
	python3 -m checkers.pairtest_check_v2
	python3 -m checkers.ch_a7_check
	python3 -m checkers.sufficiency_check
	python3 -m checkers.reduct_check
	python3 -m checkers.core_insufficiency_counterexample
	python3 -m checkers.ch_b1_check
	python3 -m checkers.ch_datacomms_check
	python3 -m checkers.discernibility_check
	python3 -m checkers.synthesis_exactness_check
	python3 -m checkers.authority_compiler_check
	python3 -m checkers.proof_status_lint
	@echo "See appendix-a-proofs.md for the proofs these checkers verify."

# Phase 2: run the derivation procedure itself (loss model in, P* + coverage list out).
derive:
	@echo "Running derivation procedure (loss-model.yaml -> P*, coverage list)..."
	python3 derive.py

# v2 (prereg-p5-v2): the v2 derivation procedure (CH-A5/CH-A6's primary computation).
derive_v2:
	@echo "Running v2 derivation procedure (loss-model.yaml v2_losses + pair-test-grid.yaml v2 -> P* v2, coverage list v2)..."
	python3 derive_v2.py

# Phase 3: the experiment scenarios (baseline / derived-P* / over-inclusive, grant on/off, replay injection).
experiments:
	@echo "Running experiment scenarios (both workflows)..."
	python3 experiments.py

# Phase 3 / V3-equivalent gate: 30-seed statistical sweep (prereg/seeds.json).
sweep:
	@echo "30-seed statistical sweep (prereg/seeds.json), CH-A1-CH-A4 + 95% CIs..."
	@echo "Checkpointed per seed under out/results/sweep/ -- safe to re-run/resume."
	python3 sweep.py

# Phase 5: populate the paper draft from committed machine output only.
# v0.4 is the live draft (paper5-authority-derivation-draft-v0.1.md/
# -populated.md are frozen at commit 37a2e7f, v0.2's at commit 7112031,
# and v0.3's at commit 382be13 -- see README.md's version-split note --
# none touched by this pipeline).
paper: experiments sweep formal
	@echo "v0.4 isolation-hypothesis delta (prereg-p5-v3.1: isolated ArmState vs. v0.3's frozen shared-state result)..."
	python3 -m checkers.isolation_delta_check
	@echo "Populating paper draft from out/results/sweep_summary.json + out/checkers/*.json..."
	python3 populate_paper.py

# Milestone D5 (prereg-p5-v5): the two registered synthesis benchmarks
# (planted-reduct scaling, cost-aware synthesis) + one contract_change_delta
# demonstration. NOT wired into release-check or `paper` -- like
# isolation_delta_check.py, it is expensive (~3 minutes: run_cost_aware_
# experiment's build_discernibility_family calls are O(|true-verdict
# tuples| x |false-verdict tuples|) per domain, over v1's 7,776-tuple and
# v2's 24,624-tuple real reachable sets, twice each for the cardinality
# and cost backends) for what prereg/v5-synthesis.md itself registers as
# descriptive, non-gating output (only Experiment 1's `exact` and
# Experiment 2's SUPPORTED/NOT-SUPPORTED carry a pass/fail character, and
# neither is a correctness property of THIS repo's derivation results --
# unlike `make formal`'s checkers -- so neither belongs in the mandatory
# release gate). Re-run explicitly after any change to discernibility.py,
# synthesis.py, benchmarks.py, or the real domains' declared models.
# Experiment 1 (planted-reduct scaling) is exploratory_v5_0 as of
# prereg-p5-v5.1 -- kept, superseded as the primary scaling claim by
# `discernibility-scaling` below (benchmarks.py itself is unmodified).
benchmarks:
	@echo "Synthesis benchmarks (prereg-p5-v5): planted-reduct scaling (exploratory_v5_0, see prereg-p5-v5.1) + cost-aware synthesis + contract_change_delta demo..."
	@echo "(~3 minutes -- see Makefile comment above this target for why.)"
	mkdir -p out/results
	python3 benchmarks.py

# Milestone (prereg-p5-v5.1): discernibility scaling on GROWING
# reachable sets (>=10^3/10^4/10^5 tuples, two planted reducts, not
# one) -- the successor to Experiment 1 above. All three synthesis.py
# backends, plus v2/v4/data-and-communications as real measured points.
# NOT wired into release-check or `paper`, same reasoning as
# `benchmarks`. Takes several minutes (dominated by the three real
# domains' own build_discernibility_family cost, paid once per backend
# per domain -- the synthetic families themselves stay under 3 seconds
# even at 100,001 tuples, by design: only one tuple carries the True
# verdict, so their own discernibility-family cost is linear in
# reachable-set size, not quadratic).
discernibility-scaling:
	@echo "Discernibility scaling (prereg-p5-v5.1): growing reachable sets, two planted reducts, three backends, six families..."
	mkdir -p out/results
	python3 discernibility_scaling_benchmark.py

# Milestone E, Step 4 (prereg-p5-v6.1): AuthorityBench run all -- all
# four registered baselines (manual least-privilege, Xu-and-Stoller
# mining, essential-variable analysis, exhaustive reduct) on all three
# registered domains (v2, v4, data-and-communications), all six metrics.
# Depends on `authority-bench-domains` (Step 2's YAML packaging, itself
# depending on `formal`) and `xu-stoller-validation` (Step 3's gate
# decision this run reads, not re-decides). Writes out/results/
# authority_bench_v6_1.json -- out/results/authority_bench.json is v6.0's
# own exploratory two-baseline/three-domain result (commit 0ecfeb3),
# frozen, not touched by this target. NOT wired into release-check or
# `paper`, same reasoning as `benchmarks`: not a correctness gate on this
# repo's own derivation results. Takes well under a minute (all 3
# domains, well inside the prereg's own 20-minute-per-domain
# tractability budget).
authority-bench: authority-bench-domains xu-stoller-validation
	@echo "AuthorityBench run all (prereg-p5-v6.1): four baselines x three domains x six metrics..."
	mkdir -p out/results
	python3 authority_bench.py

# Milestone E, Step 2 (prereg-p5-v6.1): per-domain YAML packaging
# (candidate-context/loss-model/reachability/baseline-manual-policy/
# expected-certificates) for all three registered AuthorityBench
# domains. Depends on `formal` (reduct_check.json/ch_b1_check.json/
# ch_datacomms_check.json must be fresh) -- run explicitly, not part of
# release-check, same non-gating reasoning as `benchmarks`/
# `authority-bench`.
authority-bench-domains: formal
	@echo "Packaging AuthorityBench's three domains as YAML (authority_bench_domains/)..."
	python3 build_authority_bench_domain_yaml.py

# Milestone E, Step 3 (prereg-p5-v6.1): the Xu-and-Stoller validation
# gate for the "ABAC policy mining" baseline -- runs mining_baseline.py
# (unmodified) against the real "Health Care Sample Policy" case study
# from Xu and Stoller's own published software release, and checks the
# result against Figure 5's published statistics under the tolerance
# registered in xu_stoller_validation.py's own module docstring, decided
# there before this was ever run. NOT wired into release-check or `paper`
# -- same reasoning as `benchmarks`/`authority-bench`: a one-time gate
# decision (VALIDATED vs. EXCLUDED: UNVALIDATED), not a correctness
# property of this repo's own derivation results, and not something that
# needs re-deciding on every release. Re-run explicitly after any change
# to mining_baseline.py.
xu-stoller-validation:
	@echo "Xu-and-Stoller validation gate (prereg-p5-v6.1): mining_baseline.py vs. the real healthcare.abac case study..."
	mkdir -p out/results
	python3 xu_stoller_validation.py

# Milestone E, Step 6 (prereg-p5-v6.1): a genuinely bare `git clone` of
# this repo alone (NOT the pinned siblings, which bootstrap.sh's own
# phase clones) through `bash bootstrap.sh && make release-check`,
# timed end to end in a disposable temp directory this script deletes
# when it finishes. Writes out/reproduction_timing.json; run `make
# release-check` again afterward (or just `python3 reproducibility_
# report.py`) to fold the timing into out/reproducibility-report.json's
# own `reproduction_timing` field. NOT wired into release-check itself
# -- it would be circular (this repo's own release-check already runs
# inside the sequence being timed) and takes far longer than a normal
# release-check (bootstrap.sh clones four more repos over the network
# and runs sarc-suite-one-pass's own full release-check as its
# imported-baseline verification step). Target "about five minutes"
# (task brief's own E4 language) is descriptive, not a pass/fail gate --
# see time_reproduction.py's own module docstring.
time-reproduction:
	@echo "Timed bare-clone reproduction (prereg-p5-v6.1): git clone + bootstrap.sh + make release-check, in a disposable temp directory..."
	mkdir -p out
	python3 time_reproduction.py

# Repair 3 (no separate prereg -- tooling, not a registered result): the
# same bare-clone+bootstrap+restore harness as `time-reproduction` above,
# timing `make quick-reproduce` instead of `make release-check`, so the
# two figures are measured under identical bare-clone conditions and are
# genuinely comparable side by side. Writes out/reproduction_timing_quick.json,
# folded into out/reproducibility-report.json's own quick_reproduce_timing
# field alongside reproduction_timing.
time-quick-reproduce:
	@echo "Timed bare-clone reproduction, quick-reproduce path (repair 3): git clone + bootstrap.sh + make quick-reproduce, in a disposable temp directory..."
	mkdir -p out
	python3 time_reproduction.py quick-reproduce

release-check:
	@echo "=== release-check: full test suite ==="
	mkdir -p out
	python3 -m pytest -v --junit-xml=out/pytest-junit.xml
	@echo "=== release-check: formal double-run byte identity ==="
	rm -rf /tmp/sarc-p5-release-check-formal-1 /tmp/sarc-p5-release-check-formal-2
	mkdir -p /tmp/sarc-p5-release-check-formal-1 /tmp/sarc-p5-release-check-formal-2
	$(MAKE) formal
	cp out/checkers/*.json /tmp/sarc-p5-release-check-formal-1/
	$(MAKE) formal
	cp out/checkers/*.json /tmp/sarc-p5-release-check-formal-2/
	diff -rq /tmp/sarc-p5-release-check-formal-1 /tmp/sarc-p5-release-check-formal-2
	@rm -rf /tmp/sarc-p5-release-check-formal-1 /tmp/sarc-p5-release-check-formal-2
	@echo "formal double-run byte-identical: OK"
	@echo "=== release-check: mutation testing (hard gate, >=0.85; see ADR-003-mutation-testing.md) ==="
	$(MAKE) mutate
	@echo "=== release-check: populated-draft freshness ==="
	@echo "(isolation_delta_check.json is NOT recomputed here -- it re-sweeps all 60"
	@echo " (seed, workflow) cells against the real imported simulation, minutes not"
	@echo " seconds; committed as of the v0.4 commit, re-run explicitly via"
	@echo " 'make paper' or 'python3 -m checkers.isolation_delta_check' after any"
	@echo " change to experiments.py, prereg/seeds.json, or the declared loss model.)"
	cp paper5-authority-derivation-draft-v0.4-populated.md /tmp/sarc-p5-populated-committed.md
	python3 populate_paper.py
	diff /tmp/sarc-p5-populated-committed.md paper5-authority-derivation-draft-v0.4-populated.md
	@rm -f /tmp/sarc-p5-populated-committed.md
	@echo "populated draft byte-identical to freshly regenerated: OK"
	@echo "=== release-check: citation gate ==="
	python3 citation_check.py paper5-authority-derivation-draft-v0.4.md
	@echo "=== release-check: typed-numerals lint ==="
	python3 -m checkers.typed_numerals_lint
	@echo "=== release-check: terminology lint ==="
	python3 -m checkers.terminology_lint
	@echo "=== release-check: PROOF-STATUS lint ==="
	python3 -m checkers.proof_status_lint
	@echo "=== release-check: reproducibility report (out/reproducibility-report.json) ==="
	python3 reproducibility_report.py
	@echo ""
	@echo "release-check: ALL CHECKS PASS"

# `release-check`'s own recipe, minus the mutation-testing gate --
# deliberately duplicated rather than factored out (Make has no clean
# way to splice a skippable step into the MIDDLE of a target's own
# recipe without a fragile sub-make chain; both targets are short
# enough that keeping them in obvious lockstep by eye is the more
# robust choice). If release-check's own recipe changes, mirror the
# change here too, everything except the mutation section. Exists so
# `time_reproduction.py quick-reproduce` can report a genuine "full
# path minus mutation" timing alongside the ~35-minute full figure
# (repair 3, NOVELTY.md's Eleventh amendment).
#
# An assumption this comment used to make, corrected by actually
# measuring it: this used to say mutation testing was release-check's
# "dominant cost (roughly 30 of the 35 minutes)", written before this
# target was ever timed end to end. The real bare-clone figures are
# ~35.4 minutes WITH mutation and ~36.5 minutes WITHOUT it -- two
# independent runs, not a controlled paired trial, so mutation's own
# marginal cost cannot be cleanly isolated by subtracting them; the
# pytest suite + double `make formal` run + populated-draft
# regeneration + lints dominate the wall-clock either way, in this
# shared environment, at least as much as mutation does. This target
# still earns its keep: it gives a contributor without mutmut set up,
# or who just wants the hard gate skipped rather than the fast(er)
# path, a real one -- "quick" undersells it; "release-check minus the
# mutation gate" is the honest description.
quick-reproduce:
	@echo "=== quick-reproduce: full test suite ==="
	mkdir -p out
	python3 -m pytest -v --junit-xml=out/pytest-junit.xml
	@echo "=== quick-reproduce: formal double-run byte identity ==="
	rm -rf /tmp/sarc-p5-quick-reproduce-formal-1 /tmp/sarc-p5-quick-reproduce-formal-2
	mkdir -p /tmp/sarc-p5-quick-reproduce-formal-1 /tmp/sarc-p5-quick-reproduce-formal-2
	$(MAKE) formal
	cp out/checkers/*.json /tmp/sarc-p5-quick-reproduce-formal-1/
	$(MAKE) formal
	cp out/checkers/*.json /tmp/sarc-p5-quick-reproduce-formal-2/
	diff -rq /tmp/sarc-p5-quick-reproduce-formal-1 /tmp/sarc-p5-quick-reproduce-formal-2
	@rm -rf /tmp/sarc-p5-quick-reproduce-formal-1 /tmp/sarc-p5-quick-reproduce-formal-2
	@echo "formal double-run byte-identical: OK"
	@echo "=== quick-reproduce: mutation testing SKIPPED (see release-check for the hard gate) ==="
	@echo "=== quick-reproduce: populated-draft freshness ==="
	cp paper5-authority-derivation-draft-v0.4-populated.md /tmp/sarc-p5-quick-populated-committed.md
	python3 populate_paper.py
	diff /tmp/sarc-p5-quick-populated-committed.md paper5-authority-derivation-draft-v0.4-populated.md
	@rm -f /tmp/sarc-p5-quick-populated-committed.md
	@echo "populated draft byte-identical to freshly regenerated: OK"
	@echo "=== quick-reproduce: citation gate ==="
	python3 citation_check.py paper5-authority-derivation-draft-v0.4.md
	@echo "=== quick-reproduce: typed-numerals lint ==="
	python3 -m checkers.typed_numerals_lint
	@echo "=== quick-reproduce: terminology lint ==="
	python3 -m checkers.terminology_lint
	@echo "=== quick-reproduce: PROOF-STATUS lint ==="
	python3 -m checkers.proof_status_lint
	@echo "=== quick-reproduce: reproducibility report (out/reproducibility-report.json) ==="
	python3 reproducibility_report.py
	@echo ""
	@echo "quick-reproduce: ALL CHECKS PASS (mutation gate not included -- not a substitute for release-check)"

mutate:
	@echo "Mutation testing participation.py + derive.py + reduct.py (hard gate, >=0.85; see ADR-003-mutation-testing.md)..."
	rm -rf mutants .mutmut-cache
	mutmut run
	mutmut results
	mutmut export-cicd-stats
	python3 mutation_check.py

clean:
	@echo "Cleaning up outputs..."
	rm -rf out/
	rm -f paper5-authority-derivation-draft-v0.4-populated.md
	rm -rf .pytest_cache .hypothesis
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

help:
	@echo "Paper 5: Deriving Authority (sarc-authority-derivation)"
	@echo ""
	@echo "  make bootstrap      Clone pinned siblings + toolchain + verify imported baseline"
	@echo "  make ci-local       bootstrap + test + formal (local acceptance for ci.yml)"
	@echo "  make test           Run the test suite"
	@echo "  make formal         V2 gate: exhaustive checkers + proof lint"
	@echo "  make derive         Run the derivation procedure (loss model -> P* + coverage list)"
	@echo "  make experiments    Run the Phase 3 experiment scenarios"
	@echo "  make sweep          30-seed statistical sweep, CH-A1-CH-A4 means + 95% CIs"
	@echo "  make paper          Populate the paper draft from committed machine output"
	@echo "  make release-check  MANDATORY before any release: tests + formal double-run identity + mutation gate + citation gate + lint + reproducibility report"
	@echo "  make quick-reproduce  release-check's full path MINUS the mutation gate (see Makefile comment); not a substitute for release-check"
	@echo "  make mutate         Mutation testing (V5-equivalent gate, target >=0.85)"
	@echo "  make benchmarks     Synthesis benchmarks (prereg-p5-v5): scaling (exploratory_v5_0) + cost-aware + contract_change_delta (~3 min, not part of release-check)"
	@echo "  make discernibility-scaling  Discernibility scaling on growing reachable sets (prereg-p5-v5.1): two planted reducts, three backends, six families"
	@echo "  make authority-bench AuthorityBench run all (prereg-p5-v6.1): four baselines x three domains x six metrics (not part of release-check)"
	@echo "  make authority-bench-domains  Package the 3 AuthorityBench domains as YAML (prereg-p5-v6.1)"
	@echo "  make xu-stoller-validation  Xu-and-Stoller mining-baseline validation gate (prereg-p5-v6.1, ~1 sec)"
	@echo "  make time-reproduction  Timed bare-clone reproduction: git clone + bootstrap.sh + make release-check (prereg-p5-v6.1, slow)"
	@echo "  make time-quick-reproduce  Same harness, timing make quick-reproduce instead (repair 3): comparable bare-clone figure minus mutation"
	@echo "  make clean          Remove all outputs"
	@echo ""
	@echo "See README.md and RESEARCH-GUIDE.md for full documentation."
