"""
Tests for Place endpoints.
Run:  python tests/test_places.py

Places need an existing User and Amenity, so we create them first.
"""
from helpers import check, post, get, put, summary

print("\n--- Place Tests ---")

# --- setup: create a user and an amenity we can reference -------------------
_, owner = post("/api/v1/users/", {
    "first_name": "Bob",
    "last_name": "Brown",
    "email": "bob@example.com",
    "password": "pass",
})
OWNER_ID = owner["id"]

_, amenity = post("/api/v1/amenities/", {"name": "Pool"})
AMENITY_ID = amenity["id"]

# --- valid creation ----------------------------------------------------------
status, place = post("/api/v1/places/", {
    "title": "Nice Flat",
    "description": "A cozy place in the city center.",
    "price": 99.0,
    "latitude": 48.85,
    "longitude": 2.35,
    "owner_id": OWNER_ID,
    "amenity_ids": [AMENITY_ID],
})
check("POST /places/ returns 201", status == 201)
check("Response has an id", "id" in place)
check("Title is correct", place.get("title") == "Nice Flat")
check("Extended 'owner' field included", isinstance(place.get("owner"), dict))
check("Owner has first_name", place["owner"].get("first_name") == "Bob")
check("Extended 'amenities' list included", isinstance(place.get("amenities"), list))
check("Amenity name is embedded", place["amenities"][0].get("name") == "Pool")
check("'reviews' list included (empty for now)", place.get("reviews") == [])
PLACE_ID = place["id"]

# --- get one -----------------------------------------------------------------
status, data = get(f"/api/v1/places/{PLACE_ID}")
check("GET /places/<id> returns 200", status == 200)
check("GET returns extended owner info", isinstance(data.get("owner"), dict))
check("GET returns amenities list", len(data.get("amenities", [])) == 1)

# --- list all ----------------------------------------------------------------
status, data = get("/api/v1/places/")
check("GET /places/ returns 200", status == 200)
check("At least one place in list", len(data) >= 1)
check("List items include owner info", isinstance(data[0].get("owner"), dict))

# --- update ------------------------------------------------------------------
status, data = put(f"/api/v1/places/{PLACE_ID}", {
    "title": "Great Flat",
    "price": 120.0,
})
check("PUT /places/<id> returns 200", status == 200)
check("Title was updated", data.get("title") == "Great Flat")
check("Price was updated", data.get("price") == 120.0)

# --- validation errors -------------------------------------------------------
status, _ = post("/api/v1/places/", {
    "title": "Cheap",
    "description": "",
    "price": -5.0,
    "latitude": 10.0,
    "longitude": 10.0,
    "owner_id": OWNER_ID,
})
check("POST with negative price returns 400", status == 400)

status, _ = post("/api/v1/places/", {
    "title": "Weird",
    "description": "",
    "price": 10.0,
    "latitude": 999.0,
    "longitude": 10.0,
    "owner_id": OWNER_ID,
})
check("POST with bad latitude (999) returns 400", status == 400)

status, _ = post("/api/v1/places/", {
    "title": "Weird",
    "description": "",
    "price": 10.0,
    "latitude": 10.0,
    "longitude": 999.0,
    "owner_id": OWNER_ID,
})
check("POST with bad longitude (999) returns 400", status == 400)

status, _ = post("/api/v1/places/", {
    "title": "Ghost",
    "description": "",
    "price": 10.0,
    "latitude": 10.0,
    "longitude": 10.0,
    "owner_id": "fake-owner-id",
})
check("POST with fake owner_id returns 400", status == 400)

status, _ = post("/api/v1/places/", {
    "title": "No amenity",
    "description": "",
    "price": 10.0,
    "latitude": 10.0,
    "longitude": 10.0,
    "owner_id": OWNER_ID,
    "amenity_ids": ["fake-amenity-id"],
})
check("POST with fake amenity_id returns 400", status == 400)

status, _ = post("/api/v1/places/", {
    "title": "",
    "description": "",
    "price": 10.0,
    "latitude": 10.0,
    "longitude": 10.0,
    "owner_id": OWNER_ID,
})
check("POST with empty title returns 400", status == 400)

# --- not found ---------------------------------------------------------------
status, _ = get("/api/v1/places/fake-id-000")
check("GET with fake id returns 404", status == 404)

status, _ = put("/api/v1/places/fake-id-000", {"title": "Ghost"})
check("PUT with fake id returns 404", status == 404)

summary()
