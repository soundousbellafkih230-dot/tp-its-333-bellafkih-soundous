from flask_swagger_ui import get_swaggerui_blueprint
import os
import sqlite3
import jwt
from flask import Flask, request

app = Flask(__name__)

DB_PATH = os.getenv("PERSON_DB_PATH", "database.db")
JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret_change_me")
JWT_ALGO = "HS256"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS persons(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def require_jwt(fn):
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return {"error": "Missing Bearer token"}, 401
        token = auth.split(" ", 1)[1].strip()
        try:
            jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        except Exception:
            return {"error": "Invalid token"}, 401
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

@app.get("/healthz")
def healthz():
    return {"status": "ok"}, 200

@app.post("/persons")
@require_jwt
def create_person():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    if not name:
        return {"error": "name requis"}, 400

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO persons(name) VALUES(?)", (name,))
    conn.commit()
    person_id = cur.lastrowid
    conn.close()
    return {"id": person_id, "name": name}, 201

@app.get("/persons/<int:person_id>")
@require_jwt
def get_person(person_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM persons WHERE id=?", (person_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {"error": "person not found"}, 404
    return {"id": row[0], "name": row[1]}, 200

@app.delete("/persons/<int:person_id>")
@require_jwt
def delete_person(person_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM persons WHERE id=?", (person_id,))
    conn.commit()
    deleted = cur.rowcount
    conn.close()
    if deleted == 0:
        return {"error": "person not found"}, 404
    return "", 204

# ---------- Swagger UI ----------
SWAGGER_URL = '/apidocs'
API_URL = '/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Person Service"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route("/swagger.json")
def swagger_json():
    return {
        "openapi": "3.0.0",
        "info": {"title": "Person Service API", "version": "1.0"},
        "paths": {
            "/persons": {
                "post": {"summary": "Créer une personne"}
            },
            "/persons/{id}": {
                "get": {"summary": "Lire une personne"},
                "delete": {"summary": "Supprimer une personne"}
            }
        }
    }

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5001, debug=True)
