# Case 53 review

The plexus-archiver upgrade of Plexus IO 3.2.0 to 3.3.0 is provisionally **behavioural**, pending independent human review.

PRE completed successfully with 177 reported tests, zero failures/errors and two skips. BREAKING reported 177 tests, zero failures, 22 errors and two skips, and Maven BUILD FAILURE. Fresh Surefire XML agrees with the Maven totals. All errors are ArchiverException reporting "Not a directory" for a directory symlink.

ArchiveEntry.createDirectoryEntry checks resource.isDirectory() and throws this exception at source line 230. In Plexus IO 3.2.0, PlexusIoFileResource.isDirectory() calls File.isDirectory(), following the link. Version 3.3.0 instead uses FileAttributes.isDirectory() when those attributes are present; its attributes are read with NOFOLLOW_LINKS. The same symlink consequently stops being reported as a directory. The API exists and executes in both versions; the observed break is its changed result.

A standalone probe compiled against each archived dependency JAR in the same BREAKING-image environment creates a directory and a symlink, then constructs the same FileResource with FileAttributes. Version 3.2.0 reports File.isDirectory=true, resource.isDirectory=true, resource.isSymbolicLink=true; version 3.3.0 reports true, false, true. Source, shell command, output and disassembly are retained in logs/case53_evidence/. This focused probe supports the mechanism; the original full image runs supply the test outcomes.

The sole source/POM change is the Plexus IO version in root pom.xml. The affected test classpath changes only this JAR. Automatic triage says AUTO_RUNTIME_REVIEW_REQUIRED; this agent diagnosis is a separate provisional classification. The image's tee pipeline returns zero even on Maven failure, so conclusions use Maven output and fresh XML. Raw logs have prefix 46698497. No repair was attempted.
