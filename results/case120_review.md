# Case 120 review

ApkToolBoxGUI updates log4j-core from 2.17.2 to 2.19.0. The root POM version is the sole archived source/POM change. Only Core changes on the affected test classpath; Log4j API remains at 2.17.2.

Both original images were run. PRE succeeds with 13 tests and no failures, errors or skips. BREAKING reports 13 tests, zero failures, six errors and no skips. Maven and four fresh Surefire XML reports per phase agree. The fresh errors all report failed initialization of ThreadContextDataInjector, LoggerContext or client utility classes. Those messages alone do not establish that the named classes are missing.

The initiating raw-log error is different: StatusLogger records NoClassDefFoundError for org/apache/logging/log4j/util/ServiceLoaderUtil, caused by ClassNotFoundException. Its first frame is ThreadContextDataInjector.getServiceProviders during that class's static initialization. Actual resolved JAR inspection confirms ServiceLoaderUtil is absent from retained API 2.17.2, and disassembly of updated Core shows the new reference. Thus the primary missing-type binary incompatibility explains the later initialization failures, supporting NON_BEHAVIORAL with binary_linkage_incompatibility=YES.

The initiating error, all six subsequent errors, original runs, fresh reports, source, JARs and disassembly are preserved. Independent human review remains pending, with reviewer/final labels blank. Automated screening remains separate. Explicit Maven output determines build outcomes because the original tee pipeline masks Maven failures in Docker's exit code. No repair or substitution control was run.
