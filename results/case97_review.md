# Case 97 review

recheck.cli updates Logback Classic 1.2.11 to 1.4.1. The root POM version is the sole archived source/POM change. The affected classpath retains SLF4J 1.7.36.

PRE passes all 12 tests. BREAKING reports two failed assertions about absent warning text. The retained SLF4J LoggerFactory calls StaticLoggerBinder.getSingleton directly and handles NoClassDefFoundError. The PRE Classic JAR contains that binder, while 1.4.1 supplies a service-provider descriptor and omits the binder. The log records failure to load the class and selection of a no-operation logger.

The assertions follow the missing binary binding, supporting a non-behavioural assessment pending independent review. Both original runs, fresh Surefire XML and JAR inspection are archived. The explicit Maven outcome establishes failure because the image pipes Maven through tee.
