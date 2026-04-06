"""Base class that all SQLAlchemy models inherit from."""
import uuid
from datetime import datetime, timezone
from app import db


def _generate_uuid():
    return str(uuid.uuid4())


def _now():
    return datetime.now(timezone.utc)


class BaseModel(db.Model):
    """Common id/timestamp fields and helpers for all entities."""

    __abstract__ = True

    id = db.Column(db.String(60), primary_key=True, default=_generate_uuid)
    created_at = db.Column(db.DateTime, nullable=False, default=_now)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=_now,
        onupdate=_now,
    )

    def update(self, data):
        """Update mutable fields from a dictionary."""
        protected = {"id", "created_at", "updated_at"}
        for key, value in data.items():
            if key in protected:
                continue
            setattr(self, key, value)
        self.updated_at = _now()

    def to_dict(self):
        """Return a JSON-friendly dictionary representation."""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
