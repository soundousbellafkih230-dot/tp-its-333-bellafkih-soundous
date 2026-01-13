from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

## EXO1: API GET: renvoyer un helloworld - API end point name: "api/salutation"
@app.route('/api/salutation', methods=['GET'])
def hello_world():
    return jsonify({"message": "Hello World"}), 200

## EXO2: API POST: renvoyer un nom fourni en parametre - API end point name: "api/utilisateurs"
@app.route('/api/utilisateurs', methods=['POST'])
def get_user_name():
    data = request.get_json()
    if data and 'nom' in data:
        return jsonify({"nom_recu": data['nom']}), 200
    return jsonify({"error": "Nom manquant"}), 400

# to be tested with curl: 
# >> curl -i -X GET http://localhost:5000/api/salutation
# >> curl -i -X POST -H 'Content-Type: application/json' -d '{"nom": "Bob"}' http://localhost:5000/api/utilisateurs

if __name__ == '__main__':
    app.run(debug=True)