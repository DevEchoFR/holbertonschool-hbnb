"""
Tests for User endpoints.
Run:  python tests/test_users.py
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tests.helpers import check, post, post_auth, get, put, put_auth, delete_auth, summary, create_admin_user

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

# Log in as alice to get a token for authenticated requests
status, login_data = post("/api/v1/auth/login", {
    "email": "alice@example.com",
    "password": "secret123",
})
check("Login returns 200", status == 200)
ALICE_TOKEN = login_data.get("access_token", "")

# --- get one -----------------------------------------------------------------
status, data = get(f"/api/v1/users/{USER_ID}")
check("GET /users/<id> returns 200", status == 200)
check("Returned user has correct email", data.get("email") == "alice@example.com")

# --- list all ----------------------------------------------------------------
status, data = get("/api/v1/users/")
check("GET /users/ returns 200", status == 200)
check("At least one user in list", len(data) >= 1)

# --- update ------------------------------------------------------------------
status, data = put_auth(f"/api/v1/users/{USER_ID}", {"first_name": "Alicia"}, ALICE_TOKEN)
check("PUT /users/<id> returns 200", status == 200)
check("first_name was updated", data.get("first_name") == "Alicia")
check("Password still NOT in update response", "password" not in data)

# --- unauthorized update (no token) ------------------------------------------
status, _ = put(f"/api/v1/users/{USER_ID}", {"first_name": "Hacker"})
check("PUT without token returns 401", status == 401)

# --- admin token for remaining auth checks -----------------------------------
create_admin_user("Admin", "Users", "admin_users@example.com", "adminpass")
_, admin_login = post("/api/v1/auth/login", {
    "email": "admin_users@example.com",
    "password": "adminpass",
})
ADMIN_TOKEN = admin_login.get("access_token", "")

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

status, _ = put_auth("/api/v1/users/fake-id-000", {"first_name": "Ghost"}, ADMIN_TOKEN)
check("PUT with fake id returns 404 (admin)", status == 404)

# non-admin trying to update another user gets 403
status, _ = put_auth("/api/v1/users/fake-id-000", {"first_name": "Ghost"}, ALICE_TOKEN)
check("PUT on another user's id returns 403 for non-admin", status == 403)

# --- admin edit user via /admin/users/<id> ------------------------------------
status, data = put_auth(f"/api/v1/admin/users/{USER_ID}", {"first_name": "AliceEdited"}, ADMIN_TOKEN)
check("Admin PUT /admin/users/<id> returns 200", status == 200)
check("first_name was updated by admin", data.get("first_name") == "AliceEdited")

status, _ = put_auth("/api/v1/admin/users/fake-id-000", {"first_name": "Ghost"}, ADMIN_TOKEN)
check("Admin PUT with fake id returns 404", status == 404)

# non-admin cannot use admin edit endpoint
status, _ = put_auth(f"/api/v1/admin/users/{USER_ID}", {"first_name": "Hacker"}, ALICE_TOKEN)
check("Non-admin PUT /admin/users/<id> returns 403", status == 403)

# --- delete user (admin only) -------------------------------------------------
# create a throwaway user to delete
_, del_user = post("/api/v1/users/", {
    "first_name": "Del",
    "last_name": "Me",
    "email": "delme@example.com",
    "password": "pass",
})
DEL_USER_ID = del_user["id"]

# non-admin cannot delete
_, del_login = post("/api/v1/auth/login", {"email": "alice@example.com", "password": "secret123"})
# alice's token may have changed (first_name edit), re-login
_, alice_relogin = post("/api/v1/auth/login", {"email": "alice@example.com", "password": "secret123"})
ALICE_TOKEN2 = alice_relogin.get("access_token", ALICE_TOKEN)

status, _ = delete_auth(f"/api/v1/admin/users/{DEL_USER_ID}", ALICE_TOKEN2)
check("DELETE /admin/users/<id> by non-admin returns 403", status == 403)

# admin can delete
status, _ = delete_auth(f"/api/v1/admin/users/{DEL_USER_ID}", ADMIN_TOKEN)
check("DELETE /admin/users/<id> by admin returns 200", status == 200)

# already deleted → 404
status, _ = delete_auth(f"/api/v1/admin/users/{DEL_USER_ID}", ADMIN_TOKEN)
check("DELETE already-deleted user returns 404", status == 404)

# fake id → 404
status, _ = delete_auth("/api/v1/admin/users/fake-id-000", ADMIN_TOKEN)
check("DELETE /admin/users/ with fake id returns 404", status == 404)

# admin cannot delete themselves
_, admin_login2 = post("/api/v1/auth/login", {
    "email": "admin_users@example.com",
    "password": "adminpass",
})
ADMIN_TOKEN2 = admin_login2.get("access_token", ADMIN_TOKEN)
# find admin's own ID via user list
_, all_users = get("/api/v1/users/")
admin_self = next((u for u in all_users if u.get("email") == "admin_users@example.com"), None)
if admin_self:
    status, _ = delete_auth(f"/api/v1/admin/users/{admin_self['id']}", ADMIN_TOKEN2)
    check("Admin DELETE self returns 400", status == 400)

summary()
