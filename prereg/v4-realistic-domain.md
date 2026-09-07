# v4: A Realistic Software-and-Cloud Domain for Core-Versus-Reduct Evidence (pre-registration)

Status: PRE-REGISTRATION. No code in this commit. To be tagged
`prereg-p5-v4` on this commit, by the author, via the GitHub web
interface (this pipeline never creates or pushes tags). No v4 code
(`domain_v4.py`, `losses_v4.py`, any new checker reading this file's
declared structure) may be written before this file is committed and
tagged, per this project's own registration discipline.

v0.1-v0.4's own results, checkers, and outputs stay frozen and cited as
prior iterations. Nothing already committed is retroactively edited to
match v4's outcome.

## Provenance and motivation

Every core-versus-reduct result so far (CH-A8, CH-A9, CH-A10,
Negative Proposition N) is either the artifact's own single retail-
procurement domain (six or seven declared losses over nine or ten
candidate properties, `prereg/loss-model.yaml`) or an abstract two-state
toy fixture built to exhibit one specific failure mode. Milestone C asks
a different question: on a domain built independently, from a different
application area, with loss predicates transcribed from published
security/access-control sources rather than authored for this project --
does the core-versus-reduct distinction (Definitions 4-6,
`prereg/v3-core-reduct-correction.md`) show up at all, or is the
procurement domain's own core-happens-to-be-sufficient result (CH-A8,
CH-A10) an artifact of that one domain's particular structure? Both
outcomes are registered as valid below; `reduct.py`'s machinery
(unchanged, not touched by this milestone) is applied to a new domain,
not modified for it.

## The domain: software-and-cloud execution agent

An agent (a CI pipeline, an on-call engineer, a contractor, an
automation bot) requests to execute one operation against one repository
resource. Ten candidate observations, each a per-decision field with a
small declared finite domain (exhaustive sweep, matching v1's/v2's own
convention -- no candidate property has a continuous or unbounded
domain):

| # | Property | Declared domain |
|---|---|---|
| 1 | `actor_identity` | `{agent-ci-bot, agent-oncall-engineer, agent-contractor, agent-automated-pipeline}` |
| 2 | `delegated_role` | `{role-owner, role-deployer, role-contractor-readonly, role-security-admin}` |
| 3 | `repository` | `{repo-billing, repo-public-website, repo-internal-tools}` |
| 4 | `branch` | `{main, staging, feature}` |
| 5 | `environment` | `{production, staging, development}` |
| 6 | `resource_owner` | `{tenant-a, tenant-b}` |
| 7 | `operation` | `{read, write, deploy, delete, grant_role}` |
| 8 | `approval_token` | `{valid, absent}` |
| 9 | `deployment_window` | `{in_window, out_of_window}` |
| 10 | `data_classification` | `{public, internal, secret}` |

Rank-0 (fully unconstrained) size: 4x4x3x3x3x2x5x2x2x3 = 51,840 tuples --
larger than v2's 24,624, still exhaustively enumerable in the same style
`domain.py`'s existing `rank0_reachable_tuples*` functions already use,
no sampling.

**Declared background configuration** (analogous to `loss-model.yaml`'s
`role_entitlement_ceiling`/`role_entitlement_window`/`role_allowed_
classes` -- per-role policy the gate is built with, not itself a
candidate observation, same non-candidacy argument `ADR-002-
participation-tuple-design.md` already makes for v1/v2's own per-role
tables):

- **Role scope** (read by the `cross_tenant_action` loss predicate --
  NOT baked into reachability except where the second bullet below says
  so): `delegated_role -> allowed resource_owner set` -- `role-owner`
  and `role-security-admin`: both tenants (unscoped); `role-deployer`
  and `role-contractor-readonly`: `{tenant-a}` only. Deliberately NOT
  keyed by `actor_identity`: this domain's tenant boundary is a property
  of the role granted for one decision, not of who holds it, so
  `actor_identity`'s own participation (if any) has to come from
  elsewhere -- registered here, not engineered around, since a candidate
  property genuinely not mattering (v1's/v2's own `workflow`) is exactly
  the kind of honest finding this exercise exists to allow.
- **Role operation ceiling**: `delegated_role -> allowed operation set`
  -- `role-owner`: all five; `role-deployer`: `{read, write, deploy}`;
  `role-contractor-readonly`: `{read}`; `role-security-admin`: `{read,
  grant_role}`.
- **Role data-classification clearance**: `delegated_role -> highest
  data_classification cleared` -- `role-owner` and `role-security-admin`:
  `secret`; `role-deployer`: `internal`; `role-contractor-readonly`:
  `public`.
