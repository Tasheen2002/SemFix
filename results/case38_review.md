# Case 38 review

The `recheck` upgrade of SLF4J API from 1.7.36 to 2.0.0 is provisionally **behavioural**, pending human review.

PRE reported 737 tests, including four skips, with zero failures or errors. BREAKING reported 737 tests, including four skips and 30 errors. SLF4J ignores the unchanged Logback 1.2.11 legacy binding and returns a no-operation logger. LogUnit's Logback adapter 1.1.3 casts that logger to Logback's `Logger` in `LogbackLogProvider.addAppenderToType`. The changed logger selection leads to `ClassCastException` in test setup. Case 31 reproduces the same mechanism for the separate upgrade to SLF4J 2.0.4.

The root POM changes only the SLF4J API version. Maven summaries and fresh reports agree. The image command pipes Maven through `tee`, which masks its failing exit code. Logs have prefix `34e00b73` under `logs/batch_triage/`, and the reports and source archives are under `logs/case38_evidence/`.
