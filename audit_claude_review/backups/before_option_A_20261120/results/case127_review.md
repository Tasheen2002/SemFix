# Case 127 review

Both original Refactoring-Bot images ran. PRE passed all 62 tests. BREAKING reported 62 tests with one error in GrammarServiceTest.testCheckComment. Maven and fresh Surefire XML agree. The archived client sources match and the root POM changes only the ANTLR runtime version. The affected classpath replaces 4.7.2 with 4.11.1.

The generated lexer identifies ANTLR 4.7.1 as its generator. Its static initialization calls ATNDeserializer.deserialize(char[]). Disassembly confirms the method exists in both runtime JARs. The same generated lexer and probe bytecode initialized successfully with 4.7.2. With 4.11.1, the same method resolved and rejected the serialized grammar data with 'version 3 (expected 4)'. The resulting UnsupportedOperationException and InvalidClassException are wrapped by ExceptionInInitializerError.

The change in accepted input supports PROVISIONAL_BEHAVIORAL with no binary linkage failure. The generated-data compatibility boundary remains pending independent human review. The probe runs are archived separately from the original test counts.
