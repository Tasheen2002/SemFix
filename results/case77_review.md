# Case 77 review

Artipie http updates the junit-jupiter-engine dependency inside the Maven Surefire plugin from 5.8.1 to 5.10.0. This is the sole archived source/POM change. The project test dependencies still resolve Jupiter Engine 5.8.2 and Platform Engine 1.8.2.

PRE passes 906 test executions across two Surefire goals, each reporting the same 453 tests. The report directory retains one 453-test XML set because both executions write to that directory. BREAKING reports zero tests and fails in the first forked test process. The original Surefire dump records NoSuchMethodError for TestDescriptor.getAncestors() in StackTracePruningEngineExecutionListener. A diagnostic Maven rerun with debug logging reproduces the error and shows Platform Launcher 1.10.0 resolved alongside the older project engine. The resolved launcher bytecode calls the method. Platform Engine 1.8.2 lacks it.

The failed fork and missing method support a non-behavioural test infrastructure incompatibility assessment, pending independent review. Automated triage marks the main log as uncertain because it omits the exception type retained in the fork dump. The original images, dump, diagnostic log and disassembly are archived. Explicit Maven output establishes failure because the original command pipes Maven through tee.
