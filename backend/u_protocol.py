# u_protocol.py

from flask import Blueprint
from common import db

bp = Blueprint("u_protocol", __name__)

@bp.get("/api/protocols")
def protocols_public():
    with db() as conn:
        rows = conn.execute("SELECT * FROM protocols").fetchall()
        total = conn.execute("SELECT COUNT(*) FROM users WHERE role='participant'").fetchone()[0]
    items = []
    with db() as conn:
        for r in rows:
            voted = conn.execute("SELECT COUNT(DISTINCT user_code) FROM votes WHERE protocol_id=?", (r[0],)).fetchone()[0]
            items.append(dict(id=r[0], num=r[1], start=r[3], end=r[4], status=r[5],
                              vote_type=r[6], voted=voted, total=total))
    return {"items": items}

@bp.get("/api/protocols/<int:pid>/info")
def protocol_info(pid):
    with db() as conn:
        row = conn.execute("SELECT file_name, folder FROM protocols WHERE id=?", (pid,)).fetchone()
    return {"file": row[0], "folder": row[1]}

@bp.get("/api/protocols/<int:pid>/questions")
def questions_list(pid):
    with db() as conn:
        rows = conn.execute("SELECT * FROM questions WHERE protocol_id=? ORDER BY qnum", (pid,)).fetchall()
    return {"items":[dict(id=r[0], qnum=r[2], opt1=r[3], opt2=r[4], opt3=r[5]) for r in rows]}