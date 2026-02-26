"""Review model."""
from app.models.base_model import BaseModel


class Review(BaseModel):
    """A review is feedback a user leaves for a place they visited."""

    def __init__(self, text, rating, user_id, place_id):
        super().__init__()
        self._validate(text, rating)
        self.text = text
        self.rating = int(rating)
        self.user_id = user_id
        self.place_id = place_id

    @staticmethod
    def _validate(text, rating):
        if not text or not str(text).strip():
            raise ValueError("text is required")
        try:
            r = int(rating)
        except (TypeError, ValueError):
            raise ValueError("rating must be an integer between 1 and 5")
        if not (1 <= r <= 5):
            raise ValueError("rating must be between 1 and 5")

    def update(self, data: dict):
        if "text" in data and (
                not data["text"] or not str(data["text"]).strip()):
            raise ValueError("text is required")
        if "rating" in data:
            try:
                r = int(data["rating"])
            except (TypeError, ValueError):
                raise ValueError("rating must be an integer between 1 and 5")
            if not (1 <= r <= 5):
                raise ValueError("rating must be between 1 and 5")
            data["rating"] = r
        super().update(data)
