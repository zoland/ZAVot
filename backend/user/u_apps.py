# u_apps.py

from flask import Blueprint
from common import db, BASE_FOLDER, list_folder, download_link

bp = Blueprint("u_apps", __name__)

@bp.get("/api/protocols/<int:pid>/files")
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