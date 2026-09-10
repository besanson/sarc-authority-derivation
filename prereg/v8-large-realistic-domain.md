# v8: A Large, Non-Planted Enterprise Code/Cloud Domain (pre-registration)

Status: PRE-REGISTRATION. No code in this commit. To be tagged
`prereg-p5-v8` on this commit, by the author, via the GitHub web
interface (this pipeline never creates or pushes tags). No v8 code
(`domain_v8.py`, `losses_v8.py`, `costs_v8.py`, any new checker or
`synthesis.py` extension reading this file's declared structure) may be
written before this file is committed and tagged, per this project's
own registration discipline.

v0.1-v0.4's, v4's, and v7's own results, checkers, and outputs stay
frozen and cited as prior iterations. Nothing already committed is
retroactively edited to match this package's outcome.

## Provenance and motivation

CH-B1/CH-B2 (v4, v7) establish core-versus-reduct and cost-sensitive
differentiation on a 10-candidate-property domain. This package asks
whether the same distinctions survive at a scale close to a real
enterprise's actual attribute surface -- 30-50 candidate properties,
not planted to exhibit any particular structure -- and whether this
project's own machinery (`reduct.py`, `synthesis.py`, unmodified except
one small, justified addition registered below) still produces sound,
certified answers when exhaustive reduct enumeration is no longer an
option at all (`C(35, 7)` alone is 6,724,520; the full power set is
`2^35`, astronomically past `prereg/v5.3-combinatorial-hardness-
scaling.md`'s own synthetic 100-property scaling result's own tractable
range for anything exhaustive).

**Sizing, not outcome, pre-checked**: the reachable-tuple COUNT below
was verified computationally tractable (a plain combinatorial
multiplication, run before any of this domain's actual loss predicates
or reachability logic existed as code) so that `build_discernibility_
family`'s own O(|verdict=true| x |verdict=false|) pairwise construction
(`discernibility.py`) finishes in minutes, not hours -- an engineering
feasibility check, exactly the same kind of pre-registration arithmetic
`prereg/v5.3-combinatorial-hardness-scaling.md` already did for its own
synthetic construction. No core, reduct, or cost outcome for THIS
domain was computed, peeked at, or used to choose any declared value
below; every declared property domain, reachability rule, and loss
predicate was chosen for organisational plausibility alone, before this
document was written, and is frozen by this commit.

## The domain: a larger, independently-structured enterprise code/cloud action

An agent (the same four kinds of principal v4 already uses, unmodified
here except a larger, independent property surface) requests to execute
one operation against one repository resource. **35 candidate
properties, seven from each of five families** (identity and
delegation; resource; action; workflow; evidence and state) -- three
more than v4's ten, from a structurally different, deliberately larger
design, not an extension of v4's own ten:

### Family 1: Identity and delegation

| # | Property | Declared domain |
|---|---|---|
| 1 | `actor_identity` | `{ci-bot, oncall-engineer, contractor, automated-pipeline}` |
| 2 | `delegated_role` | `{role-owner, role-deployer, role-contractor-readonly, role-security-admin}` |
| 3 | `actor_authentication_strength` | `{mfa, hardware-key}` |
| 4 | `delegation_chain_depth` | `{direct, one-hop-delegated}` |
| 5 | `session_assurance_level` | `{medium, high}` |
| 6 | `identity_provider_trust_tier` | `{tier-1-internal, tier-3-external}` |
| 7 | `on_call_status` | `{on-call, not-on-call}` |

### Family 2: Resource

| # | Property | Declared domain |
|---|---|---|
| 8 | `repository` | `{repo-billing, repo-public-website, repo-internal-tools, repo-ml-pipeline}` |
| 9 | `resource_owner` | `{tenant-a, tenant-b, tenant-c}` |
| 10 | `resource_environment` | `{production, staging, development}` |
| 11 | `resource_criticality_tier` | `{tier-0-critical, tier-1-important, tier-2-standard}` |
| 12 | `data_classification` | `{public, internal, confidential, secret}` |
| 13 | `data_residency_region` | `{us, eu, apac}` |
| 14 | `encryption_at_rest_status` | `{encrypted, unencrypted}` |