- **Recovery-path declaration**: `(repository, operation) -> has a
  declared remediation operator` -- `deploy` on any repository has
  `rollback` declared; `delete` on `repo-internal-tools` has `scope-down`
  declared (a deletable staging area); `delete` on `repo-billing` or
  `repo-public-website` has none declared (no rollback/backup path
  registered for those two).

These four tables are declared, machine-readable configuration
(Machine-readable registration below), not candidate observations, by
the same argument v1's/v2's per-role tables already make.

## Loss predicates (six, transcribed from published sources -- citations named here, fetch-verified in Phase C3, not asserted from memory in this commit, exactly the discipline `prereg/v3-core-reduct-correction.md`'s own "Citations to be fetch-verified in Phase B" section already established)

Each predicate below is a deterministic boolean function of the ten
candidate fields and the four declared tables above -- no field outside
this file's own declared structure, no LLM or fuzzy judgment call,
matching this project's own "no LLM inside the derivation" standing
rule.

1. **`unauthorised_mutation`**. `operation in {write, deploy, delete,
   grant_role}` (a mutating operation) AND `operation` is not in
   `delegated_role`'s declared operation ceiling. Source category:
   role-based access control's own mediation-of-mutating-operations
   principle -- to be cited against Sandhu et al., "Role-Based Access
   Control Models" (IEEE Computer, 1996), and/or NIST SP 800-53's AC-3
   (Access Enforcement) control.
