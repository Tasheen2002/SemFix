import pandas as pd
from pathlib import Path

INPUT_FILE = Path(
    r"C:\Users\TASHEEN\Desktop\Research Implementation\results\bump_metadata.csv"
)

OUTPUT_FILE = Path(
    r"C:\Users\TASHEEN\Desktop\Research Implementation\results\test_failure_candidates.csv"
)

# Read all BUMP metadata
df = pd.read_csv(INPUT_FILE)

print(f"Total BUMP cases: {len(df)}")

# Show all BUMP failure categories
print("\nFailure categories:")
print(df["failure_category"].value_counts())

# Initial semantic candidates:
# BUMP cases whose breaking state is classified as TEST_FAILURE
test_failures = df[
    df["failure_category"] == "TEST_FAILURE"
].copy()

# Save them separately
test_failures.to_csv(
    OUTPUT_FILE,
    index=False
)

print()
print("===================================")
print("TEST_FAILURE filtering completed")
print("===================================")
print(f"TEST_FAILURE candidates: {len(test_failures)}")
print(f"Saved to: {OUTPUT_FILE}")