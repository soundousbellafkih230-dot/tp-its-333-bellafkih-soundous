import os
import sqlite3
import datetime
import jwt
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

DB_PATH = os.getenv("AUTH_DB_PATH", "users.db")
JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret_change_me")
JWT_ALGO = "HS256"
JWT_EXP_MIN = int(os.getenv("JWT_EXP_MIN", "120"))  # 2h

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.get("/healthz")
def healthz():
    return {"status": "ok"}, 200

@app.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {"error": "username et password requis"}, 400

    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users(username, password_hash) VALUES(?, ?)",
            (username, generate_password_hash(password))
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return {"error": "username déjà utilisé"}, 409

    conn.close()
    return {"message": "user créé"}, 201

@app.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {"error": "username et password requis"}, 400

    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    conn.close()

    if not row or not check_password_hash(row[0], password):
        return {"error": "identifiants invalides"}, 401

    payload = {
        "sub": username,
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=JWT_EXP_MIN),
        "scope": "api"
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
    return {"token": token}, 200

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
