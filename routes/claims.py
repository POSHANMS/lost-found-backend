from flask import Blueprint, request, jsonify
from extensions import db
from models.claim import Claim
from models.item import Item
from models.notification import Notification
from utils.auth_middleware import token_required

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

    if "message" not in data:
        return jsonify({"error": "Message is required"}), 400
    
    new_claim = Claim(
        message=data["message"],
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

    if response not in ["approved", "rejected"]:
        return jsonify({"error": "Status must be approved or rejected"}), 400
    
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

    return jsonify({"message": f"Claim {response} successfully"}), 200