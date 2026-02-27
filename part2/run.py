"""Entry point – run this file to start the server."""
from flask import Flask
from flask_restx import Api

from app.api.v1.users import ns as users_ns
from app.api.v1.amenities import ns as amenities_ns
from app.api.v1.places import ns as places_ns
from app.api.v1.reviews import ns as reviews_ns


def create_app():
    """Create and configure the Flask app."""
    app = Flask(__name__)

    # Set up the API with Swagger documentation
    api = Api(
        app,
        version="1.0",
        title="HBnB API",
        description="HBnB Application API",
        doc="/",
    )

    # Register each namespace (group of related endpoints)
    api.add_namespace(users_ns,     path="/users")
    api.add_namespace(amenities_ns, path="/amenities")
    api.add_namespace(places_ns,    path="/places")
    api.add_namespace(reviews_ns,   path="/reviews")

    return app


# Create the app instance
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
