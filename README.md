# sarc-authority-derivation

**This paper's own thesis** (Definition 4 defines sufficiency, Definition 5
minimality, `paper5-authority-derivation-draft-v0.5.md`, never asserted
loosely): **Minimal Sufficient Governance Context** -- compile declared
losses and reachable execution semantics into exact, cost-aware runtime
authority contracts for autonomous systems.

Author: Gaston Besanson. Drafting, engineering, formal derivation, and
citation verification were AI-assisted (Claude); the author is solely
responsible for all claims.

## Realistic multiple reducts: core != reduct, on a real domain

A real code/cloud execution-agent domain (`domain_v4.py`, not planted to
exhibit this): the individually-indispensable **core** is *not* enough
on its own, and there is more than one way to close the gap.

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

Prints a 6-of-10-attribute core that is **not sufficient**, and exactly
two 7-attribute reducts, differing in one observation (`branch` vs.
`environment`) -- machine-checked (`checkers/ch_b1_check.py`), not
hand-picked. This is the flagship result: a real domain where a
declared-only policy the shape of most shipped authority configs would
not be exactly sufficient, and where the gap closes in more than one
operationally-different way.

## One call: `authority_compiler`

```python
from authority_compiler import derive_authority_contract
# loss_model: Dict[str, Callable]; reachable_semantics: List[tuple];
# candidate_context: Dict[str, List[value]] -- see src/authority_compiler/api.py
contract = derive_authority_contract(loss_model, reachable_semantics, candidate_context)
contract.core_attributes            # Definition 6
contract.minimum_cardinality_reduct # Definition 5, cardinality-MaxSAT
contract.minimum_cost_reduct        # Definition 5, weighted MaxSAT (if observation_costs given)
contract.sufficiency_certificate    # the partition itself, not a bare boolean
```

Installable: `pip install .` (or a built wheel, `python -m build`) gives
a real, standalone `authority_compiler` package -- verified in a fresh
virtual environment with no repository root, pythonpath, editable
install, or sibling directory (`make package-smoke-test`).

## One command: `authority-bench`

```bash
authority-bench          # four baselines x three domains x six metrics -> out/results/authority_bench_v6_1.json
authority-bench --help
```

## Symbolic scaling

Discernibility-family synthesis (SAT / cardinality-MaxSAT / weighted
MaxSAT, `synthesis.py`) on candidate-attribute universes up to 100
properties, where exhaustive reduct enumeration is registered as
expected -- and confirmed -- infeasible within a 300-second budget,
while every synthesis backend still solves in well under a second
(`prereg/v5.3-combinatorial-hardness-scaling.md`,
`out/results/discernibility_scaling_v5_3.json`).

## Cost-aware synthesis

Weighted MaxSAT selects a sufficient (Definition 5) contract by
declared observation cost, not cardinality alone -- proved on a small
hand-derived domain first (`benchmarks.py`'s XOR-bijection construction),
then registered
against a realistic domain (`prereg/v7-cost-sensitive-contracts.md`).

## Live paper

[`paper5-authority-derivation-draft-v0.5.md`](paper5-authority-derivation-draft-v0.5.md)
([populated](paper5-authority-derivation-draft-v0.5-populated.md)).

## Reproduction

[`REPRODUCTION.md`](REPRODUCTION.md): exact commands, expected output
hashes, and measured elapsed times, from a bare clone -- and an issue
template for reporting an independent reproduction attempt.

---

## History: the v1-v0.4 procurement-domain result (below the fold)

This artifact's own originating result -- a formal participation
criterion and a machine-checkable derivation from a declared loss model
to the core observation set a pre-action authority gate must check, on
a registered retail-procurement domain -- is unchanged and is Part II
of the live paper above, in full. Prereg tags `prereg-p5-v1`,
`prereg-p5-v2`, `prereg-p5-v3`, `prereg-p5-v3.1`, `prereg-p5-v4`,
`prereg-p5-v5`, `prereg-p5-v5.1`, `prereg-p5-v5.3`, and `prereg-p5-v6`/
`prereg-p5-v6.1` were each created via the GitHub web interface after
their commits; commit order establishes precedence.

Earlier paper versions are frozen and no longer regenerated or edited:
v0.1 as of commit `37a2e7f` ([source](paper5-authority-derivation-draft-v0.1.md),
[populated](paper5-authority-derivation-draft-v0.1-populated.md)), v0.2
as of commit `7112031` ([source](paper5-authority-derivation-draft-v0.2.md),
[populated](paper5-authority-derivation-draft-v0.2-populated.md)), v0.3
as of commit `382be13` ([source](paper5-authority-derivation-draft-v0.3.md),
[populated](paper5-authority-derivation-draft-v0.3-populated.md)), v0.4
as of the commit Package B's version-split makes
([source](paper5-authority-derivation-draft-v0.4.md),
[populated](paper5-authority-derivation-draft-v0.4-populated.md)) --
v0.4's own 60-second example (the v2 procurement model: a 9-property
core that is sufficient and the unique reduct, CH-A8/CH-A10) is
preserved there, unedited.
