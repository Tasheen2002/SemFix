# Case 24 review

The `sign-maven-plugin` upgrade from SLF4J API 1.7.36 to 2.0.4 is provisionally **behavioural**, pending human review.

PRE passed all 38 tests. BREAKING reported 38 tests, 12 errors, zero assertion failures, and zero skips. SLF4J ignores the unchanged `slf4j-mock` 2.3.0 legacy binding and supplies a no-operation logger. The test library's `LoggerAnnotationEngine.findLoggersMocks` tries to cast that logger to `org.simplify4u.slf4jmock.internal.ProxyMock` during Mockito setup and throws `ClassCastException`.

The archived source files match, the root POM changes only the SLF4J version, and the affected test classpath paths differ only in the SLF4J API JAR. Both image commands pipe Maven through `tee`, which masks Maven's failing exit code. The build summaries and fresh reports establish the outcomes. Case 22 shows the same logger selection mechanism with a different upgrade and mock version.

The logs have prefix `1cf2cb24` under `logs/batch_triage/`. The archives are under `logs/case24_evidence/`.
