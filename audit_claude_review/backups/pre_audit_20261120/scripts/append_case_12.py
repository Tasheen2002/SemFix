import csv
from pathlib import Path

CSV_PATH = Path("results/behavioral_classification.csv")

CASE_ID = "1266a8c84cd04cedfa316bed94b1e9b014da872f"

new_row = {
    "case_id": CASE_ID,
    "project": "pay-adminusers",
    "dependency_group": "org.slf4j",
    "dependency_artifact": "slf4j-api",
    "old_version": "1.7.36",
    "new_version": "2.0.1",
    "bump_category": "TEST_FAILURE",

    "pre_build_status": "SUCCESS",
    "breaking_build_status": "FAILURE",

    "pre_tests": "726",
    "breaking_tests": "726",
    "breaking_failures": "0",
    "breaking_errors": "12",

    "test_effect_type": "TEST_ERROR",
    "test_effect_subtype": "RUNTIME_EXCEPTION",

    "main_exception": "java.lang.ClassCastException",

    # The immediate exception occurs in client test code
    # when it casts the logger returned by SLF4J.
    "failure_origin": "CLIENT",

    "origin_library": "",

    "binary_linkage_incompatibility": "NO",

    "behavioral_status": "PROVISIONAL_BEHAVIORAL",

    "behavior_change_type": "OTHER_BEHAVIORAL_CHANGE",

    "behavior_description": (
        "After updating slf4j-api from 1.7.36 to 2.0.1, "
        "SLF4J no longer uses the existing Logback 1.7-style binding. "
        "The old binding is ignored and SLF4J falls back to the "
        "NOP logger implementation. Client test code expects a "
        "ch.qos.logback.classic.Logger and casts the returned logger, "
        "causing java.lang.ClassCastException."
    ),

    "pre_log": "logs/batch_triage/1266a8c8_pre.log",
    "breaking_log": "logs/batch_triage/1266a8c8_breaking.log",

    "review_status": "PENDING_SECOND_REVIEW",
    "reviewer_1_label": "PROVISIONAL_BEHAVIORAL",
    "reviewer_2_label": "",
    "final_label": "",

    "notes": (
        "PRE build using slf4j-api 1.7.36 completes successfully. "
        "EventMessageHandlerTest runs 8 tests with 0 failures and "
        "0 errors. The complete PRE build runs 726 tests successfully. "
        "After updating to slf4j-api 2.0.1, SLF4J reports that no "
        "SLF4J providers were found and that the existing "
        "logback-classic 1.2.11 binding targeting SLF4J 1.7.x is "
        "ignored. SLF4J therefore defaults to the NOP logger. "
        "EventMessageHandlerTest.setUp then attempts to cast "
        "org.slf4j.helpers.NOPLogger to ch.qos.logback.classic.Logger, "
        "causing java.lang.ClassCastException. Additional Dropwizard "
        "tests fail during class initialization because the logger "
        "context cannot be acquired. The later NoClassDefFoundError "
        "'Could not initialize class' messages are secondary effects "
        "of failed class initialization and are not evidence of a "
        "missing class. BREAKING runs 726 tests with 0 failures and "
        "12 errors. No binary linkage incompatibility was identified. "
        "Reviewer 1 therefore classifies this case as "
        "PROVISIONAL_BEHAVIORAL pending independent second review."
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

    print(
        f"Case {CASE_ID} already exists. "
        "Nothing added."
    )

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

    print(
        f"Added Case 12: {CASE_ID}"
    )