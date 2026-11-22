# Case 35 review

The `pay-cardid` upgrade of Dropwizard Sentry from 2.0.22 to 2.0.28-3 is provisionally **behavioural**, pending human review.

PRE passed all 44 tests. BREAKING reported 34 tests and one class setup error, with zero assertion failures or skips. `CardIdResourceITest` fails while loading the unchanged YAML configuration. Jackson rejects `logging.appenders.[1].stacktraceAppPackages` as an unrecognized property on `SentryAppenderFactory`. Dropwizard reports a `ConfigurationParsingException`.

The resolved 2.0.22 appender class has the old property and its accessor methods. The resolved 2.0.28-3 class exposes `inAppIncludes` and lacks the old members. The failure occurs during deserialization by property name. The changed set of accepted configuration properties explains the startup failure. Case 28 shows the same mechanism with the separate 2.0.28-8 upgrade.

The root POM changes only the Dropwizard Sentry version. Resolved Sentry libraries move from 1.7.30 to 5.5.2. Maven summaries agree with the fresh Surefire reports. The `tee` pipeline masks Maven's failing exit code. Logs have prefix `30149ce4` under `logs/batch_triage/`, and the archives, JARs and disassembly are under `logs/case35_evidence/`.
