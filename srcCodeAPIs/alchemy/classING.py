from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

# ---------------- CONFIG ----------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecole.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
SECRET_KEY = "ma_cle_secrete"

db = SQLAlchemy(app)

# ---------------- CLASSES ----------------
class Groupe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    etudiants = db.relationship('Etudiant', backref='groupe', lazy=True)

class Etudiant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groupe.id'))

# ---------------- CREATION BASE ----------------
with app.app_context():
    db.create_all()
    if not Groupe.query.filter_by(nom="ITS2").first():
        its2 = Groupe(nom="ITS2")
        e1 = Etudiant(nom="soundous", groupe=its2)
        e2 = Etudiant(nom="jihane", groupe=its2)
        e3 = Etudiant(nom="Siham", groupe=its2)
        db.session.add(its2)
        db.session.add_all([e1, e2, e3])
        db.session.commit()

# ---------------- JWT ----------------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'Token manquant !'}), 401
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except:
            return jsonify({'message': 'Token invalide !'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['POST'])
def login():
    auth = request.json
    if auth and auth.get('username') == "admin" and auth.get('password') == "1234":
        token = jwt.encode({'user': auth['username'], 
                            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                            SECRET_KEY, algorithm="HS256")
        return jsonify({'token': token})
    return jsonify({'message': 'Login échoué !'}), 401

# ---------------- ROUTES API ----------------
@app.route('/')
def index():
    groupe = Groupe.query.filter_by(nom="ITS2").first()
    return {
        "groupe": groupe.nom,
        "etudiants": [e.nom for e in groupe.etudiants]
    }

@app.route('/new', methods=['POST'])
@token_required
def add_etudiant():
    data = request.json
    nom = data.get('nom')
    if not nom:
        return jsonify({"message": "Nom manquant"}), 400
    its2 = Groupe.query.filter_by(nom="ITS2").first()
    e = Etudiant(nom=nom, groupe=its2)
    db.session.add(e)
    db.session.commit()
    return jsonify({"message": f"Étudiant {nom} ajouté ✅"})

@app.route('/etudiants')
def liste_etudiants():
    groupe = Groupe.query.filter_by(nom="ITS2").first()
    return {
        "groupe": groupe.nom,
        "etudiants": [e.nom for e in groupe.etudiants]
    }

# ---------------- SWAGGER ----------------
SWAGGER_URL = '/swagger'  # URL accessible via navigateur
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Gestion Étudiants API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# ---------------- LANCEMENT ----------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False)

