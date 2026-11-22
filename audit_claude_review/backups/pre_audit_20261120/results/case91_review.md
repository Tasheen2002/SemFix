# Case 91 review

semantic-metrics updates OkHttp 3.3.1 to 3.14.9. The root POM version is the sole archived source/POM change. The test classpath also updates Okio while retaining MockWebServer and okhttp-ws 3.3.1.

PRE passes all 111 tests. BREAKING reports 111 tests with two errors in OkRemoteTest setup. Maven reactor totals and fresh Surefire XML agree. Automated triage captures the last module's 23 tests.

Both tests fail with VerifyError because a loaded class inherits from a final class. The retained MockWebServer$5 extends RealWebSocket. The old okhttp-ws JAR defines that superclass as abstract, while the upgraded OkHttp JAR defines the same binary name as final. A same-container probe loads the exact nested class with the PRE and BREAKING dependency classpaths. PRE loads successfully and BREAKING reproduces the VerifyError. The class declarations identify the incompatible inheritance. This supports a non-behavioural binary incompatibility assessment pending independent review.

Both original runs, reports, classpath probe and JARs are archived. The explicit Maven outcome establishes failure because the image pipes Maven through tee.
