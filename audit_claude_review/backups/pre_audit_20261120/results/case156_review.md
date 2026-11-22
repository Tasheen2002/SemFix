# Case 156 review

PRE: BUILD SUCCESS, 72 tests, no failures/errors/skips. BREAKING: BUILD FAILURE, 72 tests, 2 assertion failures, no errors/skips. JasmineResultLoggerTest expects captured log messages but receives an empty list.

Both original Docker images were run. All archived client source hashes match; only pom.xml changes slf4j-api 1.7.32 to 2.0.5. The affected test classpath retains slf4j-test 1.2.0. Direct JAR inspection confirms its StaticLoggerBinder and TestLoggerFactory remain present, while updated LoggerFactory uses provider discovery and reports ignoring the legacy binding.

One probe compiled once against the PRE API executes identical class bytes with each original image's affected-test JAR classpath. Calls link and succeed: PRE returns TestLoggerFactory/TestLogger, BREAKING returns NOPLoggerFactory/NOPLogger. This supports a provisional behavioral assessment based on changed logger selection and loss of captured log messages, with no primary missing-class/method linkage failure. The observed integration is test logging.

Evidence: logs/case156_evidence/ including logger_probe_results.json; original logs logs/batch_triage/d2fb00d2_*.log. Independent human review pending; final label blank. No repair attempted.
