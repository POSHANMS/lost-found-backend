from flask import Blueprint, request, jsonify
from extensions import db, limiter
from models.user import User
import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from schemas.user_schema import RegisterSchema, LoginSchema


auth_bp = Blueprint("auth", __name__)

# ─── HELPER: generate tokens ───────────────────────────────────────────────

def generate_tokens(user_id):
    access_token = jwt.encode(
        {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(minutes=30)        # expires in 30 mins
        },
        os.getenv("JWT_SECRET"),
        algorithm="HS256"
    )
    refresh_token = jwt.encode(
        {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(days=30)       # expires in 30 days
        },
        os.getenv("JWT_REFRESH_SECRET"),
        algorithm="HS256"
    )
    return access_token, refresh_token

# ─── REGISTER ──────────────────────────────────────────────────────────────

@auth_bp.route("/register", methods=["POST"])
@limiter.limit("5 per minute")                      # max 5 register attempts per minute
def register():
    data = request.get_json()                       # get JSON body from request

    # validate input using Marshmallow schema
    schema = RegisterSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    # check if email already exists
    existing_user = User.query.filter_by(email=data["email"]).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 409
    
    # hash the password before saving
    hashed_password = bcrypt.hashpw(
        data["password"].encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    # create new user
    new_user = User(
        name=data["name"],
        email=data["email"],
        password=hashed_password,
        phone=data["phone"],
        department=data["department"]
    )

    db.session.add(new_user)
    db.session.commit()

    access_token, refresh_token = generate_tokens(new_user.id)

    return jsonify({
        "message": "Registration successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role
        }
    }), 201

# ─── LOGIN ─────────────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")                 # max 10 login attempts per minute

def login():
    data = request.get_json()

    schema = LoginSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    # find user by email
    user = User.query.filter_by(email=data["email"]).first()
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401
    
    # check if user is banned
    if user.is_banned:
        return jsonify({"error": "Your account has been banned"}), 403
    
    # verify password
    if not bcrypt.checkpw(data["password"].encode("utf-8"), user.password.encode("utf-8")):
        return jsonify({"error": "Invalid email or password"}), 401
    
    access_token, refresh_token = generate_tokens(user.id)

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }), 200

# ─── REFRESH TOKEN ─────────────────────────────────────────────────────────

@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    data = request.get_json()

    if "refresh_token" not in data:
        return jsonify({"error": "Refresh token is required"}), 400
    
    try:
        payload = jwt.decode(
            data["refresh_token"],
            os.getenv("JWT_REFRESH_SECRET"),
            algorithms=["HS256"]
        )
        user_id = payload["user_id"]
        access_token, refresh_token = generate_tokens(user_id)

        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 200
    
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Refresh token expired, please login again"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid refresh token"}), 401