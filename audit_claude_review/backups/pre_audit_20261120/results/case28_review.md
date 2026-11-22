# Case 28 review

The `pay-cardid` upgrade of Dropwizard Sentry from 2.0.22 to 2.0.28-8 is provisionally **behavioural**, pending human review.

PRE passed all 44 tests. BREAKING reported 34 tests and one class setup error, with zero assertion failures or skips. `CardIdResourceITest` fails while loading the unchanged YAML configuration. Jackson rejects `logging.appenders.[1].stacktraceAppPackages` as an unrecognized property on `SentryAppenderFactory`, and Dropwizard surfaces the error as a `ConfigurationParsingException`.

Disassembly of the resolved appender classes shows the old property and its accessor methods in 2.0.22. The 2.0.28-8 class exposes `inAppIncludes` and lacks those old members. The failing operation is YAML deserialization by property name. The update changes the accepted configuration and the application fails during startup.

The root POM changes only the Dropwizard Sentry version. The resolved Sentry libraries also move from 1.7.30 to 5.6.0 through that update. Maven summaries match the fresh reports. The image command pipes Maven through `tee`, which masks Maven's failing exit code. Logs have prefix `22eec990` under `logs/batch_triage/`. The archives, JARs and disassembly are under `logs/case28_evidence/`.