2. **`production_deployment_without_approval`**. `environment ==
   production` AND `operation == deploy` AND `approval_token == absent`.
   Source category: change-management / deployment-approval-gate
   practice -- to be cited against NIST SP 800-53's CM-3 (Configuration
   Change Control) and/or the change-management chapter of Google's
   *Site Reliability Engineering* (O'Reilly, freely published).
3. **`secret_exposure`**. `data_classification == secret` AND
   `operation in {read, write}` AND `data_classification` exceeds
   `delegated_role`'s declared clearance. Source category: secrets-
   management guidance -- to be cited against OWASP's secrets-management
   cheat sheet and/or CWE-798 (Use of Hard-coded Credentials, as the
   canonical weakness class this predicate detects exposure paths for).
4. **`cross_tenant_action`**. `resource_owner` is outside
   `delegated_role`'s declared scope (role-scope table above). Genuinely
   satisfiable, not defined away by reachability: the reachability rule
   below constrains only `role-contractor-readonly` to `tenant-a` (real
   provisioning -- contractors are never onboarded into `tenant-b`'s
   systems at all); `role-deployer` remains reachable against BOTH
   tenants (deployers share cross-tenant CI infrastructure) even though
   its declared scope is `tenant-a` only, so `role-deployer` acting on
   `tenant-b` is exactly this predicate's live, catchable case. Source
   category: multi-tenant isolation -- to be cited against the Cloud Security
   Alliance's Cloud Controls Matrix (tenant-isolation domain) and/or
   NIST SP 800-125 (guide to security for full virtualization
   technologies).
5. **`privilege_escalation`**. `operation == grant_role` AND
   `delegated_role` is not `role-owner` or `role-security-admin` (i.e.
   a role without declared grant authority attempting to grant one
   anyway). Source category: MITRE ATT&CK's Privilege Escalation tactic
   (TA0004), a directly citable, actively maintained taxonomy.
6. **`destructive_action_without_recovery_path`**. `operation == delete`
   AND `(repository, operation)` has no declared remediation operator
   (recovery-path table above). Source category: contingency-planning /
   backup-before-destroy practice -- to be cited against NIST SP 800-34
   (Contingency Planning Guide) and/or MITRE ATT&CK's Data Destruction
   technique (T1485) as the failure mode this predicate exists to catch.

**Registration discipline for the citations above**: each "to be cited
against" pointer names a real, independently checkable source by title
and (where applicable) identifier; Phase C3 fetch-verifies each via 2+
independently-worded searches (this project's own citation discipline,
`citation_check.py`) before any predicate's implementation is presented
as sourced, and records url/title/first_author/year in
`verified-citations.json` exactly as v3's Pawlak/Skowron-Rauszer/
Macaroons/UCAN/Biscuit entries already do. A source that does not
verify is replaced with one that does, or the predicate is marked
`[CITE: ...]`-pending in any paper prose -- never asserted unverified.

## Reachability rules (organisational constraints; remediation operators)

- **Production branch implies production environment**: `branch == main`
  is reachable only paired with `environment == production`;
  `branch == staging` only with `environment == staging`; `branch ==
  feature` only with `environment == development`. (A one-to-one branch/
  environment pairing -- deliberately simpler than v1's/v2's own multi-
  valued role/window pairings, so this constraint's own effect on
  candidacy is easy to attribute.)
- **Delegated role implies resource-owner scope -- narrowly, a real
  provisioning fact, not the full policy boundary**: a tuple is
  reachable only if, WHEN `delegated_role == role-contractor-readonly`,
  `resource_owner == tenant-a` -- contractors are never onboarded into
  `tenant-b`'s systems at all, so a contractor-readonly/`tenant-b` tuple
  cannot occur, full stop. `role-deployer` is NOT constrained by this
  rule: it shares cross-tenant CI infrastructure (both tenants are
  reachable for it), even though its declared scope (role-scope table
  above) is `tenant-a` only -- deliberately so, since a reachability
  rule that fully excluded every out-of-scope tuple for every scoped
  role would make `cross_tenant_action`'s own loss predicate
  unsatisfiable by construction (nothing outside scope would ever be
  reachable to violate it), the opposite of what a loss predicate over a
  reachable set is for. `role-owner` and `role-security-admin` reach
  both tenants unconstrained, per their unscoped role-scope entry.
- **Remediation operators**: `rollback` (deploy) and `scope-down`
  (delete on `repo-internal-tools`) are declared, not candidate fields
  themselves -- their PRESENCE as a declared table entry is what
  `destructive_action_without_recovery_path` reads (recovery-path table
  above), mirroring how `composition.py`'s remediation operators feed
  this whole series' reachable-set construction without being candidate
  properties of the decision itself (`appendix-a-proofs.md`'s Proposition
  0/0-general).

`domain_v4.rank0_reachable_tuples()` (Phase C3) is the declared-
constraint-filtered product of the ten domains above under both bullets;
`executable_reachable_tuples()` folds in the remediation operators'
declared effect exactly as v1's/v2's own `executable_reachable_tuples*`
functions already do for this artifact's procurement domain -- ported
pattern, not a new mechanism.

## Decision rule (two-sided; core-sufficient-and-unique is a valid outcome, registered explicitly, not treated as a null result)

**CH-B1 (does this independently-built domain's core fail to be
sufficient, or does more than one reduct exist?)** Decision rule: run
`sufficiency()` and `exact_reducts()` (`reduct.py`, unmodified) against
`domain_v4.executable_reachable_tuples()` and the six-predicate registry
above. **SUPPORTED** (the falsification -- core-versus-reduct actually
bites on an independently-built domain) iff the core is *not* sufficient
(a concrete counterexample pair is reported) OR more than one reduct is
found. **NOT SUPPORTED** iff the core is sufficient AND is the unique
reduct -- registered here, explicitly, as a fully valid, fully reportable
outcome: a domain where core-versus-reduct happens not to matter is
itself evidence about when the distinction is and is not consequential,
not a failed exercise, exactly the standing rule "a registered negative
outcome is reported as NOT SUPPORTED and kept." Either way, `reduct.py`'s
own certificate/counterexample output (Definition 4's sufficiency check,
run directly) is what decides it, not this document's own expectation.

No hypothesis is registered about WHICH loss predicates end up in the
core or WHICH candidate properties turn out redundant -- Phase C3 reports
whatever `sufficiency()`/`exact_reducts()` actually find, the same
discipline CH-A8/CH-A10 already followed for the procurement domain.

## Machine-readable registration (this commit)

- `prereg/v4-realistic-domain.md` (this file) is the only file this
  commit touches. The four declared background-configuration tables
  above (role scope, role operation ceiling, role clearance,
  recovery-path declaration) and the ten candidate domains'
  exact value sets are registered by the table text above -- Phase C3
  transcribes them into `domain_v4.py` unchanged, not re-decided during
  implementation.
- No v4 code (`domain_v4.py`, `losses_v4.py`, or any checker reading
  either) exists yet or is written in this commit -- registration only.

## Registration discipline

- No v4 formal-model or checker code may run before this file is
  committed and tagged `prereg-p5-v4`, by the author, via the GitHub web
  interface.
- v0.1-v0.4's own results, checkers, and outputs stay exactly as
  committed -- byte-frozen apart from the informational
  `generated_at_head_sha` stamp any fresh `make formal` run naturally
  refreshes.
- The six loss predicates' logical definitions above are fixed by this
  registration; Phase C3 may not adjust a predicate's logic to change
  CH-B1's outcome once measured -- exactly the standing rule "registered
  semantics are never retuned to chase a result."
- `NOVELTY.md` gains a fifth amendment once CH-B1's outcome is known,
  stating plainly which registered outcome obtained, the same discipline
  every prior amendment already follows.
- Citations named above ("to be cited against") are not asserted as
  verified by this commit; Phase C3 fetch-verifies each before any paper
  prose treats a predicate as sourced.
