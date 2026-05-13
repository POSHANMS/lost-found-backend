from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os
from models.user import User
from models.item import Item
from models.claim import Claim
from models.notification import Notification

# Load all variables from .env file into environment
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Load configuration from environment variables
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

# Initialize all extensions
db = SQLAlchemy(app)    # handles database
ma = Marshmallow(app)   # handles input validation
mail = Mail(app)        # handles emails
socketio = SocketIO(app, cors_allowed_origins="*")  # handles real-time

# Initialize rate limiter (limits requests to prevent abuse)
limiter = Limiter(
    get_remote_address,     # identifies user by their IP address
    app=app,
    default_limits=["200 per day", "50 per hour"]   # global default limits
)

# Register route blueprints (we will create these files next)
# from routes.auth import auth_bp
# from routes.items import items_bp
# from routes.claims import claims_bp
# from routes.admin import admin_bp
# app.register_blueprint(auth_bp, url_prefix="/api/auth")
# app.register_blueprint(items_bp, url_prefix="/api/items")
# app.register_blueprint(claims_bp, url_prefix="/api/claims")
# app.register_blueprint(admin_bp, url_prefix="/api/admin")

# Test route to confirm server is running
@app.route("/")
def index():
    return {"message": "FindIt API is running!"}

# Start the server
if __name__ == "__main__":
    with app.app_context():
        db.create_all()                # creates all tables in PostgreSQL if they don't exist
    socketio.run(app, debug=True)