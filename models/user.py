from extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "users"     # actual table name in PostgreSQL

    id = db.Column(db.Integer, primary_key=True)                        # unique ID for each user
    name = db.Column(db.String(100), nullable=False)                    # full name, cannot be empty
    email = db.Column(db.String(120), unique=True, nullable=False)      # email, must be unique
    password = db.Column(db.String(255), nullable=False)                # hashed password
    phone = db.Column(db.String(20), nullable=False)                    # phone number
    department = db.Column(db.String(100), nullable=False)              # e.g. CSE, ECE, MBA
    role = db.Column(db.String(20), default="student")                  # student or admin
    is_banned = db.Column(db.Boolean, default=False)                    # admin can ban users
    created_at = db.Column(db.DateTime, default=datetime.utcnow)        # when account was created

    # one user can have many items posted
    items = db.relationship("Item", backref="owner", lazy=True)

    # one user can have many claims made
    claims = db.relationship("Claim", backref="claimant", lazy=True)

    # one user can have many notifications
    notifications = db.relationship("Notification", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.email}>"   # how user object prints in terminal