# u_res.py

from flask import Blueprint
import io, csv
from common import db

bp = Blueprint("u_res", __name__)

@bp.get("/api/protocols/<int:pid>/results")
def results(pid):
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

        if vote_type == "тайное":
            return {"totals": totals}

        rows = conn.execute("SELECT user_code, question_id, vote FROM votes WHERE protocol_id=?", (pid,)).fetchall()
        return {"totals": totals, "rows": rows}

@bp.get("/api/protocols/<int:pid>/results.csv")
def results_csv(pid):
    with db() as conn:
        rows = conn.execute("SELECT user_code, question_id, vote FROM votes WHERE protocol_id=?", (pid,)).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["user_code","question_id","vote"])
    writer.writerows(rows)
    return output.getvalue(), 200, {"Content-Type":"text/csv"}