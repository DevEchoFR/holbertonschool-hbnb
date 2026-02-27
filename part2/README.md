# HBnB - Part 2: RESTful API with Flask

## Description

This is Part 2 of the HBnB project. We build a REST API using Flask and Flask-RESTx.
The project follows a layered architecture with:
- A **Presentation Layer** (API endpoints)
- A **Business Logic Layer** (Models + Facade)
- A **Persistence Layer** (In-Memory Repository)

## Project Structure

```
part2/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── users.py
│   │       ├── places.py
│   │       ├── reviews.py
│   │       └── amenities.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py
│   │   ├── user.py
│   │   ├── place.py
│   │   ├── review.py
│   │   └── amenity.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── facade.py
│   └── persistence/
│       ├── __init__.py
│       └── repository.py
├── tests/
│   ├── __init__.py
│   ├── helpers.py          <- shared test client and utilities
│   ├── test_users.py       <- user endpoint tests
│   ├── test_amenities.py   <- amenity endpoint tests
│   ├── test_places.py      <- place endpoint tests
│   ├── test_reviews.py     <- review endpoint tests
│   └── run_all.py          <- run all test files at once
├── run.py
├── config.py
├── requirements.txt
└── README.md
```

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python run.py
```

The API will be available at `http://localhost:5000/api/v1/`  
Swagger documentation: `http://localhost:5000/api/v1/doc`

## Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| POST | /api/v1/users/ | Create a user |
| GET | /api/v1/users/ | List all users |
| GET | /api/v1/users/\<id\> | Get a user |
| PUT | /api/v1/users/\<id\> | Update a user |
| POST | /api/v1/amenities/ | Create an amenity |
| GET | /api/v1/amenities/ | List all amenities |
| GET | /api/v1/amenities/\<id\> | Get an amenity |
| PUT | /api/v1/amenities/\<id\> | Update an amenity |
| POST | /api/v1/places/ | Create a place |
| GET | /api/v1/places/ | List all places |
| GET | /api/v1/places/\<id\> | Get a place |
| PUT | /api/v1/places/\<id\> | Update a place |
| POST | /api/v1/reviews/ | Create a review |
| GET | /api/v1/reviews/\<id\> | Get a review |
| PUT | /api/v1/reviews/\<id\> | Update a review |
| DELETE | /api/v1/reviews/\<id\> | Delete a review |
| GET | /api/v1/places/\<id\>/reviews | List reviews for a place |

## Testing

Each resource has its own test file inside the `tests/` folder.

```bash
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
| `tests/test_reviews.py` | Create, get, update, delete reviews – validation, links & 404 |

## Notes

- Passwords are **never** returned in any API response.
- Only **reviews** support the `DELETE` method.
- Place responses include embedded **owner** info and **amenities** list.
- All data is stored in memory – it resets every time the server restarts.

---

# ✍️ Author

Holberton School — HBnB Project
Team: 👥 - [David Roset](https://github.com/DevEchoFR) - [Tom Marchal](https://github.com/TomMrcl)