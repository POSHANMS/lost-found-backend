from flask import request, jsonify
from functools import wraps
import jwt
import os

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # check if Authorization header exists
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            # format is "Bearer <token>" — we split and take the token part
            parts = auth_header.split(" ")
            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]

        if not token:
            return jsonify({"error": "Token is missing"}), 401
        
        try:
            # decode the token using our secret key
            payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
            current_user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        # pass the user_id to the actual route function
        return f(current_user_id, *args, **kwargs)
    
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        from models.user import User

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
            
            # check if user is actually an admin
            user = User.query.get(current_user_id)
            if not user or user.role != "admin":
                return jsonify({"error": "Admin access required"}), 403
            
            return f(current_user_id, *args, **kwargs)
        
        return decorated