# Case 64 review

github-checks-plugin updates the Jenkins github-api plugin from 1.117 to 1.303-400.v35c2d8258028. The root POM version is the only archived source/POM change. The resolved test classpath also changes transitive dependencies, including okhttp-api 3.14.9 to 4.9.2-20211102.

PRE passes all 49 tests. BREAKING runs 49 tests with one assertion failure and zero errors or skips. Maven and the eight fresh Surefire reports in each run agree. The sole failure is ArchitectureTest.NO_JENKINS_INSTANCE_CALL.

The unchanged ArchUnit test scans io.jenkins.plugins packages. Its rule restricts direct calls to Jenkins.get() and related singleton accessors. The updated okhttp-api JAR contains JenkinsOkHttpClient, which is absent from the old okhttp-api JAR. Disassembly confirms two Jenkins.get() instructions in newClientBuilder, matching the violations reported by ArchUnit. The assertion evaluates dependency bytecode against an architecture rule. This is assessed as non-behavioural under the project's runtime semantics criterion, pending independent human review. The binary-linkage flag is NO because this is a static rule failure. Automated triage flags the assertion as a likely behavioural candidate.

The 52ba94ad logs and case64_evidence directory retain both runs, source, reports, resolved JARs and disassembly. Explicit Maven output establishes the build result because the tee pipeline masks Maven's exit status.
