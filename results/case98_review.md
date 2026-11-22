# Case 98 review

junit-quickcheck updates Mockito 4.11.0 to 5.2.0. The root POM version is the sole archived source/POM change.

PRE succeeds with 1,114 reported tests including 20 skips. BREAKING stops in core after 510 tests with one failure and 18 skips. Maven and fresh Surefire XML agree. The failing test expects [3, 6] and receives an empty list from the composite generator.

The test stubs doShrink and depends on the final Generator.shrink method to call it. The resolved Mockito JARs show that the default changes from the subclass mock maker to the inline mock maker. Inline mocking intercepts the unstubbed final method. The project has no mock-maker override in the archived source.

A disposable BREAKING-image control sets mock-maker-subclass and reruns the exact failing test. It passes with Mockito 5.2.0 on the test classpath. The control covers one test. This supports a provisional behavioural assessment pending independent review.
