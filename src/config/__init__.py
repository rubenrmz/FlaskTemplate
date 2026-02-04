# src/config/__init__.py
from .settings import Config
from .cors import get_cors_config
from .extensions import cors, limiter