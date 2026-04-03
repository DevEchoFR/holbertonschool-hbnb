# HBnB - Part 3: Enhanced Backend (Auth + Database)

## Project Goal

Part 3 turns the HBnB API into a secure, persistent backend by adding:

- JWT authentication with Flask-JWT-Extended
- Role-based authorization using the user `is_admin` flag
- SQLAlchemy ORM with SQLite for development/testing
- MySQL-ready production configuration
- Database-backed CRUD for users, amenities, places, and reviews

## Stack

- Flask
- Flask-RESTx
- Flask-Bcrypt
- Flask-JWT-Extended
- Flask-SQLAlchemy
- SQLite (development + tests)
- MySQL (production via PyMySQL)

## Project Structure

```text
part3/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   └── v1/
│   │       ├── admin.py
│   │       ├── amenities.py
│   │       ├── auth.py
│   │       ├── places.py
│   │       ├── reviews.py
│   │       └── users.py
│   ├── models/
│   │   ├── amenity.py
│   │   ├── base_model.py
│   │   ├── place.py
│   │   ├── review.py
│   │   └── user.py
│   ├── persistence/
│   │   └── repository.py
│   └── services/
│       └── facade.py
├── tests/
│   ├── helpers.py
│   ├── run_all.py
│   ├── test_amenities.py
│   ├── test_places.py
│   ├── test_reviews.py
│   └── test_users.py
├── DB_SCHEMA.md
├── config.py
├── README.md
├── requirements.txt
└── run.py
```

## Architecture

- Presentation layer: Flask-RESTx namespaces under `app/api/v1`
- Business layer: models + facade in `app/models` and `app/services/facade.py`
- Persistence layer: SQLAlchemy repository in `app/persistence/repository.py`

The API never accesses the database session directly from endpoints. Endpoints use the facade.

```text
HTTP Request
  |
  v
Presentation Layer (Flask-RESTx Namespaces)
  |
  v
Business Layer (Facade + Domain Models)
  |
  v
Persistence Layer (SQLAlchemy Repository)
  |
  v
SQLite (dev/test) or MySQL (production)
```

## Configuration

Configuration classes are defined in `config.py`:

- `DevelopmentConfig`
- `TestingConfig`
- `ProductionConfig`

Default database URIs:

- Development: `sqlite:///hbnb_dev.db`
- Testing: `sqlite:///:memory:`
- Production: `mysql+pymysql://...`

Supported environment variables:

- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `DATABASE_URL`
- `DEV_DATABASE_URL`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_HOST`
- `MYSQL_PORT`
- `MYSQL_DATABASE`

## Run Locally

```bash
cd part3
pip install -r requirements.txt
export APP_ENV=development  # or testing / production
python run.py
```

- API base: `http://localhost:5000/api/v1/`
- Swagger UI: `http://localhost:5000/`

Environment selection notes:

- `run.py` now reads `APP_ENV` (or `FLASK_ENV`) to choose config.
- Supported values: `development`, `testing`, `production`.
- If unset, it defaults to development.

## Authentication Flow

### 1) Register a user

Endpoint:

`POST /api/v1/users/`

Example body:

```json
{
  "first_name": "Alice",
  "last_name": "Smith",
  "email": "alice@example.com",
  "password": "strong-password",
  "is_admin": false
}
```

Passwords are hashed with bcrypt and are never returned in responses.

### 2) Login and get JWT

Endpoint:

`POST /api/v1/auth/login`

Example body:

```json
{
  "email": "alice@example.com",
  "password": "strong-password"
}
```

Successful response contains `access_token`.

### 3) Send token on protected routes

```http
Authorization: Bearer <access_token>
```

## Authorization Rules

- `POST /api/v1/amenities/`: admin only
- `PUT /api/v1/amenities/<amenity_id>`: admin only
- `POST /api/v1/places/`: authenticated users (non-admin owner is forced to current user)
- `PUT /api/v1/places/<place_id>`: owner or admin
- `POST /api/v1/reviews/`: authenticated users (non-admin author is forced to current user)
- `PUT /api/v1/reviews/<review_id>`: author or admin
- `DELETE /api/v1/reviews/<review_id>`: author or admin

## Admin Operations

Dedicated admin namespace:

- `GET /api/v1/admin/users`: list all users (admin only)
- `PUT /api/v1/admin/users/<user_id>/role`: grant/revoke admin role (admin only)

Example body for role update:

```json
{
  "is_admin": true
}
```

## Database Model

Relational schema and ER diagram are documented in:

- `DB_SCHEMA.md`

Main relationships:

- One user owns many places
- One user writes many reviews
- One place has many reviews
- Places and amenities are many-to-many

## Tests

Run all tests:

```bash
python tests/run_all.py
```

Run individual test modules:

```bash
python tests/test_users.py
python tests/test_amenities.py
python tests/test_places.py
python tests/test_reviews.py
```

## Notes

- Tables are created automatically on app startup.
- The codebase is now fully database-backed (no in-memory repository for runtime CRUD).
- Test helpers reset the test database for isolated test execution.

## ✍️ Author

Holberton School — HBnB Project
Team: 👥 - [David Roset](https://github.com/DevEchoFR) - [Tom Marchal](https://github.com/TomMrcl)
