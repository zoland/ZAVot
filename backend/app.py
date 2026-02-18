from flask import Flask, request, jsonify, session
from yandex_disk import create_folder, upload_file, list_folder, download_link
from datetime import datetime
import os, sqlite3, csv, io
import unicodedata

app = Flask(__name__, static_folder="../frontend", static_url_path="")
app.secret_key = os.getenv("SECRET_KEY", "change_me")

BASE_FOLDER = "disk:/04ЧР_ОП"
ADMIN_CODE = os.getenv("ADMIN_CODE", "Z")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "zoland")
DB_PATH = "bulbul.db"

def db():
    return sqlite3.connect(DB_PATH)

def log_action(code, action):
    with db() as conn:
        conn.execute("INSERT INTO logs (participant_code, action, created_at) VALUES (?, ?, ?)",
                     (code, action, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()

@app.get("/")
def index():
    return app.send_static_file("index.html")

# ---- AUTH ----
@app.post("/api/login")
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
        row = conn.execute("SELECT role FROM users WHERE code=? AND password=?",
                           (code, password)).fetchone()
    if row:
        session["role"] = row[0]
        session["code"] = code
        log_action(code, "login")
        return {"role": row[0]}

    return {"error": "invalid"}, 401

@app.post("/api/logout")
def logout():
    session.clear()
    return {"ok": True}

# ---- ADMIN: USERS ----
@app.get("/api/admin/users")
def users_list():
    if session.get("role") != "admin": return {"error":"unauthorized"}, 401
    with db() as conn:
        rows = conn.execute("SELECT * FROM users").fetchall()
    return {"items":[dict(id=r[0], code=r[1], role=r[2], password=r[3]) for r in rows]}

@app.post("/api/admin/users")
def users_add():
    if session.get("role") != "admin": return {"error":"unauthorized"}, 401
    d = request.json
    code = unicodedata.normalize("NFC", d["code"])
    password = unicodedata.normalize("NFC", d["password"])
    with db() as conn:
        conn.execute("INSERT INTO users (code,role,password) VALUES (?,?,?)",
                     (d["code"], d["role"], d["password"]))
        conn.commit()
    log_action("ADMIN", f"user_add {d['code']}")
    return {"ok": True}

@app.delete("/api/admin/users/<int:uid>")
def users_delete(uid):
    if session.get("role") != "admin": return {"error":"unauthorized"}, 401
    with db() as conn:
        conn.execute("DELETE FROM users WHERE id=?", (uid,))
        conn.commit()
    log_action("ADMIN", f"user_delete {uid}")
    return {"ok": True}


@app.get("/api/protocols/<int:pid>/info")
def protocol_info(pid):
    with db() as conn:
        row = conn.execute("SELECT file_name, folder FROM protocols WHERE id=?", (pid,)).fetchone()
    return {"file": row[0], "folder": row[1]}


# ---- ADMIN: LOGS ----
@app.get("/api/admin/logs")
def logs_list():
    if session.get("role") != "admin": return {"error":"unauthorized"}, 401
    with db() as conn:
        rows = conn.execute("SELECT * FROM logs ORDER BY created_at DESC").fetchall()
    return {"items":[dict(id=r[0], code=r[1], action=r[2], created_at=r[3]) for r in rows]}

@app.delete("/api/admin/logs/<int:lid>")
def logs_delete(lid):
    if session.get("role") != "admin": return {"error":"unauthorized"}, 401
    with db() as conn:
        conn.execute("DELETE FROM logs WHERE id=?", (lid,))
        conn.commit()
    return {"ok": True}

# ---- ADMIN: PROTOCOLS ----
@app.get("/api/admin/protocols")
def protocols_list():
    if session.get("role") != "admin": return {"error":"unauthorized"}, 401
    with db() as conn:
        rows = conn.execute("SELECT * FROM protocols").fetchall()
    return {"items":[dict(id=r[0], num=r[1], file=r[2], start=r[3], end=r[4],
                          status=r[5], vote_type=r[6], folder=r[7]) for r in rows]}

@app.put("/api/admin/protocols/<int:pid>")
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

@app.post("/api/admin/protocols/create")
def protocols_create():
    if session.get("role") != "admin":
        return {"error":"unauthorized"}, 401

    try:
        if "file" not in request.files:
            return {"error":"Файл протокола обязателен"}, 400

        num = int(request.form["num"])
        date_start = request.form["date_start"]
        date_end = request.form["date_end"]
        status = request.form["status"]
        vote_type = request.form["vote_type"]
        file = request.files["file"]

        folder = f"протокол_{num:02d}_{date_start}"
        create_folder(BASE_FOLDER)  # гарантируем базовую папку
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

    except Exception as e:
        return {"error": str(e)}, 500
    

@app.delete("/api/admin/protocols/<int:pid>")
def protocols_delete(pid):
    if session.get("role") != "admin": return {"error":"unauthorized"}, 401
    with db() as conn:
        conn.execute("DELETE FROM protocols WHERE id=?", (pid,))
        conn.commit()
    log_action("ADMIN", f"protocol_delete {pid}")
    return {"ok": True}

# ---- QUESTIONS ----
@app.get("/api/protocols/<int:pid>/questions")
def questions_list(pid):
    with db() as conn:
        rows = conn.execute("SELECT * FROM questions WHERE protocol_id=? ORDER BY qnum", (pid,)).fetchall()
    return {"items":[dict(id=r[0], qnum=r[2], opt1=r[3], opt2=r[4], opt3=r[5]) for r in rows]}

@app.post("/api/admin/protocols/<int:pid>/questions")
def questions_set(pid):
    if session.get("role") != "admin": return {"error":"unauthorized"}, 401
    items = request.json.get("items", [])
    with db() as conn:
        conn.execute("DELETE FROM questions WHERE protocol_id=?", (pid,))
        for q in items:
            conn.execute("INSERT INTO questions (protocol_id, qnum, opt1, opt2, opt3) VALUES (?,?,?,?,?)",
                         (pid, q["qnum"], q["opt1"], q["opt2"], q["opt3"]))
        conn.commit()
    return {"ok": True}

# ---- MATERIALS ----
@app.post("/api/admin/protocols/<int:pid>/materials")
def materials_upload(pid):
    if session.get("role") != "admin": return {"error":"unauthorized"}, 401
    file = request.files["file"]
    with db() as conn:
        row = conn.execute("SELECT folder FROM protocols WHERE id=?", (pid,)).fetchone()
    folder = row[0]
    disk_path = f"{BASE_FOLDER}/{folder}/{file.filename}"
    tmp_path = f"/tmp/{file.filename}"
    file.save(tmp_path)
    upload_file(tmp_path, disk_path)
    return {"ok": True}

@app.get("/api/protocols/<int:pid>/files")
def protocol_files(pid):
    with db() as conn:
        row = conn.execute("SELECT folder FROM protocols WHERE id=?", (pid,)).fetchone()
    folder = row[0]
    path = f"{BASE_FOLDER}/{folder}"
    data = list_folder(path)
    files = []
    for i in data.get("_embedded", {}).get("items", []):
        if i["type"] == "file":
            href = download_link(i["path"])
            files.append({"name": i["name"], "href": href})
    return {"files": files}

# ---- PUBLIC LIST ----
@app.get("/api/protocols")
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



@app.delete("/api/admin/protocols/<int:pid>/materials")
def materials_delete(pid):
    if session.get("role") != "admin": return {"error":"unauthorized"}, 401
    name = request.args.get("name")
    with db() as conn:
        folder = conn.execute("SELECT folder FROM protocols WHERE id=?", (pid,)).fetchone()[0]
    path = f"{BASE_FOLDER}/{folder}/{name}"
    delete_file(path)
    return {"ok": True}

# ---- VOTES ----
@app.post("/api/vote")
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

@app.get("/api/protocols/<int:pid>/results")
def results(pid):
    with db() as conn:
        proto = conn.execute("SELECT vote_type FROM protocols WHERE id=?", (pid,)).fetchone()
        vote_type = proto[0]
        questions = conn.execute("SELECT id,qnum,opt1,opt2,opt3 FROM questions WHERE protocol_id=? ORDER BY qnum", (pid,)).fetchall()

        totals = []
        for q in questions:
            cnt1 = conn.execute("SELECT COUNT(*) FROM votes WHERE protocol_id=? AND question_id=? AND vote=?",
                                (pid, q[0], q[2])).fetchone()[0]
            cnt2 = conn.execute("SELECT COUNT(*) FROM votes WHERE protocol_id=? AND question_id=? AND vote=?",
                                (pid, q[0], q[3])).fetchone()[0]
            cnt3 = conn.execute("SELECT COUNT(*) FROM votes WHERE protocol_id=? AND question_id=? AND vote=?",
                                (pid, q[0], q[4])).fetchone()[0]
            totals.append({"qnum": q[1], "opt1": q[2], "opt2": q[3], "opt3": q[4], "c1": cnt1, "c2": cnt2, "c3": cnt3})

        if vote_type == "тайное":
            return {"totals": totals}

        rows = conn.execute("SELECT user_code, question_id, vote FROM votes WHERE protocol_id=?", (pid,)).fetchall()
        return {"totals": totals, "rows": rows}

# ---- RESULTS EXPORT CSV ----
@app.get("/api/protocols/<int:pid>/results.csv")
def results_csv(pid):
    with db() as conn:
        rows = conn.execute("SELECT user_code, question_id, vote FROM votes WHERE protocol_id=?", (pid,)).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["user_code","question_id","vote"])
    writer.writerows(rows)
    return output.getvalue(), 200, {"Content-Type":"text/csv"}

if __name__ == "__main__":
    app.run(debug=True)