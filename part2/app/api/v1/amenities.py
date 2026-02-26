"""Amenity endpoints – /api/v1/amenities/"""
from flask_restx import Namespace, Resource, fields
from app.services.facade import facade

ns = Namespace("amenities", description="Amenity operations")

amenity_input_model = ns.model("AmenityInput", {
    "name": fields.String(required=True),
})

amenity_output_model = ns.model("AmenityOutput", {
    "id":         fields.String,
    "name":       fields.String,
    "created_at": fields.String,
    "updated_at": fields.String,
})


@ns.route("/")
class AmenityList(Resource):

    @ns.marshal_list_with(amenity_output_model)
    def get(self):
        """List all amenities."""
        return [a.to_dict() for a in facade.list_amenities()], 200

    @ns.expect(amenity_input_model, validate=True)
    @ns.response(201, "Created")
    @ns.response(400, "Bad Request")
    def post(self):
        """Create a new amenity."""
        data = ns.payload
        try:
            amenity = facade.create_amenity(data)
        except (ValueError, KeyError) as e:
            ns.abort(400, str(e))
        return amenity.to_dict(), 201


@ns.route("/<string:amenity_id>")
class AmenityDetail(Resource):

    @ns.marshal_with(amenity_output_model)
    @ns.response(404, "Not Found")
    def get(self, amenity_id):
        """Get a single amenity."""
        amenity = facade.get_amenity(amenity_id)
        if amenity is None:
            ns.abort(404, "Amenity not found")
        return amenity.to_dict(), 200

    @ns.expect(amenity_input_model, validate=True)
    @ns.response(200, "Updated")
    @ns.response(400, "Bad Request")
    @ns.response(404, "Not Found")
    def put(self, amenity_id):
        """Update an amenity."""
        data = ns.payload
        try:
            amenity = facade.update_amenity(amenity_id, data)
        except ValueError as e:
            ns.abort(400, str(e))
        if amenity is None:
            ns.abort(404, "Amenity not found")
        return amenity.to_dict(), 200
