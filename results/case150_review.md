# Case 150 review

PRE: BUILD SUCCESS, 757 tests, no failures/errors/skips. BREAKING: BUILD FAILURE, 726 reported tests, no failures, 12 errors, no skips. Eight EventMessageHandlerTest methods fail in setUp when NOPLogger is cast to Logback Logger. Four resource test classes fail during initialization because Dropwizard cannot acquire the logger context.

The four resource classes contain 35 PRE tests (Create 7, Find 7, Search 3, Update 18) but produce four class-level BREAKING error entries, explaining the net reduction of 31. Those 31 are not skipped or passing tests. Later Could not initialize class NoClassDefFoundError entries are secondary to ExceptionInInitializerError and IllegalStateException: Unable to acquire the logger context; they do not establish a primary missing-class linkage error.

Both original Docker images were run. All archived client source files match; only pom.xml changes slf4j-api 1.7.36 to 2.0.3. The actual test classpath retains Logback Classic/Core 1.2.11. Direct JAR inspection confirms StaticLoggerBinder, Logger and LoggerContext remain present. Updated LoggerFactory disassembly and original logs show provider discovery ignoring the retained legacy binder.

One probe compiled once against the PRE API executes identical class bytes with the affected test's JAR classpath in both original images. Calls link and succeed: PRE returns LoggerContext/Logback Logger, BREAKING returns NOPLoggerFactory/NOPLogger. This supports a provisional behavioral classification based on changed provider selection/returned implementations, with no primary binary linkage failure.

Evidence: logs/case150_evidence/ including logger_probe_results.json, and original logs logs/batch_triage/c5db2b61_*.log. Independent human review pending; final label blank. No repair attempted.
