# Case 78 review

jasmine-maven-plugin upgrades SLF4J API 1.7.32 to 2.0.2. The archived root POM version and the API JAR in the affected test classpath are the only changes. Both runs retain slf4j-test 1.2.0.

PRE passes all 72 tests. BREAKING reports 72 tests with two failed assertions and zero errors or skips. JasmineResultLoggerTest.shouldLogHeader and shouldLogDetails both see an empty list of captured messages and fail their header assertions. The details test stops at that assertion.

The upgraded API reports ignoring the retained slf4j-test StaticLoggerBinder and selects a no-operation logger. JAR inspection verifies that the old binder is still present and the test library has no service-provider descriptor. The changed logger selection supports a provisional behavioural classification pending independent review.

Both original runs, source, fresh Surefire XML and resolved JARs are archived. Explicit Maven output determines the build outcome because the command pipes Maven through tee.
