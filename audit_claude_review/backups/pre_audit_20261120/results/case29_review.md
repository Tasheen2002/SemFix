# Case 29 review

The `webapp` upgrade of Log4j API from 2.16.0 to 2.19.0 is a **non-behavioural binary linkage incompatibility**, pending human review.

PRE reported 122 tests, including two skips, with zero failures or errors. BREAKING reported 103 tests, including one skip and 90 errors, with zero assertion failures.

Log4j Core stays at 2.16.0 and references `LoaderUtil.getClassLoaders()`. The resolved Log4j API 2.19.0 class lacks that method. The resulting `NoSuchMethodError` occurs during logging startup, followed by 89 class-initialization errors. Case 25 shows the same method mismatch against a separate API upgrade to 2.18.0.

The archived source files match and only the Log4j API version changes in the POM. Maven summaries match the fresh reports. The image command pipes Maven through `tee`, masking the failing Maven exit code. Logs have prefix `24d59062` under `logs/batch_triage/`. The archives, JARs and disassembly are under `logs/case29_evidence/`.
