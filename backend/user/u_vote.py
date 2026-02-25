# u_vote.py

from flask import Blueprint, request, session
from common import db, log_action

bp = Blueprint("u_vote", __name__)

@bp.post("/api/vote")
def vote():
    role = session.get("role")
    code = session.get("code")
    if role not in ("участник",): return {"error":"unauthorized"}, 401

    data = request.json
    pid = data["protocol_id"]
    votes = data["votes"]

    with db() as conn:
        conn.execute("DELETE FROM votes WHERE protocol_id=? AND user_code=?", (pid, code))
        for v in votes:
            conn.execute("INSERT INTO votes (protocol_id, user_code, question_id, vote) VALUES (?,?,?,?)",
                         (pid, code, v["question_id"], v["vote"]))
        conn.commit()

    log_action(code, f"vote protocol {pid}")
    return {"ok": True}