# login.py

from flask import Blueprint, request, session
import unicodedata
from common import db, log_action, ADMIN_CODE, ADMIN_PASSWORD

bp = Blueprint("login", __name__)

@bp.post("/api/login")
def login():
    data = request.json
    code = unicodedata.normalize("NFC", data.get("code",""))
    password = unicodedata.normalize("NFC", data.get("password",""))

    if code == ADMIN_CODE and password == ADMIN_PASSWORD:
        session["role"] = "admin"
        session["code"] = code
        log_action(code, "admin_login")
        return {"role":"admin"}

    with db() as conn:
        row = conn.execute(
            "SELECT role FROM users WHERE code=? AND password=?",
            (code, password)
        ).fetchone()

    if row:
        session["role"] = row[0]
        session["code"] = code
        log_action(code, "login")
        return {"role": row[0]}

    return {"error": "invalid"}, 401

@bp.post("/api/logout")
def logout():
    session.clear()
    return {"ok": True}