### Family 3: Action

| # | Property | Declared domain |
|---|---|---|
| 15 | `operation` | `{read, write, deploy, delete, grant_role}` |
| 16 | `operation_criticality` | `{low, medium, high}` |
| 17 | `batch_size` | `{single-item, bulk}` |
| 18 | `automation_level` | `{manual, fully-automated}` |
| 19 | `api_or_console_origin` | `{api, console}` |
| 20 | `rate_limit_bucket_state` | `{normal, throttled}` |
| 21 | `destination_endpoint_class` | `{internal-only, external-facing}` |

### Family 4: Workflow

| # | Property | Declared domain |
|---|---|---|
| 22 | `workflow_stage` | `{draft, review, approved, executing, completed}` |
| 23 | `change_ticket_linked` | `{linked, not-linked}` |
| 24 | `approval_token` | `{valid, absent, expired}` |
| 25 | `approval_quorum_met` | `{met, not-met}` |
| 26 | `deployment_window` | `{out_of_window, in_window}` |
| 27 | `rollback_plan_declared` | `{declared, not-declared}` |
| 28 | `sla_tier` | `{gold, silver, bronze}` |

### Family 5: Evidence and state

| # | Property | Declared domain |
|---|---|---|
| 29 | `audit_logging_enabled` | `{enabled, disabled}` |
| 30 | `session_recording_enabled` | `{enabled, disabled}` |
| 31 | `previous_violation_flag` | `{clean, flagged}` |
| 32 | `anomaly_score_bucket` | `{normal, elevated}` |
| 33 | `evidence_retention_class` | `{standard, extended, legal-hold}` |
| 34 | `network_zone` | `{corp-trusted, vpn, public-internet}` |
| 35 | `device_posture` | `{managed-compliant, managed-noncompliant, unmanaged}` |

Every declared value above occurs on at least one reachable tuple under
the reachability rules below (verified by the same sizing check, not
assumed) -- no candidate property carries a structurally-unreachable
value, matching this project's own "exhaustive sweep, no vacuous
domain entries" convention (v1-v4's own `rank0_reachable_tuples*`
discipline).

## Reachability (the six organisational categories the task brief itself names)

Six independent (or jointly-constrained, where named) drivers generate
the entire reachable set; every other property above is a **fully
deterministic function of one or two of these drivers** (tables below)
-- not free, not sampled, not planted toward any particular reduct: the
determinism reflects ordinary enterprise metadata redundancy (most
attributes of a request ARE derived from a handful of real decisions),
the same phenomenon `branch`/`environment`'s 1:1 pairing already
demonstrated on a smaller scale in v4.

**1. Delegation state** (`actor_identity`, `delegated_role` jointly
constrained -- which roles a given kind of principal actually holds,
five valid pairs, a real provisioning fact, not a full cross product):
`(ci-bot, role-deployer)`, `(oncall-engineer, role-owner)`,
`(oncall-engineer, role-deployer)`, `(contractor, role-contractor-
readonly)`, `(automated-pipeline, role-security-admin)`.

**2. Resource topology** (`repository`, `resource_owner` jointly
constrained -- which tenant a given repository actually belongs to,
five valid pairs): `(repo-billing, tenant-a)`, `(repo-public-website,
tenant-a)`, `(repo-public-website, tenant-b)`, `(repo-internal-tools,
tenant-b)`, `(repo-ml-pipeline, tenant-c)`.

**3. Workflow constraints x approval state** (`workflow_stage`,
`approval_token` jointly constrained, nine valid pairs): `draft` and
`review` are reachable with ANY of the three `approval_token` values
(six pairs); `approved`, `executing`, and `completed` are reachable
ONLY with `approval_token == valid` (three pairs) -- a live-in-progress
change cannot be in an approved/executing/completed stage on an absent
or expired token, a real process constraint, not an artifact.

**4. Environment topology** (`resource_environment`, `network_zone`,
`device_posture` jointly constrained, six valid triples):
`(production, corp-trusted, managed-compliant)`, `(staging, corp-
trusted, managed-compliant)`, `(staging, vpn, managed-compliant)`,
`(staging, vpn, managed-noncompliant)`, `(development, corp-trusted,
managed-compliant)`, `(development, public-internet, unmanaged)`.

