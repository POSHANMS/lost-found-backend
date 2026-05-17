from flask import Blueprint, request, jsonify
from extensions import db
from models.claim import Claim
from models.item import Item
from models.notification import Notification
from utils.auth_middleware import token_required
from schemas.claim_schema import ClaimSchema, ClaimResponseSchema
from utils.email import send_claim_notification, send_claim_response

claims_bp = Blueprint("claims", __name__)

# ─── MAKE A CLAIM (protected) ──────────────────────────────────────────────

@claims_bp.route("/<int:item_id>", methods=["POST"])
@token_required
def make_claim(current_user_id, item_id):
    item = Item.query.get(item_id)

    if not item:
        return jsonify({"error": "Item not found"}), 404
    
    # user cannot claim their own item
    if item.user_id == current_user_id:
        return jsonify({"error": "You cannot claim your own item"}), 400
    
    # check if user already claimed this item
    existing_claim = Claim.query.filter_by(
        user_id=current_user_id,
        item_id=item_id
    ).first()

    if existing_claim:
        return jsonify({"error": "You already claimed this item"}), 409
    
    data = request.get_json()

    schema = ClaimSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    # verify the answer before creating claim
    answer = data.get("answer", "").strip().lower()
    correct_answer = (item.verification_answer or "").strip().lower()

    if answer not in correct_answer and correct_answer not in answer:
        return jsonify({"error": "Wrong answer to verification question"}), 400

    new_claim = Claim(
        message=data.get("message", ""),
        user_id=current_user_id,
        item_id=item_id
    )

    db.session.add(new_claim)

    # notify the item owner that someone claimed their item
    notification = Notification(
        message=f"Someone claimed your item: {item.title}",
        user_id=item.user_id
    )
    db.session.add(notification)
    db.session.commit()

    # emit real time notification via Socket.io
    from extensions import socketio
    socketio.emit('notification', {
        'message': f"Someone claimed your item: {item.title}"
    }, room=f"user_{item.user_id}")

    # send email to item owner
    try:
        send_claim_notification(
            to_email=item.owner.email,
            item_title=item.title,
            claimant_name=new_claim.claimant.name
        )
    except Exception:
        pass    # don't fail the request if email fails

    return jsonify({"message": "Claim submitted successfully"}), 201


# ─── GET CLAIMS FOR AN ITEM (protected - only item owner) ─────────────────

@claims_bp.route("/<int:item_id>", methods=["GET"])
@token_required
def get_claims(current_user_id, item_id):
    item = Item.query.get(item_id)

    if not item:
        return jsonify({"error": "Item not found"}), 404
    
    if item.user_id != current_user_id:
        return jsonify({"error": "Unauthorized"}), 403
    
    claims = Claim.query.filter_by(item_id=item_id).all()

    return jsonify({
        "claims": [
            {
                "id": claim.id,
                "message": claim.message,
                "status": claim.status,
                "created_at": claim.created_at.isoformat(),
                "claimant_name": claim.claimant.name,
                "claimant_email": claim.claimant.email
            }
            for claim in claims
        ]
    }), 200

# ─── APPROVE OR REJECT CLAIM (protected - only item owner) ────────────────

@claims_bp.route("/<int:claim_id>/respond", methods=["PUT"])
@token_required
def respond_to_claim(current_user_id, claim_id):
    claim = Claim.query.get(claim_id)

    if not claim:
        return jsonify({"error": "Claim not found"}), 404
    
    # only item owner can approve or reject
    if claim.item.user_id != current_user_id:
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json()
    response = data.get("status")

    schema = ClaimResponseSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    claim.status = response

    # if approved, mark item as resolved
    if response == "approved":
        claim.item.is_resolved = True

    # notify the claimant about the decision
    notification = Notification(
        message=f"Your claim for '{claim.item.title}' was {response}",
        user_id=claim.user_id
    )
    db.session.add(notification)
    db.session.commit()

    # emit real time notification via Socket.io
    from extensions import socketio
    socketio.emit('notification', {
        'message': f"Your claim for '{claim.item.title}' was {response}"
    }, room=f"user_{claim.user_id}")

    # send email to claimant
    try:
        send_claim_response(
            to_email=claim.claimant.email,
            item_title=claim.item.title,
            status=response
        )
    except Exception:
        pass    # don't fail the request if email fails

    return jsonify({"message": f"Claim {response} successfully"}), 200

# ─── GET MY CLAIMS (protected) ─────────────────────────────────────────────

@claims_bp.route("/mine", methods=["GET"])
@token_required
def get_my_claims(current_user_id):
    claims = Claim.query.filter_by(user_id=current_user_id).all()

    return jsonify({
        "claims": [
            {
                "id": claim.id,
                "item_id": claim.item_id,
                "item_title": claim.item.title if claim.item else "Unknown",
                "message": claim.message,
                "status": claim.status,
                "created_at": claim.created_at.isoformat(),
            }
            for claim in claims
        ]
    }), 200