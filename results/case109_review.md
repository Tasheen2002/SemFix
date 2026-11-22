# Case 109 review

dependency-track-maven-plugin updates Guice from 5.1.0 to 7.0.0. The root POM version is the only changed archived source/POM. Fresh test classpaths change the Guice JAR and add jakarta.inject-api 2.0.1; javax.inject 1 and Sisu 0.3.5 remain present.

Both original images were run. PRE succeeds with 223 reported tests, zero failures/errors and three skips. BREAKING fails with 223 tests, zero failures, 54 errors and three skips. Maven and 42 fresh Surefire XML reports per phase agree. One primary ExceptionInInitializerError wraps IllegalArgumentException: org.eclipse.sisu.Parameters is not a binding annotation. The other 53 errors say Could not initialize class org.eclipse.sisu.wire.ParameterKeys. These are cascading initialization failures, not evidence that ParameterKeys is missing.

Actual artifact inspection confirms Sisu Parameters, javax.inject.Qualifier and Guice Key exist in both environments. Guice's internal binding-annotation checker recognizes javax.inject.Qualifier in 5.1.0 and jakarta.inject.Qualifier in 7.0.0. Both versions expose the same public Key.get(Class, Class<? extends Annotation>) signature. The Sisu annotation remains meta-annotated with javax.inject.Qualifier.

A focused diagnostic compiles AnnotationCompatibilityProbe once to Java 11 bytecode, then runs that identical class file against each original image's dependency classpath. Key.get(String.class, Parameters.class) returns a Key under Guice 5.1.0 (exit 0), but throws the same IllegalArgumentException under Guice 7.0.0 (exit 1). Both runs print the existing javax qualifier metadata and Java 11.0.19. The probe's source, compiled class hash, commands, image IDs and complete output are archived. No client source or dependency was substituted. This isolates changed acceptance/validation behavior through a compatible API call, supporting a PROVISIONAL_BEHAVIORAL assessment with binary_linkage_incompatibility=NO.

Automated triage records AUTO_RUNTIME_REVIEW_REQUIRED; it is not the basis of the semantic verdict. This is an evidence-backed agent assessment, not independent human confirmation. Reviewer/final labels remain blank. No repair was attempted or added to verified_repairs. Explicit Maven outcomes establish original build results because the image pipes Maven through tee.

## Label correction (2026-11-20)

This addendum was added after the AI second review and the researcher's rule decisions. The assessment above is Codex's original text and is unchanged.

- Previous label: PROVISIONAL_BEHAVIORAL (OTHER_BEHAVIORAL_CHANGE)
- Corrected label: **NON_BEHAVIORAL**
- Reason: Rule R3 (approved 2026-11-20): javax->jakarta namespace migration, labelled NON_BEHAVIORAL consistently with cases 83, 93, 164 and 180. Mechanism unchanged: Guice 7 no longer recognises @javax.inject.Qualifier on Sisu @Parameters (AnnotationCompatibilityProbe).
- Records: `results/behavioral_classification.csv` (notes), `audit_claude_review/CHANGELOG.md`, `results/final_classification_rule_based.csv`.
