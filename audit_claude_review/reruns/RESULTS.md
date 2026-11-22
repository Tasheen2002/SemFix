# Targeted verification checks (2026-11-20)

All checks ran in fresh `--rm` containers from the original BUMP **BREAKING** images, each with a unique `audit-claude-case<N>-<check>` name. Maven's exit code was captured directly; no `tee`. Each log records whether the run was offline or online. Offline attempts failed only because `maven-dependency-plugin` is not cached in the images, so those checks fell back to Maven Central (public downloads only). The images for Cases 3, 21, 30, 69 and 71 were pulled from `ghcr.io/chains-project/breaking-updates` for these runs. No workspace files were changed by the runs. Per-run metadata, including image ID and timings, is in `runs.jsonl`.

| Case | Check | Change made | Maven result | Finding | Effect on label |
|---|---|---|---|---|---|
| 104 | `dependency:tree` | none | exit 0 | The project declares `dss-pades` 5.9 directly next to `dss-pades-pdfbox` 5.10.2 | Confirms NON_BEHAVIORAL (R1 linkage) |
| 122 | `dependency:tree` | none | exit 0 | jackson-core 2.9.8 pinned with databind 2.12.6.1 (annotations 2.11.0) | Confirms NON_BEHAVIORAL (R1) |
| 143 | `dependency:tree` | none | exit 0 | jackson-core and annotations 2.14.1 with databind 2.15.2 (provided scope) | Confirms NON_BEHAVIORAL (R1) |
| 178 | `dependency:tree` | none | exit 0 | spring-web/core/beans/context 4.1.6.RELEASE with spring-webmvc 5.3.18 | Confirms NON_BEHAVIORAL (R1) |
| 105 | `test-compile dependency:tree` | none | exit 0 | log4j-api 2.11.2 (via spring-boot-starter-log4j2 2.1.3) with log4j-core 2.16.0 | Confirms NON_BEHAVIORAL (R1) |
| 3 | `dependency:tree` | none | exit 0 | jackson-core 2.4.2 and annotations 2.4.1 with databind 2.9.10.8 | Confirms NON_BEHAVIORAL (R1) |
| 21 | `test-compile dependency:tree` | none | exit 0 | avans-session-spymemcached resolves jackson-core 2.4.2, which lacks TSFBuilder needed by cbor 2.13.3 | Confirms NON_BEHAVIORAL (R1) |
| 71 | `test-compile dependency:tree` | none | exit 1* | `flogger` 0.7.1 (via google-extensions 0.7.1) with `flogger-system-backend` 0.6. Codex's direction of the mismatch is correct. | Confirms NON_BEHAVIORAL (R1) |
| 116 | module test run with the surefire dump kept | none | exit 1 | Dump: `Unsupported version of junit:junit: 3.8.1. Please upgrade to version 4.12 or later.` | Confirms NON_BEHAVIORAL (R10 tooling) |
| 30 | **control:** add `org.eclipse.persistence.asm` 9.4.0, keep MOXy 4.0.1 | one dependency added | **exit 0, 737 tests, 0 F / 0 E / 4 S** (BREAKING: 15 E) | The missing ASM provider fully explains the failure | Confirms NON_BEHAVIORAL (R13 packaging) |
| 69 | **control:** set retained `js` 22.0.0 → 22.1.0, keep `js-scriptengine` 22.1.0 | one version aligned | **exit 0, 80 tests, 0 F / 0 E / 1 S** (BREAKING: 3 F / 9 E) | The failure was a mismatch between two GraalJS artifacts | **Supports NON_BEHAVIORAL (R2)**; contradicts Codex's PROVISIONAL_BEHAVIORAL |

\* Case 71's exit 1 comes from `maven-enforcer-plugin` in the unrelated later module `pubsublite-beam-io`. The tree for the module under test (`google-cloud-pubsublite`) was produced before that point.

Case 116's `runs.jsonl` row has an empty `maven_exit` because the check script exits with the test-phase code; the log records `MAVEN_TEST_EXIT=1`.

**Summary:** 11 of 11 checks completed, and all agree with the classification evidence. One check (Case 69) resolves a disputed label in favour of NON_BEHAVIORAL. None of the checks found a behavioral case mislabelled as non-behavioral.
