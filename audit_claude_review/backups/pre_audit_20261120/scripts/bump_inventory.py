import csv
import json
from pathlib import Path


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BUMP_BENCHMARK_DIR = Path(
    r"C:\Users\TASHEEN\Desktop\Research Implementation\bump\data\benchmark"
)

OUTPUT_FILE = Path(
    r"C:\Users\TASHEEN\Desktop\Research Implementation\results\bump_metadata.csv"
)

if not BUMP_BENCHMARK_DIR.exists():
    raise FileNotFoundError(
        f"BUMP benchmark directory not found: {BUMP_BENCHMARK_DIR}"
    )


# ---------------------------------------------------------
# Read all BUMP JSON files
# ---------------------------------------------------------

rows = []

json_files = sorted(BUMP_BENCHMARK_DIR.glob("*.json"))

print(f"Found {len(json_files)} BUMP case files.")


for json_file in json_files:

    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        dependency = data.get("updatedDependency", {})

        row = {
            "case_id": data.get("breakingCommit", ""),
            "project": data.get("project", ""),
            "organisation": data.get("projectOrganisation", ""),

            "dependency_group": dependency.get(
                "dependencyGroupID", ""
            ),

            "dependency_artifact": dependency.get(
                "dependencyArtifactID", ""
            ),

            "previous_version": dependency.get(
                "previousVersion", ""
            ),

            "new_version": dependency.get(
                "newVersion", ""
            ),

            "dependency_scope": dependency.get(
                "dependencyScope", ""
            ),

            "version_update_type": dependency.get(
                "versionUpdateType", ""
            ),

            "java_version": data.get(
                "javaVersionUsedForReproduction", ""
            ),

            "failure_category": data.get(
                "failureCategory", ""
            ),

            "pre_command": data.get(
                "preCommitReproductionCommand", ""
            ),

            "breaking_command": data.get(
                "breakingUpdateReproductionCommand", ""
            ),

            "pull_request_url": data.get(
                "url", ""
            ),
        }

        rows.append(row)

    except Exception as e:
        print(
            f"ERROR reading {json_file.name}: {e}"
        )


# ---------------------------------------------------------
# Write CSV
# ---------------------------------------------------------

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)


fieldnames = [
    "case_id",
    "project",
    "organisation",
    "dependency_group",
    "dependency_artifact",
    "previous_version",
    "new_version",
    "dependency_scope",
    "version_update_type",
    "java_version",
    "failure_category",
    "pre_command",
    "breaking_command",
    "pull_request_url",
]


with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as csv_file:

    writer = csv.DictWriter(
        csv_file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(rows)


print()
print("===================================")
print("BUMP inventory completed")
print("===================================")
print(f"Cases processed : {len(rows)}")
print(f"CSV saved to    : {OUTPUT_FILE}")