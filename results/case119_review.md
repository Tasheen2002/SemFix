# Case 119 review

html2pop3 updates logback-classic from 1.4.5 to 1.4.6. The root POM version is the sole archived source/POM change. Only the Classic JAR changes on the affected test classpath; Logback Core remains at 1.4.5.

Both original images were run. PRE succeeds with five tests, zero failures/errors/skips. BREAKING reports five tests with zero failures, two errors and zero skips. Maven and two fresh Surefire XML reports per phase agree. FilterTest.testAdd fails during logger initialization with NoSuchMethodError for CachingDateFormatter(String, ZoneId, Locale). FilterTest.testIsAllow then reports Could not initialize class FilterTest, a consequence of the earlier failure.

Actual JAR disassembly confirms the updated Classic DateConverter.start invokes the constructor descriptor (String;ZoneId;Locale;)V. Retained Core 1.4.5 exposes one-argument String and two-argument String/ZoneId constructors, but not the requested three-argument constructor. This is a binary incompatibility between Classic and Core despite the patch-level update, supporting NON_BEHAVIORAL with binary_linkage_incompatibility=YES.

Independent human review remains pending, with reviewer/final labels blank. Automated screening is separate from the evidence-backed assessment. Explicit Maven outcomes and fresh XML determine results because the original tee pipeline masks build failure in Docker's exit code. No repair or substitution control was run.
