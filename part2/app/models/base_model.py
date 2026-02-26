"""Base class that all models inherit from."""
import uuid
from datetime import datetime


class BaseModel:
    """Every object in our app gets an id and timestamps from here."""

    def __init__(self):
        # Generate a unique ID for each object
        self.id = str(uuid.uuid4())
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()

    def update(self, data):
        """Update the object's fields with the given dictionary."""
        for key, value in data.items():
            # We never let anyone change the id or timestamps directly
            if key in ("id", "created_at", "updated_at"):
                continue
            setattr(self, key, value)
        self.updated_at = datetime.utcnow().isoformat()

    def to_dict(self):
        """Return a dictionary of the object (used to build JSON responses)."""
        return dict(self.__dict__)
