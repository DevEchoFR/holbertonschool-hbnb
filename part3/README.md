# HBnB - Part 2: RESTful API with Flask

## Description

This is Part 2 of the HBnB project. We build a REST API using Flask and Flask-RESTx.
The project follows a layered architecture:

- **Presentation Layer** – Flask-RESTx namespaces (API endpoints + Swagger UI)
- **Business Logic Layer** – Models (`User`, `Place`, `Review`, `Amenity`) + `HBnBFacade`
- **Persistence Layer** – `InMemoryRepository` (dict-based, no database required)

The **Facade** is the single entry point between the API and storage.  
The API **never** touches the repository directly.

---

## Project Structure

```
part2/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── users.py        # User endpoints
│   │       ├── places.py       # Place endpoints + sub-resource /places/<id>/reviews
│   │       ├── reviews.py      # Review endpoints
│   │       └── amenities.py    # Amenity endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py       # Shared UUID id + UTC timestamps
│   │   ├── user.py
│   │   ├── place.py
│   │   ├── review.py
│   │   └── amenity.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── facade.py           # HBnBFacade – the only path to storage
│   └── persistence/
│       ├── __init__.py
│       └── repository.py       # InMemoryRepository
├── tests/
│   ├── __init__.py
│   ├── helpers.py              # Shared test client and utilities
│   ├── test_users.py           # User endpoint tests
│   ├── test_amenities.py       # Amenity endpoint tests
│   ├── test_places.py          # Place endpoint tests
│   ├── test_reviews.py         # Review endpoint tests
│   └── run_all.py              # Run all test files at once
├── run.py
├── config.py
├── requirements.txt
└── README.md
```

---

## How to Run

```bash
cd part2

# Install dependencies
pip install -r requirements.txt

# Start the server
python run.py
```

- API base URL: `http://localhost:5000/api/v1/`
- Swagger UI: `http://localhost:5000/api/v1/doc`

---

## Endpoints

### Users

| Method | Route | Description |
|--------|-------|-------------|
| `POST` | `/api/v1/users/` | Create a user |
| `GET` | `/api/v1/users/` | List all users |
| `GET` | `/api/v1/users/<id>` | Get a user |
| `PUT` | `/api/v1/users/<id>` | Update a user |

### Amenities

| Method | Route | Description |
|--------|-------|-------------|
| `POST` | `/api/v1/amenities/` | Create an amenity |
| `GET` | `/api/v1/amenities/` | List all amenities |
| `GET` | `/api/v1/amenities/<id>` | Get an amenity |
| `PUT` | `/api/v1/amenities/<id>` | Update an amenity |

### Places

| Method | Route | Description |
|--------|-------|-------------|
| `POST` | `/api/v1/places/` | Create a place |
| `GET` | `/api/v1/places/` | List all places (extended) |
| `GET` | `/api/v1/places/<id>` | Get a place (extended) |
| `PUT` | `/api/v1/places/<id>` | Update a place |
| `GET` | `/api/v1/places/<id>/reviews` | List all reviews for a place |

### Reviews

| Method | Route | Description |
|--------|-------|-------------|
| `POST` | `/api/v1/reviews/` | Create a review |
| `GET` | `/api/v1/reviews/<id>` | Get a review |
| `PUT` | `/api/v1/reviews/<id>` | Update a review |
| `DELETE` | `/api/v1/reviews/<id>` | Delete a review |

---

## Data Models

All models inherit from `BaseModel` which provides:

| Field | Type | Description |
|---|---|---|
| `id` | string (UUID) | Auto-generated unique identifier |
| `created_at` | string (ISO 8601) | UTC timestamp set at creation |
| `updated_at` | string (ISO 8601) | UTC timestamp updated on every change |

### User

| Field | Type | Rules |
|---|---|---|
| `first_name` | string | Required, non-empty |
| `last_name` | string | Required, non-empty |
| `email` | string | Required, must match `user@domain.tld` format |
| `password` | string | Required, **never returned in any response** |

### Place

| Field | Type | Rules |
|---|---|---|
| `title` | string | Required, non-empty |
| `description` | string | Optional |
| `price` | float | Required, >= 0 |
| `latitude` | float | Required, -90 to 90 |
| `longitude` | float | Required, -180 to 180 |
| `owner_id` | string | Required, must reference an existing user |
| `amenity_ids` | list[string] | Optional, each ID must reference an existing amenity |

Place responses (`GET /places/` and `GET /places/<id>`) include embedded data:

```json
{
  "owner":     { "id": "...", "first_name": "...", "last_name": "..." },
  "amenities": [ { "id": "...", "name": "..." } ],
  "reviews":   [ { "id": "...", "text": "...", "rating": 4 } ]
}
```

### Review

| Field | Type | Rules |
|---|---|---|
| `text` | string | Required, non-empty |
| `rating` | integer | Required, 1–5 |
| `user_id` | string | Required, must reference an existing user |
| `place_id` | string | Required, must reference an existing place |

### Amenity

| Field | Type | Rules |
|---|---|---|
| `name` | string | Required, non-empty |

---

## Architecture

```
HTTP Request
     │
     ▼
┌──────────────────────┐
│  Presentation Layer  │  Flask-RESTx Namespaces
│  (API Endpoints)     │  /api/v1/{users,places,reviews,amenities}
└────────┬─────────────┘
         │ calls only
         ▼
┌──────────────────────┐
│  Business Logic      │  HBnBFacade
│  (Facade + Models)   │  User · Place · Review · Amenity · BaseModel
└────────┬─────────────┘
         │ uses
         ▼
┌──────────────────────┐
│  Persistence Layer   │  InMemoryRepository
│  (Storage)           │  { "User": {id: obj}, "Place": {…}, … }
└──────────────────────┘
```

Key design decisions:
- The **Facade** validates cross-model references (e.g. `owner_id` must exist before a place is saved).
- When a review is deleted, it is also removed from the owning place's and user's review lists.
- **Passwords** are stored as `_password` and excluded from all `to_dict()` / API responses.
- Only **reviews** expose a `DELETE` endpoint.
- All data is stored **in memory** — it resets on every server restart.

---

## Testing

```bash
cd part2

# Run all tests at once
python tests/run_all.py

# Or run a single file
python tests/test_users.py
python tests/test_amenities.py
python tests/test_places.py
python tests/test_reviews.py
```

| File | What it tests |
|------|---------------|
| `tests/test_users.py` | Create, get, list, update users – validation & 404 |
| `tests/test_amenities.py` | Create, get, list, update amenities – validation & 404 |
| `tests/test_places.py` | Create, get, list, update places – extended data, validation & 404 |
| `tests/test_reviews.py` | Create, get, update, delete reviews – validation, place link & 404 |

---

# ✍️ Author

Holberton School — HBnB Project   
Team: 👥 - [David Roset](https://github.com/DevEchoFR) - [Tom Marchal](https://github.com/TomMrcl)
