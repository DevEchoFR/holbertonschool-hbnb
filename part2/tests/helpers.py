"""
Shared test helpers used by every test file.
Import this module to get a ready-to-use Flask test client.
"""
import sys
import os

# Make sure both 'part2/' AND 'part2/tests/' are importable no matter
# which directory the user calls Python from.
_PART2 = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PART2 not in sys.path:
    sys.path.insert(0, _PART2)

from run import create_app

# One app instance shared across all test files
app = create_app()
app.testing = True
client = app.test_client()

# ---- counters ---------------------------------------------------------------
passed = 0
failed = 0


def check(description, condition):
    """Print PASS or FAIL and update counters."""
    global passed, failed
    if condition:
        print(f"  PASS  {description}")
        passed += 1
    else:
        print(f"  FAIL  {description}")
        failed += 1


# ---- HTTP helpers -----------------------------------------------------------
import json


def post(url, body):
    r = client.post(url, json=body)
    return r.status_code, json.loads(r.data)


def get(url):
    r = client.get(url)
    return r.status_code, json.loads(r.data)


def put(url, body):
    r = client.put(url, json=body)
    return r.status_code, json.loads(r.data)


def delete(url):
    r = client.delete(url)
    return r.status_code, json.loads(r.data)


def summary():
    """Print final results and exit with error code if any test failed."""
    import sys
    print(f"\n{'=' * 40}")
    print(f"  Results: {passed} passed, {failed} failed")
    print(f"{'=' * 40}\n")
    if failed > 0:
        sys.exit(1)
