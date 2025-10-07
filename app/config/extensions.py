# app/config/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
ma = Marshmallow()
cors = CORS()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per hour"],
    storage_uri="memory://"  # Prod: "redis://localhost:6379"
)