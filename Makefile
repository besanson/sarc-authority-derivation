.PHONY: bootstrap test formal derive derive_v2 experiments sweep paper release-check mutate ci-local clean help

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
# v2 additions (tag prereg-p5-v2: Proposition 0-general + CH-A5/CH-A6/CH-A7)
# and v3 additions (tag prereg-p5-v3: Proposition 1'/N + CH-A8/CH-A9/CH-A10)
# run alongside v1's own gate below, never in place of it.
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
# v0.3 is the live draft (paper5-authority-derivation-draft-v0.1.md/
# -populated.md are frozen at commit 37a2e7f, and v0.2's at commit
# 7112031 -- see README.md's version-split note -- neither touched by
# this pipeline).
paper: experiments sweep formal
	@echo "Populating paper draft from out/results/sweep_summary.json + out/checkers/*.json..."
	python3 populate_paper.py

release-check:
	@echo "=== release-check: full test suite ==="
	python3 -m pytest -v
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
	@echo "=== release-check: populated-draft freshness ==="
	cp paper5-authority-derivation-draft-v0.3-populated.md /tmp/sarc-p5-populated-committed.md
	python3 populate_paper.py
	diff /tmp/sarc-p5-populated-committed.md paper5-authority-derivation-draft-v0.3-populated.md
	@rm -f /tmp/sarc-p5-populated-committed.md
	@echo "populated draft byte-identical to freshly regenerated: OK"
	@echo "=== release-check: citation gate ==="
	python3 citation_check.py paper5-authority-derivation-draft-v0.3.md
	@echo "=== release-check: typed-numerals lint ==="
	python3 -m checkers.typed_numerals_lint
	@echo "=== release-check: PROOF-STATUS lint ==="
	python3 -m checkers.proof_status_lint
	@echo ""
	@echo "release-check: ALL CHECKS PASS"

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
	rm -f paper5-authority-derivation-draft-v0.3-populated.md
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
	@echo "  make release-check  MANDATORY before any release: tests + formal double-run identity + citation gate + lint"
	@echo "  make mutate         Mutation testing (V5-equivalent gate, target >=0.85)"
	@echo "  make clean          Remove all outputs"
	@echo ""
	@echo "See README.md and RESEARCH-GUIDE.md for full documentation."
