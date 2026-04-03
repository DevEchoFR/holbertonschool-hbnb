"""User model."""
import re
from app.models.base_model import BaseModel
from app import db


class User(BaseModel):
    """Represents a person who signed up on HBnB."""

    __tablename__ = "users"

    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    places = db.relationship(
        "Place",
        back_populates="owner",
        cascade="all, delete-orphan",
    )
    reviews = db.relationship(
        "Review",
        back_populates="author",
        cascade="all, delete-orphan",
    )

    def __init__(self, first_name, last_name, email, password, is_admin=False):
        self._validate(first_name, last_name, email, password)
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = ""
        self.hash_password(password)
        self.is_admin = is_admin  # Flag to indicate if user is an admin

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

    # --- password hashing -------------------------------------------------

    def hash_password(self, password):
        """Hash the password using bcrypt before storing it."""
        from app import bcrypt
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        """Verify if the provided password matches the hashed password."""
        from app import bcrypt
        if not self.password:
            return False
        return bcrypt.check_password_hash(self.password, password)

    # --- update -----------------------------------------------------------

    def update(self, data):
        protected = ("id", "created_at", "updated_at")
        for key, value in data.items():
            if key in protected:
                continue
            if key == "password":
                if not value or not str(value).strip():
                    raise ValueError("password is required")
                self.hash_password(value)
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
        self.updated_at = datetime.utcnow()

    # --- serialisation ----------------------------------------------------

    def to_dict(self):
        """Return user data as a dict. Password is NEVER included."""
        d = super().to_dict()
        d.update({
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "is_admin": self.is_admin,
        })
        return d
