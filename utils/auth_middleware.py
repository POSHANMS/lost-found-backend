from flask import request, jsonify
from functools import wraps
import jwt
import os

def token_required(f):
    # @wraps preserves the original function name
    # without it, all protected routes would have the same name "decorated"
    # which causes the Flask endpoint conflict error we just fixed
    @wraps(f)
    def decorated(**kwargs):
        # kwargs contains URL parameters like item_id, claim_id
        # example: if route is /<int:item_id>, kwargs = {"item_id": 1}
        token = None

        # check if Authorization header exists in the request
        # React will send: Authorization: Bearer eyJhbGci...
        if "Authorization" in request.headers:
            parts = request.headers["Authorization"].split(" ")
            # split "Bearer eyJhbGci..." into ["Bearer", "eyJhbGci..."]
            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]   # take only the token part

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            # decode the token using our secret key
            # this also checks if token is expired automatically
            payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
            current_user_id = payload["user_id"]   # extract user_id from token
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        # pass current_user_id as first argument to the actual route function
        # kwargs passes along item_id, claim_id etc from the URL
        return f(current_user_id, **kwargs)

    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(**kwargs):
        from models.user import User   # imported here to avoid circular import

        token = None
        if "Authorization" in request.headers:
            parts = request.headers["Authorization"].split(" ")
            if len(parts) == 2:
                token = parts[1]

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
            current_user_id = payload["user_id"]
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        # extra check — verify user exists AND is actually an admin
        # token_required only checks if token is valid
        # admin_required also checks if the user's role is "admin"
        user = User.query.get(current_user_id)
        if not user or user.role != "admin":
            return jsonify({"error": "Admin access required"}), 403

        return f(current_user_id, **kwargs)

    return decorated