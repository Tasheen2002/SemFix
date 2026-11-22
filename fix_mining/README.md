# Developer-fix mining for the 56 BEHAVIORAL cases

**Date:** 2026-11-21. **Input:** classification v1.0 (56 BEHAVIORAL cases, 18 projects). **Method:** read-only.
- Git history from full clones in `repos/`. Nothing was checked out, built or run.
- GitHub REST API: one unauthenticated call per PR, for the PR's state.

**Status:** fixes identified and **validated on the BUMP BREAKING images** (2026-11-21); see *Validation* below.

## Method

1. **PR refs** (`scripts/fetch_prs.py`). For all 56 cases, the current head of `refs/pull/<n>/head` **is** the BUMP breaking commit. No fix was ever pushed into a bump PR.
2. **PR state** (`scripts/fetch_pr_meta.py`): **0 of 56 merged.** 53 were closed and 3 are still open (Cases 48, 70, 145).
3. **Version trace** (`scripts/trace_versions.py`):
   - **Start point:** the merge-base of the default branch and the breaking commit.
   - **Walk:** every first-parent commit on the default branch that touches any `pom.xml`, resolving the dependency's version across all POMs.
   - **Landing commit:** the first commit where the version reaches at least the breaking version.
   - **What it records:** for the landing commit, the files changed and the other dependency changes in the POMs.
4. **Failing tests** (`scripts/failing_tests.py`), taken from our original BREAKING logs.
5. **Catalogue** (`scripts/build_fix_catalog.py`). Each project family was inspected by hand, and the status, fix type and the commit it rests on are recorded. Patches (developer commit vs its first parent) go in `patches/`.

## Results

| Fix status | Cases | Projects (cases) |
|---|---:|---|
| **FIXED** (developer fix found) | **23** | listed in the fix-type table below |
| UPSTREAM_RESOLVED_CANDIDATE | 3 | plexus-archiver (53): 3.3.0 skipped, 3.3.1 POM-only. btrplace (163, 168): 2.4.9 skipped, 2.4.10 POM-only. |
| LANDED_MECHANISM_UNCLEAR | 2 | geostore (14, 114): h2 2.2.220 arrived in a 22-dependency security sweep; the rejected `varchar(10000000)` is still in the schema |
| NOT_ADOPTED (project active) | 12 | sign-maven-plugin (8): still slf4j 1.7.36. junit-quickcheck (4): still Mockito 4.11.0. |
| NOT_ADOPTED_PROJECT_INACTIVE | 15 | recheck (7), jasmine-maven-plugin (7), geoserver-shell (1) |
| REPOSITORY_MIGRATED | 1 | gax-java (113), retired in favour of google-cloud-java |

### Fix types of the 23 FIXED cases (12 unique fix commits across all 28 fix candidates)

| Fix type | Cases | Developer change | Matches classified behavior |
|---|---|---|---|
| CLIENT_CODE_ADAPTATION | 13 | `catch (IOException \| IllegalArgumentException e)` in `ReportBuilder` | Yes |
| TEST_ADAPTATION_API_CONFIG | 20 | `XStream.allowTypes(LogPanelPreferenceModel.class)` in the failing test | Yes |
| TEST_EXPECTATION_UPDATE | 158, 181 | New exception-message assertion; regenerated expected `Microdata1.nq` | Yes |
| CONFIGURATION_ADAPTATION | 28, 35, 39, 162, 166 | `stacktraceAppPackages` renamed to `inAppIncludes` in `config.yaml` | Yes |
| COMPANION_DEPENDENCY_UPGRADE | 2, 18, 132 (pdb); 100, 148, 184 (jadler) | logback-classic 1.2.x → 1.3.x together with slf4j 2, POM only | Yes (R5) |
| FRAMEWORK_MIGRATION | 12, 15, 27, 150, 159, 185, 186 (pay-adminusers); 171 (dropwizard-pac4j) | Dropwizard 2 → 3 / 4; slf4j now from the framework BOM | Likely; large diff, not a minimal fix |

