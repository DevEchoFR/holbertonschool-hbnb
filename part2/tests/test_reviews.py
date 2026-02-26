"""
Tests for Review endpoints.
Run:  python tests/test_reviews.py

Reviews need an existing User and Place, so we create them first.
"""
from helpers import check, post, get, put, delete, summary

print("\n--- Review Tests ---")

# --- setup: create a user and a place to review -----------------------------
_, owner = post("/api/v1/users/", {
    "first_name": "Carol",
    "last_name": "White",
    "email": "carol@example.com",
    "password": "pass",
})
OWNER_ID = owner["id"]

_, place = post("/api/v1/places/", {
    "title": "Beach House",
    "description": "Lovely beach view.",
    "price": 150.0,
    "latitude": 25.0,
    "longitude": -80.0,
    "owner_id": OWNER_ID,
})
PLACE_ID = place["id"]

# --- valid creation ----------------------------------------------------------
status, review = post("/api/v1/reviews/", {
    "text": "Really enjoyed my stay!",
    "rating": 5,
    "user_id": OWNER_ID,
    "place_id": PLACE_ID,
})
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
status, data = put(f"/api/v1/reviews/{REVIEW_ID}", {
    "text": "Absolutely fantastic!",
    "rating": 5,
})
check("PUT /reviews/<id> returns 200", status == 200)
check("Text was updated", data.get("text") == "Absolutely fantastic!")

# --- validation errors -------------------------------------------------------
status, _ = post("/api/v1/reviews/", {
    "text": "Meh",
    "rating": 10,
    "user_id": OWNER_ID,
    "place_id": PLACE_ID,
})
check("POST with rating > 5 returns 400", status == 400)

status, _ = post("/api/v1/reviews/", {
    "text": "Meh",
    "rating": 0,
    "user_id": OWNER_ID,
    "place_id": PLACE_ID,
})
check("POST with rating < 1 returns 400", status == 400)

status, _ = post("/api/v1/reviews/", {
    "text": "",
    "rating": 3,
    "user_id": OWNER_ID,
    "place_id": PLACE_ID,
})
check("POST with empty text returns 400", status == 400)

status, _ = post("/api/v1/reviews/", {
    "text": "Good",
    "rating": 3,
    "user_id": "fake-user-id",
    "place_id": PLACE_ID,
})
check("POST with fake user_id returns 400", status == 400)

status, _ = post("/api/v1/reviews/", {
    "text": "Good",
    "rating": 3,
    "user_id": OWNER_ID,
    "place_id": "fake-place-id",
})
check("POST with fake place_id returns 400", status == 400)

status, _ = put(f"/api/v1/reviews/{REVIEW_ID}", {"rating": 6})
check("PUT with rating > 5 returns 400", status == 400)

# --- not found ---------------------------------------------------------------
status, _ = get("/api/v1/reviews/fake-id-000")
check("GET with fake id returns 404", status == 404)

status, _ = put("/api/v1/reviews/fake-id-000", {"text": "Ghost"})
check("PUT with fake id returns 404", status == 404)

# --- delete ------------------------------------------------------------------
status, data = delete(f"/api/v1/reviews/{REVIEW_ID}")
check("DELETE /reviews/<id> returns 200", status == 200)

# review must be gone
status, _ = get(f"/api/v1/reviews/{REVIEW_ID}")
check("GET deleted review returns 404", status == 404)

# place's review list must be empty now
status, data = get(f"/api/v1/places/{PLACE_ID}/reviews")
check("Place review list is empty after delete", len(data) == 0)

# second delete must 404
status, _ = delete(f"/api/v1/reviews/{REVIEW_ID}")
check("DELETE already-deleted review returns 404", status == 404)

# delete a fake id
status, _ = delete("/api/v1/reviews/fake-id-000")
check("DELETE with fake id returns 404", status == 404)

summary()
