"""
Tests for Review endpoints.
Run:  python tests/test_reviews.py

Reviews need an existing User and Place, so we create them first.
"""
from helpers import check, post, post_auth, get, put_auth, delete_auth, summary

print("\n--- Review Tests ---")

# --- setup: create a user and a place to review -----------------------------
_, owner = post("/api/v1/users/", {
    "first_name": "Carol",
    "last_name": "White",
    "email": "carol@example.com",
    "password": "pass",
})
OWNER_ID = owner["id"]

_, owner_login = post("/api/v1/auth/login", {
    "email": "carol@example.com",
    "password": "pass",
})
OWNER_TOKEN = owner_login["access_token"]

# create admin to manage amenities (if needed) and privileged delete checks
post("/api/v1/users/", {
    "first_name": "Admin",
    "last_name": "Reviews",
    "email": "admin_reviews@example.com",
    "password": "adminpass",
    "is_admin": True,
})
_, admin_login = post("/api/v1/auth/login", {
    "email": "admin_reviews@example.com",
    "password": "adminpass",
})
ADMIN_TOKEN = admin_login["access_token"]

_, place = post_auth("/api/v1/places/", {
    "title": "Beach House",
    "description": "Lovely beach view.",
    "price": 150.0,
    "latitude": 25.0,
    "longitude": -80.0,
    "owner_id": OWNER_ID,
}, OWNER_TOKEN)
PLACE_ID = place["id"]

# --- valid creation ----------------------------------------------------------
status, review = post_auth("/api/v1/reviews/", {
    "text": "Really enjoyed my stay!",
    "rating": 5,
    "user_id": OWNER_ID,
    "place_id": PLACE_ID,
}, OWNER_TOKEN)
check("POST /reviews/ returns 201", status == 201)
check("Response has an id", "id" in review)
check("Text is correct", review.get("text") == "Really enjoyed my stay!")
check("Rating is correct", review.get("rating") == 5)
check("user_id is linked", review.get("user_id") == OWNER_ID)
check("place_id is linked", review.get("place_id") == PLACE_ID)
REVIEW_ID = review["id"]

# --- get one -----------------------------------------------------------------
status, data = get(f"/api/v1/reviews/{REVIEW_ID}")
check("GET /reviews/<id> returns 200", status == 200)
check("Text matches", data.get("text") == "Really enjoyed my stay!")

# --- review appears in place's review list -----------------------------------
status, data = get(f"/api/v1/places/{PLACE_ID}/reviews")
check("GET /places/<id>/reviews returns 200", status == 200)
check("Review appears in place's review list", len(data) >= 1)
check("Review id matches", data[0].get("id") == REVIEW_ID)

# --- update ------------------------------------------------------------------
status, data = put_auth(f"/api/v1/reviews/{REVIEW_ID}", {
    "text": "Absolutely fantastic!",
    "rating": 5,
}, OWNER_TOKEN)
check("PUT /reviews/<id> returns 200", status == 200)
check("Text was updated", data.get("text") == "Absolutely fantastic!")

# --- validation errors -------------------------------------------------------
status, _ = post_auth("/api/v1/reviews/", {
    "text": "Meh",
    "rating": 10,
    "user_id": OWNER_ID,
    "place_id": PLACE_ID,
}, OWNER_TOKEN)
check("POST with rating > 5 returns 400", status == 400)

status, _ = post_auth("/api/v1/reviews/", {
    "text": "Meh",
    "rating": 0,
    "user_id": OWNER_ID,
    "place_id": PLACE_ID,
}, OWNER_TOKEN)
check("POST with rating < 1 returns 400", status == 400)

status, _ = post_auth("/api/v1/reviews/", {
    "text": "",
    "rating": 3,
    "user_id": OWNER_ID,
    "place_id": PLACE_ID,
}, OWNER_TOKEN)
check("POST with empty text returns 400", status == 400)

status, _ = post_auth("/api/v1/reviews/", {
    "text": "Good",
    "rating": 3,
    "user_id": "fake-user-id",
    "place_id": PLACE_ID,
}, OWNER_TOKEN)
check("POST with fake user_id is overridden to current user", status == 201)

status, _ = post_auth("/api/v1/reviews/", {
    "text": "Good",
    "rating": 3,
    "user_id": OWNER_ID,
    "place_id": "fake-place-id",
}, OWNER_TOKEN)
check("POST with fake place_id returns 400", status == 400)

status, _ = put_auth(f"/api/v1/reviews/{REVIEW_ID}", {"rating": 6}, OWNER_TOKEN)
check("PUT with rating > 5 returns 400", status == 400)

# --- not found ---------------------------------------------------------------
status, _ = get("/api/v1/reviews/fake-id-000")
check("GET with fake id returns 404", status == 404)

status, _ = put_auth("/api/v1/reviews/fake-id-000", {"text": "Ghost"}, OWNER_TOKEN)
check("PUT with fake id returns 404", status == 404)

# --- delete ------------------------------------------------------------------
status, data = delete_auth(f"/api/v1/reviews/{REVIEW_ID}", ADMIN_TOKEN)
check("DELETE /reviews/<id> returns 200", status == 200)

# review must be gone
status, _ = get(f"/api/v1/reviews/{REVIEW_ID}")
check("GET deleted review returns 404", status == 404)

# place's review list must be empty now
status, data = get(f"/api/v1/places/{PLACE_ID}/reviews")
check(
    "Deleted review no longer appears in place review list",
    all(item.get("id") != REVIEW_ID for item in data)
)

# second delete must 404
status, _ = delete_auth(f"/api/v1/reviews/{REVIEW_ID}", ADMIN_TOKEN)
check("DELETE already-deleted review returns 404", status == 404)

# delete a fake id
status, _ = delete_auth("/api/v1/reviews/fake-id-000", ADMIN_TOKEN)
check("DELETE with fake id returns 404", status == 404)

summary()
