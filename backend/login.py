# backend/login.py
from flask import Blueprint, request, jsonify, session
from auth import generate_token

import json, os

bp = Blueprint("login", __name__)

def load_users():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "users.json")
    path = os.path.normpath(path)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
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

    # ✅ Устанавливаем сессию
    session["role"] = user.get("role")
    session["code"] = code

    token = generate_token(code, user.get("role"))
    return jsonify({"ok": True, "token": token, "role": user.get("role")})