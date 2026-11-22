# Case 39 review

The `pay-cardid` upgrade of Dropwizard Sentry from 2.0.22 to 2.0.26-3 is provisionally **behavioural**, pending human review.

PRE passed all 44 tests. BREAKING reported 34 tests and one class setup error, with zero assertion failures or skips. `CardIdResourceITest` fails during configuration loading. Jackson rejects `logging.appenders.[1].stacktraceAppPackages` as an unrecognized property on `SentryAppenderFactory`. Dropwizard wraps this as `ConfigurationParsingException`.

Disassembly of the resolved appender JARs shows the old property's accessors in 2.0.22. The 2.0.26-3 class exposes `inAppIncludes` and lacks the old members. The upgrade changes which properties the unchanged YAML can supply. Cases 28 and 35 reproduce the same configuration failure against different versions.

The root POM changes only the Dropwizard Sentry version, and the resolved transitive Sentry version moves from 1.7.30 to 5.5.0. Maven summaries match the fresh reports. The `tee` pipeline masks Maven's failing exit code. Logs have prefix `359f45ab` under `logs/batch_triage/`. The archives, JARs and disassembly are under `logs/case39_evidence/`.
