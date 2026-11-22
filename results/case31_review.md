# Case 31 review

The `recheck` upgrade of SLF4J API from 1.7.36 to 2.0.4 is provisionally **behavioural**, pending human review.

PRE reported 737 tests with four skips and zero failures or errors. BREAKING reported 737 tests with four skips and 30 errors. SLF4J ignores the unchanged Logback 1.2.11 legacy binding and supplies a no-operation logger. LogUnit's Logback adapter 1.1.3 tries to cast the returned logger to `ch.qos.logback.classic.Logger` in `LogbackLogProvider.addAppenderToType`. All 30 reported errors are `ClassCastException` at logging capture setup. The logger returned by the same call changes after the upgrade.

The root POM changes only the SLF4J version. The build summaries and fresh Surefire reports agree. The Docker command pipes Maven through `tee`, masking the failing Maven exit code. Logs have prefix `28745a38` under `logs/batch_triage/`, and reports and source are under `logs/case31_evidence/`.
