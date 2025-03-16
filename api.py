from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# 📌 Configuration de la base de données MySQL avec les variables d'environnement
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DB')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# 📌 Modèle Countries (Liste des pays)
class Country(db.Model):
    __tablename__ = "Countries"
    id_country = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    continent = db.Column(db.String(100))
    population = db.Column(db.BigInteger)
    pandemic_data = db.relationship("PandemicData", backref="country", cascade="all, delete")

# 📌 Modèle PandemicData (Données des pandémies)
class PandemicData(db.Model):
    __tablename__ = "PandemicData"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False)
    id_country = db.Column(db.Integer, db.ForeignKey("Countries.id_country"), nullable=False)
    
    Deaths = db.Column(db.Integer)
    Recovered = db.Column(db.Integer)
    total_cases = db.Column(db.Integer)
    total_deaths = db.Column(db.Integer)
    total_recovered = db.Column(db.Integer)
    total_tests = db.Column(db.BigInteger)
    new_cases = db.Column(db.Integer)
    new_deaths = db.Column(db.Integer)
    New_recovered = db.Column(db.Integer)
    active_cases = db.Column(db.Integer)
    serious_critical = db.Column(db.Integer)
    TrueConfirmed = db.Column(db.Integer)
    Active = db.Column(db.Integer)

# 📌 Création des tables si elles n'existent pas encore
with app.app_context():
    db.create_all()

# 📌 Route pour récupérer la liste des pays
@app.route("/countries", methods=["GET"])
def get_countries():
    countries = Country.query.all()
    return jsonify([
        {"id_country": c.id_country, "name": c.name, "continent": c.continent, "population": c.population}
        for c in countries
    ])

# 📌 Route pour récupérer les données d’un pays donné
@app.route("/data", methods=["GET"])
def get_data():
    country_id = request.args.get("id_country", type=int)
    if not country_id:
        return jsonify({"error": "id_country est requis"}), 400

    # Sélectionner uniquement les colonnes nécessaires
    fields = ["date", "id_country", "total_cases", "new_cases", "total_deaths", "new_deaths", "total_recovered", "active_cases", "serious_critical", "TrueConfirmed", "New_recovered"]

    # Récupérer les données pour ce pays
    pandemies = PandemicData.query.join(Country, PandemicData.id_country == Country.id_country) \
                                  .with_entities(*[getattr(PandemicData, f) if f != "continent" and f != "population" else getattr(Country, f) for f in fields]) \
                                  .filter(PandemicData.id_country == country_id) \
                                  .all()
    
    return jsonify([dict(zip(fields, p)) for p in pandemies])

# 📌 Route pour ajouter une entrée
@app.route("/add", methods=["POST"])
def add_data():
    data = request.json

    # Vérifier si le pays existe, sinon l'ajouter
    country = Country.query.filter_by(name=data["country"]).first()
    if not country:
        country = Country(name=data["country"], continent=data["continent"], population=data["population"])
        db.session.add(country)
        db.session.commit()

    # Ajouter les données pandémiques
    new_entry = PandemicData(
        date=data["date"],
        id_country=country.id_country,
        total_cases=data["total_cases"],
        total_deaths=data["total_deaths"],
        new_cases=data["new_cases"],
        new_deaths=data["new_deaths"],
        total_recovered=data["total_recovered"],
        active_cases=data["active_cases"],
        serious_critical=data["serious_critical"],
        TrueConfirmed=data["TrueConfirmed"]
    )
    db.session.add(new_entry)
    db.session.commit()
    
    return jsonify({"message": "Donnée ajoutée avec succès"}), 201

# 📌 Route pour mettre à jour les données pandémiques d'un pays pour une date donnée
from datetime import datetime

@app.route("/update/<int:id_country>/<string:date>", methods=["PUT"])
def update_data(id_country, date):
    data = request.json

    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Format de date invalide, doit être YYYY-MM-DD"}), 400

    # Vérifier si le pays existe
    country = Country.query.filter_by(id_country=id_country).first()
    if not country:
        return jsonify({"error": "Pays non trouvé"}), 404

    # Vérifier si une donnée existe déjà
    entry = PandemicData.query.filter_by(id_country=id_country, date=date_obj).first()

    if entry:
        print(f"🔄 Donnée trouvée : {entry.__dict__}")  # Voir les données actuelles avant update

        # Mise à jour des champs
        entry.total_cases = data.get("total_cases", entry.total_cases)
        entry.total_deaths = data.get("total_deaths", entry.total_deaths)
        entry.new_cases = data.get("new_cases", entry.new_cases)
        entry.new_deaths = data.get("new_deaths", entry.new_deaths)
        entry.New_recovered = data.get("New_recovered", entry.New_recovered)

        try:
            db.session.flush()  # Force SQLAlchemy à préparer la requête SQL
            print(f"✅ Données mises à jour : {entry.__dict__}")  # Vérifier que les valeurs ont changé
            db.session.commit()  # Enregistrer en base
            print("✅ Commit réussi !")
            return jsonify({"message": "Donnée mise à jour avec succès"}), 200
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur commit : {e}")
            return jsonify({"error": f"Erreur lors de l'enregistrement des données : {e}"}), 500
    else:
        return jsonify({"error": "Donnée non trouvée"}), 404


@app.route("/data/<int:id_country>/<string:date>", methods=["DELETE"])
def delete_data(id_country, date):
    # Convertir la date en format datetime
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Format de date invalide, attendu YYYY-MM-DD"}), 400

    # Vérifier si la donnée existe dans la base
    entry = PandemicData.query.filter_by(id_country=id_country, date=date_obj).first()
    
    if entry:
        # Supprimer la donnée de la base de données
        db.session.delete(entry)
        db.session.commit()
        return jsonify({"message": "Donnée supprimée avec succès"}), 200
    else:
        return jsonify({"error": "Donnée non trouvée pour ce pays et cette date"}), 404

from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = "/docs"  # URL où Swagger UI sera accessible
API_URL = "/static/openapi.yaml"  # Lien vers le fichier OpenAPI

swagger_ui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)



if __name__ == "__main__":
    app.run(debug=True)
