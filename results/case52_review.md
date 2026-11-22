# Case 52 review

The junit-quickcheck Mockito upgrade from 4.11.0 to 5.4.0 is provisionally **behavioural**, pending human review.

PRE passed the full reactor with 1,114 reported tests, including 21 skips. BREAKING stopped in core after 510 reported tests, including 18 skips and one assertion failure. CompositeGeneratorTest.shrinkingChoosesAComponentCapableOfShrinkingTheValue expects [3, 6] but receives an empty list. Maven and fresh Surefire reports agree on these totals.

Generator.shrink is final and delegates to doShrink. The test mocks component generators and stubs doShrink. Mockito 4.11.0 defaults to ByteBuddyMockMaker, which allows the real final shrink method to reach the stub. Mockito 5.4.0 defaults to InlineByteBuddyMockMaker, which intercepts the final shrink method and returns its unstubbed empty-list default. Disassembly of the actual Mockito JARs confirms the default plugin change. The archived project contains no mock-maker override.

A disposable BREAKING-image control adds `mock-maker-subclass` at `core/src/test/resources/mockito-extensions/org.mockito.plugins.MockMaker` and runs `mvn -B -pl core -am -Dtest=CompositeGeneratorTest#shrinkingChoosesAComponentCapableOfShrinkingTheValue -Dsurefire.failIfNoSpecifiedTests=false test`. The exact failing test then passes with one test, zero failures/errors/skips and BUILD SUCCESS. The control retains Mockito 5.4.0, confirmed by its Surefire classpath. This is a focused causal experiment; the full upgraded suite was only run under the original default configuration.

Only the Mockito version changes in the project POM. Byte Buddy dependencies also change transitively. The original image command pipes Maven through tee, masking its failing exit code. Logs have prefix `4631885d` under `logs/batch_triage/`. Source archives, reports, Mockito JARs, disassembly and the separate control log/XML/state are under `logs/case52_evidence/`.