**5. Data sensitivity**: `data_classification` (four values) is an
independent driver, unconstrained by the other five.

**6. Tool capabilities**: `operation` (five values) is an independent
driver, unconstrained by the other five.

**Rank-0 reachable-tuple count** (the product of the six drivers'
valid-combination counts above, exhaustively verified by direct
enumeration, not estimated): `5 (delegation) x 5 (resource) x 9
(workflow/approval) x 6 (environment) x 4 (data_classification) x 5
(operation) = 27,000`. Every one of the other 29 declared properties is
then a deterministic function of these six (derivation tables below),
so the reachable set's true cardinality is exactly 27,000, not 27,000
times some further free-property multiplier.

### Deterministic derivation tables (the other 29 properties)

- `actor_authentication_strength` (from `actor_identity`): ci-bot,
  automated-pipeline -> `hardware-key`; oncall-engineer, contractor ->
  `mfa`.
- `delegation_chain_depth` (from `delegated_role`): role-contractor-
  readonly -> `one-hop-delegated`; all others -> `direct`.
- `session_assurance_level` (from `actor_authentication_strength`):
  `hardware-key` -> `high`; `mfa` -> `medium`.
- `identity_provider_trust_tier` (from `actor_identity`): contractor ->
  `tier-3-external`; all others -> `tier-1-internal`.
- `on_call_status` (from `actor_identity`): oncall-engineer ->
  `on-call`; all others -> `not-on-call`.
- `resource_criticality_tier` (from `repository`): repo-billing ->
  `tier-0-critical`; repo-public-website, repo-ml-pipeline ->
  `tier-1-important`; repo-internal-tools -> `tier-2-standard`.
- `data_residency_region` (from `resource_owner`): tenant-a -> `us`;
  tenant-b -> `eu`; tenant-c -> `apac`.
- `encryption_at_rest_status` (from `data_classification`): `public` ->
  `unencrypted`; `internal`, `confidential`, `secret` -> `encrypted`.
- `operation_criticality` (from `operation`): `read` -> `low`; `write`
  -> `medium`; `deploy`, `delete`, `grant_role` -> `high`.
- `batch_size` (from `operation`): `delete` -> `bulk`; all others ->
  `single-item`.
- `automation_level` (from `actor_identity`): ci-bot, automated-
  pipeline -> `fully-automated`; oncall-engineer, contractor ->
  `manual`.
- `api_or_console_origin` (from `automation_level`): `fully-automated`
  -> `api`; `manual` -> `console`.
- `rate_limit_bucket_state` (from `automation_level`): `fully-
  automated` -> `throttled`; `manual` -> `normal`.
- `destination_endpoint_class` (from `repository`): repo-public-
  website -> `external-facing`; all others -> `internal-only`.
- `change_ticket_linked` (from `resource_criticality_tier` +
  `operation_criticality`): `linked` iff `resource_criticality_tier !=
  tier-2-standard` AND `operation_criticality == high`; else `not-
  linked`.
- `approval_quorum_met` (from `workflow_stage` + `approval_token`):
  `met` iff `workflow_stage` in `{approved, executing, completed}`
  (which, per reachability rule 3, always pairs with `approval_token ==
  valid`); `not-met` iff `workflow_stage` in `{draft, review}`.
- `deployment_window` (from `workflow_stage`): `draft`, `review` ->
  `out_of_window`; `approved`, `executing`, `completed` -> `in_window`.
- `rollback_plan_declared` (from `repository` + `operation`): `declared`
  iff `operation == deploy`, OR (`operation == delete` AND `repository
  == repo-internal-tools`); else `not-declared`.
- `sla_tier` (from `resource_criticality_tier`): `tier-0-critical` ->
  `gold`; `tier-1-important` -> `silver`; `tier-2-standard` -> `bronze`.
- `audit_logging_enabled` (from `resource_criticality_tier`): `tier-0-
  critical`, `tier-1-important` -> `enabled`; `tier-2-standard` ->
  `disabled`.
- `session_recording_enabled` (from `delegated_role`): role-contractor-
  readonly -> `enabled`; all others -> `disabled`.
