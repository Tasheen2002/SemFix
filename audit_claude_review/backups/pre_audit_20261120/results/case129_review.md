# Case 129 review

Both original oripa images ran. PRE passed 67 tests. BREAKING reports 67 tests and 48 errors, with Maven and 31 fresh Surefire reports per phase agreeing. The archived root POM changes only Log4j Core from 2.12.1 to 2.15.0. The test classpath retains Log4j API 2.12.1.

GeometryTest records NoSuchFieldError for EMPTY_BYTE_ARRAY. Other tests report class initialization failures, and 16 report unfinished Mockito sessions. The Mockito reports were not independently isolated. A small logger startup probe using the same compiled bytecode and resolved dependency JARs succeeds in PRE and fails in BREAKING with NoSuchFieldError at ConfigurationSource initialization. Its disassembly reads org.apache.logging.log4j.util.Constants.EMPTY_BYTE_ARRAY with descriptor [B. The retained API Constants class does not declare the field.

The isolated missing field supports a NON_BEHAVIORAL binary incompatibility assessment pending independent human review. Probe results are archived separately from the original tests.
