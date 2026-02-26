"""
Run ALL test files one by one and show a final summary.
Run from part2/:  python tests/run_all.py
"""
import subprocess
import sys
import os

TEST_FILES = [
    "tests/test_users.py",
    "tests/test_amenities.py",
    "tests/test_places.py",
    "tests/test_reviews.py",
]

# Run each file as its own process so storage is always fresh
results = {}
for test_file in TEST_FILES:
    print(f"\n{'=' * 50}")
    print(f"  Running {test_file}")
    print(f"{'=' * 50}")
    proc = subprocess.run(
        [sys.executable, test_file],
        cwd=os.path.join(os.path.dirname(__file__), ".."),
    )
    results[test_file] = proc.returncode == 0

# Final summary
print(f"\n{'=' * 50}")
print("  FINAL SUMMARY")
print(f"{'=' * 50}")
all_passed = True
for name, ok in results.items():
    status = "PASS" if ok else "FAIL"
    print(f"  {status}  {name}")
    if not ok:
        all_passed = False

print(f"{'=' * 50}\n")
sys.exit(0 if all_passed else 1)
