# Case 65 review

html2pop3 updates Logback Classic 1.4.1 to 1.4.3. The root POM version is the sole archived source/POM change, and the affected test classpath retains Logback Core 1.4.1.

PRE passes all five tests. BREAKING reports five tests with two errors, zero failures and zero skips. Maven and two fresh Surefire reports per run agree. FilterTest.testAdd fails during logger initialization because SanityChecker cannot be loaded. FilterTest.testIsAllow then fails to initialize the same test class.

The updated Classic's DefaultJoranConfigurator constructs JoranConfigurator, whose bytecode references ch.qos.logback.core.joran.sanity.SanityChecker. Inspection of the resolved Core 1.4.1 JAR confirms the class is absent. The primary NoClassDefFoundError wraps ClassNotFoundException. The subsequent initialization error is a consequence. This is a non-behavioural binary incompatibility, pending independent human review.

The 52c06990 logs and case65_evidence directory contain the image runs, fresh reports, source, resolved JARs and bytecode inspection. The explicit Maven result and reports establish failure because the tee pipeline masks Maven's exit status.
