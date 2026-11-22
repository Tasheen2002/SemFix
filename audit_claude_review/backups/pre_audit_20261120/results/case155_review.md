# Case 155 review

PRE: BUILD SUCCESS, 38 tests, no failures/errors/skips. BREAKING: BUILD FAILURE, 38 tests, 12 ClassCastException errors, no failures/skips. LoggerAnnotationEngine.findLoggersMocks attempts to cast NOPLogger to org.simplify4u.slf4jmock.internal.ProxyMock during test mock initialization.

Both original Docker images were run. All archived client source hashes match; only pom.xml changes slf4j-api 1.7.36 to 2.0.5. The affected test classpath retains slf4j-mock and slf4j-mock-common 2.3.0. Direct JAR inspection confirms StaticLoggerBinder remains in slf4j-mock and internal.ProxyMock remains in slf4j-mock-common. The cast is visible in LoggerAnnotationEngine disassembly from the common JAR.

A probe compiled once against the PRE API executes identical class bytes with each original image's affected-test JAR classpath. Calls link and succeed: PRE selects the mock factory/logger proxy, BREAKING selects NOPLoggerFactory/NOPLogger and reports ignoring the legacy binding. This supports a provisional behavioral assessment (changed provider selection and return implementation), with no primary missing-class/method linkage error. The observed impact is in test logging integration.

Evidence: logs/case155_evidence/ including logger_probe_results.json; original logs logs/batch_triage/d154a6b3_*.log. Independent human review pending; final label blank. No repair attempted.
