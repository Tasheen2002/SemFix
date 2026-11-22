# Case 92 review

The webapp updates Log4j Core 2.16.0 to 2.20.0. The root POM version is the sole archived source/POM change. The affected test classpath retains Log4j API 2.16.0.

PRE succeeds with 122 reported tests including two skips. BREAKING reports 103 tests with 90 errors and one skip. Maven and fresh Surefire XML agree. One error names the absent ServiceLoaderUtil class. The other 89 report failed class initialization.

The upgraded Core JAR references ServiceLoaderUtil. The retained API JAR lacks the class, and the run records ClassNotFoundException for it. This establishes a non-behavioural binary incompatibility assessment, pending independent review. Both original runs, reports and inspected JARs are archived. The image pipes Maven through tee, so the explicit build result establishes failure.
