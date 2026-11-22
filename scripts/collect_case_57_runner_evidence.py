"""Collect fresh randomized-runner counts and retained events for Case 57.

Run after both original image containers stop. Existing output is never overwritten.
"""
import csv
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    with (ROOT / "results/test_failure_candidates.csv").open(encoding="utf-8-sig", newline="") as stream:
        candidate = list(csv.DictReader(stream))[56]
    case_id = candidate["case_id"]
    for phase in ("pre", "breaking"):
        base = ROOT / "logs/case57_evidence" / phase
        archive = json.loads((base / "archive_summary.json").read_text())
        container = "bump-" + case_id + "-" + phase
        info = json.loads(subprocess.check_output(["docker", "inspect", container], text=True))[0]
        if info["State"]["Status"] != "exited":
            raise ValueError("Container is not stopped")
        log = (ROOT / f"logs/batch_triage/{case_id[:8]}_{phase}.log").read_text(encoding="utf-8", errors="replace")
        rows = []
        for match in re.finditer(r"^\[INFO\] Tests summary: (\d+) suites?, (\d+) tests?([^\r\n]*)", log, re.M):
            counts = {"suites": int(match[1]), "tests": int(match[2])}
            for term in ("failure", "error", "ignored"):
                values = re.findall(r"(\d+) " + term, match[3])
                counts[term + ("s" if term != "ignored" else "")] = sum(map(int, values))
            rows.append({"line": log[:match.start()].count("\n") + 1, "summary": match[0], "counts": counts})
        if not rows:
            raise ValueError("No randomized module summaries found")
        totals = {key: sum(r["counts"][key] for r in rows) for key in ("suites", "tests", "failures", "errors", "ignored")}
        events = []
        process = subprocess.Popen(["docker", "cp", container + ":" + archive["working_directory"] + "/.", "-"], stdout=subprocess.PIPE)
        try:
            with tarfile.open(fileobj=process.stdout, mode="r|") as stream:
                for member in stream:
                    name = PurePosixPath(member.name)
                    if not member.isfile() or name.is_absolute() or ".." in name.parts:
                        continue
                    parts = name.parts
                    if "target" not in parts or not re.fullmatch(r"junit4-[\w.-]+\.(events|suites)", name.name):
                        continue
                    module = "/".join(parts[:parts.index("target")]) or "."
                    if module not in archive["cleaned_modules"]:
                        continue
                    destination = base / "runner-events" / Path(*parts)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    with destination.open("xb") as output:
                        output.write(stream.extractfile(member).read())
                    events.append(name.as_posix())
            if process.wait() != 0:
                raise RuntimeError("Docker evidence stream failed")
        finally:
            process.stdout.close()
            if process.poll() is None:
                process.kill()
                process.wait()
        result = {"case_id": case_id, "phase": phase, "count_source": "Original Maven randomized-runner module summaries", "module_summaries": rows, "aggregate_counts": totals, "retained_runner_files": events, "limitation": "Successful randomized-runner event files may be deleted by the runner; no Surefire XML exists."}
        with (base / "randomized_summary.json").open("x", encoding="utf-8") as output:
            json.dump(result, output, indent=2)
        print(phase, totals, "retained runner files:", len(events))

if __name__ == "__main__":
    main()
