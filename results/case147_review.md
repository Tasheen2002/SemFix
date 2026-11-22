# Case 147 review

PRE: BUILD SUCCESS, 38 tests, no failures/errors/skips. BREAKING: BUILD FAILURE, 38 tests, 12 ClassCastException errors, no failures/skips. Five SignMojoTest invocations and seven EnvironmentTest invocations fail during logging mock initialization. LoggerAnnotationEngine.findLoggersMocks casts NOPLogger to org.simplify4u.slf4jmock.internal.ProxyMock.

Both original images were run. All archived client source files match; only pom.xml changes slf4j-api 1.7.36 to 2.0.7. The affected classpath retains slf4j-mock and slf4j-mock-common 2.3.0. Resolved-JAR inspection confirms StaticLoggerBinder remains in slf4j-mock, while internal.ProxyMock remains in slf4j-mock-common. Its caller's cast is archived in disassembly. The older non-internal ProxyMock namespace was also checked and is absent; it is not the type named in these failures.

A probe compiled once against the PRE API runs identical class bytes with each original image's affected-test JAR classpath. Both calls link successfully: PRE returns a mock proxy, BREAKING returns NOPLoggerFactory/NOPLogger and reports ignoring the legacy binder. This supports a provisional behavioral classification based on changed logger selection, with no primary binary linkage error. The observed impact is in test logging integration.

Evidence: logs/case147_evidence/, including mock_common_inspection.json for each phase and logger_probe_results.json; original logs logs/batch_triage/c3d0aba8_*.log. Independent human review pending; final label blank. No repair attempted.
