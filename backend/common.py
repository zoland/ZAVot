# common.py
import os, sys, sqlite3
from datetime import datetime

# Подключаем конфиг
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'config'))
from env import get_config

cfg = get_config()

DB_PATH = cfg["DB_PATH"]
ADMIN_CODE = os.getenv("ADMIN_CODE", "Z")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "zoland")

def db():
    return sqlite3.connect(DB_PATH)

def log_action(code, action):
    now = datetime.now()
    with db() as conn:
        conn.execute(
            "INSERT INTO logs (u_code, action, l_date, l_time) VALUES (?, ?, ?, ?)",
            (code, action, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"))
        )
        conn.commit()

def setup_app(app):
    app.secret_key = cfg.get("SECRET_KEY", "change_me")