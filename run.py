# run.py
import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logs_dir = os.path.join(BASE_DIR, "logs")
os.makedirs(logs_dir, exist_ok=True)

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)