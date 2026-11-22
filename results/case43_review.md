# Case 43 review

The `a` project's GraalJS ScriptEngine upgrade from 22.3.2 to 23.0.0 is provisionally **non-behavioural**, pending human review.

PRE reported 80 tests, including one skip, with zero failures or errors. BREAKING reported the same 80 tests and one skip, with 79 UnsupportedClassVersionError errors. The JVM rejects GraalJSEngineFactory during test setup. Its class-file header changes from major version 55 in the resolved 22.3.2 JAR to 61 in 23.0.0. The Java 11 runtime supports class-file versions up to 55.

Only the ScriptEngine dependency version changes in the archived POM. The affected classpath paths differ only in that JAR. Maven and fresh Surefire summaries agree. The image command pipes Maven through tee, masking its failing exit code. Case 7 records the analogous issue against version 23.0.1.

Logs have prefix `3b47c247` under `logs/batch_triage/`. Fresh reports, source archives, image provenance and both JARs are under `logs/case43_evidence/`.
