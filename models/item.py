from extensions import db
from datetime import datetime

class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)               # e.g. "Black Wallet"
    description = db.Column(db.Text, nullable=False)                # detailed description
    category = db.Column(db.String(50), nullable=False)             # Electronics, Documents, etc.
    status = db.Column(db.String(10), nullable=False)               # "lost" or "found"
    location = db.Column(db.String(200), nullable=False)            # where it was lost/found
    latitude = db.Column(db.Float, nullable=True)                   # for map pin
    longitude = db.Column(db.Float, nullable=True)                  # for map pin
    image_url = db.Column(db.String(500), nullable=True)            # Cloudinary image URL
    is_resolved = db.Column(db.Boolean, default=False)            # True when item is returned
    verification_question = db.Column(db.String(300), nullable=True)   # question to verify ownership
    verification_answer = db.Column(db.String(300), nullable=True)      # answer (never shown publicly)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)    # when item was posted

    # which user posted this item
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # one item can have many claims
    claims = db.relationship("Claim", backref="item", lazy=True)

    def __repr__(self):
        return f"<Item {self.title} - {self.status}>"