# a_protocol.py

from flask import Blueprint, request, session
from common import db, log_action, BASE_FOLDER, create_folder, upload_file

bp = Blueprint("a_protocol", __name__)

@bp.get("/api/admin/protocols")
def protocols_list():
    if session.get("role") != "admin": return {"error":"unauthorized"}, 401
    with db() as conn:
        rows = conn.execute("SELECT * FROM protocols").fetchall()
    return {"items":[dict(id=r[0], num=r[1], file=r[2], start=r[3], end=r[4],
                          status=r[5], vote_type=r[6], folder=r[7]) for r in rows]}

@bp.put("/api/admin/protocols/<int:pid>")
def protocols_update(pid):
    if session.get("role") != "admin": return {"error":"unauthorized"}, 401
    d = request.json
    with db() as conn:
        conn.execute("""UPDATE protocols
                        SET num=?, file_name=?, date_start=?, date_end=?, status=?, vote_type=?
                        WHERE id=?""",
                     (d["num"], d["file"], d["start"], d["end"], d["status"], d["vote_type"], pid))
        conn.commit()
    return {"ok": True}

@bp.post("/api/admin/protocols/create")
def protocols_create():
    if session.get("role") != "admin":
        return {"error":"unauthorized"}, 401

    if "file" not in request.files:
        return {"error":"Файл протокола обязателен"}, 400

    num = int(request.form["num"])
    date_start = request.form["date_start"]
    date_end = request.form["date_end"]
    status = request.form["status"]
    vote_type = request.form["vote_type"]
    file = request.files["file"]

    folder = f"протокол_{num:02d}_{date_start}"
    create_folder(BASE_FOLDER)
    create_folder(f"{BASE_FOLDER}/{folder}")

    disk_path = f"{BASE_FOLDER}/{folder}/{file.filename}"
    tmp_path = f"/tmp/{file.filename}"
    file.save(tmp_path)
    upload_file(tmp_path, disk_path)

    with db() as conn:
        cur = conn.execute("""INSERT INTO protocols
        (num, file_name, date_start, date_end, status, vote_type, folder)
        VALUES (?,?,?,?,?,?,?)""",
        (num, file.filename, date_start, date_end, status, vote_type, folder))
        pid = cur.lastrowid
        conn.commit()

    log_action("ADMIN", f"protocol_create {folder}")
    return {"ok": True, "id": pid}

@bp.delete("/api/admin/protocols/<int:pid>")
def protocols_delete(pid):
    if session.get("role") != "admin": return {"error":"unauthorized"}, 401
    with db() as conn:
        conn.execute("DELETE FROM protocols WHERE id=?", (pid,))
        conn.commit()
    log_action("ADMIN", f"protocol_delete {pid}")
    return {"ok": True}

@bp.post("/api/admin/protocols/<int:pid>/questions")
def questions_set(pid):
    if session.get("role") != "admin": return {"error":"unauthorized"}, 401
    items = request.json.get("items", [])
    with db() as conn:
        conn.execute("DELETE FROM questions WHERE protocol_id=?", (pid,))
        for q in items:
            conn.execute("""INSERT INTO questions
                (protocol_id, qnum, opt1, opt2, opt3, default_vote)
                VALUES (?,?,?,?,?,?)""",
                (pid, q["qnum"], q["opt1"], q["opt2"], q["opt3"], q.get("default_vote"))
            )
        conn.commit()
    return {"ok": True}
