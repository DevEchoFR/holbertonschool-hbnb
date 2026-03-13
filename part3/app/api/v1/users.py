"""User endpoints – /api/v1/users/"""
from flask_restx import Namespace, Resource, fields
from app.services.facade import facade

ns = Namespace("users", description="User operations")

# ------------------------------------------------------------------
# Request / Response models
# ------------------------------------------------------------------
user_input_model = ns.model("UserInput", {
    "first_name": fields.String(required=True),
    "last_name":  fields.String(required=True),
    "email":      fields.String(required=True),
    "password":   fields.String(required=True),
})

user_update_model = ns.model("UserUpdate", {
    "first_name": fields.String,
    "last_name":  fields.String,
    "email":      fields.String,
    "password":   fields.String,
})

user_output_model = ns.model("UserOutput", {
    "id":         fields.String,
    "first_name": fields.String,
    "last_name":  fields.String,
    "email":      fields.String,
    "created_at": fields.String,
    "updated_at": fields.String,
})


# ------------------------------------------------------------------
# Collection: /api/v1/users/
# ------------------------------------------------------------------
@ns.route("/")
class UserList(Resource):

    @ns.marshal_list_with(user_output_model)
    def get(self):
        """List all users."""
        return [u.to_dict() for u in facade.list_users()], 200

    @ns.expect(user_input_model, validate=True)
    @ns.response(201, "Created")
    @ns.response(400, "Bad Request")
    def post(self):
        """Create a new user."""
        data = ns.payload
        try:
            user = facade.create_user(data)
        except (ValueError, KeyError) as e:
            ns.abort(400, str(e))
        return user.to_dict(), 201


# ------------------------------------------------------------------
# Item: /api/v1/users/<id>
# ------------------------------------------------------------------
@ns.route("/<string:user_id>")
class UserDetail(Resource):

    @ns.marshal_with(user_output_model)
    @ns.response(404, "Not Found")
    def get(self, user_id):
        """Get a single user."""
        user = facade.get_user(user_id)
        if user is None:
            ns.abort(404, "User not found")
        return user.to_dict(), 200

    @ns.expect(user_update_model, validate=True)
    @ns.response(200, "Updated")
    @ns.response(400, "Bad Request")
    @ns.response(404, "Not Found")
    def put(self, user_id):
        """Update a user."""
        data = ns.payload
        try:
            user = facade.update_user(user_id, data)
        except ValueError as e:
            ns.abort(400, str(e))
        if user is None:
            ns.abort(404, "User not found")
        return user.to_dict(), 200
