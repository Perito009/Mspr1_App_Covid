import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import time
import datetime

API_URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="📊 Dashboard DOKVID", layout="wide")
st.title("📊 Dashboard Interactif - Pandémies COVID")

# 📌 Onglets : Dashboard | Gestion des données
tabs = st.tabs(["📊 Dashboard", "⚙️ Gestion des données"])

# ✅ Charger la liste des pays et continents
# @st.cache_data
def get_countries():
    response = requests.get(f"{API_URL}/countries")
    df = pd.DataFrame(response.json())
    df = df[df["continent"].apply(lambda x: isinstance(x, str) and x.strip() != "0")]
    return df

countries_df = get_countries()
continent_list = sorted(countries_df["continent"].dropna().unique().tolist())

default_continent = "Africa" if "Africa" in continent_list else continent_list[2]

if "selected_continent" not in st.session_state:
    st.session_state.selected_continent = default_continent

selected_continent = st.sidebar.selectbox(
    "🌎 Continent",
    continent_list,
    key="selected_continent"
)

filtered_countries = countries_df[countries_df["continent"] == selected_continent]

if "selected_country_id" not in st.session_state or st.session_state.selected_continent != selected_continent:
    st.session_state.selected_country_id = filtered_countries["id_country"].iloc[0]

country_dict = dict(zip(filtered_countries["id_country"], filtered_countries["name"]))

country_id = st.sidebar.selectbox(
    "🏳️ Pays",
    options=country_dict.keys(),
    format_func=lambda x: country_dict[x],
    key="selected_country_id"
)

