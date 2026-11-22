# Case 25 review

The `webapp` upgrade of Log4j API from 2.16.0 to 2.18.0 is a **non-behavioural binary linkage incompatibility**, pending human review.

PRE reported 67 tests, including two skips, with zero failures or errors. BREAKING reported 61 tests, including one skip and 48 errors, with zero assertion failures.

Log4j Core remains at 2.16.0. Its class files reference `LoaderUtil.getClassLoaders()`. Disassembly of the resolved Log4j API 2.18.0 JAR shows that `LoaderUtil` lacks that method, and the BREAKING reports record the matching `NoSuchMethodError`. The other 47 errors are class-initialization failures after the logging bootstrap fails.

The archived sources match and the only POM change is the Log4j API version. Maven summaries match the fresh reports. Both containers return zero because the image command pipes Maven output through `tee`. The build logs have prefix `1eb6d9d5` under `logs/batch_triage/`, and the reports, JARs and disassembly are under `logs/case25_evidence/`.
