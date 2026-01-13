from flask import Flask, jsonify

# Utilisation de deux tirets bas __ de chaque côté
app = Flask(__name__)

# 1. Base de données avec Soundous
patients_db = [
    {
        "id": 1405,
        "nom": "Soundous",
        "parametres_sante": {"GS": "A+", "maladie": "Aucune"}
    },
    {
        "id": 2002,
        "nom": "Marc",
        "parametres_sante": {"GS": "O-", "maladie": "Diabète"}
    },
    {
        "id": 3000,
        "nom": "Soundous",
        "parametres_sante": {"GS": "B-", "maladie": "Grippe"}
    }
]

# 2. Route API
@app.route('/sante/<int:patient_id>/<choix>', methods=['GET'])
def api_sante(patient_id, choix):
    # Recherche du patient par son ID unique
    patient_trouve = None
    for p in patients_db:
        if p["id"] == patient_id:
            patient_trouve = p
            break

    if patient_trouve is None:
        return jsonify({"erreur": "Patient introuvable"}), 404

    sante = patient_trouve.get("parametres_sante", {})

    # Vérification si le choix est dans les paramètres de santé ou les infos générales
    if choix in sante:
        resultat = {choix: sante[choix]}
    elif choix in patient_trouve:
        resultat = {choix: patient_trouve[choix]}
    else:
        return jsonify({"erreur": f"Le paramètre '{choix}' n'existe pas"}), 404

    return jsonify(resultat)

# Lancement du serveur (avec deux tirets bas __ )
if __name__ == '__main__':
    app.run(debug=True)