# Case 130 review

Both original pay-cardid images ran. PRE passed 47 tests. BREAKING reports 37 tests and one error during CardIdResourceITest setup. Maven totals and six fresh reports per phase agree. The root POM changes only dropwizard-sentry from 2.1.2-4 to 4.0.0. Sentry and Sentry Logback change transitively from 6.5.0 to 6.23.0. The test classpath retains Dropwizard Logging 2.1.6.

Both Sentry artifacts register SentryAppenderFactory under META-INF/services/io.dropwizard.logging.AppenderFactory. The new provider bytecode extends io.dropwizard.logging.common.AbstractAppenderFactory. The retained Logging artifact has only io.dropwizard.logging.AbstractAppenderFactory. The original stack shows NoClassDefFoundError and ClassNotFoundException for the newer superclass. The observed failure is a binary linkage error while loading the provider.

The assessment is NON_BEHAVIORAL pending independent human review. Both original logs, test reports, dependency artifacts and service descriptors are archived.
