# Case 80 review

The webapp updates Log4j API 2.16.0 to 2.20.0. The root POM version is the only archived source/POM change. The affected test classpath retains Log4j Core 2.16.0.

PRE succeeds with 122 reported tests including two skips. BREAKING reports 103 tests, 90 errors, zero failures and one skip. Maven and fresh Surefire XML agree. The updated run reports fewer tests while multiple classes fail to initialize.

The primary NoSuchMethodError names LoaderUtil.getClassLoaders(). Disassembly shows the old API declares this method, the updated API omits it, and the retained Core invokes it. The remaining 89 reports are NoClassDefFoundError initialization errors in the logging, helper and test runner classes. This supports a non-behavioural binary incompatibility assessment pending independent review.

Both original runs, reports, resolved JARs and disassembly are archived. Explicit Maven output establishes failure because the command pipes Maven through tee.
