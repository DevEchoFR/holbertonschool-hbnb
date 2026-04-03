"""Place model."""
from app.models.base_model import BaseModel
from app import db


place_amenities = db.Table(
    "place_amenities",
    db.Column("place_id", db.String(60), db.ForeignKey("places.id"), primary_key=True),
    db.Column("amenity_id", db.String(60), db.ForeignKey("amenities.id"), primary_key=True),
)


class Place(BaseModel):
    """A place is a property listed for rent."""

    __tablename__ = "places"

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True, default="")
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    owner_id = db.Column(db.String(60), db.ForeignKey("users.id"), nullable=False)

    owner = db.relationship("User", back_populates="places")
    reviews = db.relationship(
        "Review",
        back_populates="place",
        cascade="all, delete-orphan",
    )
    amenities = db.relationship(
        "Amenity",
        secondary=place_amenities,
        back_populates="places",
    )

    def __init__(self, title, description, price,
                 latitude, longitude, owner_id, amenity_ids=None):
        self._validate(title, price, latitude, longitude)
        self.title = title
        self.description = description
        self.price = float(price)
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.owner_id = owner_id

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
        d = super().to_dict()
        d.update({
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "owner_id": self.owner_id,
            "amenity_ids": [amenity.id for amenity in self.amenities],
        })
        return d
