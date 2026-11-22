# Case 145 review

PRE: BUILD SUCCESS, 737 reported tests, no failures/errors, 4 skipped. BREAKING: BUILD FAILURE, 737 reported tests, 30 errors, 4 skipped. Reported tests include skipped tests. All 30 errors are ClassCastException when LogbackLogProvider.addAppenderToType casts org.slf4j.helpers.NOPLogger to ch.qos.logback.classic.Logger.

Both original images were run. All archived client source files match; pom.xml alone updates slf4j-api 1.7.36 to 2.0.6. Actual test classpaths retain Logback Classic/Core 1.2.11 and Logunit Core/Logback 1.1.3. JAR inspection confirms Logback Logger and StaticLoggerBinder remain present, with the original Logunit cast visible in disassembly. The updated API ignores the retained legacy binding and selects NOPLoggerFactory.

One probe compiled once against the old API executes identical class bytes with each original image's affected-test JAR classpath. Calls link and succeed in both phases: PRE returns LoggerContext/Logback Logger, BREAKING returns NOPLoggerFactory/NOPLogger. The changed logger selection supports a provisional behavioral classification, with no primary binary linkage failure. Observed errors occur in test logging integration.

Evidence: logs/case145_evidence/ including logger_probe_results.json, and original logs logs/batch_triage/bdbdd72d_*.log. Independent human review pending; final label blank. No repair attempted.
