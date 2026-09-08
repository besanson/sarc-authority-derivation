# sarc-authority-derivation

Author: Gaston Besanson. Drafting, engineering, formal derivation, and citation verification were AI-assisted (Claude); the author is solely responsible for all claims.

Prereg tags `prereg-p5-v1`, `prereg-p5-v2`, `prereg-p5-v3`, `prereg-p5-v3.1`, `prereg-p5-v4`, and `prereg-p5-v5` were each created via the GitHub web interface after their commits; commit order establishes precedence.

Paper draft, live: [`paper5-authority-derivation-draft-v0.4.md`](paper5-authority-derivation-draft-v0.4.md) ([populated](paper5-authority-derivation-draft-v0.4-populated.md)). Earlier versions are frozen and no longer regenerated or edited: v0.1 as of commit `37a2e7f` ([source](paper5-authority-derivation-draft-v0.1.md), [populated](paper5-authority-derivation-draft-v0.1-populated.md)), v0.2 as of commit `7112031` ([source](paper5-authority-derivation-draft-v0.2.md), [populated](paper5-authority-derivation-draft-v0.2-populated.md)), v0.3 as of commit `382be13` ([source](paper5-authority-derivation-draft-v0.3.md), [populated](paper5-authority-derivation-draft-v0.3-populated.md)).

## 60-second example

Runs the derivation on the registered v2 model and prints its core
attribute set (Definition 6), whether that core is sufficient
(Definition 4), and the full exact reduct enumeration (Definition 5) --
after `bash bootstrap.sh` has cloned the pinned siblings once, this
finishes in well under a minute:

```bash
python3 <<'EOF'
from domain import (
    CANDIDATE_PROPERTIES_V2,
    executable_reachable_tuples_v2,
    load_loss_model,
    load_pair_test_grid,
    property_domains_v2,
)
from losses import load_loss_registry_v2
from reduct import compute_core, exact_reducts, sufficiency

loss_model = load_loss_model()
grid = load_pair_test_grid()
registry = load_loss_registry_v2(loss_model)
reachable = executable_reachable_tuples_v2(property_domains_v2(grid))

core, redundant, _witnesses = compute_core(reachable, registry, CANDIDATE_PROPERTIES_V2)
print(f"core ({len(core)} of {len(CANDIDATE_PROPERTIES_V2)} candidates):", core)
print("redundant:", redundant)

is_sufficient, certificate = sufficiency(tuple(core), reachable, registry)
print("core sufficient:", is_sufficient, "--", certificate)

reducts, subsets_considered = exact_reducts(CANDIDATE_PROPERTIES_V2, reachable, registry)
print(f"reducts ({subsets_considered} subsets tested after pruning):", [sorted(r) for r in reducts])
EOF
```

On the committed v2 model this prints a 9-property core that is sufficient
and the unique reduct (CH-A8, CH-A10, `paper5-authority-derivation-draft-v0.4.md`)
-- machine-checked per instance, not assumed in general (Negative
Proposition N, `appendix-a-proofs.md`).