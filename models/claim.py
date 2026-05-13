from extensions import db
from datetime import datetime

class Claim(db.Model):
    __tablename__ = "claims"

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)                    # why they think it's theirs
    status = db.Column(db.String(20), default="pending")            # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)    # when claim was made

    # which user made this claim
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # which item is being claimed
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)

    def __repr__(self):
        return f"<Claim by user {self.user_id} on item {self.item_id}>"