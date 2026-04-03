"""Admin endpoints – /api/v1/admin/"""
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required

from app.api.v1.auth import require_admin_claim
from app.services.facade import facade


ns = Namespace("admin", description="Administrator operations")


user_role_update_model = ns.model("UserRoleUpdate", {
    "is_admin": fields.Boolean(required=True, description="Grant or revoke admin role"),
})


user_output_model = ns.model("AdminUserOutput", {
    "id": fields.String,
    "first_name": fields.String,
    "last_name": fields.String,
    "email": fields.String,
    "is_admin": fields.Boolean,
    "created_at": fields.String,
    "updated_at": fields.String,
})


@ns.route("/users")
class AdminUsers(Resource):

    @jwt_required()
    @ns.response(200, "Success")
    @ns.response(401, "Unauthorized")
    @ns.response(403, "Forbidden")
    @ns.marshal_list_with(user_output_model)
    def get(self):
        """List all users (admin only)."""
        require_admin_claim(ns)
        return [u.to_dict() for u in facade.list_users()], 200


@ns.route("/users/<string:user_id>/role")
class AdminUserRole(Resource):

    @jwt_required()
    @ns.expect(user_role_update_model, validate=True)
    @ns.response(200, "Updated")
    @ns.response(400, "Bad Request")
    @ns.response(401, "Unauthorized")
    @ns.response(403, "Forbidden")
    @ns.response(404, "Not Found")
    @ns.marshal_with(user_output_model)
    def put(self, user_id):
        """Set or unset a user's admin role (admin only)."""
        require_admin_claim(ns)
        user = facade.update_user(user_id, {"is_admin": bool(ns.payload["is_admin"])})
        if user is None:
            ns.abort(404, "User not found")
        return user.to_dict(), 200
