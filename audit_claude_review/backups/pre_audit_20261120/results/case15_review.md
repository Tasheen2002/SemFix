# Case 15: agent assessment awaiting human review

Case ID: `14e2c8d47384137d1fff33d9a1441af3d1ef29a3`  
Project: `alphagov/pay-adminusers`  
Update: `org.slf4j:slf4j-api` **1.7.36 → 2.0.5**  
BUMP category: `TEST_FAILURE`  
Automated triage: `AUTO_RUNTIME_REVIEW_REQUIRED`  
Agent assessment: `PROVISIONAL_BEHAVIORAL` (provider/default implementation change)  
Human review: **pending**. This assessment does not populate Reviewer 1, Reviewer 2, or the final label.

| Environment | Surefire reports | Reported tests | Failures | Errors | Skipped | Maven result | Container exit |
|---|---:|---:|---:|---:|---:|---|---:|
| PRE | 79 | 747 | 0 | 0 | 0 | SUCCESS | 0 |
| BREAKING | 79 | 715 | 0 | 12 | 0 | FAILURE | 1 |

Both images ran `mvn clean test -B` from `/pay-adminusers`, using Java 11.0.27, Maven 3.9.9, and Alpine Linux 3.22.0. The ARM64 images ran under emulation on an AMD64 Docker host. Both source and test compilation succeeded. Fresh Surefire reports were copied after each clean build; these are not reports inherited from the image.

All 440 files in the archived source/resource trees match by SHA-256. The only POM change is the SLF4J version. In `EventMessageHandlerTest`'s reported runtime classpath, the only differing path is `slf4j-api-1.7.36.jar` versus `slf4j-api-2.0.5.jar`; Logback Classic and Core remain 1.2.11. This comparison checks paths and versions, not byte identity of every dependency JAR. Maven requested Guava metadata during BREAKING dependency resolution; the affected test's classpath paths nevertheless differ only in SLF4J.

The BREAKING log reports that no SLF4J providers were found, that the old Logback binding is ignored, and that SLF4J defaults to a NOP logger. The unchanged test setup casts the result of `LoggerFactory.getLogger(EventMessageHandler.class)` to `ch.qos.logback.classic.Logger` at `src/test/java/uk/gov/pay/adminusers/queue/event/EventMessageHandlerTest.java:111`. All eight methods in that test class error with `ClassCastException`, because the returned object is `org.slf4j.helpers.NOPLogger`.

Four resource-test classes also fail during static initialization. Each stack trace reaches `IllegalStateException: Unable to acquire the logger context` in Dropwizard logging. Their later `NoClassDefFoundError: Could not initialize class` messages are consequences of initialization failure, not evidence that those classes are absent. No missing-method, missing-class, or other primary binary-linkage failure was identified in the inspected reports.

| Resource-test class | PRE tests | BREAKING reported tests/errors |
|---|---:|---|
| ServiceResourceCreateTest | 7 | 1 / 1 |
| ServiceResourceFindTest | 7 | 1 / 1 |
| ServiceResourceSearchTest | 3 | 1 / 1 |
| ServiceResourceUpdateTest | 19 | 1 / 1 |

These classes account for 36 PRE test cases, replaced by four class-level error entries in BREAKING. This explains the net decrease of 32 in Surefire's reported total. It does **not** represent 32 skipped or passing tests. The twelve errors comprise eight logger-cast errors and four initialization errors.

The behavior is consistent with Case 12's logging-provider issue, but Case 15 has its own source snapshot, versions, logs, and test totals. Human classification should decide whether provider/binding changes fit the study's semantic codebook. Keep these related cases in the same project/family partition when designing later retrieval and evaluation splits.

No repair was attempted for Case 15. No new verified-repair entry was created. The original fourteen classification records and Case 14 repair remain unchanged.

Evidence paths relative to the workspace:

- `logs/batch_triage/14e2c8d4_pre.log`
- `logs/batch_triage/14e2c8d4_breaking.log`
- `logs/case15_evidence/pre/surefire-reports/`
- `logs/case15_evidence/breaking/surefire-reports/`
- `logs/case15_evidence/pre/src/` and `breaking/src/`
- `logs/case15_evidence/pre/pom.xml` and `breaking/pom.xml`
- `logs/case15_evidence/source_comparison.json`
- `logs/case15_evidence/dependency_update.diff`
- `logs/case15_evidence/pre_environment.txt` and `breaking_environment.txt`
- `logs/case15_evidence/pre_container_state.json` and `breaking_container_state.json`
- `results/case15_assessment.json`

PRE image digest: `sha256:50edd48115779dd263253c31cb6a808fb0b191708f9a8b567f533b5374e9713d`  
BREAKING image digest: `sha256:7a95b14dcb4be1c69dfee389117106611b3e078ff5fdd308d6674faf6edfdd04`

Before reproduction, the runner and existing classification/batch/repair artifacts were copied into `results/backups/before_case15_20261108_180501_869/` with a SHA-256 manifest. The runner now backs up batch CSV replacements, writes them atomically, refuses unreadable batch data, protects existing logs unless an explicitly forced rerun backs them up, and supports retained named containers for evidence extraction. Its preservation behavior was checked with temporary CSVs; the Case 14 skip path was checked without running Docker tests. No earlier experiment was rerun.

Next unprocessed candidate: Case 16, `1750bac074c30b06ae5cdff7a25db401a4f45de2`, `dropwizard-pac4j`, Jackson Databind 2.10.5.1 → 2.13.4. Inspect saved evidence before starting it.
