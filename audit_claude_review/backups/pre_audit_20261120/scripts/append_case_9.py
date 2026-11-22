import csv
from pathlib import Path

CSV_PATH = Path("results/behavioral_classification.csv")

CASE_ID = "0ee8b9376b967938e8efd89a0959214a30d1b3fb"

new_row = {
    "case_id": CASE_ID,
    "project": "junit-quickcheck",
    "dependency_group": "org.mockito",
    "dependency_artifact": "mockito-core",
    "old_version": "4.11.0",
    "new_version": "5.1.1",
    "bump_category": "TEST_FAILURE",
    "pre_build_status": "SUCCESS",
    "breaking_build_status": "FAILURE",
    "pre_tests": "510",
    "breaking_tests": "510",
    "breaking_failures": "1",
    "breaking_errors": "0",
    "test_effect_type": "TEST_FAILURE",
    "test_effect_subtype": "TEST_ASSERTION",
    "main_exception": "java.lang.AssertionError",
    "failure_origin": "UPDATED_LIBRARY",
    "origin_library": "org.mockito:mockito-core:5.1.1",
    "binary_linkage_incompatibility": "NO",
    "behavioral_status": "PROVISIONAL_BEHAVIORAL",
    "behavior_change_type": "OTHER_BEHAVIORAL_CHANGE",
    "behavior_description": (
        "Updating Mockito from 4.11.0 to 5.1.1 changes the default MockMaker "
        "from the subclass-based ByteBuddyMockMaker to InlineByteBuddyMockMaker. "
        "The affected test uses mocked Generator instances where Generator.shrink "
        "is a final method. Under Mockito 4.11.0, the final shrink method is not "
        "intercepted by the default subclass mock maker, so the real shrink method "
        "executes and reaches the stubbed doShrink method, returning [3, 6]. "
        "Under Mockito 5.1.1, the default inline mock maker intercepts the final "
        "shrink method. Because shrink itself is not stubbed, the mock returns an "
        "empty list, changing the observed test result from [3, 6] to []."
    ),
    "pre_log": "logs/0ee8b937_pre.log",
    "breaking_log": "logs/0ee8b937_breaking.log",
    "review_status": "PENDING_SECOND_REVIEW",
    "reviewer_1_label": "PROVISIONAL_BEHAVIORAL",
    "reviewer_2_label": "",
    "final_label": "",
    "notes": (
        "PRE with mockito-core 4.11.0: 510 tests, 0 failures, 0 errors, "
        "18 skipped, BUILD SUCCESS. BREAKING with mockito-core 5.1.1: "
        "510 tests, 1 failure, 0 errors, 18 skipped, BUILD FAILURE. "
        "Failing test: CompositeGeneratorTest."
        "shrinkingChoosesAComponentCapableOfShrinkingTheValue. "
        "Assertion expected [3, 6] but actual result was []. "
        "Generator.shrink(SourceOfRandomness,Object) is final and calls doShrink. "
        "Mockito 4.11.0 DefaultMockitoPlugins maps MockMaker to "
        "org.mockito.internal.creation.bytebuddy.ByteBuddyMockMaker, while "
        "Mockito 5.1.1 maps MockMaker to "
        "org.mockito.internal.creation.bytebuddy.InlineByteBuddyMockMaker. "
        "No project-specific mockito-extensions override exists. "
        "Causal validation: using Mockito 5.1.1 but forcing mock-maker-subclass "
        "makes the exact failing test pass with 1 test, 0 failures, 0 errors, "
        "BUILD SUCCESS. Classified as PROVISIONAL_BEHAVIORAL pending independent review."
    ),
}

with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

if CASE_ID in {row["case_id"] for row in rows}:
    print(f"Case {CASE_ID} already exists. Nothing added.")
else:
    with CSV_PATH.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(new_row)

    print(f"Added Case 9: {CASE_ID}")