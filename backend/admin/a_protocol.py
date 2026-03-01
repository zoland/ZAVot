# a_protocol.py
from flask import Blueprint, request, session
from common import db, log_action, BASE_FOLDER, create_folder, upload_file, delete_file

bp = Blueprint("a_protocol", __name__)

@bp.get("/api/admin/protocols")
def protocols_list():
    if session.get("role") != "admin": return {"error":"unauthorized"}, 401
    with db() as conn:
        rows = conn.execute("SELECT * FROM protocols").fetchall()
    return {"items":[dict(
        id=r[0], num=r[1], file=r[2], date=r[3],
        status=r[4], vote_type=r[5], folder=r[6],
        qcount=r[7], quorum_default=r[8]
    ) for r in rows]}

@bp.put("/api/admin/protocols/<int:pid>")
def protocols_update(pid):
    if session.get("role") != "admin": return {"error":"unauthorized"}, 401
    d = request.json
    with db() as conn:
        conn.execute("""UPDATE protocols
                        SET num=?, file_name=?, date=?, status=?, vote_type=?, quorum_default=?
                        WHERE id=?""",
                     (d["num"], d["file"], d["date"], d["status"],
                      d["vote_type"], d["quorum_default"], pid))
        conn.commit()
    return {"ok": True}

@bp.post("/api/admin/protocols/create")
def protocols_create():
    if session.get("role") != "admin":
        return {"error":"unauthorized"}, 401

    if "file" not in request.files:
        return {"error":"Файл протокола обязателен"}, 400

    num = int(request.form["num"])
    date = request.form["date"]
    status = request.form["status"]
    vote_type = request.form["vote_type"]
    qcount = int(request.form["qcount"])
    quorum_default = request.form["quorum_default"]
    file = request.files["file"]

    folder = f"протокол_{num:02d}_{date}"
    create_folder(BASE_FOLDER)
    create_folder(f"{BASE_FOLDER}/{folder}")

    disk_path = f"{BASE_FOLDER}/{folder}/{file.filename}"
    tmp_path = f"/tmp/{file.filename}"
    file.save(tmp_path)
    upload_file(tmp_path, disk_path)

    with db() as conn:
        cur = conn.execute("""INSERT INTO protocols
        (num, file_name, date, status, vote_type, folder, qcount, quorum_default)
        VALUES (?,?,?,?,?,?,?,?)""",
        (num, file.filename, date, status, vote_type, folder, qcount, quorum_default))
        pid = cur.lastrowid

        for qnum in range(1, qcount+1):
            conn.execute("""INSERT INTO questions
                (protocol_id, qnum, opt1, opt2, opt3, default_vote, quorum)
                VALUES (?,?,?,?,?,?,?)""",
                (pid, qnum, "За", "Против", "Воздержался", "Воздержался", quorum_default))

        # ⚠️ замените users/code на реальные таблицу/поле
        users = conn.execute("SELECT code FROM users").fetchall()
        qrows = conn.execute("SELECT id FROM questions WHERE protocol_id=?", (pid,)).fetchall()
        for u in users:
            for q in qrows:
                conn.execute("""INSERT INTO votes
                    (protocol_id, question_id, user_code, vote, voted)
                    VALUES (?,?,?,?,?)""",
                    (pid, q[0], u[0], "Воздержался", 0))

        conn.commit()

    log_action("ADMIN", f"protocol_create {folder}")
    return {"ok": True, "id": pid}

@bp.delete("/api/admin/protocols/<int:pid>")
def protocols_delete(pid):
    if session.get("role") != "admin": return {"error":"unauthorized"}, 401
    with db() as conn:
        folder = conn.execute("SELECT folder FROM protocols WHERE id=?", (pid,)).fetchone()[0]
        conn.execute("DELETE FROM votes WHERE protocol_id=?", (pid,))
        conn.execute("DELETE FROM questions WHERE protocol_id=?", (pid,))
        conn.execute("DELETE FROM protocols WHERE id=?", (pid,))
        conn.commit()
    delete_file(f"{BASE_FOLDER}/{folder}")
    log_action("ADMIN", f"protocol_delete {pid}")
    return {"ok": True}

@bp.get("/api/admin/protocols/<int:pid>/questions")
def questions_get(pid):
    if session.get("role") != "admin": return {"error":"unauthorized"}, 401
    with db() as conn:
        p = conn.execute("SELECT qcount, quorum_default FROM protocols WHERE id=?", (pid,)).fetchone()
        qcount, qdef = p[0], p[1]
        rows = conn.execute("SELECT qnum, quorum FROM questions WHERE protocol_id=? ORDER BY qnum", (pid,)).fetchall()

        if not rows:
            for qnum in range(1, qcount+1):
                conn.execute("""INSERT INTO questions
                    (protocol_id, qnum, opt1, opt2, opt3, default_vote, quorum)
                    VALUES (?,?,?,?,?,?,?)""",
                    (pid, qnum, "За", "Против", "Воздержался", "Воздержался", qdef))
            conn.commit()
            rows = conn.execute("SELECT qnum, quorum FROM questions WHERE protocol_id=? ORDER BY qnum", (pid,)).fetchall()

    return {"qcount": qcount, "items":[{"qnum":r[0], "quorum":r[1]} for r in rows]}

@bp.put("/api/admin/protocols/<int:pid>/questions")
def questions_set(pid):
    if session.get("role") != "admin": return {"error":"unauthorized"}, 401
    items = request.json.get("items", [])
    with db() as conn:
        for q in items:
            conn.execute("""UPDATE questions SET quorum=?
                            WHERE protocol_id=? AND qnum=?""",
                         (q["quorum"], pid, q["qnum"]))
        conn.commit()
    return {"ok": True}
