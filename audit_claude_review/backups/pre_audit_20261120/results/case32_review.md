# Case 32 review

The `html2pop3` upgrade of Logback Classic from 1.2.11 to 1.4.0 is a **non-behavioural binary linkage incompatibility**, pending human review.

PRE passed all five tests. BREAKING reported five tests and two errors. The first `FilterTest` error is a `NoSuchMethodError` during `ContextInitializer.autoConfig`. Logback Classic 1.4.0 calls `EnvUtil.logbackVersion()`, which is absent from the resolved Logback Core 1.2.11. The second error reports that the failed test class could not initialize. Disassembly of the two resolved JARs confirms the call and the absent method.

Only the Logback Classic version changes in the archived project POM. Logback Core 1.2.11 and SLF4J API 2.0.0 appear in the same test's classpath in both runs. Maven summaries match the fresh reports. The `tee` pipeline masks Maven's failing exit code. Logs have prefix `2b60dcd8` under `logs/batch_triage/`, and reports, JARs and disassembly are under `logs/case32_evidence/`.
