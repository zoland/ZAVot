# backend/admin/a_dir.py

from flask import Blueprint, request, jsonify
import requests
from shared.yandex_disk import list_folder, headers, BASE_URL

a_dir_bp = Blueprint("a_dir", __name__)

# --- Вспомогательные функции ---
def get_disk_info():
    r = requests.get(f"{BASE_URL}", headers=headers())
    r.raise_for_status()
    data = r.json()
    total = data.get("total_space", 0)
    used = data.get("used_space", 0)
    return {
        "total": total,
        "used": used,
        "free": total - used
    }

def build_tree(path: str, level: int = 0):
    data = list_folder(path)
    items = data.get("items", data.get("_embedded", {}).get("items", []))

    # сортируем: папки → файлы
    items_sorted = sorted(items, key=lambda x: (x.get("type") != "dir", x.get("name", "")))

    result = []
    for item in items_sorted:
        result.append({
            "name": item.get("name"),
            "type": item.get("type"),
            "size": item.get("size", 0),
            "level": level
        })
        if item.get("type") == "dir":
            sub_path = f"{path.rstrip('/')}/{item.get('name')}"
            result.extend(build_tree(sub_path, level + 1))

    return result

# --- API ---
@a_dir_bp.route("/api/admin/dir/quota", methods=["GET"])
def dir_quota():
    info = get_disk_info()
    return jsonify(info)

@a_dir_bp.route("/api/admin/dir/tree", methods=["GET"])
def dir_tree():
    path = request.args.get("path", "disk:/04ЧР_ОП")
    items = build_tree(path)
    return jsonify({"path": path, "items": items})