- `previous_violation_flag` (from `actor_identity`): contractor ->
  `flagged`; all others -> `clean`.
- `anomaly_score_bucket` (from `previous_violation_flag`): `flagged` ->
  `elevated`; `clean` -> `normal`.
- `evidence_retention_class` (from `data_classification`): `public`,
  `internal` -> `standard`; `confidential` -> `extended`; `secret` ->
  `legal-hold`.

Declared role tables used only by the loss predicates below (background
configuration, not candidate observations -- the same non-candidacy
argument `ADR-002-participation-tuple-design.md` and
`prereg/v4-realistic-domain.md` already make for this project's other
per-role tables):

- **Role operation ceiling**: role-owner -> all five operations; role-
  deployer -> `{read, write, deploy}`; role-contractor-readonly ->
  `{read}`; role-security-admin -> `{read, grant_role}`.
- **Role data-classification clearance**: role-owner, role-security-
  admin -> `secret`; role-deployer -> `internal`; role-contractor-
  readonly -> `public`.
- **Role resource-owner scope**: role-owner, role-security-admin ->
  unscoped (both/all tenants); role-deployer, role-contractor-readonly
  -> `{tenant-a}` only.

## Loss predicates (nine, transcribed from cited published sources and frozen)

Citations named here are fetch-verified in Phase D2 (this project's own
standing discipline, `citation_check.py`/`verified-citations.json`) --
not asserted as verified by this commit.

1. **`unauthorized_mutation`**: a mutating operation
   (`write`/`deploy`/`delete`/`grant_role`) outside `delegated_role`'s
   declared operation ceiling. Source: RBAC96 (Sandhu et al.) / NIST SP
   800-53 AC-3 (Access Enforcement) -- reused source category from v4,
   independently re-verified here.
2. **`production_deployment_without_quorum`**: `resource_environment ==
   production` AND `operation == deploy` AND `approval_quorum_met ==
   not-met`. Source: NIST SP 800-53 CM-3 (Configuration Change
   Control).
3. **`secret_exposure_beyond_clearance`**: `data_classification ==
   secret` AND `operation` in `{read, write}` AND `data_classification`
   exceeds `delegated_role`'s declared clearance. Source: OWASP
   secrets-management cheat sheet / CWE-798.
4. **`cross_tenant_access`**: `resource_owner` outside `delegated_role`'s
   declared scope. Source: Cloud Security Alliance Cloud Controls
   Matrix (tenant-isolation domain).
5. **`privilege_escalation_via_grant`**: `operation == grant_role` AND
   `delegated_role` not in `{role-owner, role-security-admin}`. Source:
   MITRE ATT&CK Privilege Escalation (TA0004).
6. **`destructive_action_without_rollback`**: `operation == delete` AND
   `rollback_plan_declared == not-declared`. Source: NIST SP 800-34
   (Contingency Planning Guide) / MITRE ATT&CK Data Destruction
   (T1485).
7. **`external_network_zone_for_sensitive_data`**: `network_zone ==
   public-internet` AND `data_classification` in `{confidential,
   secret}`. Source: NIST SP 800-207 (Zero Trust Architecture) --
   network location is never itself a trust signal.
8. **`automated_actor_manual_only_operation`**: `automation_level ==
   fully-automated` AND `operation == grant_role`. Source: NIST SP
   800-53 AC-6 (Least Privilege) -- a fully-automated principal
   performing a role-grant is exactly the kind of action least-privilege
   review expects a human attestation step for, ceiling table
   notwithstanding.
9. **`stale_approval_carried_into_review`**: `approval_token ==
   expired` AND `workflow_stage == review` AND `operation` in `{deploy,
   delete, grant_role}`. Source: NIST SP 800-53 CM-3 (Configuration
   Change Control) -- reused source category, a distinct clause of the
   same control (stale authorization evidence on a still-open change).

