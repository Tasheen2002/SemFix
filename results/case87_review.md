# Case 87 review

pay-cardid updates Dropwizard Sentry 2.1.2-4 to 4.0.1-2. The root POM version is the only archived source/POM change. The Sentry libraries also change transitively. The test classpath retains Dropwizard Logging 2.1.6.

PRE passes all 47 tests. BREAKING reports 37 tests with one error in CardIdResourceITest and no failures or skips. The integration class stops during setup when Jackson cannot resolve the sentry appender type in the unchanged YAML. Maven and fresh Surefire XML agree.

The old Sentry JAR registers under io.dropwizard.logging.AppenderFactory, the interface in the retained logging JAR. The upgraded Sentry JAR registers under io.dropwizard.logging.common.AppenderFactory. Its implementation also extends the newer common-package base class. The retained runtime cannot discover the upgraded provider under its service interface. This is assessed as a non-behavioural missing compatible provider, pending independent review. The observed exception is subtype lookup failure, so the binary linkage flag is NO.

Both runs, reports, service descriptor inspection and class signatures are archived. Explicit Maven output establishes failure because the command pipes Maven through tee.
