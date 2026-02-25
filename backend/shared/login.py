# backend/shared/login.py
from flask import Blueprint, request, jsonify
from shared.auth import generate_token

import json, os

bp = Blueprint("login", __name__)

# временно читаем из data/users.json
def load_users():
    path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "users.json")
    path = os.path.normpath(path)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    # дефолт для старта
    return {"admin": {"password": "1234", "role": "admin"}}

@bp.post("/api/login")
def login():
    data = request.get_json(force=True)
    code = data.get("code", "")
    password = data.get("password", "")

    users = load_users()
    user = users.get(code)

    if not user or user.get("password") != password:
        return jsonify({"ok": False, "error": "Неверный код или пароль"}), 401

    token = generate_token(code, user.get("role"))
    return jsonify({"ok": True, "token": token, "role": user.get("role")})