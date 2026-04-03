"""
Tests for Amenity endpoints.
Run:  python tests/test_amenities.py
"""
from part3.HBnB.tests.helpers import check, post, post_auth, get, put_auth, summary

print("\n--- Amenity Tests ---")

# --- setup admin auth -------------------------------------------------------
post("/api/v1/users/", {
	"first_name": "Admin",
	"last_name": "User",
	"email": "admin_amenities@example.com",
	"password": "adminpass",
	"is_admin": True,
})
_, login = post("/api/v1/auth/login", {
	"email": "admin_amenities@example.com",
	"password": "adminpass",
})
ADMIN_TOKEN = login["access_token"]

# --- valid creation ----------------------------------------------------------
status, amenity = post_auth("/api/v1/amenities/", {"name": "WiFi"}, ADMIN_TOKEN)
check("POST /amenities/ returns 201", status == 201)
check("Response has an id", "id" in amenity)
check("Name is correct", amenity.get("name") == "WiFi")
check("created_at is present", "created_at" in amenity)
AMENITY_ID = amenity.get("id")

# --- get one -----------------------------------------------------------------
status, data = get(f"/api/v1/amenities/{AMENITY_ID}")
check("GET /amenities/<id> returns 200", status == 200)
check("Amenity name matches", data.get("name") == "WiFi")

# --- list all ----------------------------------------------------------------
status, data = get("/api/v1/amenities/")
check("GET /amenities/ returns 200", status == 200)
check("At least one amenity in list", len(data) >= 1)

# --- update ------------------------------------------------------------------
status, data = put_auth(f"/api/v1/amenities/{AMENITY_ID}", {"name": "Fast WiFi"}, ADMIN_TOKEN)
check("PUT /amenities/<id> returns 200", status == 200)
check("Name was updated", data.get("name") == "Fast WiFi")

# create a second amenity to confirm list grows
post_auth("/api/v1/amenities/", {"name": "Pool"}, ADMIN_TOKEN)
status, data = get("/api/v1/amenities/")
check("List grows after second amenity", len(data) >= 2)

# --- validation errors -------------------------------------------------------
status, _ = post_auth("/api/v1/amenities/", {"name": ""}, ADMIN_TOKEN)
check("POST with empty name returns 400", status == 400)

status, _ = post_auth("/api/v1/amenities/", {"name": "   "}, ADMIN_TOKEN)
check("POST with whitespace-only name returns 400", status == 400)

status, _ = put_auth(f"/api/v1/amenities/{AMENITY_ID}", {"name": ""}, ADMIN_TOKEN)
check("PUT with empty name returns 400", status == 400)

# --- not found ---------------------------------------------------------------
status, _ = get("/api/v1/amenities/fake-id-000")
check("GET with fake id returns 404", status == 404)

status, _ = put_auth("/api/v1/amenities/fake-id-000", {"name": "Ghost"}, ADMIN_TOKEN)
check("PUT with fake id returns 404", status == 404)

summary()
