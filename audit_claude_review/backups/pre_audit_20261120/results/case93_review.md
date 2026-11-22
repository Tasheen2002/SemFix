# Case 93 review

billy updates Hibernate Validator 6.1.7.Final to 7.0.4.Final. Only the root POM changes among archived source and POM files.

PRE succeeds with 279 tests including four skips. BREAKING stops in billy-core with 20 tests and 19 errors. Maven and fresh Surefire XML agree. The initial javax.validation.NoProviderFoundException fails BillyValidator initialization and subsequent tests report failed initialization.

The retained Validation API 2.0.2 provides the javax interface. The resolved PRE validator JAR registers a javax provider, and the updated JAR registers a Jakarta provider. The initiating failure is discovery of a compatible provider. This is assessed as non-behavioural with the binary-linkage flag set to NO, pending independent review.

Both runs, resolved JARs and reports are archived. Explicit Maven output establishes failure because the image pipes Maven through tee.
