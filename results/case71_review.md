# Case 71 review

java-pubsublite updates Flogger google-extensions 0.6 to 0.7.1 in the root POM. The test classpath also upgrades Flogger core to 0.7.1 and retains the system backend at 0.6.

PRE passes 372 tests. BREAKING runs 331 tests and reports 123 errors before skipping the Beam module. Its raw XML reports 337 entries and 129 errors because six tests have separate setup and teardown error entries. Counting each test once yields the Maven totals. Both raw and reconciled counts are archived.

Logging initialization fails because DefaultPlatform in the retained backend invokes StaticMethodCaller.callGetterFromSystemProperty(String, Class). Disassembly of the resolved JARs confirms the method exists in Flogger 0.6 and is absent in 0.7.1. The resulting NoSuchMethodError prevents logger initialization and leads to subsequent class-initialization and teardown errors. This supports a non-behavioural binary incompatibility assessment pending independent review.

Maven's explicit build result establishes failure because the image pipes Maven through tee.
