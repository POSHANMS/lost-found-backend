from flask import Blueprint, request, jsonify
from extensions import db
from models.notification import Notification
from utils.auth_middleware import token_required

notifications_bp = Blueprint("notifications", __name__)

# ─── GET ALL NOTIFICATIONS (protected) ─────────────────────────────────────

@notifications_bp.route("/", methods=["GET"])
@token_required
def get_notifications(current_user_id):
    notifications = Notification.query.filter_by(
        user_id=current_user_id
    ).order_by(Notification.created_at.desc()).all()

    return jsonify({
        "notifications": [
            {
                "id": n.id,
                "message": n.message,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat(),
            }
            for n in notifications
        ]
    }), 200


# ─── MARK NOTIFICATION AS READ ──────────────────────────────────────────────

@notifications_bp.route("/read", methods=["PUT"])
@token_required
def mark_read(current_user_id):
    data = request.get_json()
    notification_id = data.get("notification_id")

    if notification_id:
        # mark specific notification as read
        notif = Notification.query.filter_by(
            id=notification_id,
            user_id=current_user_id
        ).first()
        if notif:
            notif.is_read = True
    else:
        # mark ALL notifications as read
        Notification.query.filter_by(
            user_id=current_user_id,
            is_read=False
        ).update({"is_read": True})

    db.session.commit()
    return jsonify({"message": "Marked as read"}), 200