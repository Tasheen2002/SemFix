import csv
from pathlib import Path

CSV_PATH = Path("results/behavioral_classification.csv")

CASE_ID = "12684ee6cfd293b27c08495f97900bcd849b452c"

new_row = {
    "case_id": CASE_ID,
    "project": "cucumber-reporting",
    "dependency_group": "commons-io",
    "dependency_artifact": "commons-io",
    "old_version": "2.7",
    "new_version": "2.11.0",
    "bump_category": "TEST_FAILURE",

    "pre_build_status": "SUCCESS",
    "breaking_build_status": "FAILURE",

    "pre_tests": "345",
    "breaking_tests": "345",
    "breaking_failures": "0",
    "breaking_errors": "1",

    "test_effect_type": "TEST_ERROR",
    "test_effect_subtype": "RUNTIME_EXCEPTION",
    "main_exception": "java.lang.IllegalArgumentException",

    "failure_origin": "UPDATED_LIBRARY",
    "origin_library": "commons-io:commons-io:2.11.0",

    "binary_linkage_incompatibility": "NO",

    "behavioral_status": "PROVISIONAL_BEHAVIORAL",
    "behavior_change_type": "EXCEPTION_OR_CRASH_CHANGE",

    "behavior_description": (
        "After updating Apache Commons IO from 2.7 to 2.11.0, "
        "FileUtils.copyFile() throws IllegalArgumentException "
        "when the source path refers to a directory rather than "
        "a regular file. The client method copyCustomResources() "
        "catches IOException and converts it into ValidationException, "
        "but does not catch IllegalArgumentException. As a result, "
        "the new exception escapes and causes a previously passing "
        "test to fail."
    ),

    "pre_log": "logs/batch_triage/12684ee6_pre.log",
    "breaking_log": "logs/batch_triage/12684ee6_breaking.log",

    "review_status": "PENDING_SECOND_REVIEW",
    "reviewer_1_label": "PROVISIONAL_BEHAVIORAL",
    "reviewer_2_label": "",
    "final_label": "",

    "notes": (
        "PRE: commons-io 2.7, BUILD SUCCESS, 345 tests, "
        "0 failures, 0 errors, 2 skipped. ReportBuilderTest "
        "runs 25 tests successfully. "
        "BREAKING: commons-io 2.11.0, BUILD FAILURE, "
        "345 tests, 0 failures, 1 error. "
        "The affected test is "
        "copyCustomResources_OnDirAsFile_ThrowsIOException. "
        "The test passes a directory "
        "'src/test/resources/js' to copyCustomResources() "
        "and expects ValidationException. "
        "In the breaking version, FileUtils.copyFile() throws "
        "java.lang.IllegalArgumentException: "
        "Parameter 'srcFile' is not a file. "
        "The exception originates at "
        "org.apache.commons.io.FileUtils.requireFile() "
        "and propagates through FileUtils.copyFile() to "
        "ReportBuilder.copyCustomResources(ReportBuilder.java:174). "
        "The client catches FileNotFoundException and IOException, "
        "but not IllegalArgumentException. "
        "This is evidence of an exception-behavior change, "
        "rather than binary linkage incompatibility. "
        "Reviewer 1 classification is PROVISIONAL_BEHAVIORAL. "
        "Final classification requires independent second review. "
        "A repair has not yet been implemented or verified."
    ),
}

with CSV_PATH.open(
    "r",
    encoding="utf-8-sig",
    newline=""
) as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

existing_ids = {
    row["case_id"]
    for row in rows
}

if CASE_ID in existing_ids:
    print(f"Case {CASE_ID} already exists. Nothing added.")
else:
    with CSV_PATH.open(
        "a",
        encoding="utf-8",
        newline=""
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )
        writer.writerow(new_row)

    print(f"Added Case 13: {CASE_ID}")