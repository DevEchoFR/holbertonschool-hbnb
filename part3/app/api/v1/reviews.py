"""Review endpoints – /api/v1/reviews/"""
from flask_restx import Namespace, Resource, fields
from app.services.facade import facade

ns = Namespace("reviews", description="Review operations")

review_input_model = ns.model("ReviewInput", {
    "text":     fields.String(required=True),
    "rating":   fields.Integer(required=True),
    "user_id":  fields.String(required=True),
    "place_id": fields.String(required=True),
})

review_update_model = ns.model("ReviewUpdate", {
    "text":   fields.String,
    "rating": fields.Integer,
})

review_output_model = ns.model("ReviewOutput", {
    "id":         fields.String,
    "text":       fields.String,
    "rating":     fields.Integer,
    "user_id":    fields.String,
    "place_id":   fields.String,
    "created_at": fields.String,
    "updated_at": fields.String,
})


# ------------------------------------------------------------------
# Collection: /api/v1/reviews/
# ------------------------------------------------------------------
@ns.route("/")
class ReviewList(Resource):

    @ns.expect(review_input_model, validate=True)
    @ns.response(201, "Created")
    @ns.response(400, "Bad Request")
    def post(self):
        """Create a new review."""
        data = ns.payload
        try:
            review = facade.create_review(data)
        except (ValueError, KeyError) as e:
            ns.abort(400, str(e))
        return review.to_dict(), 201


# ------------------------------------------------------------------
# Item: /api/v1/reviews/<id>
# ------------------------------------------------------------------
@ns.route("/<string:review_id>")
class ReviewDetail(Resource):

    @ns.marshal_with(review_output_model)
    @ns.response(404, "Not Found")
    def get(self, review_id):
        """Get a single review."""
        review = facade.get_review(review_id)
        if review is None:
            ns.abort(404, "Review not found")
        return review.to_dict(), 200

    @ns.expect(review_update_model, validate=True)
    @ns.response(200, "Updated")
    @ns.response(400, "Bad Request")
    @ns.response(404, "Not Found")
    def put(self, review_id):
        """Update a review."""
        data = ns.payload
        try:
            review = facade.update_review(review_id, data)
        except ValueError as e:
            ns.abort(400, str(e))
        if review is None:
            ns.abort(404, "Review not found")
        return review.to_dict(), 200

    @ns.response(200, "Deleted")
    @ns.response(404, "Not Found")
    def delete(self, review_id):
        """Delete a review."""
        deleted = facade.delete_review(review_id)
        if not deleted:
            ns.abort(404, "Review not found")
        return {"message": "Review deleted"}, 200
