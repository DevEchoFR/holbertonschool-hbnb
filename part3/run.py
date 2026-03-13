"""Entry point – run this file to start the server."""
from config import DevelopmentConfig
from app import create_app


# Create the app instance with DevelopmentConfig
app = create_app(DevelopmentConfig)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
