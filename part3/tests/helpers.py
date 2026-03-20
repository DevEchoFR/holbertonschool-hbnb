"""
Shared test helpers used by every test file.
Import this module to get a ready-to-use Flask test client.
"""
import sys
import os

# Make sure both 'part3/' AND 'part3/tests/' are importable no matter
# which directory the user calls Python from.
_PART3 = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PART3 not in sys.path:
    sys.path.insert(0, _PART3)

from config import TestingConfig
from app import create_app, db

# One app instance shared across all test files
app = create_app(TestingConfig)
app.testing = True
client = app.test_client()

# Ensure each test process starts from a clean database.
with app.app_context():
    db.drop_all()
    db.create_all()

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


def post_auth(url, body, token):
    r = client.post(url, json=body, headers={"Authorization": f"Bearer {token}"})
    return r.status_code, json.loads(r.data)


def get(url):
    r = client.get(url)
    return r.status_code, json.loads(r.data)


def put(url, body):
    r = client.put(url, json=body)
    return r.status_code, json.loads(r.data)


def put_auth(url, body, token):
    r = client.put(url, json=body, headers={"Authorization": f"Bearer {token}"})
    return r.status_code, json.loads(r.data)


def delete(url):
    r = client.delete(url)
    return r.status_code, json.loads(r.data)


def delete_auth(url, token):
    r = client.delete(url, headers={"Authorization": f"Bearer {token}"})
    return r.status_code, json.loads(r.data)


def summary():
    """Print final results and exit with error code if any test failed."""
    import sys
    print(f"\n{'=' * 40}")
    print(f"  Results: {passed} passed, {failed} failed")
    print(f"{'=' * 40}\n")
    if failed > 0:
        sys.exit(1)
