# Case 151 review

PRE: BUILD SUCCESS, 737 reported tests, no failures/errors, 4 skipped. BREAKING: BUILD FAILURE, 737 reported tests, 30 errors, 4 skipped. Reported tests include the four skipped tests. All 30 errors are ClassCastException from LogbackLogProvider.addAppenderToType when NOPLogger is cast to ch.qos.logback.classic.Logger.

Both original Docker images were run. All archived client source hashes match; only pom.xml changes slf4j-api 1.7.36 to 2.0.1. The affected test classpath retains Logback Classic/Core 1.2.11 and Logunit Core/Logback 1.1.3. Direct JAR inspection confirms StaticLoggerBinder and Logback Logger remain present. Logunit's cast and updated LoggerFactory provider discovery are archived in disassembly.

A probe compiled once against the PRE API executes identical class bytes with each original image's affected-test JAR classpath. Calls link and succeed in both phases: PRE selects LoggerContext/Logback Logger, BREAKING selects NOPLoggerFactory/NOPLogger and reports ignoring the legacy binding. This supports a provisional behavioral assessment based on changed provider selection and return implementation, with no primary binary linkage failure. The observed impact is in test logging integration.

Evidence: logs/case151_evidence/ including logger_probe_results.json; original logs logs/batch_triage/c8a572a7_*.log. Independent human review pending; final label blank. No repair attempted.
