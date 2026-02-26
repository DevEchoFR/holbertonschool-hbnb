"""User model."""
import re
from app.models.base_model import BaseModel


class User(BaseModel):
    """Represents a person who signed up on HBnB."""

    def __init__(self, first_name, last_name, email, password):
        super().__init__()
        self._validate(first_name, last_name, email, password)
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self._password = password  # underscore = private, never sent to client
        self.place_ids = []   # list of place ids owned by this user
        self.review_ids = []  # list of review ids written by this user

    # --- validation -------------------------------------------------------

    @staticmethod
    def _validate(first_name, last_name, email, password):
        """Check that all required fields are present and valid."""
        if not first_name or not first_name.strip():
            raise ValueError("first_name is required")
        if not last_name or not last_name.strip():
            raise ValueError("last_name is required")
        if not email or not email.strip():
            raise ValueError("email is required")
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            raise ValueError("Invalid email format")
        if not password or not password.strip():
            raise ValueError("password is required")

    # --- update -----------------------------------------------------------

    def update(self, data):
        protected = ("id", "created_at", "updated_at")
        for key, value in data.items():
            if key in protected:
                continue
            if key == "password":
                if not value or not str(value).strip():
                    raise ValueError("password is required")
                self._password = value
                continue
            if key == "email":
                if not value or not re.match(
                        r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value):
                    raise ValueError("Invalid email format")
            if key in ("first_name", "last_name") and (
                    not value or not str(value).strip()):
                raise ValueError(f"{key} is required")
            setattr(self, key, value)
        from datetime import datetime
        self.updated_at = datetime.utcnow().isoformat()

    # --- serialisation ----------------------------------------------------

    def to_dict(self):
        """Return user data as a dict. Password is NEVER included."""
        d = super().to_dict()
        d.pop("_password", None)  # remove the password before sending
        return d
