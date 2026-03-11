# vector.py

from flask import Flask, request, jsonify
from pathlib import Path
import os
from datetime import datetime

app = Flask(__name__)

API_TOKEN = os.getenv("VECTOR_API_TOKEN", "dev-token")

DATA_DIR = Path(__file__).parent / "data"

def check_auth(req):
    auth = req.headers.get("Authorization", "")
    return auth == f"Bearer {API_TOKEN}"

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True, "service": "zv-vector-test"})

@app.route("/vector/get-latest", methods=["GET"])
def vector_get_latest():
    if not check_auth(request):
        return jsonify({"error": "unauthorized"}), 401

    project_id = request.args.get("project_id", "").strip()
    doc_type = request.args.get("type", "").strip()

    if project_id != "ZV":
        return jsonify({"error": "unknown project_id"}), 400
    if doc_type != "doc":
        return jsonify({"error": "only type=doc is supported in this test"}), 400

    file_path = DATA_DIR / "ZV_doc.txt"
    if not file_path.exists():
        return jsonify({"error": f"file not found: {file_path.name}"}), 404

    content = file_path.read_text(encoding="utf-8")

    return jsonify({
        "project_id": "ZV",
        "type": "doc",
        "version": 1,
        "source_file": str(file_path.name),
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "content": content
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
    