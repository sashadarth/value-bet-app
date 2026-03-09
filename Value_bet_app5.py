import streamlit as st
import requests
import pandas as pd

# 🔴 CAMBIA LA PRIMA VOLTA: inserisci la tua API Key SportDB.dev
API_KEY = "bh67CfAZ4YcWIyQTHynAGv52AqnEzNjLSAHOYAeG"

# 🔴 PASSWORD DEL MESE (cambia ogni mese)
PASSWORD_MESE = "negri"

# --- Login ---
pw = st.text_input("Inserisci la password del mese", type="password")
if pw != PASSWORD_MESE:
    st.error("Password errata!")
    st.stop()

st.title("Calcolo Value Bet SportDB.dev")

# --- Funzione per ottenere tutte le nazioni / leghe ---
def get_competitions():
    url_countries = "https://api.sportdb.dev/api/football/countries"
    headers = {"X-API-Key": API_KEY}
    try:
        response = requests.get(url_countries, headers=headers, timeout=10)
        response.raise_for_status()
        countries = response.json().get("data", [])
        competitions_dict = {}
        for country in countries:
            slug = country["slug"]
            url_comp = f"https://api.sportdb.dev/api/football/{slug}"
            r = requests.get(url_comp, headers=headers, timeout=10)
            r.raise_for_status()
            comps = r.json().get("data", [])
            for comp in comps:
                competitions_dict[f"{comp['name']} ({country['name']})"] = {
                    "country_slug": slug,
                    "competition_slug": comp["slug"],
                    "available_seasons": comp.get("seasons", [])
                }
        return competitions_dict
    except requests.exceptions.RequestException as e:
        st.error(f"Errore nel recupero dati: {e}")
        st.stop()

competitions = get_competitions()
lega = st.selectbox("Scegli la lega", list(competitions.keys()))
selected = competitions[lega]

# --- Selezione stagione disponibile ---
stagioni = selected["available_seasons"]
if not stagioni:
    st.error("Non ci sono stagioni disponibili per questa lega.")
    st.stop()
season = st.selectbox("Scegli la stagione", stagioni)

# --- Funzione per ottenere squadre della stagione ---
def get_teams(country_slug, competition_slug, season):
    url = f"https://api.sportdb.dev/api/football/{country_slug}/{competition_slug}/{season}/standings"
    headers = {"X-API-Key": API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        teams = [team["team"]["name"] for team in data.get("data", [])]
        if not teams:
            st.error("Nessuna squadra trovata per questa stagione.")
            st.stop()
        return teams
    except requests.exceptions.RequestException as e:
        st.error(f"Errore nel recupero squadre: {e}")
        st.stop()

squadre = get_teams(selected["country_slug"], selected["competition_slug"], season)
squadra_casa = st.selectbox("Squadra in casa", squadre)
squadra_ospite = st.selectbox("Squadra ospite", squadre)

# --- Mercati principali ---
mercati = [
    "1X2","Doppia Chance","Draw No Bet","Risultato Esatto",
    "Risultato Primo Tempo","Risultato Secondo Tempo","Risultato + Over/Under",
    "Over/Under Gol","Multigol","Gol/No Gol","Gol Primo Tempo",
    "Gol Secondo Tempo","Squadra Segna Primo Gol","Squadra Segna Ultimo Gol",
    "Entrambe + Over","1 + Over/Under","2 + Over/Under",
    "Corner Totali","Corner Casa","Corner Ospite","Corner Primo Tempo",
    "Corner Secondo Tempo","Primo a 3 Corner","Primo a 5 Corner","Primo a 7 Corner",
    "Almeno X Corner Squadra","Corner Handicap",
    "Cartellini Totali","Cartellini Casa","Cartellini Ospite","Cartellini Primo Tempo","Cartellini Handicap",
    "Falli Casa","Falli Ospite","Falli Totali","Falli Primo Tempo","Falli Secondo Tempo",
    "Tiri Totali","Tiri Casa","Tiri Ospite","Tiri in Porta Totali","Tiri in Porta Casa","Tiri in Porta Ospite"
]

# --- Inserimento quote bookmaker ---
quote_input = {}
for mercato in mercati:
    quote_input[mercato] = st.number_input(f"Inserisci quota {mercato}", min_value=1.0, step=0.01)

# --- Calcolo value bet ---
def calcola_value(dati):
    df = pd.DataFrame(dati)
    df["value_%"] = (df["prob_matematica"] / df["quota_book"] - 1) * 100
    return df

# --- Bottone calcolo ---
if st.button("Calcola Value Bet"):
    dati_matematici = []
    for mercato in mercati:
        prob = 0.5  # probabilità placeholder: sostituire con calcolo reale se disponibile
        dati_matematici.append({
            "mercato": mercato,
            "prob_matematica": prob,
            "quota_book": quote_input[mercato]
        })
    df_value = calcola_value(dati_matematici)
    
    # Evidenzia verde/rosso
    def coloriza(row):
        return ["background-color: lightgreen" if isinstance(v,(int,float)) and v>0 else
                "background-color: salmon" for v in row]
    
    st.subheader("Value Bet")
    st.dataframe(df_value.style.apply(coloriza, axis=1))
