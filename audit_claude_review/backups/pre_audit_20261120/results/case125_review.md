# Case 125 review

dropwizard-pac4j updates Jetty Server from 9.4.35.v20201120 to 10.0.14 in the root POM. This is the sole archived source/POM change. The affected classpath replaces the Server JAR and adds jetty-servlet-api 4.0.6; Jetty Util remains at 9.4.35.v20201120.

Both original images were run. PRE succeeds with 16 tests, zero failures/errors/skips. BREAKING reports 16 tests, zero failures, ten errors and zero skips. Maven and four fresh Surefire XML reports per phase agree directly. One primary error names missing org/eclipse/jetty/util/component/AbstractLifeCycle$StopException. Nine other errors report failed initialization of Dropwizard's MutableServletContextHandler and cascade from startup failure.

Actual JAR inspection confirms StopException is absent from retained Jetty Util 9.4.35. The upgraded Server class references that nested type; its disassembly and the original missing-class stack corroborate the requirement. This is a binary incompatibility between Jetty generations, not evidence that MutableServletContextHandler itself is missing. The evidence supports NON_BEHAVIORAL with binary_linkage_incompatibility=YES.

Independent human review remains pending, with reviewer/final labels blank. Automated triage is separate from the curated assessment. Both original runs, fresh reports, source/POM snapshots, exact artifacts and disassembly are preserved. Explicit Maven outcomes determine the builds because the tee pipeline masks Maven failure in Docker's exit code. No repair or substitution control was run.
