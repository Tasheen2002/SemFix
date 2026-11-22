# Case 27 review

The `pay-adminusers` upgrade of SLF4J API from 1.7.36 to 2.0.6 is provisionally **behavioural**, pending human review.

PRE passed all 729 tests. BREAKING reported 697 tests with 12 errors, zero assertion failures, and zero skips. SLF4J ignores the unchanged Logback 1.2.11 legacy binding and returns a no-operation logger. Eight `EventMessageHandlerTest` setup calls try to cast the returned logger to Logback's `Logger`, causing `ClassCastException`. Four Dropwizard resource-test classes fail to initialize because `LoggingUtil.getLoggerContext` cannot obtain a Logback logger context. Surefire reports those class setup failures in place of their individual test executions.

The archived sources match and the root POM changes only the SLF4J API version. Maven's summaries agree with the fresh Surefire reports. Both image commands pipe Maven output through `tee`, which masks Maven's failing exit code. The build logs have prefix `22413589` under `logs/batch_triage/`. The evidence archives are under `logs/case27_evidence/`.
