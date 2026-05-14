from flask import Flask
from extensions import db, ma, mail, socketio, limiter
from dotenv import load_dotenv
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import os

load_dotenv()

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "https://your-vercel-app.vercel.app"])

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["RATELIMIT_STORAGE_URI"] = os.getenv("REDIS_URL")

db.init_app(app)
ma.init_app(app)
mail.init_app(app)
socketio.init_app(app, cors_allowed_origins="*")
limiter.init_app(app)

from models.user import User
from models.item import Item
from models.claim import Claim
from models.notification import Notification

from routes.auth import auth_bp
app.register_blueprint(auth_bp, url_prefix="/api/auth")

from routes.items import items_bp
app.register_blueprint(items_bp, url_prefix="/api/items")

from routes.claims import claims_bp
app.register_blueprint(claims_bp, url_prefix="/api/claims")

from routes.admin import admin_bp
app.register_blueprint(admin_bp, url_prefix="/api/admin")

@app.route("/")
def index():
    return {"message": "FindIt API is running!"}

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)