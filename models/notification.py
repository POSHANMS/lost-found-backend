from app import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(300), nullable=False)             # e.g. "Your claim was approved"
    is_read = db.Column(db.Boolean, default=False)                  # True when user has seen it
    created_at = db.Column(db.DateTime, default=datetime.utcnow)    # when notification was created

    # which user receives this notification
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<Notification for user {self.user_id} - read:{self.is_read}>"