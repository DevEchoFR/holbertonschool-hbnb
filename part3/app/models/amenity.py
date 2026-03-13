"""Amenity model."""
from app.models.base_model import BaseModel


class Amenity(BaseModel):
    """An amenity is a feature a place can have, like WiFi or a Pool."""

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
