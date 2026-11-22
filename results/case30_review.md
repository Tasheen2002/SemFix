# Case 30 review

The `recheck` upgrade of EclipseLink MOXy from 3.0.2 to 4.0.1 is provisionally **non-behavioural**, pending human review. The resolved runtime loses the ASM implementation needed to initialize EclipseLink's bytecode generation.

PRE reported 737 tests, including four skips, with zero failures or errors. BREAKING reported 737 tests, including four skips and 15 errors, with zero assertion failures. The first reported initialization error wraps EclipseLink validation error 7359, `No any ASM service available`. The other 14 errors report that `ASMFactory` could not initialize.

The PRE test classpath contains EclipseLink ASM 9.1.0. The BREAKING classpath lacks that artifact. The resolved MOXy 3.0.2 POM declares ASM at default compile scope, while the resolved MOXy 4.0.1 POM declares it at test scope. The Core 4.0.1 POM declares it as optional and provided. Disassembly shows that `ASMFactory` probes for the EclipseLink or OW2 ASM `ClassVisitor`. The PRE ASM JAR contains the EclipseLink class. The causal evidence supports a missing runtime implementation reported by a validation check, so the binary linkage flag is recorded as `NO`. The automated linkage cue `ClassNotFoundException: not existent` occurs in both PRE and BREAKING and is unrelated to the 15 errors.

The archived sources match and only the MOXy version changes in the project POM. Maven summaries match the fresh reports. The image command pipes Maven through `tee`, masking its failing exit code. The logs have prefix `25926ea2` under `logs/batch_triage/`. The archives, resolved POMs, JARs and disassembly are under `logs/case30_evidence/`.
