# Case 86 review

java-datastore updates surefire-junit47 3.0.0-M5 to 3.0.0-M6 in datastore-v1-proto-client/pom.xml. This is the sole archived source or POM change. The Maven Surefire plugin remains at 3.0.0-M5.

PRE passes 237 tests across the reactor. BREAKING reports no executed tests. The provider fails before running datastore-v1-proto-client tests, and Maven skips the remaining modules. No fresh XML reports are produced in BREAKING.

Maven reports NoSuchMethodError for the DirectoryScannerParameters constructor with a boolean argument. The resolved M5 caller bytecode invokes that signature, while the M6 Surefire API supplied by the updated provider lacks it. The resolved JARs and disassembly corroborate the binary incompatibility. The non-behavioural assessment is pending independent human review.

Maven's explicit build outcome establishes failure because the command pipes Maven through tee.
