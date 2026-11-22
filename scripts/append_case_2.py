from pathlib import Path
import csv

BASE_DIR = Path(r"C:\Users\TASHEEN\Desktop\Research Implementation")
OUTPUT_CSV = BASE_DIR / "results" / "behavioral_classification.csv"

case_2 = {
    "case_id": "04c07b066b60a2e9d4f797b98dcd439a3a42f0b9",
    "project": "pdb",
    "dependency_group": "org.slf4j",
    "dependency_artifact": "slf4j-api",
    "old_version": "1.7.36",
    "new_version": "2.0.4",
    "bump_category": "TEST_FAILURE",

    "pre_build_status": "SUCCESS",
    "breaking_build_status": "FAILURE",
    "pre_tests": "291",
    "breaking_tests": "94",
    "breaking_failures": "0",
    "breaking_errors": "3",

    "test_effect_type": "TEST_ERROR",
    "test_effect_subtype": "RUNTIME_EXCEPTION",
    "main_exception": "java.lang.ClassCastException",

    "failure_origin": "CLIENT",
    "origin_library": "",

    "binary_linkage_incompatibility": "NO",

    "behavioral_status": "PROVISIONAL_BEHAVIORAL",
    "behavior_change_type": "OTHER_BEHAVIORAL_CHANGE",
    "behavior_description": (
        "After slf4j-api changed from 1.7.36 to 2.0.4, "
        "SLF4J ignored the old Logback 1.2.11 binding and used NOPLogger. "
        "The unchanged client test code explicitly casts the logger returned "
        "by LoggerFactory.getLogger() to ch.qos.logback.classic.Logger, "
        "causing ClassCastException."
    ),

    "pre_log": "logs/04c07b06_pre.log",
    "breaking_log": "logs/04c07b06_breaking.log",

    "review_status": "PENDING_SECOND_REVIEW",
    "reviewer_1_label": "BEHAVIORAL",
    "reviewer_2_label": "",
    "final_label": "",

    "notes": (
        "PRE passed 291 tests with 0 failures and 0 errors. "
        "BREAKING stopped after 94 tests with 3 errors. "
        "Only slf4j-api changed from 1.7.36 to 2.0.4; "
        "Logback 1.2.11 remained unchanged. "
        "Failing cast occurs directly in client test classes."
    ),
}

with OUTPUT_CSV.open("r", newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    fieldnames = reader.fieldnames
    existing_ids = {row["case_id"] for row in reader}

if case_2["case_id"] in existing_ids:
    print("Case 2 already exists. Nothing added.")
else:
    with OUTPUT_CSV.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow(case_2)

    print("Case 2 appended successfully.")