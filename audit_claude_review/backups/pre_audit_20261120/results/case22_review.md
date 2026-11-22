# Case 22 review

The `sign-maven-plugin` upgrade of SLF4J API from 1.7.36 to 2.0.0 is provisionally **behavioural**, pending human review.

PRE passed all 38 tests. BREAKING reported 38 tests with 12 errors and zero assertion failures or skips. SLF4J 2.0.0 ignores the legacy `StaticLoggerBinder` from the unchanged `slf4j-mock` 2.2.0 and supplies a no-operation logger. The test library's `LoggerAnnotationEngine.findLoggersMocks` casts that logger to `ProxyMock`, which throws `ClassCastException`. The changed API behaviour is the implementation selected for the logger.

The archived sources match and the only POM change is the SLF4J API version. The same mechanism was observed in the separate 2.0.2 upgrade for this project. Both containers exit zero because the Maven command pipes output through `tee`. The Maven build summaries agree with the fresh Surefire reports.

The logs have prefix `1ca02168` under `logs/batch_triage/`, and the archives are under `logs/case22_evidence/`.
