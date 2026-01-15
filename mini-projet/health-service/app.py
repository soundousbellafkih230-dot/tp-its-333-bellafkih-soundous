from flask_swagger_ui import get_swaggerui_blueprint
import os, json, jwt, requests
from flask import Flask, request

app = Flask(__name__)

DATA_PATH = os.getenv("HEALTH_DATA_PATH", "data.json")
PERSON_SERVICE_URL = os.getenv("PERSON_SERVICE_URL", "http://person-service:5001")
JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret_change_me")
JWT_ALGO = "HS256"

def ensure_data_file():
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w") as f:
            json.dump({}, f)

def read_data():
    ensure_data_file()
    with open(DATA_PATH) as f:
        return json.load(f)

def write_data(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

def require_jwt(fn):
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return {"error": "Missing Bearer token"}, 401
        token = auth.split(" ", 1)[1].strip()
        try:
            jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        except:
            return {"error": "Invalid token"}, 401
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

def person_exists(pid):
    try:
        r = requests.get(
            f"{PERSON_SERVICE_URL}/persons/{pid}",
            headers={"Authorization": request.headers.get("Authorization","")}
        )
        return r.status_code == 200
    except:
        return False

@app.get("/health/<int:pid>")
@require_jwt
def get_health(pid):
    if not person_exists(pid): return {"error":"person not found"},404
    data = read_data()
    if str(pid) not in data: return {"error":"health not found"},404
    return data[str(pid)],200

@app.post("/health/<int:pid>")
@require_jwt
def add_health(pid):
    if not person_exists(pid): return {"error":"person not found"},404
    data = read_data()
    if str(pid) in data: return {"error":"already exists"},409
    data[str(pid)] = request.get_json()
    write_data(data)
    return data[str(pid)],201

@app.put("/health/<int:pid>")
@require_jwt
def update_health(pid):
    if not person_exists(pid): return {"error":"person not found"},404
    data = read_data()
    if str(pid) not in data: return {"error":"health not found"},404
    data[str(pid)] = request.get_json()
    write_data(data)
    return data[str(pid)],200

@app.delete("/health/<int:pid>")
@require_jwt
def delete_health(pid):
    if not person_exists(pid): return {"error":"person not found"},404
    data = read_data()
    if str(pid) not in data: return {"error":"health not found"},404
    del data[str(pid)]
    write_data(data)
    return "",204

# ---------- Swagger ----------
SWAGGER_URL = '/apidocs'
API_URL = '/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL,
    config={'app_name': "Health Service"})
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route("/swagger.json")
def swagger_json():
    return {
        "openapi": "3.0.0",
        "info": {"title": "Health Service API", "version": "1.0"},
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        },
        "security": [{"bearerAuth": []}],
        "paths": {
            "/health/{id}": {
                "get": {
                    "summary": "Lire santé",
                    "security": [{"bearerAuth": []}],
                    "parameters": [
                        {"name":"id","in":"path","required":True,"schema":{"type":"integer"}}
                    ]
                },
                "post": {
                    "summary": "Ajouter santé",
                    "security": [{"bearerAuth": []}],
                    "parameters": [
                        {"name":"id","in":"path","required":True,"schema":{"type":"integer"}}
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "weight": {"type": "number"},
                                        "height": {"type": "number"},
                                        "heart_rate": {"type": "number"},
                                        "blood_pressure": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                },
                "put": {
                    "summary": "Modifier santé",
                    "security": [{"bearerAuth": []}],
                    "parameters": [
                        {"name":"id","in":"path","required":True,"schema":{"type":"integer"}}
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "weight": {"type": "number"},
                                        "height": {"type": "number"},
                                        "heart_rate": {"type": "number"},
                                        "blood_pressure": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                },
                "delete": {
                    "summary": "Supprimer santé",
                    "security": [{"bearerAuth": []}],
                    "parameters": [
                        {"name":"id","in":"path","required":True,"schema":{"type":"integer"}}
                    ]
                }
            }
        }
    }

if __name__=="__main__":
    ensure_data_file()
    app.run(host="0.0.0.0",port=5002,debug=True)
