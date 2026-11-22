import csv
from pathlib import Path

CSV_PATH = Path("results/behavioral_classification.csv")

CASE_ID = "097d93fbb2f9998ef1390ad10f92d1b70fda8b90"

new_row = {
    "case_id": CASE_ID,
    "project": "fscrawler",
    "dependency_group": "org.apache.poi",
    "dependency_artifact": "poi-ooxml",
    "old_version": "4.1.2",
    "new_version": "5.1.0",
    "bump_category": "TEST_FAILURE",
    "pre_build_status": "SUCCESS",
    "breaking_build_status": "FAILURE",
    "pre_tests": "95",
    "breaking_tests": "89",
    "breaking_failures": "2",
    "breaking_errors": "0",
    "test_effect_type": "TEST_FAILURE",
    "test_effect_subtype": "TEST_ASSERTION",
    "main_exception": "",
    "failure_origin": "UPDATED_LIBRARY",
    "origin_library": "org.apache.poi:poi-ooxml:5.1.0",
    "binary_linkage_incompatibility": "YES",
    "behavioral_status": "NON_BEHAVIORAL",
    "behavior_change_type": "",
    "behavior_description": (
        "After poi-ooxml changed from 4.1.2 to 5.1.0, the project still kept "
        "org.apache.poi:poi and poi-scratchpad at 4.1.2. The new poi-ooxml 5.1.0 "
        "expects POI 5.1.0-compatible runtime types. In the breaking runtime, "
        "POIXMLTextExtractor from poi-ooxml 5.1.0 is an interface extending "
        "POITextExtractor, while POITextExtractor from poi 4.1.2 is an abstract class. "
        "This class/interface mismatch causes document extraction to fail at runtime. "
        "The affected tests then receive null extracted text and fail assertions. "
        "This is a binary/runtime dependency incompatibility rather than a semantic "
        "behavioral change in the client program."
    ),
    "pre_log": "logs/097d93fb_pre.log",
    "breaking_log": "logs/097d93fb_breaking.log",
    "review_status": "PENDING_SECOND_REVIEW",
    "reviewer_1_label": "NON_BEHAVIORAL",
    "reviewer_2_label": "",
    "final_label": "",
    "notes": (
        "PRE uses poi 4.1.2, poi-scratchpad 4.1.2, and poi-ooxml 4.1.2 and ends in "
        "BUILD SUCCESS. BREAKING changes only poi-ooxml to 5.1.0 while poi and "
        "poi-scratchpad remain 4.1.2. The breaking log shows "
        "'POIXMLTextExtractor can not implement POITextExtractor, because it is not "
        "an interface' and also a ClassNotFoundException for "
        "org.apache.poi.poifs.crypt.agile.AgileEncryptionInfoBuilder. "
        "javap confirmed POITextExtractor in poi 4.1.2 is an abstract class, while "
        "POIXMLTextExtractor in poi-ooxml 5.1.0 is an interface extending it. "
        "The poi-ooxml 5.1.0 POM explicitly depends on poi 5.1.0. "
        "Classified as NON_BEHAVIORAL binary/runtime linkage incompatibility."
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

    print(f"Added Case 6: {CASE_ID}")