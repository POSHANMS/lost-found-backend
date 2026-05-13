from flask import Flask
from extensions import db, ma, mail, socketio, limiter
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

db.init_app(app)
ma.init_app(app)
mail.init_app(app)
socketio.init_app(app, cors_allowed_origins="*")
limiter.init_app(app)

from models.user import User
from models.item import Item
from models.claim import Claim
from models.notification import Notification

@app.route("/")
def index():
    return {"message": "FindIt API is running!"}

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)