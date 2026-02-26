"""
Tests for User endpoints.
Run:  python tests/test_users.py
"""
from helpers import check, post, get, put, summary

print("\n--- User Tests ---")

# --- valid creation ----------------------------------------------------------
status, user = post("/api/v1/users/", {
    "first_name": "Alice",
    "last_name": "Smith",
    "email": "alice@example.com",
    "password": "secret123",
})
check("POST /users/ returns 201", status == 201)
check("Response has an id", "id" in user)
check("Password is NOT in response", "password" not in user)
check("_password is NOT in response", "_password" not in user)
check("first_name is correct", user.get("first_name") == "Alice")
check("email is correct", user.get("email") == "alice@example.com")
USER_ID = user.get("id")

# --- get one -----------------------------------------------------------------
status, data = get(f"/api/v1/users/{USER_ID}")
check("GET /users/<id> returns 200", status == 200)
check("Returned user has correct email", data.get("email") == "alice@example.com")

# --- list all ----------------------------------------------------------------
status, data = get("/api/v1/users/")
check("GET /users/ returns 200", status == 200)
check("At least one user in list", len(data) >= 1)

# --- update ------------------------------------------------------------------
status, data = put(f"/api/v1/users/{USER_ID}", {"first_name": "Alicia"})
check("PUT /users/<id> returns 200", status == 200)
check("first_name was updated", data.get("first_name") == "Alicia")
check("Password still NOT in update response", "password" not in data)

# --- validation errors -------------------------------------------------------
status, _ = post("/api/v1/users/", {
    "first_name": "Bad",
    "last_name": "User",
    "email": "not-an-email",
    "password": "123",
})
check("POST with bad email returns 400", status == 400)

status, _ = post("/api/v1/users/", {
    "first_name": "",
    "last_name": "User",
    "email": "ok@example.com",
    "password": "123",
})
check("POST with empty first_name returns 400", status == 400)

status, _ = post("/api/v1/users/", {
    "first_name": "No",
    "last_name": "Pass",
    "email": "nopass@example.com",
    "password": "",
})
check("POST with empty password returns 400", status == 400)

# --- not found ---------------------------------------------------------------
status, _ = get("/api/v1/users/fake-id-000")
check("GET with fake id returns 404", status == 404)

status, _ = put("/api/v1/users/fake-id-000", {"first_name": "Ghost"})
check("PUT with fake id returns 404", status == 404)

summary()
