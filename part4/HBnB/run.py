"""Entry point – run this file to start the server."""
from part3.HBnB.config import get_config_from_env
from part3.HBnB.app import create_app


# Create the app instance from APP_ENV/FLASK_ENV (defaults to development)
app = create_app(get_config_from_env())

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
