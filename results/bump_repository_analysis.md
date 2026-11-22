# BUMP repository analysis (before fix mining)

**Repository:** https://github.com/chains-project/bump. The local clone is `bump/`, at commit `324d551`, the same commit as the remote's latest. **Date:** 2026-11-20. **Method:** read-only inspection with scripts, cross-referenced against our 188 TEST_FAILURE cases and the 56 BEHAVIORAL cases in classification v1.0.

## Summary

| Folder / file | What it is | Covers our 188 | Covers our 56 BEH | Use for fix mining |
|---|---|---:|---:|---|
| `data/benchmark/` | 571 breaking-update JSON records | 188 | 56 | **Primary input:** PR URL, breaking commit, versions, compare link |
| `data/sanity-check-failures/` | 47 records that failed BUMP's sanity check | 0 | 0 | None |
| `data/unsuccessful-reproductions/` | 4,763 updates BUMP could not reproduce | 0 | 0 | None |
| `fixes/` | 10 developer fix patches | 0 | 0 | Format reference only; all 10 are COMPILATION_FAILURE |
| `reproductionLogs/successfulReproductionLogs/` | 571 Maven logs (each a tar wrapping a `.log`) | 188 | 56 | Optional third copy of the BREAKING log |
| `reproductionLogs/unsuccessfulReproductionLogs/` | 3,765 logs | 0 | 0 | None |
| `RQData/` | Data behind the BUMP paper's research questions | partly | partly | Context only; no fix information |
| `workflowLogs/` | 78 zipped GitHub Actions CI logs | 16 | 1 (Case 52) | The original CI failure for those cases |
| `schemas/` | JSON schemas for the 3 record types | n/a | n/a | Validates the record fields we read |
| `scripts/` | Helper scripts (branch creation, reproduction, stats, link fixes) | n/a | n/a | `create_branch_for_breaking_update.sh` shows how to fetch the breaking commit |
| `src/` | Java miner and reproducer (about 2,700 lines) | n/a | n/a | Explains how cases were selected and labelled |
| root JSON files | Image sizes, repository search list, search config | 188 (`image_metadata.json`) | 56 | None |

**Main finding:** BUMP contains **no developer fixes for any of our 188 cases**. To get them we must mine GitHub ourselves, starting from the `url` and `breakingCommit` fields in `data/benchmark/`.

## 1. `data/`

### `benchmark/` (571 files, one per breaking commit)

**Fields in every record:** `url` (the PR), `project`, `projectOrganisation`, `breakingCommit`, `prAuthor`, `preCommitAuthor`, `breakingCommitAuthor`, `updatedDependency{…}`, `preCommitReproductionCommand`, `breakingUpdateReproductionCommand`, `javaVersionUsedForReproduction` (always 11), `failureCategory`, `licenseInfo`.

**`updatedDependency` fields:** `dependencyGroupID`, `dependencyArtifactID`, `previousVersion`, `newVersion`, `dependencyScope`, `versionUpdateType`, `githubCompareLink`, `mavenSourceLinkPre`, `mavenSourceLinkBreaking`, `updatedFileType`, `dependencySection`, `githubRepoSlug`, `licenseInfo`.

| failureCategory | Count |
|---|---:|
| COMPILATION_FAILURE | 235 |
| **TEST_FAILURE** | **188**: exactly our candidate set (all 188 IDs match) |
| ENFORCER_FAILURE | 121 |
| DEPENDENCY_LOCK_FAILURE | 14 |
| WERROR_FAILURE | 8 |
| DEPENDENCY_RESOLUTION_FAILURE | 5 |

- **Whole benchmark:** 153 projects. 553 PRs are from bots and 18 from humans. Updated file type: 527 JAR, 44 POM. Section: 414 dependencies, 146 dependencyManagement, 11 plugins.
- **Our 188 by version jump:** 80 major, 54 minor, 46 other, 8 patch.
- **Our 56 BEHAVIORAL:**
  - Version jump: 43 major, 6 other, 4 patch, 3 minor.
  - 56/56 are compile scope; 55 are bot PRs and 1 is a human PR.
  - 18 distinct projects.
  - Every `url` is a `/pull/<n>` link.
