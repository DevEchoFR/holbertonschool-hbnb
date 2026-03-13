"""Place endpoints – /api/v1/places/"""
from flask_restx import Namespace, Resource, fields
from app.services.facade import facade

ns = Namespace("places", description="Place operations")

# ------------------------------------------------------------------
# Models
# ------------------------------------------------------------------
place_input_model = ns.model("PlaceInput", {
    "title":       fields.String(required=True),
    "description": fields.String(default=""),
    "price":       fields.Float(required=True),
    "latitude":    fields.Float(required=True),
    "longitude":   fields.Float(required=True),
    "owner_id":    fields.String(required=True),
    "amenity_ids": fields.List(fields.String, default=[]),
})

place_update_model = ns.model("PlaceUpdate", {
    "title":       fields.String,
    "description": fields.String,
    "price":       fields.Float,
    "latitude":    fields.Float,
    "longitude":   fields.Float,
    "amenity_ids": fields.List(fields.String),
})

owner_brief = ns.model("OwnerBrief", {
    "id":         fields.String,
    "first_name": fields.String,
    "last_name":  fields.String,
})

amenity_brief = ns.model("AmenityBrief", {
    "id":   fields.String,
    "name": fields.String,
})

review_brief = ns.model("ReviewBrief", {
    "id":     fields.String,
    "text":   fields.String,
    "rating": fields.Integer,
})

place_output_model = ns.model("PlaceOutput", {
    "id":          fields.String,
    "title":       fields.String,
    "description": fields.String,
    "price":       fields.Float,
    "latitude":    fields.Float,
    "longitude":   fields.Float,
    "owner_id":    fields.String,
    "amenity_ids": fields.List(fields.String),
    "owner":       fields.Nested(owner_brief, allow_null=True),
    "amenities":   fields.List(fields.Nested(amenity_brief)),
    "reviews":     fields.List(fields.Nested(review_brief)),
    "created_at":  fields.String,
    "updated_at":  fields.String,
})


# ------------------------------------------------------------------
# Collection
# ------------------------------------------------------------------
@ns.route("/")
class PlaceList(Resource):

    @ns.marshal_list_with(place_output_model)
    def get(self):
        """List all places (extended)."""
        return facade.list_places(), 200

    @ns.expect(place_input_model, validate=True)
    @ns.response(201, "Created")
    @ns.response(400, "Bad Request")
    def post(self):
        """Create a new place."""
        data = ns.payload
        try:
            place = facade.create_place(data)
        except (ValueError, KeyError) as e:
            ns.abort(400, str(e))
        return facade._extend_place(place), 201


# ------------------------------------------------------------------
# Item
# ------------------------------------------------------------------
@ns.route("/<string:place_id>")
class PlaceDetail(Resource):

    @ns.marshal_with(place_output_model)
    @ns.response(404, "Not Found")
    def get(self, place_id):
        """Get a single place (extended)."""
        place = facade.get_place(place_id)
        if place is None:
            ns.abort(404, "Place not found")
        return place, 200

    @ns.expect(place_update_model, validate=True)
    @ns.response(200, "Updated")
    @ns.response(400, "Bad Request")
    @ns.response(404, "Not Found")
    def put(self, place_id):
        """Update a place."""
        data = ns.payload
        try:
            place = facade.update_place(place_id, data)
        except ValueError as e:
            ns.abort(400, str(e))
        if place is None:
            ns.abort(404, "Place not found")
        return place, 200


# ------------------------------------------------------------------
# Reviews sub-resource: /api/v1/places/<place_id>/reviews
# ------------------------------------------------------------------
@ns.route("/<string:place_id>/reviews")
class PlaceReviews(Resource):

    def get(self, place_id):
        """List all reviews for a place."""
        if not facade.repo.exists("Place", place_id):
            ns.abort(404, "Place not found")
        reviews = facade.list_reviews_for_place(place_id)
        return [r.to_dict() for r in reviews], 200
