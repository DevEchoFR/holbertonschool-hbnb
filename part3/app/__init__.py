"""Application factory for creating and configuring the Flask app."""
from flask import Flask
from flask_restx import Api
from flask_bcrypt import Bcrypt

from app.api.v1.users import ns as users_ns
from app.api.v1.amenities import ns as amenities_ns
from app.api.v1.places import ns as places_ns
from app.api.v1.reviews import ns as reviews_ns

# Instantiate Bcrypt for password hashing
bcrypt = Bcrypt()


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
    
    # Apply the configuration object to the app
    app.config.from_object(config_class)
    
    # Initialize Bcrypt with the Flask app
    bcrypt.init_app(app)
    
    # Set up the API with Swagger documentation
    api = Api(
        app,
        version="1.0",
        title="HBnB API",
        description="HBnB Application API",
        doc="/",
    )

    # Register each namespace (group of related endpoints)
    api.add_namespace(users_ns,     path="/api/v1/users")
    api.add_namespace(amenities_ns, path="/api/v1/amenities")
    api.add_namespace(places_ns,    path="/api/v1/places")
    api.add_namespace(reviews_ns,   path="/api/v1/reviews")

    return app
