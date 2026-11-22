# Case 114 review

geostore updates H2 from 1.3.175 to 2.1.210 in src/core/persistence/pom.xml. This is the only changed archived source/POM and the only changed POM across the complete 19-POM snapshots. StoredData still declares a stored_data String column with length=10000000.

Both original images were run. PRE succeeds with 190 reported reactor tests, zero failures/errors and 36 skips. BREAKING stops in geostore-persistence after 52 tests, zero failures, 22 errors and zero skips. Maven module totals and fresh Surefire XML agree. The failing reports wrap SQLGrammarException in PersistenceException. The first meaningful schema error rejects precision 10000000 as exceeding the new limit of 1048576; subsequent Table GS_STORED_DATA not found errors cascade from the failed CREATE TABLE.

Surefire 2.4.2 runs inside Maven: its java.class.path property describes the Maven launcher, not the test dependencies. A supplementary collection reads surefire.test.class.path directly from the untouched fresh XML. The persistence test classpath changes only H2 1.3.175 to 2.1.210. These property values are archived separately; the original archive summaries are preserved.

A focused JDBC diagnostic compiles H2PrecisionProbe once to Java 11 bytecode and executes the identical class and CREATE TABLE statement in both original images with their respective resolved H2 JARs. H2 1.3.175 accepts VARCHAR(10000000) (exit 0). H2 2.1.210 reports the same precision-limit rejection (exit 1). This isolates changed SQL-input validation through stable JDBC calls, supporting PROVISIONAL_BEHAVIORAL and binary_linkage_incompatibility=NO. Commands, image IDs, driver versions, compiled-class hash and complete output are archived.

Independent human review remains pending, with reviewer/final labels blank. This case has independent evidence and a different project snapshot/version from Case 14. No repair was applied or added to verified_repairs; the existing Case 14 patch and verified repair are preserved. Explicit Maven outcomes determine original build results because the tee pipeline masks Maven failures in Docker's exit code.
