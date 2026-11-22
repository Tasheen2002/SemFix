# Case 108 review

jcabi-ssh updates sshd-common from 2.9.2 to 2.10.0. The root POM version is the only changed archived source/POM. The affected test classpath changes only sshd-common and retains sshd-core 2.9.2.

Both original Docker images were run. PRE succeeds with five tests and no failures, errors or skips. BREAKING fails with five tests, no assertion failures, three errors and no skips. Maven and three fresh Surefire XML reports per phase agree. Two errors are NoSuchMethodError for CloseFuture.await(Duration), with SshServer.stop as the first meaningful frame. The third is IOException wrapping a JSch connection reset.

Disassembly confirms old WaitableFuture declares await(Duration), inherited by CloseFuture. The updated declaration instead takes Duration and CancelOption[]; Java varargs do not preserve the old JVM descriptor. Retained SshServer bytecode still calls CloseFuture.await:(Ljava/time/Duration;)Z. This establishes a binary incompatibility.

To investigate the connection reset separately, the original BREAKING image was rerun with only SshByPasswordTest and additional SSHD trace logging. No client source or dependency version was changed. The diagnostic again reports one test/one error and exposes NoSuchMethodError for DefaultKeyExchangeFuture.await(Duration) in AbstractSession.doKexNegotiation before the connection is reset. The original configuration, added logging configuration, command, image identity, log, stopped-container state and fresh diagnostic reports are archived. This connects the remaining connection error to the same old await descriptor, rather than assuming a separate network or behavioral cause.

The evidence supports a non-behavioral assessment pending independent human review. Reviewer/final labels remain blank. Original-image outcomes use Maven and fresh XML because the tee pipeline masks Maven failure in Docker's exit code. The diagnostic is not a repair; no repair was attempted.