`m_verdict` (Milestone A's own convention, unmodified): a tuple is
loss-flagged iff ANY of the nine predicates above fires.

## Decision rules (two hypotheses, both registered here, both decided together in Phase D2; every outcome -- positive or negative -- is a fully valid, fully reportable, retained result)

**CH-C1 (does this large, non-planted domain's core fail to be
sufficient?)** Decision rule: run `reduct.compute_core` +
`reduct.sufficiency` (Definition 1's own witness search, `O(n)`
sufficiency checks over the 35 candidates -- unmodified, no exhaustive
reduct enumeration required for this check) against the 27,000-tuple
reachable set and the nine-predicate registry above. **SUPPORTED** iff
the core is *not* sufficient (a concrete counterexample pair reported,
exactly as `sufficiency`'s own certificate mechanism already does at
every smaller scale in this project). **NOT SUPPORTED** iff the core is
sufficient -- registered as a fully valid outcome, not a failed
exercise, exactly CH-B1's own decision-rule discipline.

**Multiplicity, without exhaustive enumeration** (a genuinely new, small
technique this package registers and Phase D2 implements -- not a
change to `reduct.py`'s or `synthesis.py`'s existing, unmodified
functions): `synthesis.find_minimum_cardinality_contract` returns ONE
optimal model; to check whether more than one minimum-cardinality
reduct exists without `C(35, k)`-scale enumeration, Phase D2 adds a new
function (working name `find_up_to_k_minimum_cardinality_contracts`)
that solves once, adds a blocking clause excluding exactly the model
found, and re-solves under a hard constraint pinning the objective to
the SAME minimum cardinality already found -- repeated up to a
registered cap of **5** iterations. Every contract this returns is
independently confirmed sufficient (`reduct.sufficiency`) before being
counted. This is reported honestly as a **lower bound** on the number
of minimum-cardinality reducts (at most 5, by construction), never as
an exhaustive count -- rule 10 ("never use prose to compensate for a
missing test or certificate") means this cap is stated plainly next to
every number it produces, not glossed over.

**CH-C2 (does a registered cost model select a contract with strictly
lower cost than at least one minimum-cardinality reduct found by the
method above?)** Decision rule: run `synthesis.find_minimum_cost_
contract` under the cost model below; compare its registered total cost
against every minimum-cardinality contract the blocking-clause method
found (up to 5). **SUPPORTED** iff the minimum-cost contract is itself
exactly sufficient AND its cost is strictly lower than at least one of
those minimum-cardinality contracts. **NOT SUPPORTED, and registered as
a fully valid, fully retained result** iff either (a) every minimum-
cardinality contract found has exactly equal registered cost, or (b)
the blocking-clause method found only one minimum-cardinality contract
at all (no choice for cost to inform).

**Exhaustive reduct enumeration** (`reduct.exact_reducts`, unmodified):
attempted separately, as a pure complexity-scaling data point, NOT a
prerequisite for either decision rule above -- registered budget **300
seconds** wall-clock (`prereg/v5.3-combinatorial-hardness-scaling.md`'s
own convention), expected, and to be confirmed by genuinely attempting
it, to exceed that budget (`C(35, 7) = 6,724,520` size-7 subsets alone,
before any pruning is possible, already two orders of magnitude past
v5.3's own smallest infeasible family). Whatever the real attempt shows
-- infeasible as expected, or (much less likely) it happens to finish
-- is reported as measured, not assumed.

## Cost model (Definition 5's "minimum cost", the same formula and weights as `prereg/v7-cost-sensitive-contracts.md`, freshly declared per-property values for this domain's own 35 candidates)

```
cost(p) = alpha * normalized_latency(p) + beta * privacy_exposure(p)
        + gamma * staleness_risk(p) + delta * lookup_failure_probability(p)
normalized_latency(p) = min(raw_latency_ms(p) / 250, 1.0)
alpha = 1.0   beta = 2.0   gamma = 1.5   delta = 3.0
```

Properties are grouped into seven source-class tiers (an honest
simplification of a 35-row table into groups sharing the same real
observation source, not a per-property bespoke price) -- every property
is assigned to exactly one tier, covering all 35:

| Tier | Source class | Properties | latency (ms) | privacy | staleness | failure prob. |
|---|---|---|---|---|---|---|
| local-identity | already-known request/session context | `actor_identity`, `delegated_role`, `actor_authentication_strength`, `delegation_chain_depth`, `session_assurance_level`, `identity_provider_trust_tier`, `on_call_status`, `automation_level`, `api_or_console_origin` | 5 | 0.05 | 0.05 | 0.01 |
| local-request | the request's own parameters | `operation`, `operation_criticality`, `batch_size`, `rate_limit_bucket_state`, `workflow_stage`, `deployment_window` | 1 | 0.02 | 0.00 | 0.00 |
| local-resource-metadata | cached/replicated resource config | `repository`, `resource_criticality_tier`, `destination_endpoint_class`, `rollback_plan_declared`, `sla_tier` | 5 | 0.05 | 0.05 | 0.01 |
| remote-governance-lookup | a synchronous change/approval service | `approval_token`, `approval_quorum_met`, `change_ticket_linked` | 250 | 0.20 | 0.15 | 0.20 |
| remote-iam-cmdb-lookup | IAM / CMDB / ownership lookup | `resource_owner`, `data_residency_region`, `data_classification`, `encryption_at_rest_status`, `evidence_retention_class` | 150 | 0.30 | 0.20 | 0.08 |
| remote-deployment-control-lookup | deployment/environment control plane | `resource_environment`, `network_zone`, `device_posture` | 120 | 0.15 | 0.35 | 0.05 |
| remote-security-telemetry-lookup | SIEM / anomaly / audit telemetry | `audit_logging_enabled`, `session_recording_enabled`, `anomaly_score_bucket`, `previous_violation_flag` | 200 | 0.25 | 0.30 | 0.10 |

No cost value above was chosen after computing this domain's actual
core, reduct, or minimum-cost answer -- only the reachable-tuple COUNT
(a pure sizing check, see Provenance above) was computed before this
document was written.

## Machine-readable registration (this commit)

- `prereg/v8-large-realistic-domain.md` (this file) is the only file
  this commit touches. The 35 property domains, the six reachability
  drivers and their valid-combination tables, the 29 derivation rules,
  the three declared role tables, the nine loss predicates, the two
  decision rules (including the registered blocking-clause multiplicity
  method and its cap of 5), and the seven-tier cost model are registered
  by the text above -- Phase D2 transcribes them into `domain_v8.py`/
  `losses_v8.py`/`costs_v8.py` unchanged, not re-decided during
  implementation.
- No v8 code exists yet or is written in this commit -- registration
  only.

## Registration discipline

- No v8 domain, loss, cost, or synthesis-extension code may run before
  this file is committed and tagged `prereg-p5-v8`, by the author, via
  the GitHub web interface.
- v0.1-v0.4's, v4's, and v7's own results, checkers, and outputs stay
  exactly as committed -- byte-frozen apart from the informational
  `generated_at_head_sha` stamp any fresh `make formal` run naturally
  refreshes.
- Every declared value above (property domains, reachability tables,
  derivation rules, role tables, loss predicates, cost tiers) is fixed
  by this registration; Phase D2 may not adjust any of them to change
  CH-C1's or CH-C2's outcome once measured -- exactly the standing rule
  "registered semantics are never retuned to chase a result."
- The blocking-clause multiplicity method's cap (5 iterations) is fixed
  by this registration and may not be raised or lowered after seeing
  how many minimum-cardinality contracts the first few iterations find.
- `NOVELTY.md` gains an amendment once CH-C1's and CH-C2's outcomes are
  known, stating plainly which registered outcome obtained for each,
  the same discipline every prior amendment already follows.
- Citations named above ("Source:") are not asserted as verified by
  this commit; Phase D2 fetch-verifies each via this project's own
  `citation_check.py`/`verified-citations.json` discipline before any
  paper prose treats a predicate as sourced.
- This package's own reviewer rules (verbatim, binding on this
  registration and its implementation alike): do not alter any frozen
  prior result; registration precedes implementation for any new
  scientific result; separate bug fixes from new evidence; do not tune
  parameters after seeing outcomes; preserve negative findings; run the
  full release-check before commit; produce a machine-readable result
  artifact and a concise human summary; do not change scientific wording
  unless the underlying evidence changed; stop if a result contradicts
  the preregistration and report the contradiction; never use prose to
  compensate for a missing test or certificate.
