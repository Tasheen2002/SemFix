# Case 132 review

Both original pdb images ran. PRE reported 291 tests with 13 skips and no failures or errors. BREAKING reported 94 tests with ten skips and three errors. Maven and 25 fresh Surefire reports per phase agree. BatchUpdateTest, EngineCloseTest and EngineGeneralTest fail during class setup, reducing the number of reported tests.

Only the SLF4J API version changes in the archived root POM and on the affected test classpath. Both images retain Logback Classic 1.2.11 and its StaticLoggerBinder. The updated API reports ignoring the legacy binder and returns a no-operation logger. The same compiled probe returns Logback Logger under 1.7.36 and NOPLogger under 2.0.5. The unchanged test setup casts to the former and throws ClassCastException with the latter.

The logger selection change through a compatible call supports PROVISIONAL_BEHAVIORAL pending independent review. Diagnostic results are recorded separately from the original counts.
