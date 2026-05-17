from flask import Blueprint, request, jsonify
from extensions import db
from models.user import User
from models.item import Item
from models.claim import Claim
from utils.auth_middleware import admin_required
from utils.cache import cache_delete_pattern

admin_bp = Blueprint("admin", __name__)

# ─── GET ALL USERS (admin only) ────────────────────────────────────────────

@admin_bp.route("/users", methods=["GET"])
@admin_required
def admin_get_all_users(current_user_id):
    users = User.query.all()

    return jsonify({
        "users": [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "department": user.department,
                "role": user.role,
                "is_banned": user.is_banned,
                "created_at": user.created_at.isoformat()
            }
            for user in users
        ]
    }), 200

# ─── BAN OR UNBAN USER (admin only) ───────────────────────────────────────

@admin_bp.route("/users/<int:user_id>/ban", methods=["PUT"])
@admin_required
def admin_ban_user(current_user_id, user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # toggle ban status
    user.is_banned = not user.is_banned
    db.session.commit()

    status = "banned" if user.is_banned else "unbanned"
    return jsonify({"message": f"User {status} successfully"}), 200

# ─── GET ALL ITEMS (admin only) ────────────────────────────────────────────

@admin_bp.route("/items", methods=["GET"])
@admin_required
def admin_get_all_items(current_user_id):
    items = Item.query.order_by(Item.created_at.desc()).all()

    return jsonify({
        "items": [
            {
                "id": item.id,
                "title": item.title,
                "status": item.status,
                "is_resolved": item.is_resolved,
                "posted_by": item.owner.name,
                "created_at": item.created_at.isoformat()
            }
            for item in items
        ]
    }), 200

# ─── DELETE ANY ITEM (admin only) ─────────────────────────────────────────

@admin_bp.route("/items/<int:item_id>", methods=["DELETE"])
@admin_required
def admin_delete_item(current_user_id, item_id):
    item = Item.query.get(item_id)

    if not item:
        return jsonify({"error": "Item not found"}), 404
    
    db.session.delete(item)
    db.session.commit()

    cache_delete_pattern("items:*")

    return jsonify({"message": "Item deleted successfully"}), 200

# ─── GET DASHBOARD STATS (admin only) ─────────────────────────────────────

@admin_bp.route("/stats", methods=["GET"])
@admin_required
def admin_get_stats(current_user_id):
    total_users = User.query.count()
    total_items = Item.query.count()
    lost_items = Item.query.filter_by(status="lost").count()
    found_items = Item.query.filter_by(status="found").count()
    resolved_items = Item.query.filter_by(is_resolved=True).count()
    total_claims = Claim.query.count()

    return jsonify({
        "total_users": total_users,
        "total_items": total_items,
        "lost_items": lost_items,
        "found_items": found_items,
        "resolved_items": resolved_items,
        "total_claims": total_claims
    }), 200