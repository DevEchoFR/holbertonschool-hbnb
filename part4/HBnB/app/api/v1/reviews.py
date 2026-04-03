"""Review endpoints – /api/v1/reviews/"""
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
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
    @ns.response(401, "Unauthorized")
    @ns.response(403, "Forbidden")
    @jwt_required()
    def post(self):
        """Create a new review."""
        data = ns.payload
        current_user_id = get_jwt_identity()
        claims = get_jwt()

        if not claims.get("is_admin", False):
            data["user_id"] = current_user_id
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
    @ns.response(401, "Unauthorized")
    @ns.response(403, "Forbidden")
    @jwt_required()
    def put(self, review_id):
        """Update a review."""
        data = ns.payload
        current_user_id = get_jwt_identity()
        claims = get_jwt()

        review_model = facade.get_review_model(review_id)
        if review_model is None:
            ns.abort(404, "Review not found")
        if not claims.get("is_admin", False) and review_model.user_id != current_user_id:
            ns.abort(403, "You can only update your own reviews")
        try:
            review = facade.update_review(review_id, data)
        except ValueError as e:
            ns.abort(400, str(e))
        if review is None:
            ns.abort(404, "Review not found")
        return review.to_dict(), 200

    @ns.response(200, "Deleted")
    @ns.response(404, "Not Found")
    @ns.response(401, "Unauthorized")
    @ns.response(403, "Forbidden")
    @jwt_required()
    def delete(self, review_id):
        """Delete a review."""
        current_user_id = get_jwt_identity()
        claims = get_jwt()

        review_model = facade.get_review_model(review_id)
        if review_model is None:
            ns.abort(404, "Review not found")
        if not claims.get("is_admin", False) and review_model.user_id != current_user_id:
            ns.abort(403, "You can only delete your own reviews")
        deleted = facade.delete_review(review_id)
        if not deleted:
            ns.abort(404, "Review not found")
        return {"message": "Review deleted"}, 200
