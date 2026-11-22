from pathlib import Path
import csv

BASE_DIR = Path(r"C:\Users\TASHEEN\Desktop\Research Implementation")
OUTPUT_CSV = BASE_DIR / "results" / "behavioral_classification.csv"

case_5 = {
    "case_id": "072528ee5e678feabeaa1e2962725134564bdd3c",
    "project": "sign-maven-plugin",
    "dependency_group": "org.slf4j",
    "dependency_artifact": "slf4j-api",
    "old_version": "1.7.36",
    "new_version": "2.0.2",
    "bump_category": "TEST_FAILURE",
    "pre_build_status": "SUCCESS",
    "breaking_build_status": "FAILURE",
    "pre_tests": "38",
    "breaking_tests": "38",
    "breaking_failures": "0",
    "breaking_errors": "12",
    "test_effect_type": "TEST_ERROR",
    "test_effect_subtype": "RUNTIME_EXCEPTION",
    "main_exception": "java.lang.ClassCastException",
    "failure_origin": "LIBRARY_USED_FOR_TESTING",
    "origin_library": "org.simplify4u:slf4j-mock:2.2.0",
    "binary_linkage_incompatibility": "NO",
    "behavioral_status": "PROVISIONAL_BEHAVIORAL",
    "behavior_change_type": "OTHER_BEHAVIORAL_CHANGE",
    "behavior_description": (
        "After slf4j-api changed from 1.7.36 to 2.0.2, SLF4J ignored the "
        "old 1.7-style StaticLoggerBinder provided by slf4j-mock 2.2.0 and "
        "returned org.slf4j.helpers.NOPLogger. The unchanged slf4j-mock "
        "2.2.0 testing library expected a ProxyMock logger and explicitly "
        "cast the logger instance to org.simplify4u.slf4jmock.ProxyMock. "
        "The cast therefore failed with java.lang.ClassCastException. "
        "The project compiled successfully, but 12 tests ended with runtime "
        "errors because of the changed runtime logging behavior."
    ),
    "pre_log": "logs/072528ee_pre.log",
    "breaking_log": "logs/072528ee_breaking.log",
    "review_status": "PENDING_SECOND_REVIEW",
    "reviewer_1_label": "PROVISIONAL_BEHAVIORAL",
    "reviewer_2_label": "",
    "final_label": "",
    "notes": (
        "PRE used slf4j-api 1.7.36 and slf4j-mock 2.2.0 and completed "
        "38 tests with 0 failures and 0 errors, BUILD SUCCESS. "
        "BREAKING changed only slf4j-api to 2.0.2 while slf4j-mock "
        "remained 2.2.0. BREAKING completed 38 tests with 0 failures "
        "and 12 errors, BUILD FAILURE. SLF4J reported that the "
        "StaticLoggerBinder from slf4j-mock targets SLF4J 1.7.x and was "
        "ignored. slf4j-mock LoggerAnnotationEngine.findLoggersMocks "
        "reads the logger field and performs a cast to ProxyMock. "
        "With SLF4J 2.0.2 the runtime logger was NOPLogger, causing "
        "ClassCastException. No binary linkage error such as "
        "NoSuchMethodError or NoClassDefFoundError was observed. "
        "Classified provisionally as behavioral pending independent "
        "second review."
    ),
}

with OUTPUT_CSV.open("r", newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    fieldnames = reader.fieldnames
    existing_ids = {row["case_id"] for row in reader}

if case_5["case_id"] in existing_ids:
    print("Case 5 already exists. Nothing added.")
else:
    with OUTPUT_CSV.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow(case_5)

    print("Case 5 appended successfully.")