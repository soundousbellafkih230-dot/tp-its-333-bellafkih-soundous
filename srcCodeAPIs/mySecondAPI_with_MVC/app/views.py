from app import app
from flask import render_template, request, jsonify
import sqlite3
import jwt
import datetime

# --- CODE POUR L'EXERCICE ---

# 1. Route pour afficher le formulaire de l'étudiant
@app.route('/new-student')
def new_student_form():
    # On utilise new.html comme demandé dans le schéma MVC
    return render_template('new.html')

# 2. Route pour enregistrer l'étudiant (Action du formulaire)
@app.route('/new', methods=['POST'])
def add_record():
    # Récupération des données du formulaire selon les noms (n, add, pin)
    nm = request.form['n']
    addr = request.form['add']
    pin = request.form['pin']

    try:
        # Connexion à SQLite et insertion comme dans la slide
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO etudiants (nom, addr, pin) VALUES (?,?,?)", (nm, addr, pin))
            con.commit()
            msg = "Enregistrement réussi"
    except:
        con.rollback()
        msg = "Erreur lors de l'insertion"
    finally:
        con.close()
        return jsonify({"message": msg}), 200

# 3. Route pour l'authentification Admin avec JWT (Consigne en rouge)
@app.route('/login-admin', methods=['POST'])
def login_admin():
    # On génère un token JWT qui expire dans 30 minutes
    token = jwt.encode({
        'user': 'admin',
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }, app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({'token': token}), 200