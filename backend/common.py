# common.py
import os, sqlite3
from datetime import datetime
from services.yandex_disk import (
    create_folder, upload_file, list_folder,
    download_link, delete_file
)

BASE_FOLDER = "disk:/04ЧР_ОП"
ADMIN_CODE = os.getenv("ADMIN_CODE", "Z")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "zoland")
DB_PATH = "ZAVot.db"

def db():
    return sqlite3.connect(DB_PATH)

def log_action(code, action):
    with db() as conn:
        conn.execute(
            "INSERT INTO logs (participant_code, action, created_at) VALUES (?, ?, ?)",
            (code, action, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()

def setup_app(app):
    app.secret_key = os.getenv("SECRET_KEY", "change_me")