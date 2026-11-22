# Case 89 review

junit-quickcheck updates Mockito 4.11.0 to 5.3.1. The root POM version is the sole archived source/POM change. Byte Buddy components also change transitively.

PRE succeeds with 1,114 tests including 20 skips. BREAKING stops in core after 510 reported tests with one assertion failure and 18 skips. Maven and fresh Surefire reports agree. CompositeGeneratorTest.shrinkingChoosesAComponentCapableOfShrinkingTheValue expects [3, 6] and receives an empty list.

The test stubs doShrink and relies on the final Generator.shrink method to call it. Actual JAR disassembly shows the default MockMaker changes from subclass to inline. The inline mock maker intercepts the unstubbed final method and returns the default empty list. The archived project has no MockMaker override.

A focused control adds the mock-maker-subclass override inside a disposable BREAKING-image container. The exact failing test passes with Mockito 5.3.1 verified on the Surefire classpath. The control covers one test. The original full-suite run establishes the failure under the new default. This supports a provisional behavioural assessment pending independent review.

The original runs, reports, JARs and control evidence are archived. Explicit Maven output establishes failure because the original command pipes Maven through tee.
