# common.py
# common.py
import os, sqlite3
from datetime import datetime

BASE_FOLDER = "disk:/04ЧР_ОП"
ADMIN_CODE = os.getenv("ADMIN_CODE", "Z")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "zoland")

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'ZAVot.db')

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
    app.secret_key = os.getenv("SECRET_KEY", "change_me")