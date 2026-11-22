"""Check evidence and preservation for research cases 60 through 65."""
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
BACKUP = ROOT / "results/backups/before_cases60_65"
EXPECTED = {
    60: ((32, 0, 0, 0), (18, 0, 0, 0), "NON_BEHAVIORAL"),
    61: ((32, 0, 0, 0), (18, 1, 5, 0), "NON_BEHAVIORAL"),
    62: ((95, 0, 0, 3), (89, 1, 0, 1), "NON_BEHAVIORAL"),
    63: ((3566, 0, 0, 10), (3564, 0, 0, 9), "NON_BEHAVIORAL"),
    64: ((49, 0, 0, 0), (49, 1, 0, 0), "NON_BEHAVIORAL"),
    65: ((5, 0, 0, 0), (5, 0, 2, 0), "NON_BEHAVIORAL"),
}
POM_CHANGES = {60: ["clearinghouse/pom.xml"], 61: ["core/pom.xml"], 63: []}

def read_rows(path):
    return list(csv.DictReader(io.StringIO(path.read_text(encoding="utf-8-sig"), newline="")))

def require(condition, message):
    if not condition:
        raise ValueError(message)

def main():
    csv_path = ROOT / "results/behavioral_classification.csv"
    original = csv_path.read_bytes()
    require(original.startswith((BACKUP / "behavioral_classification.csv").read_bytes()), "Original 59 records changed")
    rows = read_rows(csv_path)
    candidates = read_rows(ROOT / "results/test_failure_candidates.csv")
    triage = read_rows(ROOT / "results/batch_triage_results.csv")
    require(len(rows) >= 65, "Missing cases")
    require(len({r["case_id"] for r in rows}) == len(rows), "Duplicate IDs")
    require([r["case_id"] for r in rows[:65]] == [r["case_id"] for r in candidates[:65]], "Candidate order differs")
    require((ROOT / "results/verified_repairs.jsonl").read_bytes() == (BACKUP / "verified_repairs.jsonl").read_bytes(), "Verified repairs changed")
    require((ROOT / "repairs/case14_h2_clob.patch").read_bytes() == (BACKUP / "case14_h2_clob.patch").read_bytes(), "Case 14 patch changed")
    previous_triage = read_rows(BACKUP / "batch_triage_results.csv")
    require(all(r in triage for r in previous_triage), "Previous automated triage records changed")
    require(len(triage) == len(previous_triage) + 6, "Unexpected new triage count")
    checked = {}
    for n, expected in EXPECTED.items():
        row = rows[n-1]
        require(row["behavioral_status"] == expected[2], f"Case {n} assessment differs")
        require(row["review_status"] == "PENDING_HUMAN_REVIEW", f"Case {n} review status differs")
        require(all(row[k] == "" for k in ("reviewer_1_label", "reviewer_2_label", "final_label")), "Human labels unexpectedly filled")
        require(len([r for r in triage if r["case_id"] == row["case_id"]]) == 1, f"Case {n} missing/duplicate triage")
        base = ROOT / f"logs/case{n}_evidence"
        manifest = json.loads((base / "sha256_manifest.json").read_text())
        for name, digest in manifest.items():
            with (ROOT / name).open("rb") as stream:
                require(hashlib.file_digest(stream, "sha256").hexdigest() == digest, f"Hash differs: {name}")
        required_files = {p.relative_to(ROOT).as_posix() for p in base.rglob("*") if p.is_file() and p.name != "sha256_manifest.json"}
        required_files.update((f"scripts/append_case_{n}.py", f"results/case{n}_review.md"))
        require(required_files <= manifest.keys(), f"Case {n} manifest incomplete")
        for index, phase in enumerate(("pre", "breaking")):
            summary = json.loads((base / phase / "archive_summary.json").read_text())
            require(summary["container_state"]["Status"] == "exited", f"Case {n} container unfinished")
            require(summary["case_id"] == row["case_id"], "Archive ID differs")
            log = (ROOT / row[f"{phase}_log"]).read_text(encoding="utf-8", errors="replace")
            require("BUILD " + ("SUCCESS" if phase == "pre" else "FAILURE") in log, "Maven outcome differs")
            if n == 62:
                require(summary["report_count"] == 0, "Unexpected Surefire XML for randomized runner")
                runner = json.loads((base / phase / "randomized_summary.json").read_text())
                matches = re.findall(r"^\[INFO\] Tests summary: \d+ suites?, (\d+) tests?([^\r\n]*)", log, re.M)
                counts = [sum(int(m[0]) for m in matches)]
                for term in ("failure", "error", "ignored"):
                    counts.append(sum(int(value) for _, rest in matches for value in re.findall(r"(\d+) " + term, rest)))
                require(counts == [runner["aggregate_counts"][key] for key in ("tests", "failures", "errors", "ignored")], "Randomized summary differs from Maven")
            else:
                counts = [summary["aggregate_counts"][key] for key in ("tests", "failures", "errors", "skipped")]
                matches = re.findall(r"^(?:\[[A-Z]+\] )?Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)[ \t]*$", log, re.M)
                log_counts = tuple(map(sum, zip(*(map(int, values) for values in matches)))) if matches else (0, 0, 0, 0)
                require(log_counts == tuple(counts), "XML and Maven counts differ")
            require(tuple(counts) == expected[index], f"Case {n} {phase} counts differ: {counts}")
        before, after = [json.loads((base / phase / "archive_summary.json").read_text())["source_and_pom_sha256"] for phase in ("pre", "breaking")]
        require(before.keys() == after.keys() and [key for key in before if before[key] != after[key]] == POM_CHANGES.get(n, ["pom.xml"]), "Unexpected source/POM change")
        if n == 63:
            old_pom, new_pom = [(base / phase / "test-junit4-pom.xml").read_text() for phase in ("pre", "breaking")]
            updated_pom, count = re.subn(r"(<artifactId>surefire-junit4</artifactId>\s*<version>)3\.0\.0-M5", r"\g<1>3.0.0-M6", old_pom)
            require(count == 1 and updated_pom == new_pom, "Unexpected nested POM change")
        csv_counts = [int(row[key]) for key in ("pre_tests", "breaking_tests", "breaking_failures", "breaking_errors")]
        require(csv_counts == [expected[0][0], *expected[1][:3]], "CSV test counts differ")
        require(row["binary_linkage_incompatibility"] == ("NO" if n == 64 else "YES"), "Binary classification differs")
        result = subprocess.run([sys.executable, str(ROOT / f"scripts/append_case_{n}.py")], cwd=ROOT, capture_output=True, text=True)
        require(result.returncode == 0, result.stderr)
        require(csv_path.read_bytes() == original, f"Case {n} idempotency changed CSV")
        checked[str(n)] = {"assessment": expected[2], "pre_counts": expected[0], "breaking_counts": expected[1], "manifest_files_checked": len(manifest), "append_idempotent": True}
    output = {"passed": True, "classification_records": len(rows), "counts_through_65": dict(Counter(r["behavioral_status"] for r in rows[:65])), "previous_59_records_byte_preserved": True, "verified_repairs_and_case14_patch_preserved": True, "human_review_pending_for_new_cases": True, "cases": checked}
    (ROOT / "results/cases60_65_completion_check.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
