# Case 18 review

Case 18 covers the `feedzai/pdb` upgrade of `org.slf4j:slf4j-api` from 1.7.36 to 2.0.6. The provisional assessment is **behavioural**, pending human review. The automated result is `AUTO_RUNTIME_REVIEW_REQUIRED`.

| Run | Reported tests | Failures | Errors | Skipped | Maven result |
|---|---:|---:|---:|---:|---|
| PRE | 291 | 0 | 0 | 13 | BUILD SUCCESS |
| BREAKING | 94 | 0 | 3 | 10 | BUILD FAILURE |

Fresh Surefire reports match the Maven totals. The three affected test classes each report one setup error in BREAKING. Those classes account for 200 reported tests in PRE, which explains the difference in totals. Both image commands pipe Maven output through `tee` and the containers exit 0. Maven's build summary and Surefire reports establish the BREAKING outcome.

The BREAKING log says that SLF4J found no providers, ignored Logback 1.2.11's legacy `StaticLoggerBinder`, and selected its no-operation logger. Three unchanged test setup methods call `LoggerFactory.getLogger(Logger.ROOT_LOGGER_NAME)` and cast the result to `ch.qos.logback.classic.Logger` before setting its level. The returned `org.slf4j.helpers.NOPLogger` triggers a `ClassCastException` in each setup method.

| Test class | Failing setup location |
|---|---|
| `BatchUpdateTest` | `initStatic`, line 143 |
| `EngineCloseTest` | `initStatic`, line 102 |
| `EngineGeneralTest` | `initStatic`, line 181 |

The 181 archived source and POM paths match in both runs. The only content difference is the SLF4J version in the root POM. In the three affected test reports, the only classpath path change is the SLF4J API JAR, and Logback Classic remains at 1.2.11. The causal change is which logger implementation the API returns. The cast fails in client test code.

The mechanism matches the earlier `pdb` case for SLF4J 2.0.4. Case 18 has its own runs and evidence for the 2.0.6 update. The archived source, report summaries and original Surefire reports are under `logs/case18_evidence/`. The raw build logs are `logs/batch_triage/18e92e4e_pre.log` and `logs/batch_triage/18e92e4e_breaking.log`.