- **Links for the 56:**
  - **`githubCompareLink`:** usable for 47 of 56, which gives the library's own diff between the two versions. It is missing for 9 cases (14, 20, 28, 35, 39, 70, 114, 162, 166): dropwizard-sentry, h2database and JSON-java have no matching tags, and Case 20's library has no GitHub repository.
  - **`mavenSourceLinkPre` / `mavenSourceLinkBreaking`:** present for all 56. These are the library's source jars, a fallback for the 9 cases.

### `sanity-check-failures/` (47) and `unsuccessful-reproductions/` (4,763)

These use the same record format. Unsuccessful records have no `failureCategory` or reproduction commands. Neither set overlaps our 188, so they do not matter for us. One note: BUMP's README mentions `data/in-progress-reproductions`, and `scripts/calculate_stats.sh` still counts it, but that folder does not exist in the current repository.

## 2. `fixes/` (10 patches)

Each file is `<breakingCommit>.patch`, a developer fix in unified-diff format. All 10 are **COMPILATION_FAILURE** cases:

| Project | Dependency |
|---|---|
| pdb | mysql-connector-java |
| simplelocalize-cli | snakeyaml |
| biapi | jasperreports |
| camunda-platform-7-mockito | spring-context |
| flink-faker | datafaker |
| license-maven-plugin | maven-dependency-tree |
| guice | struts2-core |
| flacoco | maven-surefire-common |
| scoverage-maven-plugin | doxia-site-renderer |
| ci-sauce | plexus-archiver |

None of them is one of our cases. The patches touch Java sources only, not the POM. They are useful as a format model (we can store mined fixes the same way: `fixes/<breakingCommit>.patch`), but they cannot be used as ground truth for behavioral repair.

## 3. `reproductionLogs/` (2.3 GB)

- **`successfulReproductionLogs/`:** 571 files, one per benchmark case. Each `.log` is a tar archive wrapping the real Maven log. All 188 of our cases are present. These are BUMP's own reproduction logs, so they are an independent third copy of the BREAKING outcome, after our original runs and the 47-case reruns. They are not needed for the labels.
- **`unsuccessfulReproductionLogs/`:** 3,765 logs, with no overlap with our cases.

## 4. `RQData/` (data behind the BUMP paper's RQs)

| File | Entries | Covers our 188 | Contents / relevance |
|---|---:|---:|---|
| `compilation-error-count.csv` | 17 error types | n/a | javac error frequencies; compilation only |
| `japicmp-results.json`, `japicmp-revapi-analysis-results.json` | 243 each | **0** | API-diff analysis for compilation failures. None exists for our test-failure cases, so we would have to run japicmp/revapi ourselves if needed. |
| `dep-diff.json` | 568 | 188 | Dependencies removed or added between PRE and BREAKING. For the 56: 42 change exactly 1 dependency; 14 change several (3/3, 6/6, 2/2, 3/5), meaning the bot already bumped companion artifacts together. |
| `test-types.json` | 203 | 188 | Per-case skipped / total / failures / errors / `randomisedTestFailures`. Eight cases carry `SureFirePluginError` (4, 23, 60, 63, 86, 121, 177) or `JUnitError` (77). |
| `image-execution-times.json`, `grouped-dependencies.csv` | 572 / list | 188 | Build time and image size; dependency popularity (for example jackson-databind in 13 projects, slf4j-api in 7). Context only. |

**`randomisedTestFailures` check.** The flag is above 0 for 13 of our cases: 6, 36, 50, 51, 57, 62, 79, 103, 106, 111, 115, 131 and 167. All 13 are the same POI version-skew family, labelled NON_BEHAVIORAL under rule R1 (linkage). The flag does not touch any BEHAVIORAL case, so no v1.0 label changes. It does deserve a sentence in the threats-to-validity section, because a reader could take it to mean flakiness.

## 5. `workflowLogs/` (78 folders)

Each folder is named by breaking commit and holds zipped GitHub Actions logs (`logs_<run>.zip`), i.e. the failure as it happened in the project's own CI. 16 of our cases have them: 7, 11, 19, 43, 52, 77, 87, 88, 109, 116, 118, 130, 143, 164, 179 and 183. Only **Case 52** is BEHAVIORAL. They are of limited use for fix mining.

