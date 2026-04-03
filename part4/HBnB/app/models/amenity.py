"""Amenity model."""
from app.models.base_model import BaseModel
from app import db


class Amenity(BaseModel):
    """An amenity is a feature a place can have, like WiFi or a Pool."""

    __tablename__ = "amenities"

    name = db.Column(db.String(128), nullable=False, unique=True)

    places = db.relationship(
        "Place",
        secondary="place_amenities",
        back_populates="amenities",
    )

    def __init__(self, name: str):
        super().__init__()
        if not name or not name.strip():
            raise ValueError("name is required")
        self.name = name

    def update(self, data: dict):
        if "name" in data:
            if not data["name"] or not str(data["name"]).strip():
                raise ValueError("name is required")
        super().update(data)

    def to_dict(self):
        d = super().to_dict()
        d.update({"name": self.name})
        return d
