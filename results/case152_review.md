# Case 152 review

PRE: BUILD SUCCESS, 180 reported tests, no failures/errors, 9 skipped. BREAKING: BUILD FAILURE, 134 reported tests, 131 errors, 1 skipped. Totals include skipped tests and class-level errors; the changed number of reported tests is not evidence of successful or skipped executions for tests prevented from running.

The earliest meaningful error in the original BREAKING log is NoSuchMethodError for org.apache.logging.log4j.util.LoaderUtil.getClassLoaders():java.lang.ClassLoader[], called by org.apache.logging.log4j.core.impl.ThreadContextDataInjector.getServiceProviders during static initialization. The archived XML reports later NoClassDefFoundError: Could not initialize class failures across logging and client thermodynamic classes. These are cascades, not proof that the client classes disappeared or independently changed behavior.

Both original Docker images were run. All archived client source hashes match; only pom.xml changes log4j-api 2.17.2 to 2.18.0, while the actual test classpath retains log4j-core 2.17.2. Direct inspection/disassembly confirms the same core invokes the exact getClassLoaders descriptor, present in PRE LoaderUtil but absent in BREAKING LoaderUtil. This is a method-level binary incompatibility.

Agent assessment: NON_BEHAVIORAL, binary linkage flag YES. Evidence: logs/case152_evidence/, including both resolved Log4j JARs and their disassemblies, and logs/batch_triage/c923de11_*.log. Independent human review pending; final label blank. No repair attempted.