## 6. `schemas/`

Draft JSON schemas (`breaking-update.schema.json` and `breaking-update-dependency.schema.json`) for successful, unsuccessful and not-attempted records. They match the fields listed above. The repository's `validate-json-files.yml` workflow checks every data file against them.

## 7. `scripts/`

| Script | Purpose |
|---|---|
| `create_branch_for_breaking_update.sh` | Fetches the PR repository at `breakingCommit` into a branch. This is the same fetch we will need, to diff the breaking commit against a later fixed commit. |
| `reproduce_failure.sh` | The original reproduction ladder: PRE compile, then BREAKING compile, then PRE test, then BREAKING test, labelling the result. |
| `calculate_stats.sh` | README statistics. |
| `add-licenses.py`, `fix-github-links.py` + `manual_repo_mapping.json` | Fill `licenseInfo` and `githubCompareLink`. The mapping hand-maps dependency → library repository. |
| `requirements.txt` | pandas, requests. |

## 8. `src/` (Java; Maven `pom.xml` at the root)

- **`miner/`** (GitHubMiner, PullRequestFilters, RepositoryFilters, BreakingUpdate, …) searches GitHub for PRs that:
  - change only a dependency `<version>` in a `pom.xml`;
  - have a failing CI check;
  - fall within the search window.
- **`search_config.json`** sets the repository thresholds: at least 10 stars, at least 100 commits, at least 3 contributors.
- **Consequence:** every case is a one-line version-bump PR, so the "fix" is whatever the developers did after that PR.
- **`reproducer/`** builds the PRE and BREAKING Docker images and assigns `failureCategory`. The rules are regexes in `ResultManager.FAILURE_PATTERNS`: for example, `[ERROR] Tests run:` or `There are test failures` leads to TEST_FAILURE. Three consequences:
  - BUMP's TEST_FAILURE is a **log-pattern** label, not a semantic one. That is why our RQ1 split into BEHAVIORAL and NON_BEHAVIORAL is needed and is a contribution.
  - It explains why linkage errors that surface in tests (R1) are filed under TEST_FAILURE.
  - BUMP records no fix information.
- **`DependencyRefLinkFinder`** produces the compare links.

## 9. Root files

| File | Contents |
|---|---|
| `image_metadata.json` | 619 entries: `.m2` and project folder sizes per image; covers all 188 |
| `found_repositories.json` | 4,120 candidate repositories scanned by the miner |
| `search_config.json` | Mining thresholds (see above) |
| `renovate.json`, `.github/workflows/` | `tests.yml`, `update-readme.yml`, `validate-json-files.yml`; repository maintenance |
| `github_packages_credentials.json` | 48 bytes. **Not opened**: it may hold credentials, and nothing we need is in it. |

## Implications for fix mining (the 56 BEHAVIORAL cases)

1. **No ready-made fixes.** All ground-truth fixes must be mined from GitHub.
2. **Mining inputs per case, all from `data/benchmark/<id>.json`:**
   - `url` gives the PR. Look at its later commits and whether it was merged or closed.
   - `breakingCommit` is the starting point for searching the default branch for the first commit where the dependency is at least `newVersion` and the failing tests pass.
   - `githubCompareLink` (47/56) or the Maven source jars (56/56) explain what changed in the library. This becomes the knowledge base for retrieval.
3. **Scale.** 56 cases in 18 projects; duplicate groups from v1.0 share a fix and must stay in the same evaluation fold.
4. **Companion upgrades.** In 14 of the 56, the bot PR already changed several dependencies (`dep-diff.json`). We still need to decide whether a later companion upgrade counts as a valid repair.
5. **Validation stays on the BUMP images.** Apply the mined patch to the BREAKING image (`git apply --check`), run the failing tests, and check `dependency:tree`.

## Reproducing this analysis

The numbers above come from read-only Python passes over `bump/`, cross-referenced with `results/test_failure_candidates.csv` and `results/final_classification_rule_based.csv`. No BUMP file was modified.
