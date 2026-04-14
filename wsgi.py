# wsgi.py
from gevent import monkey
monkey.patch_all()

from src import create_app

app = create_app()