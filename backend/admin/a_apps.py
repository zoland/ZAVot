# a_apps.py
from flask import Blueprint, request, session
from common import db, BASE_FOLDER, upload_file, delete_file, list_folder

bp = Blueprint("a_apps", __name__)


@bp.get("/api/admin/protocols/<int:pid>/materials")
def materials_list(pid):
    if session.get("role") != "admin": 
        return {"error":"unauthorized"}, 401

    with db() as conn:
        folder = conn.execute("SELECT folder FROM protocols WHERE id=?", (pid,)).fetchone()[0]

    path = f"{BASE_FOLDER}/{folder}"
    raw = list_folder(path)

    items = []
    if isinstance(raw, dict):
        if "_embedded" in raw and isinstance(raw["_embedded"], dict):
            items = raw["_embedded"].get("items", [])
        elif "items" in raw:
            items = raw.get("items", [])
    elif isinstance(raw, list):
        items = raw

    files = []
    for it in items:
        if isinstance(it, dict):
            name = it.get("name")
        else:
            name = str(it)
        if name:
            files.append(name)

    return {"items": files}


@bp.post("/api/admin/protocols/<int:pid>/materials")
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

@bp.delete("/api/admin/protocols/<int:pid>/materials")
def materials_delete(pid):
    if session.get("role") != "admin": return {"error":"unauthorized"}, 401
    name = request.args.get("name")
    with db() as conn:
        folder = conn.execute("SELECT folder FROM protocols WHERE id=?", (pid,)).fetchone()[0]
    path = f"{BASE_FOLDER}/{folder}/{name}"
    delete_file(path)
    return {"ok": True}