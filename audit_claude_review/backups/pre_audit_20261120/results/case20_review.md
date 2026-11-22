# Case 20 review

The `logging-chainsaw` upgrade from XStream 1.4.17 to 1.4.19 is provisionally **behavioural**, pending human review.

PRE passed all five tests. BREAKING reported five tests and one error. The unchanged `LogPanelPreferenceModelTest.testLogPanelPreferenceModelSerialization` creates an XStream instance with a `DomDriver`, serializes a preference model, and reads it back with `fromXML`. The upgraded version rejects the model class with `ForbiddenClassException` in `SecurityMapper.realClass`. This changes which types the same deserialization call accepts under the test's default configuration.

The archived sources match and the only POM change is the XStream version. The Maven logs and fresh Surefire reports agree. The logs have prefix `19e20b0d` under `logs/batch_triage/`, and the archives are under `logs/case20_evidence/`.
