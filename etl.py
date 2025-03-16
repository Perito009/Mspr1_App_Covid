import pandas as pd
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv
import os

load_dotenv()

# 📌 Connexion à la base MySQL avec les variables d'environnement
DB_URI = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DB')}"
engine = sqlalchemy.create_engine(DB_URI)

# 📌 Charger `df_finale.csv`
df = pd.read_csv("data/df_finale.csv")

if df.empty:
    print("❌ Le fichier CSV est vide !")
    exit()

# 📌 Vérifier et renommer la colonne "Date"
if "Date" in df.columns:
    df = df.rename(columns={"Date": "date"})

# 📌 Vérifier que "date" existe
if "date" not in df.columns:
    print("❌ Erreur : La colonne 'date' est absente du fichier CSV.")
    exit()

# 📌 Convertir la colonne "date" en format datetime SQL
df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date

# 📌 Nettoyer les valeurs de `continent` et `population` dans le CSV
df['continent'] = df['continent'].fillna('Unknown')  
df['population'] = df['population'].fillna(0).astype(int)

# 📌 Étape 1 : Insérer les pays avec leurs informations
countries_df = df[["Country_Region", "continent", "population"]].drop_duplicates()

with engine.connect() as conn:
    for _, row in countries_df.iterrows():
        conn.execute(text(
            """
            INSERT INTO Countries (name, continent, population) 
            VALUES (:name, :continent, :population)
            ON DUPLICATE KEY UPDATE 
                continent = VALUES(continent), 
                population = VALUES(population);
            """
        ), {"name": row["Country_Region"], "continent": row["continent"], "population": row["population"]})
    conn.commit()

print("✅ Pays insérés avec succès dans `Countries`!")

# 📌 Étape 2 : Vérifier que les données sont bien insérées
countries_db = pd.read_sql("SELECT id_country, name, continent, population FROM Countries", con=engine)
print("📌 Vérification après insertion :")
print(countries_db.head())

# 📌 Étape 3 : Associer `id_country` aux données de `PandemicData`
df = df.merge(countries_db, left_on="Country_Region", right_on="name", how="left")
print("📌 Colonnes disponibles après merge :", df.columns.tolist())

# Supprimer les colonnes en fonction des nouveaux noms générés par le merge
df = df.drop(columns=["Country_Region", "continent_x", "population_x", "name"])


# 📌 Vérifier que toutes les colonnes nécessaires sont là
expected_columns_pandemic = ["date", "id_country", "Deaths", "Recovered", "total_cases", "total_deaths",
                             "total_recovered", "total_tests", "New_cases", "New_deaths", "New_recovered",
                             "active_cases", "Serious_Critical", "TrueConfirmed", "Active"]

missing_columns_pandemic = [col for col in expected_columns_pandemic if col not in df.columns]
if missing_columns_pandemic:
    print(f"❌ Colonnes manquantes dans `PandemicData` : {missing_columns_pandemic}")
    exit()

# 📌 Étape 4 : Insérer les données dans `PandemicData`
df[expected_columns_pandemic].to_sql("pandemicdata", con=engine, if_exists="append", index=False)

print("✅ Données insérées avec succès dans `PandemicData` !")
