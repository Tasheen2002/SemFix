# Researcher-written fixes (separate group)

**Date:** 2026-11-21. **Author of the fixes:** Claude (AI), on the researcher's instruction.

**Rule, set by the researcher:**
- These fixes are **not reference answers**. They only show that each case *can* be fixed.
- They must not be used to grade a repair tool's patch.
- For these cases, a tool's patch counts as a repair if the originally failing tests pass and nothing else breaks (the whole build passes).

## Scope

There are 29 cases with no validated developer fix:
- **No developer fix exists (28):** the project never adopted the new version, went inactive, or moved repositories.
- **Case 171:** the developer's fix is a framework migration that cannot be backported.

## How each fix was tested

Same procedure as the developer fixes (`../scripts/validate_fixes.py --researcher`):
1. Write a minimal patch against the breaking commit's own files (`backports/case<N>.patch`).
2. In a fresh `--rm` container of the original BREAKING image, run `git apply --check` and then `git apply`.
3. Run `mvn clean test -B`, with Maven's exit code captured directly.
4. Run `mvn dependency:tree` for POM changes.

**Passing rule** (made stricter during this work, after Case 171 attempt 4 showed BUILD SUCCESS with 0 tests): a fix passes only if
- the patch applies;
- at least one test runs, and every originally failing test class runs;
- BUILD SUCCESS with 0 failures, 0 errors, and `MAVEN_EXIT=0`.

`../scripts/recheck_results.py` re-checked all earlier results, developer and researcher-written, against this rule. Only Case 171 failed it.

## Results: 28 of 29 fixed by researcher-written patches (Case 171 is fixed by the replayed developer fix instead)

| Project | Cases | Researcher-written fix | BREAKING t/f/e | Fixed t/f/e |
|---|---|---|---|---|
| retest/recheck | 1, 31, 38, 76, 90, 145, 151 | logback 1.2.11 → 1.3.5 (an SLF4J-2 provider; same idea as the pdb/jadler developer fixes) | 737/0/30 | 737/0/0 |
| searls/jasmine-maven-plugin | 48, 56, 59, 78, 117, 142, 156 | Test binding `uk.org.lidalia:slf4j-test` 1.2.0 → its SLF4J-2 fork `com.github.valfirst:slf4j-test` 3.0.1, with the package rename in the test imports | 72/2/0 | 72/0/0 |
| s4u/sign-maven-plugin | 5, 22, 24, 134, 144, 147, 153, 155 | `org.simplify4u:slf4j-mock` → `org.simplify4u:slf4j2-mock` 2.3.0 (same author and packages, SLF4J-2 provider) | 38/0/12 | 38/0/0 |
| pholser/junit-quickcheck | 9, 52, 89, 98 | New file `core/src/test/resources/mockito-extensions/org.mockito.plugins.MockMaker` = `mock-maker-subclass`. This restores Mockito's pre-5 default and is the documented Mockito 5 option. | 510/1/0 | 1114/0/0 |
| googleapis/gax-java | 113 | Same Mockito setting, in `gax/` | 529/2/0 | 787/0/0 |
| jericks/geoserver-shell | 70 | `jsonObject.getString("id")` → `jsonObject.get("id")` in 2 places: org.json 20230227 rejects non-string values in `getString` | 205/0/2 | 205/0/0 |
| pac4j/dropwizard-pac4j | 171 | Researcher-written attempt **not fixed** after 7 tries (below); the case is fixed by the replayed developer fix | 16/0/10 | 16/0/10 |

Test totals rise in some cases because the BREAKING build stopped at the first failing module.

## Case 171: why it stays unfixed

Each attempt is kept in `results_superseded.jsonl` and in `logs/case171_fixed_attempt*.log`.

| Attempt | Change | Result |
|---|---|---|
| (derived) | logback 1.3.5 under Dropwizard 2.0 | logback 1.3 removed `JMXConfigurator`, which Dropwizard 2.0 needs |
| 1 | Dropwizard 2.0.17 → 3.0.4 (POM only) | Compile errors: packages moved to `io.dropwizard.core.*` |
| 2 | + package move in 10 files | Compile error: `io.dropwizard.Bundle` removed |
| 3 | + remove the unused `Bundle` import | Test compile errors: JUnit 4 is no longer transitive |
| 4 | + `junit:junit` 4.13.2 | BUILD SUCCESS but **0 tests ran**. Originally mis-recorded as validated, then corrected. |
| 5 | + vintage engine with no version | POM error: version missing |
| 6 | + vintage engine 5.9.3 | 16 tests run; Jackson `NoClassDefFoundError` (old jackson-databind pin) |
| 7 | + remove the jackson-databind 2.10.5.1 pin | Jetty `IllegalAccessError`: the pac4j/jee-pac4j stack against Dropwizard 3's Jetty 10 |

Each step exposed another library that would also have to move, so the researcher-written attempt was stopped by design.

**Update (2026-11-21): Case 171 is fixed by the developer's own migration.** The developer commit `f10bef101d` (Dropwizard 4) was replayed onto the breaking commit and validated (16/0/10 → 16/0/0). It is recorded in `../validation/` as a DEVELOPER_FIX. The replay also explains attempt 7's Jetty error: the breaking POM pins `jetty-server` 9.4.35 in `dependencyManagement`, and the developer removed that pin. This README keeps the failed researcher-written attempt as a record.

## Files

| File | Contents |
|---|---|
| `recipes.json` | Each fix as data (edits, source, rationale) |
| `backports/case<N>.patch` | The 29 patches |
| `logs/case<N>_fixed.log` | Full container logs |
| `results.jsonl` | Final verdict per case |
| `results_superseded.jsonl` | Earlier Case 171 attempts and the corrected record |
