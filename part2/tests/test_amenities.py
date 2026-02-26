"""
Tests for Amenity endpoints.
Run:  python tests/test_amenities.py
"""
from helpers import check, post, get, put, summary

print("\n--- Amenity Tests ---")

# --- valid creation ----------------------------------------------------------
status, amenity = post("/api/v1/amenities/", {"name": "WiFi"})
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
status, data = put(f"/api/v1/amenities/{AMENITY_ID}", {"name": "Fast WiFi"})
check("PUT /amenities/<id> returns 200", status == 200)
check("Name was updated", data.get("name") == "Fast WiFi")

# create a second amenity to confirm list grows
post("/api/v1/amenities/", {"name": "Pool"})
status, data = get("/api/v1/amenities/")
check("List grows after second amenity", len(data) >= 2)

# --- validation errors -------------------------------------------------------
status, _ = post("/api/v1/amenities/", {"name": ""})
check("POST with empty name returns 400", status == 400)

status, _ = post("/api/v1/amenities/", {"name": "   "})
check("POST with whitespace-only name returns 400", status == 400)

status, _ = put(f"/api/v1/amenities/{AMENITY_ID}", {"name": ""})
check("PUT with empty name returns 400", status == 400)

# --- not found ---------------------------------------------------------------
status, _ = get("/api/v1/amenities/fake-id-000")
check("GET with fake id returns 404", status == 404)

status, _ = put("/api/v1/amenities/fake-id-000", {"name": "Ghost"})
check("PUT with fake id returns 404", status == 404)

summary()