# @st.cache_data
def load_data(country_id):
    response = requests.get(f"{API_URL}/data?id_country={country_id}")
    df = pd.DataFrame(response.json())

    if df.empty:
        return df  # Retourner un dataframe vide si aucune donnée

    numeric_cols = ["total_cases", "new_cases", "total_deaths", "new_deaths", "total_recovered", "New_recovered"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["date"] = pd.to_datetime(df["date"], errors='coerce')

    return df

df = load_data(country_id)

# 📊 **Onglet 1 : Dashboard**
with tabs[0]:
    if not df.empty:
        fig1 = px.line(df, x="date", y="new_cases",
                       title=f"📈 Évolution des Nouveaux Cas / Jour - {country_dict[country_id]}",
                       markers=True)
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = px.line(df, x="date", y="new_deaths",
                       title=f"💀 Évolution des Nouveaux Décès / Jour - {country_dict[country_id]}",
                       markers=True)
        st.plotly_chart(fig2, use_container_width=True)

        fig3 = px.line(df, x="date", y="New_recovered",
                       title=f"❤️ Évolution des Nouvelles Guérisons / Jour - {country_dict[country_id]}",
                       markers=True)
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader(f"📋 Données détaillées - {country_dict[country_id]}")
        st.dataframe(df[["date", "total_cases", "new_cases", "total_deaths", "new_deaths", "total_recovered", "New_recovered"]])
    else:
        st.warning("Aucune donnée disponible pour ce pays.")

# ⚙️ **Onglet 2 : Gestion des données**
with tabs[1]:
    st.subheader(f"📋 Modifier ou Supprimer des données - {country_dict[country_id]}")

    if df.empty:
        st.warning("⚠️ Aucune donnée disponible pour ce pays.")
    else:
        df_editable = df.copy()
        df_editable["🗑️ Supprimer"] = False  # Ajouter une colonne pour suppression

        edited_df = st.data_editor(df_editable, num_rows="fixed", key="edit_data")

        if st.button("✅ Appliquer les modifications"):
            # st.write("Données envoyées à l'API:", update_data)  # Debug
            try:
                # Assurer que les colonnes sont identiques
                common_columns = list(df.columns)  # Prendre uniquement les colonnes du DataFrame d'origine
                edited_df = edited_df[common_columns]  # Supprime les colonnes ajoutées comme "🗑️ Supprimer"

                # Réinitialiser les index pour s'assurer qu'ils correspondent
                edited_df = edited_df.reset_index(drop=True)
                df = df.reset_index(drop=True)

                # Identifier les lignes modifiées
                modified_rows = edited_df.compare(df, keep_shape=True, keep_equal=False).dropna(how="all")

                if modified_rows.empty:
                    st.warning("⚠️ Aucune modification détectée.")
                else:
                    for index in modified_rows.index:
                        row = edited_df.loc[index]

                        update_data = {
                            "id_country": int(country_id),
                            "date": row["date"].strftime("%Y-%m-%d") if pd.notna(row["date"]) else None,
                            "new_cases": int(row["new_cases"]) if not pd.isna(row["new_cases"]) else 0,
                            "new_deaths": int(row["new_deaths"]) if not pd.isna(row["new_deaths"]) else 0,
                            "New_recovered": int(row["New_recovered"]) if not pd.isna(row["New_recovered"]) else 0
                        }

                        
                        # Envoi à l'API
                        response = requests.put(f"{API_URL}/update/{update_data['id_country']}/{update_data['date']}", json=update_data)


                        if response.status_code == 200:
                            st.success(f"✅ Données du {update_data['date']} mises à jour avec succès !")
                        else:
                            st.error(f"❌ Erreur lors de la modification des données du {update_data['date']}. Réponse API : {response.text}")

            except Exception as e:
                st.error(f"🚨 Une erreur est survenue : {e}")

    if st.button("🗑️ Supprimer les lignes sélectionnées"):
        rows_to_delete = edited_df[edited_df["🗑️ Supprimer"] == True]
        for _, row in rows_to_delete.iterrows():
            if pd.notna(row["date"]):
                # Envoi de la requête DELETE avec id_country et date
                response = requests.delete(f"{API_URL}/data/{int(country_id)}/{row['date'].strftime('%Y-%m-%d')}")

                if response.status_code == 200:
                    st.success(f"🗑️ Données du {row['date']} supprimées avec succès !")
                else:
                    st.error(f"❌ Erreur lors de la suppression des données du {row['date']}. Réponse API : {response.text}")
        time.sleep(2)        
        st.rerun()  # Recharger la page pour voir les changements

    st.subheader("➕ Ajouter une nouvelle donnée")

    # Formulaire pour saisir les nouvelles données
    with st.form("add_data_form"):
        country_name = st.text_input("Nom du pays", "")
        continent = st.text_input("Continent", "")
        population = st.number_input("Population", min_value=1, step=1)
        date = st.date_input("Date", datetime.date.today())
        total_cases = st.number_input("total_cases", min_value=0, step=1)
        total_deaths = st.number_input("total_deaths", min_value=0, step=1)
        new_cases = st.number_input("new_cases", min_value=0, step=1)
        new_deaths = st.number_input("new_deaths", min_value=0, step=1)
        total_recovered = st.number_input("total_recovered", min_value=0, step=1)
        active_cases = st.number_input("active_cases", min_value=0, step=1)
        serious_critical = st.number_input("serious_critical", min_value=0, step=1)
        true_confirmed = st.number_input("true_confirmed", min_value=0, step=1)

        submit_button = st.form_submit_button(label="Ajouter la donnée")

    # Si le formulaire est soumis
    if submit_button:
        # Créer le dictionnaire avec les données
        data = {
            "country": country_name,
            "continent": continent,
            "population": population,
            "date": date.strftime('%Y-%m-%d'),
            "total_cases": total_cases,
            "total_deaths": total_deaths,
            "new_cases": new_cases,
            "new_deaths": new_deaths,
            "total_recovered": total_recovered,
            "active_cases": active_cases,
            "serious_critical": serious_critical,
            "TrueConfirmed": true_confirmed
        }

        # Envoi des données à l'API via POST
        response = requests.post(f"{API_URL}/add", json=data)

        # Afficher un message en fonction de la réponse
        if response.status_code == 201:
            st.success("✅ Données ajoutées avec succès!")
        else:
            st.error(f"❌ Erreur lors de l'ajout des données. {response.text}")


