# a_log.py

from flask import Blueprint, session
from common import db

bp = Blueprint("a_log", __name__)

@bp.get("/api/admin/logs")
def logs_list():
    if session.get("role") != "admin": return {"error":"unauthorized"}, 401
    with db() as conn:
        rows = conn.execute("SELECT * FROM logs ORDER BY created_at DESC").fetchall()
    return {"items":[dict(id=r[0], code=r[1], action=r[2], created_at=r[3]) for r in rows]}

@bp.delete("/api/admin/logs/<int:lid>")
def logs_delete(lid):
    if session.get("role") != "admin": return {"error":"unauthorized"}, 401
    with db() as conn:
        conn.execute("DELETE FROM logs WHERE id=?", (lid,))
        conn.commit()
    return {"ok": True}