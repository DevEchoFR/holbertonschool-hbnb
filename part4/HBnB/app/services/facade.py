"""Facade – the only way the API talks to the data layer."""
from app.persistence.repository import SQLAlchemyRepository
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review
from app import db


class HBnBFacade:
    """
    This class is the 'middleman' between the API and the storage.
    The API never touches the repository directly.
    """

    def __init__(self):
        self.repo = SQLAlchemyRepository()

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------

    def create_user(self, data):
        existing = self.get_user_by_email(data["email"])
        if existing is not None:
            raise ValueError("email already registered")
        user = User(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            password=data["password"],
            is_admin=data.get("is_admin", False),
        )
        self.repo.add(user)
        return user

    def get_user(self, user_id):
        return self.repo.get("User", user_id)

    def get_user_by_email(self, email):
        """Retrieve a user by their email address."""
        return self.repo.get_by_field("User", "email", email)

    def list_users(self):
        return self.repo.get_all("User")

    def update_user(self, user_id, data):
        return self.repo.update("User", user_id, data)

    def delete_user(self, user_id):
        return self.repo.delete("User", user_id)

    # ------------------------------------------------------------------
    # Amenities
    # ------------------------------------------------------------------

    def create_amenity(self, data):
        existing = self.repo.get_by_field("Amenity", "name", data["name"])
        if existing is not None:
            raise ValueError("Amenity name already exists")
        amenity = Amenity(name=data["name"])
        self.repo.add(amenity)
        return amenity

    def get_amenity(self, amenity_id):
        return self.repo.get("Amenity", amenity_id)

    def list_amenities(self):
        return self.repo.get_all("Amenity")

    def update_amenity(self, amenity_id, data):
        return self.repo.update("Amenity", amenity_id, data)

    # ------------------------------------------------------------------
    # Places
    # ------------------------------------------------------------------

    def create_place(self, data):
        # Make sure the owner exists before creating the place
        owner = self.repo.get("User", data.get("owner_id", ""))
        if owner is None:
            raise ValueError("owner not found")

        # Make sure every amenity id exists
        amenities = []
        for aid in data.get("amenity_ids", []):
            amenity = self.repo.get("Amenity", aid)
            if amenity is None:
                raise ValueError(f"amenity {aid} not found")
            amenities.append(amenity)

        place = Place(
            title=data["title"],
            description=data.get("description", ""),
            price=data["price"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            owner_id=data["owner_id"],
        )
        place.owner = owner
        place.amenities = amenities
        self.repo.add(place)

        # Refresh so relationships are reloaded cleanly after the commit
        # (SQLAlchemy expires all attributes on commit by default).
        db.session.refresh(place)
        return place

    def get_place(self, place_id):
        """Return place with owner info and amenities list included."""
        place = self.repo.get("Place", place_id)
        if place is None:
            return None
        return self.extend_place(place)

    def list_places(self):
        return [self.extend_place(p) for p in self.repo.get_all("Place")]

    def update_place(self, place_id, data):
        place = self.repo.get("Place", place_id)
        if place is None:
            return None

        if "owner_id" in data and data["owner_id"] != place.owner_id:
            raise ValueError("owner_id cannot be changed")

        if "amenity_ids" in data:
            amenities = []
            for aid in data.get("amenity_ids", []):
                amenity = self.repo.get("Amenity", aid)
                if amenity is None:
                    raise ValueError(f"amenity {aid} not found")
                amenities.append(amenity)
            place.amenities = amenities
            data = {k: v for k, v in data.items() if k != "amenity_ids"}

        place.update(data)
        db.session.commit()
        # Refresh after commit so relationships (amenities, reviews) are
        # reloaded from the DB rather than served from the expired identity map.
        db.session.refresh(place)
        return self.extend_place(place)

    def extend_place(self, place):
        """Add owner details, amenity details and reviews to a place dict."""
        d = place.to_dict()

        # Embed owner first/last name
        owner = self.repo.get("User", place.owner_id)
        if owner:
            d["owner"] = {
                "id": owner.id,
                "first_name": owner.first_name,
                "last_name": owner.last_name,
            }
        else:
            d["owner"] = None

        # Embed amenity names
        d["amenities"] = [{"id": a.id, "name": a.name} for a in place.amenities]

        # Embed reviews with author display name for frontend usage
        d["reviews"] = []
        for review in place.reviews:
            review_data = review.to_dict()
            author = self.repo.get("User", review.user_id)
            if author is not None:
                review_data["user"] = f"{author.first_name} {author.last_name}".strip()
            d["reviews"].append(review_data)

        return d

    # ------------------------------------------------------------------
    # Reviews
    # ------------------------------------------------------------------

    def create_review(self, data):
        user = self.repo.get("User", data.get("user_id", ""))
        if user is None:
            raise ValueError("user not found")
        place = self.repo.get("Place", data.get("place_id", ""))
        if place is None:
            raise ValueError("place not found")

        review = Review(
            text=data["text"],
            rating=data["rating"],
            user_id=data["user_id"],
            place_id=data["place_id"],
        )
        review.author = user
        review.place = place
        self.repo.add(review)

        return review

    def get_review(self, review_id):
        return self.repo.get("Review", review_id)

    def list_reviews_for_place(self, place_id):
        place = self.repo.get("Place", place_id)
        if place is None:
            return []
        return place.reviews

    def update_review(self, review_id, data):
        return self.repo.update("Review", review_id, data)

    def delete_review(self, review_id):
        return self.repo.delete("Review", review_id)

    def delete_place(self, place_id):
        return self.repo.delete("Place", place_id)

    def get_place_model(self, place_id):
        """Get a place ORM model (used for authorization checks)."""
        return self.repo.get("Place", place_id)

    def get_review_model(self, review_id):
        """Get a review ORM model (used for authorization checks)."""
        return self.repo.get("Review", review_id)


# One shared instance used everywhere in the app
facade = HBnBFacade()
