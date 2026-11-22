# Case 143 review

PRE: BUILD SUCCESS, 148 tests, no failures/errors/skips. BREAKING: BUILD FAILURE, 148 tests, 5 failures and 4 errors, no skips. All nine affected JacksonResponseTest methods trace to NoClassDefFoundError for com.fasterxml.jackson.core.exc.StreamConstraintsException. Five assertion failures expect IOException but receive the same linkage error; they are not separate semantic changes.

Both original images were run. All archived client sources match; pom.xml alone changes jackson-databind 2.14.1 to 2.15.2. The actual test classpath retains jackson-core and jackson-annotations 2.14.1. JAR inspection confirms the missing class is absent from every resolved Jackson JAR. Binary-reference scanning and BaseJsonNode disassembly show the updated Databind references that class whereas PRE Databind does not.

Agent assessment: NON_BEHAVIORAL, binary linkage flag YES. Evidence: logs/case143_evidence/ and original logs logs/batch_triage/bd46a7fe_*.log. Automated cues are separate from this assessment. Independent human review pending; final label blank. No repair attempted.
