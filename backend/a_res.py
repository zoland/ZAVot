# a_res.py

from flask import Blueprint, request, session
import io, csv
from common import db, log_action

bp = Blueprint("a_res", __name__)

# --- Просмотр результатов (полная таблица) ---
@bp.get("/api/admin/protocols/<int:pid>/results")
def admin_results(pid):
    if session.get("role") != "admin":
        return {"error": "unauthorized"}, 401

    with db() as conn:
        proto = conn.execute("SELECT vote_type FROM protocols WHERE id=?", (pid,)).fetchone()
        vote_type = proto[0]
        questions = conn.execute(
            "SELECT id,qnum,opt1,opt2,opt3 FROM questions WHERE protocol_id=? ORDER BY qnum",
            (pid,)
        ).fetchall()

        totals = []
        for q in questions:
            cnt1 = conn.execute("SELECT COUNT(*) FROM votes WHERE protocol_id=? AND question_id=? AND vote=?",
                                (pid, q[0], q[2])).fetchone()[0]
            cnt2 = conn.execute("SELECT COUNT(*) FROM votes WHERE protocol_id=? AND question_id=? AND vote=?",
                                (pid, q[0], q[3])).fetchone()[0]
            cnt3 = conn.execute("SELECT COUNT(*) FROM votes WHERE protocol_id=? AND question_id=? AND vote=?",
                                (pid, q[0], q[4])).fetchone()[0]
            totals.append({"qnum": q[1], "opt1": q[2], "opt2": q[3], "opt3": q[4],
                           "c1": cnt1, "c2": cnt2, "c3": cnt3})

        # для админа всегда отдаём полную таблицу голосов
        rows = conn.execute(
            "SELECT user_code, question_id, vote FROM votes WHERE protocol_id=?",
            (pid,)
        ).fetchall()

        return {"totals": totals, "rows": rows, "vote_type": vote_type}

# --- Редактировать конкретный голос ---
@bp.put("/api/admin/protocols/<int:pid>/results/vote")
def admin_edit_vote(pid):
    if session.get("role") != "admin":
        return {"error": "unauthorized"}, 401

    data = request.json
    user_code = data["user_code"]
    question_id = data["question_id"]
    vote = data["vote"]

    with db() as conn:
        conn.execute(
            """UPDATE votes
               SET vote=?
               WHERE protocol_id=? AND user_code=? AND question_id=?""",
            (vote, pid, user_code, question_id)
        )
        conn.commit()

    log_action("ADMIN", f"edit_vote protocol={pid} user={user_code}")
    return {"ok": True}

# --- Экспорт результатов (только админ) ---
@bp.get("/api/admin/protocols/<int:pid>/results.csv")
def admin_export_csv(pid):
    if session.get("role") != "admin":
        return {"error": "unauthorized"}, 401

    with db() as conn:
        rows = conn.execute(
            "SELECT user_code, question_id, vote FROM votes WHERE protocol_id=?",
            (pid,)
        ).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["user_code","question_id","vote"])
    writer.writerows(rows)
    return output.getvalue(), 200, {"Content-Type":"text/csv"}