**Fixes that change code or configuration** confirm the classified behavior change directly. There are 9 such cases (13, 20, 158, 181 and the five pay-cardid cases): in each, the developer adapted exactly to the change we labelled:
- an exception type;
- a security default;
- a message format;
- an output format;
- a rejected config property.

## Validation on the BREAKING images

**Script:** `scripts/validate_fixes.py`. **Recipes:** `validation/recipes.json`.

**Procedure for each case:**
1. Build a minimal backport of the fix as a unified diff against the breaking commit's own file (`validation/backports/case<N>.patch`).
2. In a fresh `--rm` container of the original BREAKING image, run `git apply --check` and then `git apply`.
3. Run the original `mvn clean test -B`, with Maven's exit code recorded directly. For btrplace only the `json` module and the modules it needs were built (`-pl json -am`).
4. For POM fixes, run `mvn dependency:tree` in the same container.

Logs are in `validation/logs/`, verdicts in `validation/results.jsonl`. This was an AI validation (Claude), not a human review.

| Result | Cases |
|---|---|
| **Developer fix validated** (21) | 2, 13, 14, 18, 20, 28, 35, 39, 53, 100, 114, 132, 148, 158, 162, 163, 166, 168, 171, 181, 184 |
| **Derived minimal fix validated** (7) | 12, 15, 27, 150, 159, 185, 186 (pay-adminusers) |

Case 171 was validated by **replaying the developer's full commit** (`f10bef101d`, Dropwizard 2 → 4); see the Case 171 finding below.

**What "validated" means.** In every validated case:
- the patch applied cleanly;
- the build went from FAILURE to **BUILD SUCCESS** with 0 failures and 0 errors, and `MAVEN_EXIT=0`;
- every originally failing test class now passes;
- `dependency:tree` showed the intended versions (for example logback-classic 1.3.16 with slf4j-api 2.0.4 in Case 2; h2 2.2.220 in Cases 14 and 114).

Test totals often rise, for example 94 → 291 in pdb. That is because the BREAKING build stopped at the first failing module, while the fixed build runs every module.

