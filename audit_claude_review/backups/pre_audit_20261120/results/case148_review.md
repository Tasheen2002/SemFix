# Case 148 review

PRE: BUILD SUCCESS, 389 tests across the reactor, no failures/errors/skips. BREAKING: BUILD FAILURE, 235 tests in jadler-core, 5 ClassCastException errors, no failures/skips. Later reactor modules do not run after jadler-core fails. These missing later executions are not passing or skipped tests.

All five errors originate at JadlerMockerTest.addAppenderToStream, where LoggerFactory.getILoggerFactory() returns org.slf4j.helpers.NOPLoggerFactory instead of the expected ch.qos.logback.classic.LoggerContext. Both original Docker images were run. All archived client source files match; only root pom.xml changes slf4j-api 1.7.36 to 2.0.2. The affected jadler-core classpath retains Logback Classic/Core 1.2.11. Direct JAR inspection confirms StaticLoggerBinder and LoggerContext remain present.

One probe compiled once against the PRE API executes identical class bytes with the failing test's actual JAR classpaths in both original images. Calls link and succeed: PRE selects LoggerContext/Logback Logger, BREAKING selects NOPLoggerFactory/NOPLogger and reports ignoring the legacy binding. This supports a provisional behavioral classification (changed returned factory implementation), with no primary missing class/method linkage failure. The failing cast is in client test code.

Evidence: logs/case148_evidence/ and original logs logs/batch_triage/c4071651_*.log. Full-reactor counts are used rather than the automated triage's last-module total. Independent human review pending; final label blank. No repair attempted.
