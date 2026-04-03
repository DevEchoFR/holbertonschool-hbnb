"""Application factory for creating and configuring the Flask app."""
from flask import Flask
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# Instantiate Bcrypt for password hashing
bcrypt = Bcrypt()

# Instantiate JWTManager for JWT authentication
jwt = JWTManager()

# Instantiate SQLAlchemy for ORM/database operations
db = SQLAlchemy()


def _seed_demo_data():
    """Seed demo data for local development when the database is empty."""
    from app.services.facade import facade

    if facade.list_users():
        return

    # Users
    alice = facade.create_user({
        "first_name": "Alice",
        "last_name": "Admin",
        "email": "alice@example.com",
        "password": "AliceDemo!2026",
        "is_admin": True,
    })
    bob = facade.create_user({
        "first_name": "Bob",
        "last_name": "Guest",
        "email": "bob@example.com",
        "password": "BobDemo!2026",
        "is_admin": False,
    })

    # Amenities
    wifi = facade.create_amenity({"name": "WiFi"})
    kitchen = facade.create_amenity({"name": "Kitchen"})
    pool = facade.create_amenity({"name": "Pool"})

    # Places
    lisbon_place = facade.create_place({
        "title": "Cozy Studio in Lisbon",
        "description": "A bright studio in a lively district with scenic viewpoints nearby.",
        "price": 175,
        "latitude": 38.7223,
        "longitude": -9.1393,
        "owner_id": alice.id,
        "amenity_ids": [wifi.id, kitchen.id],
    })

    facade.create_place({
        "title": "Modern Loft in Barcelona",
        "description": "A modern loft close to restaurants and waterfront walks.",
        "price": 125,
        "latitude": 41.3874,
        "longitude": 2.1686,
        "owner_id": bob.id,
        "amenity_ids": [wifi.id, pool.id],
    })

    # Review
    facade.create_review({
        "text": "Great location and very comfortable stay.",
        "rating": 5,
        "user_id": bob.id,
        "place_id": lisbon_place.id,
    })


def create_app(config_class=None):
    """Create and configure the Flask app with the given configuration.
    
    Args:
        config_class: Configuration class to use. Defaults to DevelopmentConfig.
    
    Returns:
        Flask application instance.
    """
    # Import here to avoid circular imports
    if config_class is None:
        from config import DevelopmentConfig
        config_class = DevelopmentConfig
    
    app = Flask(__name__)

    # Allow local frontend apps (e.g., part4 static server) to call the API.
    CORS(app)
    
    # Apply the configuration object to the app
    app.config.from_object(config_class)
    
    # Initialize Bcrypt with the Flask app
    bcrypt.init_app(app)
    
    # Initialize JWTManager with the Flask app
    jwt.init_app(app)

    # Initialize SQLAlchemy with the Flask app
    db.init_app(app)

    # Import namespaces here to avoid circular imports
    from app.api.v1.users import ns as users_ns
    from app.api.v1.amenities import ns as amenities_ns
    from app.api.v1.places import ns as places_ns
    from app.api.v1.reviews import ns as reviews_ns
    from app.api.v1.auth import ns as auth_ns
    from app.api.v1.admin import ns as admin_ns
    
    # Set up the API with Swagger documentation
    api = Api(
        app,
        version="1.0",
        title="HBnB API",
        description="HBnB Application API",
        doc="/",
    )

    # Register each namespace (group of related endpoints)
    api.add_namespace(auth_ns,      path="/api/v1/auth")
    api.add_namespace(admin_ns,     path="/api/v1/admin")
    api.add_namespace(users_ns,     path="/api/v1/users")
    api.add_namespace(amenities_ns, path="/api/v1/amenities")
    api.add_namespace(places_ns,    path="/api/v1/places")
    api.add_namespace(reviews_ns,   path="/api/v1/reviews")

    # Create all database tables during app startup.
    with app.app_context():
        from app import models as _models  # noqa: F401
        db.create_all()
        if not app.config.get("TESTING", False):
            _seed_demo_data()

    return app
