"""Facade – the only way the API talks to the data layer."""
from app.persistence.repository import InMemoryRepository
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review


class HBnBFacade:
    """
    This class is the 'middleman' between the API and the storage.
    The API never touches the repository directly.
    """

    def __init__(self):
        self.repo = InMemoryRepository()

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------

    def create_user(self, data):
        user = User(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            password=data["password"],
        )
        self.repo.add(user)
        return user

    def get_user(self, user_id):
        return self.repo.get("User", user_id)

    def list_users(self):
        return self.repo.get_all("User")

    def update_user(self, user_id, data):
        return self.repo.update("User", user_id, data)

    # ------------------------------------------------------------------
    # Amenities
    # ------------------------------------------------------------------

    def create_amenity(self, data):
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
        if not self.repo.exists("User", data.get("owner_id", "")):
            raise ValueError("owner not found")

        # Make sure every amenity id exists
        for aid in data.get("amenity_ids", []):
            if not self.repo.exists("Amenity", aid):
                raise ValueError(f"amenity {aid} not found")

        place = Place(
            title=data["title"],
            description=data.get("description", ""),
            price=data["price"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            owner_id=data["owner_id"],
            amenity_ids=data.get("amenity_ids", []),
        )
        self.repo.add(place)

        # Add this place to the owner's list
        owner = self.repo.get("User", data["owner_id"])
        if owner and place.id not in owner.place_ids:
            owner.place_ids.append(place.id)

        return place

    def get_place(self, place_id):
        """Return place with owner info and amenities list included."""
        place = self.repo.get("Place", place_id)
        if place is None:
            return None
        return self._extend_place(place)

    def list_places(self):
        return [self._extend_place(p) for p in self.repo.get_all("Place")]

    def update_place(self, place_id, data):
        if "owner_id" in data and not self.repo.exists("User", data["owner_id"]):
            raise ValueError("owner not found")

        for aid in data.get("amenity_ids", []):
            if not self.repo.exists("Amenity", aid):
                raise ValueError(f"amenity {aid} not found")

        place = self.repo.update("Place", place_id, data)
        if place is None:
            return None
        return self._extend_place(place)

    def _extend_place(self, place):
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
        amenities = []
        for aid in place.amenity_ids:
            a = self.repo.get("Amenity", aid)
            if a:
                amenities.append({"id": a.id, "name": a.name})
        d["amenities"] = amenities

        # Embed reviews
        reviews = []
        for rid in place.review_ids:
            r = self.repo.get("Review", rid)
            if r:
                reviews.append(r.to_dict())
        d["reviews"] = reviews

        return d

    # ------------------------------------------------------------------
    # Reviews
    # ------------------------------------------------------------------

    def create_review(self, data):
        if not self.repo.exists("User", data.get("user_id", "")):
            raise ValueError("user not found")
        if not self.repo.exists("Place", data.get("place_id", "")):
            raise ValueError("place not found")

        review = Review(
            text=data["text"],
            rating=data["rating"],
            user_id=data["user_id"],
            place_id=data["place_id"],
        )
        self.repo.add(review)

        # Link review to its place and user
        place = self.repo.get("Place", data["place_id"])
        if place and review.id not in place.review_ids:
            place.review_ids.append(review.id)

        user = self.repo.get("User", data["user_id"])
        if user and review.id not in user.review_ids:
            user.review_ids.append(review.id)

        return review

    def get_review(self, review_id):
        return self.repo.get("Review", review_id)

    def list_reviews_for_place(self, place_id):
        return [r for r in self.repo.get_all("Review") if r.place_id == place_id]

    def update_review(self, review_id, data):
        return self.repo.update("Review", review_id, data)

    def delete_review(self, review_id):
        review = self.repo.get("Review", review_id)
        if review is None:
            return False

        # Remove from place's review list
        place = self.repo.get("Place", review.place_id)
        if place and review_id in place.review_ids:
            place.review_ids.remove(review_id)

        # Remove from user's review list
        user = self.repo.get("User", review.user_id)
        if user and review_id in user.review_ids:
            user.review_ids.remove(review_id)

        return self.repo.delete("Review", review_id)


# One shared instance used everywhere in the app
facade = HBnBFacade()
