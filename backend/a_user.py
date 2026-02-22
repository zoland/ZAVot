# a_user.py

from flask import Blueprint, request, session
import unicodedata
from common import db, log_action

bp = Blueprint("a_user", __name__)

@bp.get("/api/admin/users")
def users_list():
    if session.get("role") != "admin": return {"error":"unauthorized"}, 401
    with db() as conn:
        rows = conn.execute("SELECT * FROM users").fetchall()
    return {"items":[dict(id=r[0], code=r[1], role=r[2], password=r[3]) for r in rows]}

@bp.post("/api/admin/users")
def users_add():
    if session.get("role") != "admin": return {"error":"unauthorized"}, 401
    d = request.json
    code = unicodedata.normalize("NFC", d["code"])
    password = unicodedata.normalize("NFC", d["password"])
    with db() as conn:
        conn.execute("INSERT INTO users (code,role,password) VALUES (?,?,?)",
                     (code, d["role"], password))
        conn.commit()
    log_action("ADMIN", f"user_add {d['code']}")
    return {"ok": True}

@bp.delete("/api/admin/users/<int:uid>")
def users_delete(uid):
    if session.get("role") != "admin": return {"error":"unauthorized"}, 401
    with db() as conn:
        conn.execute("DELETE FROM users WHERE id=?", (uid,))
        conn.commit()
    log_action("ADMIN", f"user_delete {uid}")
    return {"ok": True}