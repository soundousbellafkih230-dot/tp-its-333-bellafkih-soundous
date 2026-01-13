from app import app
from flask import render_template, request, jsonify

from flask import jsonify, render_template, request
from app import app # On importe l'instance de Flask créée dans __init__.py

### EXO1 - simple API
@app.route('/api/simple', methods=['GET'])
def simple_api():
    return jsonify({"message": "Ceci est une API en structure MVC"}), 200

### EXO2 - API with simple display
@app.route('/api/display', methods=['GET'])
def simple_display():
    return render_template('index.html')

### EXO3 - API with parameters display 
@app.route('/api/parameters', methods=['GET'])
def parameters_display():
    user_name = "soundous"
    return render_template('index.html', name=user_name)

### EXO4 - API with parameters retrieved from URL 
@app.route('/api/search', methods=['GET'])
def search_api():
    query_name = request.args.get('name', 'Utilisateur inconnu')
    return jsonify({
        "status": "success",
        "message": f"Bonjour {query_name}, votre paramètre a bien été récupéré !"
    }), 200

# Version "inverse" (Paramètres vers la Vue)
@app.route('/params', methods=['GET'])
def display_params():
    nom = request.args.get('surname', 'Non renseigné')
    prenom = request.args.get('name', 'Non renseigné')
    return render_template('index.html', surname=nom, name=prenom)