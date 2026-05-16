from flask import Blueprint, request, jsonify
from extensions import db, limiter
from models.item import Item
from models.user import User
from utils.auth_middleware import token_required
from schemas.item_schema import ItemSchema
from utils.cache import cache_get, cache_set, cache_delete_pattern
from utils.cloudinary import upload_image

items_bp = Blueprint("items", __name__)

# ─── GET ALL ITEMS (public - no token needed) ──────────────────────────────

@items_bp.route("/", methods=["GET"])
def get_items():
    status = request.args.get("status")
    category = request.args.get("category")
    search = request.args.get("search")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    my_items = request.args.get("my")

    # if ?my=true, try to get current user from token
    current_user_id = None
    if my_items:
        import jwt, os
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        try:
            payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
            current_user_id = payload.get("user_id")
        except:
            pass

    cache_key = f"items:page:{page}:per:{per_page}:status:{status}:category:{category}:search:{search}:my:{my_items}:user:{current_user_id}"

    cached = cache_get(cache_key)
    if cached:
        return jsonify(cached), 200

    # filter by owner if ?my=true
    if my_items and current_user_id:
        query = Item.query.filter_by(user_id=current_user_id)
    else:
        query = Item.query.filter_by(is_resolved=False)

    if status:
        query = query.filter_by(status=status)
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Item.title.ilike(f"%{search}%"))

    items = query.order_by(Item.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    response_data = {
        "items": [
            {
                "id": item.id,
                "title": item.title,
                "description": item.description,
                "category": item.category,
                "status": item.status,
                "location": item.location,
                "latitude": item.latitude,
                "longitude": item.longitude,
                "image_url": item.image_url,
                "is_resolved": item.is_resolved,
                "created_at": item.created_at.isoformat(),
                "posted_by": item.owner.name
            }
            for item in items.items
        ],
        "total": items.total,
        "pages": items.pages,
        "current_page": items.page
    }

    cache_set(cache_key, response_data, expiry=300)
    return jsonify(response_data), 200

# ─── GET SINGLE ITEM ───────────────────────────────────────────────────────

@items_bp.route("/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    
    return jsonify({
        "id": item.id,
        "title": item.title,
        "description": item.description,
        "category": item.category,
        "status": item.status,
        "location": item.location,
        "latitude": item.latitude,
        "longitude": item.longitude,
        "image_url": item.image_url,
        "is_resolved": item.is_resolved,
        "created_at": item.created_at.isoformat(),
        "posted_by": item.owner.name,
        "user_id": item.user_id
    }), 200

# ─── POST NEW ITEM (protected) ─────────────────────────────────────────────

@items_bp.route("/", methods=["POST"])
@token_required
def create_item(current_user_id):
    # handle both JSON and form data (because image upload uses multipart)
    title = request.form.get("title")
    description = request.form.get("description")
    category = request.form.get("category")
    status = request.form.get("status")
    location = request.form.get("location")
    latitude = request.form.get("latitude")
    longitude = request.form.get("longitude")
    image_url = request.form.get("image_url")
    image_public_id = request.form.get("image_public_id")

    schema = ItemSchema()
    errors = schema.validate({
        "title": title,
        "description": description,
        "category": category,
        "status": status,
        "location": location
    })
    if errors:
        return jsonify({"errors": errors}), 400
    
    # get image_url sent from frontend (already uploaded to Cloudinary)
    image_url = request.form.get("image_url") or None

    new_item = Item(
        title=title,
        description=description,
        category=category,
        status=status,
        location=location,
        latitude=float(latitude) if latitude else None,
        longitude=float(longitude) if longitude else None,
        image_url=image_url,
        user_id=current_user_id
    )

    db.session.add(new_item)
    db.session.commit()

    # clear items cache so next request gets fresh data
    cache_delete_pattern("items:*")

    return jsonify({
        "message": "Item posted successfully",
        "item": {
            "id": new_item.id,
            "title": new_item.title,
            "status": new_item.status
        }
    }), 201

# ─── UPDATE ITEM (protected - only owner) ─────────────────────────────────

@items_bp.route("/<int:item_id>", methods=["PUT"])
@token_required
def update_item(current_user_id, item_id):
    item = Item.query.get(item_id)


    if not item:
        return jsonify({"error": "Item not found"}), 404
    
    # only the owner can update their item
    if item.user_id != current_user_id:
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json()

    item.title = data.get("title", item.title)
    item.description = data.get("description", item.description)
    item.category = data.get("category", item.category)
    item.location = data.get("location", item.location)
    item.is_resolved = data.get("is_resolved", item.is_resolved)

    db.session.commit()

    return jsonify({"message": "Item updated successfully"}), 200


# ─── DELETE ITEM (protected - only owner) ─────────────────────────────────

@items_bp.route("/<int:item_id>", methods=["DELETE"])
@token_required
def delete_item(current_user_id, item_id):
    item = Item.query.get(item_id)

    if not item:
        return jsonify({"error": "Item not found"}), 404
    
    if item.user_id != current_user_id:
        return jsonify({"error": "Unauthorized"}), 403
    
    db.session.delete(item)
    db.session.commit()

    return jsonify({"message": "Item deleted successfully"}), 200