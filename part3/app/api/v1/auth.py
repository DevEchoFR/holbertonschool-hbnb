"""Authentication endpoints – /api/v1/auth/"""
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from app.services.facade import facade

ns = Namespace("auth", description="Authentication operations")

# Request / Response models
login_model = ns.model("Login", {
    "email": fields.String(required=True, description="User email"),
    "password": fields.String(required=True, description="User password"),
})

token_response_model = ns.model("TokenResponse", {
    "access_token": fields.String(description="JWT access token"),
})


def require_admin_claim(ns_obj):
    """Abort with 403 when JWT does not include admin privileges."""
    claims = get_jwt()
    if not claims.get("is_admin", False):
        ns_obj.abort(403, "Admin privileges required")


# ------------------------------------------------------------------
# Login Endpoint: POST /api/v1/auth/login
# ------------------------------------------------------------------
@ns.route("/login")
class Login(Resource):

    @ns.expect(login_model, validate=True)
    @ns.response(200, "Login successful", token_response_model)
    @ns.response(401, "Invalid credentials")
    def post(self):
        """Authenticate user and return a JWT token."""
        credentials = ns.payload
        
        # Step 1: Retrieve the user by email
        user = facade.get_user_by_email(credentials["email"])
        
        # Step 2: Check if user exists and password is correct
        if not user or not user.verify_password(credentials["password"]):
            return {"error": "Invalid credentials"}, 401
        
        # Step 3: Create JWT token with user id and is_admin flag
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"is_admin": user.is_admin}
        )
        
        # Step 4: Return the token
        return {"access_token": access_token}, 200


# ------------------------------------------------------------------
# Protected Endpoint: GET /api/v1/auth/protected
# (For testing purposes)
# ------------------------------------------------------------------
@ns.route("/protected")
class ProtectedResource(Resource):

    @jwt_required()
    @ns.response(200, "Success")
    @ns.response(401, "Unauthorized")
    def get(self):
        """A protected endpoint that requires a valid JWT token."""
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get("is_admin", False)
        
        return {
            "message": f"Hello, user {current_user_id}",
            "is_admin": is_admin
        }, 200