**Findings:**
- **h2 (Cases 14, 114) is library-resolved.** h2 2.2.220 on its own, without the other 21 sweep changes, makes all tests pass, so the later h2 accepts `varchar(10000000)` again. Reclassified from "mechanism unclear" to UPSTREAM_RESOLVED, along with plexus-io 3.3.1 (53) and json-smart 2.4.10 (163, 168).
- **Case 181: the developer's own fix failed off their machine.**
  - **The problem:** their regenerated `Microdata1.nq` hard-coded a local graph name (`file:/Users/ed4565/…`). They repaired this themselves later in `6fa0326f` (#467).
  - **What was validated:** only their jsoup whitespace change, 12 × `"> +\n"` → `">\n"`. It is identical to their file once the graph path and blank-node IDs are normalised.
  - **The failed attempts** are kept in `validation/results_superseded.jsonl` and in the `case181_fixed_attempt*` logs.
- **pay-adminusers has a minimal fix the developers did not use.** The developers fixed this by migrating Dropwizard 2 → 3. Under the existing Dropwizard 2.0.29, a derived fix (logback-classic and logback-core 1.3.5) passes all 7 cases, for example 726/0/12 → 757/0/0.
- **Case 171 needed the framework migration, and the developer's migration does work on the breaking code.**
  - **No minimal fix:** the same logback-only fix fails under Dropwizard 2.0, because logback 1.3 removed `ch.qos.logback.classic.jmx.JMXConfigurator`, which Dropwizard 2.0's logging uses.
  - **Replay:** the developer's commit `f10bef101d` was cherry-picked onto the breaking commit. All 14 Java and README changes applied cleanly, because those files are identical between the breaking commit and the fix's parent; only `pom.xml` had drifted, with routine version bumps. The 3 POM conflict blocks were resolved with the developer's side.
  - **Two adjustments:** slf4j-api was kept at the case's version, 2.0.0 (the developer had 2.0.3), and `jax-rs-pac4j` 6.0.0-SNAPSHOT was replaced by the released 6.0.0, because snapshots can't be reproduced.
  - **Result:** 16/0/10 → 16/0/0, BUILD SUCCESS, `MAVEN_EXIT=0`. The tree shows slf4j-api 2.0.0 with logback 1.4.6 from Dropwizard 4.0.0.
  - **Diagnosis:** the breaking POM pins `jetty-server` 9.4.35 and other "convergence" versions in `dependencyManagement`. That pin is what made the researcher-written Dropwizard 3 attempt fail (`researcher_written/`), and the developer removed these pins.
  - **Patch:** `validation/case171_developer_replay.source.patch`.

## Researcher-written fixes (separate group)

For the 29 cases without a validated developer fix, researcher-written fixes were tested in [`researcher_written/`](researcher_written/README.md):
- **28 of 29 pass.** The failing tests now pass and the whole build passes.
- **Case 171's researcher-written attempt failed** after 7 bounded attempts. Case 171 is nonetheless fixed, by the replayed developer fix above, so it counts as a DEVELOPER_FIX.

**Rule (researcher's decision):** these fixes only show that a case **can be fixed**. They are **not reference answers**. For these cases a tool is judged by tests alone: the failing tests pass and nothing else breaks.

**Overall, from `developer_fixes.csv` → `reference_group`:**

| Reference group | Cases | How a repair tool is judged |
|---|---:|---|
| DEVELOPER_FIX | 21 | Compare with the developer fix, plus tests |
| DERIVED_MINIMAL_FIX | 7 | Compare with the derived fix, plus tests |
| RESEARCHER_WRITTEN_ONLY | 28 | Tests only |

**All 56 BEHAVIORAL cases now have a fix validated on their BREAKING image.**

**Validator change.** The passing rule was tightened on 2026-11-21: a case passes only if tests ran and every originally failing test class ran. All results were re-checked against it with `scripts/recheck_results.py`: 0 failures, including the replayed Case 171.

## Implications for the research

- **Validated ground truth exists for 28 of 56 cases**: 21 developer fixes, including Case 171's replayed migration, and 7 derived minimal fixes. Duplicate groups share one fix and must stay in the same evaluation fold.
- **28 cases have no developer fix.** Those projects never adopted the new version: they pinned it, went inactive, or migrated. The repair tool can still be evaluated on them by test outcome, but there is no reference patch to compare against.
- **The PR itself never contains the fix.** Developers either fixed the problem later on the default branch, often months or years later, or never fixed it.
- **The landing patches are not minimal.** They were written against a later codebase. Before using them as references we must:
  - backport a minimal version of each fix onto the BREAKING image's source;
  - apply it with `git apply --check`;
  - run the failing tests;
  - confirm `dependency:tree` shows the intended version.

## Files

| File | Contents |
|---|---|
| `developer_fixes.csv` | One row per case: PR state, fix status and type, fix commit, date, version, files, companion changes, patch path, version at HEAD, failing test classes, validation status, notes |
| `fix_summary.json` | Counts |
| `patches/` | 12 developer-fix diffs (commit vs first parent) |
| `version_trace.json` | Full version history per case |
| `pr_meta.json`, `cases.json`, `failing_tests.json` | Inputs |
| `repos/` | Full clones of the 18 projects (untrusted; never built here) |
| `scripts/` | All mining scripts (rerunnable, read-only) |

**Known gaps:**
- **Failing-test extraction:** empty for Cases 14 and 114, and only `TestSuite` for 163 and 168; the details are in those cases' reviews.
- **gax-java's successor repository** (Case 113) was not mined.
