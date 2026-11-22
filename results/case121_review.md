# Case 121 review

IDS-Messaging-Services updates junit-platform-surefire-provider from 1.0.3 to 1.3.2 specifically in core/pom.xml. This is the only changed archived source/POM. It is a separate candidate from the earlier broker, clearinghouse and paris module updates.

Both original images were run. PRE succeeds with 32 reactor tests and no failures, errors or skips. BREAKING fails in the first core module before starting tests, reporting zero tests and zero per-test failures/errors/skips. All downstream modules are skipped. There is no fresh BREAKING TEST XML. Zero report errors must not be mistaken for a successful build; Maven reports BUILD FAILURE and PluginContainerException.

The original failure names NoSuchMethodError for StringUtils.requireNonNull(Object). Maven prints the failing plugin realm directly: maven-surefire-plugin and maven-surefire-common remain at 2.19.1, the JUnit provider is 1.3.2, and common-java5 is 2.22.0. Those are plugin-realm URLs, not the application test classpath. The collection preserves every reported URL and copies the relevant JARs from the original stopped container. Successful PRE XML does not expose this plugin realm, so no PRE plugin-classpath inspection is claimed.

Disassembly identifies the actual old caller, AbstractForkInputStream in maven-surefire-common 2.19.1, invoking StringUtils.requireNonNull:(Object)Object. The selected common-java5 2.22.0 StringUtils class lacks that method. This establishes a binary test-runner incompatibility and supports NON_BEHAVIORAL with binary_linkage_incompatibility=YES.

Independent human review remains pending, with reviewer/final labels blank. Automated triage is separate from the evidence-backed agent assessment. Both original runs, fresh PRE XML, source/POM snapshots, original plugin URLs, artifact hashes and caller/callee disassembly are preserved. Explicit Maven outcomes determine results because the tee pipeline masks failure in Docker's exit code. No repair or dependency substitution was attempted.
