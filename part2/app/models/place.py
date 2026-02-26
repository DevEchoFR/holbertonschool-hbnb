"""Place model."""
from app.models.base_model import BaseModel


class Place(BaseModel):
    """A place is a property listed for rent."""

    def __init__(self, title, description, price,
                 latitude, longitude, owner_id, amenity_ids=None):
        super().__init__()
        self._validate(title, price, latitude, longitude)
        self.title = title
        self.description = description
        self.price = float(price)
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.owner_id = owner_id
        self.amenity_ids = amenity_ids if amenity_ids is not None else []
        self.review_ids = []  # reviews left for this place

    # --- validation -------------------------------------------------------

    @staticmethod
    def _validate(title, price, latitude, longitude):
        """Make sure the data makes sense before saving."""
        if not title or not str(title).strip():
            raise ValueError("title is required")
        if float(price) < 0:
            raise ValueError("price must be >= 0")
        if not (-90 <= float(latitude) <= 90):
            raise ValueError("latitude must be between -90 and 90")
        if not (-180 <= float(longitude) <= 180):
            raise ValueError("longitude must be between -180 and 180")

    def update(self, data: dict):
        for key in ("price", "latitude", "longitude"):
            if key in data:
                data[key] = float(data[key])
        if "title" in data and (
                not data["title"] or not str(data["title"]).strip()):
            raise ValueError("title is required")
        if "price" in data and data["price"] < 0:
            raise ValueError("price must be >= 0")
        if "latitude" in data and not (-90 <= data["latitude"] <= 90):
            raise ValueError("latitude must be between -90 and 90")
        if "longitude" in data and not (-180 <= data["longitude"] <= 180):
            raise ValueError("longitude must be between -180 and 180")
        super().update(data)

    def to_dict(self) -> dict:
        return super().to_dict()
