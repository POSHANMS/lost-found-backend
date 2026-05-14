from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from flask_socketio import SocketIO
import os

db = SQLAlchemy()
ma = Marshmallow()
mail = Mail()
socketio = SocketIO()
limiter = Limiter(
    get_remote_address,
    storage_uri=os.getenv("REDIS_URL")
)