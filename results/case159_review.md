# Case 159 review

PRE: BUILD SUCCESS, 739 tests, no failures/errors/skips. BREAKING: BUILD FAILURE, 708 reported tests, 12 errors, no failures/skips. Eight EventMessageHandlerTest methods fail in setUp when NOPLogger is cast to Logback Logger. Four resource test classes fail during static initialization because Dropwizard cannot acquire the logger context.

The four resource classes contain 35 PRE tests (Create 7, Find 7, Search 3, Update 18), but produce four class-level BREAKING error entries, explaining the net reduction of 31. Those absent executions are not skipped or passing tests. Later Could not initialize class NoClassDefFoundError entries are secondary to ExceptionInInitializerError and IllegalStateException: Unable to acquire the logger context. They are not evidence of a primary missing-class linkage failure.

Both original Docker images were run. All archived client source hashes match; only pom.xml changes slf4j-api 1.7.36 to 2.0.4. The actual test classpath retains Logback Classic/Core 1.2.11. Direct JAR inspection confirms StaticLoggerBinder, Logger and LoggerContext remain present. Updated LoggerFactory disassembly and original logs show provider discovery ignoring the legacy binding.

A probe compiled once against the PRE API executes identical class bytes with each original image's affected-test JAR classpath. Calls link and succeed: PRE returns LoggerContext/Logback Logger, BREAKING returns NOPLoggerFactory/NOPLogger. This supports a provisional behavioral assessment based on changed provider selection/returned implementations, with no primary binary linkage failure.

Evidence: logs/case159_evidence/ including logger_probe_results.json; original logs logs/batch_triage/d4b00540_*.log. Independent human review pending; final label blank. No repair attempted.
