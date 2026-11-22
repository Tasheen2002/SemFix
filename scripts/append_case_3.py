from pathlib import Path
import csv

BASE_DIR = Path(r"C:\Users\TASHEEN\Desktop\Research Implementation")
OUTPUT_CSV = BASE_DIR / "results" / "behavioral_classification.csv"

case_3 = {
    "case_id": "063cf862c045e0a9e401a539497e34ddaf8332b3",
    "project": "wsdoc",
    "dependency_group": "com.fasterxml.jackson.core",
    "dependency_artifact": "jackson-databind",
    "old_version": "2.4.2",
    "new_version": "2.9.10.8",
    "bump_category": "TEST_FAILURE",

    "pre_build_status": "SUCCESS",
    "breaking_build_status": "FAILURE",
    "pre_tests": "59",
    "breaking_tests": "59",
    "breaking_failures": "33",
    "breaking_errors": "0",

    "test_effect_type": "TEST_ERROR",
    "test_effect_subtype": "RUNTIME_EXCEPTION",
    "main_exception": "java.lang.NoClassDefFoundError",

    "failure_origin": "UPDATED_LIBRARY",
    "origin_library": "com.fasterxml.jackson.core:jackson-databind:2.9.10.8",

    "binary_linkage_incompatibility": "YES",

    "behavioral_status": "NON_BEHAVIORAL",
    "behavior_change_type": "",
    "behavior_description": (
        "After jackson-databind changed from 2.4.2 to 2.9.10.8, "
        "JacksonAnnotationIntrospector referenced "
        "com.fasterxml.jackson.annotation.JsonMerge. "
        "The project still used jackson-annotations 2.4.1, which does not "
        "contain JsonMerge.class. This caused NoClassDefFoundError and "
        "prevented ObjectMapper initialization."
    ),

    "pre_log": "logs/063cf862_pre.log",
    "breaking_log": "logs/063cf862_breaking.log",

    "review_status": "PENDING_SECOND_REVIEW",
    "reviewer_1_label": "NON_BEHAVIORAL",
    "reviewer_2_label": "",
    "final_label": "",

    "notes": (
        "PRE passed 59 tests. BREAKING reported 59 tests with 33 failures. "
        "Only jackson-databind changed from 2.4.2 to 2.9.10.8 while "
        "jackson-annotations remained 2.4.1. JsonMerge.class is absent from "
        "jackson-annotations 2.4.1, while jackson-databind 2.9.10.8 references it. "
        "Root failure occurs in JacksonAnnotationIntrospector.<clinit>. "
        "Classified as runtime binary/linkage incompatibility, not behavioral."
    ),
}

with OUTPUT_CSV.open("r", newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    fieldnames = reader.fieldnames
    existing_ids = {row["case_id"] for row in reader}

if case_3["case_id"] in existing_ids:
    print("Case 3 already exists. Nothing added.")
else:
    with OUTPUT_CSV.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow(case_3)

    print("Case 3 appended successfully.")