"""Check evidence and preservation for research cases 51 through 55."""
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
BACKUP = ROOT / "results/backups/before_cases51_55_20261109_135727_558"
EXPECTED = {
    51: ((95, 0, 0, 3), (89, 1, 0, 1), "NON_BEHAVIORAL"),
    52: ((1114, 0, 0, 21), (510, 1, 0, 18), "PROVISIONAL_BEHAVIORAL"),
    53: ((177, 0, 0, 2), (177, 0, 22, 2), "PROVISIONAL_BEHAVIORAL"),
    54: ((5, 0, 0, 0), (5, 0, 2, 0), "NON_BEHAVIORAL"),
    55: ((16, 0, 0, 0), (16, 0, 10, 0), "NON_BEHAVIORAL"),
}

def read_rows(path):
    return list(csv.DictReader(io.StringIO(path.read_text(encoding="utf-8-sig"), newline="")))

def require(condition, message):
    if not condition:
        raise ValueError(message)

def main():
    csv_path = ROOT / "results/behavioral_classification.csv"
    original = csv_path.read_bytes()
    require(original.startswith((BACKUP / "behavioral_classification.csv").read_bytes()), "Original 50 records changed")
    rows = read_rows(csv_path)
    candidates = read_rows(ROOT / "results/test_failure_candidates.csv")
    triage = read_rows(ROOT / "results/batch_triage_results.csv")
    require(len(rows) >= 55, "Missing cases")
    require(len({r["case_id"] for r in rows}) == len(rows), "Duplicate IDs")
    require([r["case_id"] for r in rows[:55]] == [r["case_id"] for r in candidates[:55]], "Candidate order differs")
    require((ROOT / "results/verified_repairs.jsonl").read_bytes() == (BACKUP / "verified_repairs.jsonl").read_bytes(), "Verified repairs changed")
    require((ROOT / "repairs/case14_h2_clob.patch").read_bytes() == (BACKUP / "case14_h2_clob.patch").read_bytes(), "Case 14 patch changed")
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
            if n == 51:
                require(summary["report_count"] == 0, "Unexpected randomized XML")
                matches = re.findall(r"^\[INFO\] Tests summary: \d+ suites?, (\d+) tests?(.*)$", log, re.M)
                counts = [sum(int(m[0]) for m in matches)]
                for term in ("failure", "error", "ignored"):
                    counts.append(sum(int(v) for _, rest in matches for v in re.findall(r"(\d+) " + term, rest)))
            else:
                counts = [summary["aggregate_counts"][key] for key in ("tests", "failures", "errors", "skipped")]
            require(tuple(counts) == expected[index], f"Case {n} {phase} counts differ: {counts}")
        result = subprocess.run([sys.executable, str(ROOT / f"scripts/append_case_{n}.py")], cwd=ROOT, capture_output=True, text=True)
        require(result.returncode == 0, result.stderr)
        require(csv_path.read_bytes() == original, f"Case {n} idempotency changed CSV")
        checked[str(n)] = {"assessment": expected[2], "pre_counts": expected[0], "breaking_counts": expected[1], "manifest_files_checked": len(manifest), "append_idempotent": True}
    output = {"passed": True, "classification_records": len(rows), "counts_through_55": dict(Counter(r["behavioral_status"] for r in rows[:55])), "previous_50_records_byte_preserved": True, "verified_repairs_and_case14_patch_preserved": True, "human_review_pending_for_new_cases": True, "cases": checked}
    (ROOT / "results/cases51_55_completion_check.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
