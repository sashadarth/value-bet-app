import streamlit as st
import requests
import pandas as pd

# 🔴 CAMBIA LA PRIMA VOLTA: inserisci la tua API key di API-Football
API_KEY = "4c5aadfe776d4975d63720c8acd38b9b"

# 🔴 PASSWORD DEL MESE (cambia ogni mese)
PASSWORD_MESE = "negri"

# --- Login ---
pw = st.text_input("Inserisci la password del mese", type="password")
if pw != PASSWORD_MESE:
    st.error("Password errata!")
    st.stop()

st.title("Calcolo Value Bet 2025/2026")

# --- Stagione ---
SEASON = 2025  # stagione 2025/2026

# --- Leghe con nomi completi e ID API-Football ---
lega_id = {
    "Serie A": 135,
    "Premier League": 39,
    "La Liga": 140,
    "Bundesliga": 78,
    "Ligue 1": 61,
    "Eredivisie": 88,
    "Liga Portoghese": 94,
    "Champions League": 2,
    "Europa League": 3,
    "FA Cup": 45,
    "Coppa Italia": 41,
    "Supercoppa": 42,
    "Coppa Spagnola": 43
}

# --- Seleziona lega ---
lega = st.selectbox("Scegli la lega", list(lega_id.keys()))
codice_lega = lega_id[lega]

# --- Funzione per ottenere squadre ---
def get_teams(lega_codice):
    url = f"https://v3.football.api-sports.io/teams?league={lega_codice}&season={SEASON}"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "v3.football.api-sports.io"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        st.write("Debug API response:", data)  # per controllare il JSON
        teams = [team['team']['name'] for team in data.get('response', [])]
        if not teams:
            st.error("Nessuna squadra trovata per questa lega/stagione.")
            st.stop()
        return teams
    except requests.exceptions.RequestException as e:
        st.error(f"Errore nel recupero dati: {e}")
        st.stop()

squadre = get_teams(codice_lega)
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

# --- Calcolo automatico value bet ---
def calcola_value(dati):
    df = pd.DataFrame(dati)
    df["value_%"] = (df["prob_matematica"] / df["quota_book"] - 1) * 100
    return df

# Bottone calcolo
if st.button("Calcola Value Bet"):
    dati_matematici = []
    for mercato in mercati:
        prob = 0.5  # Placeholder probabilità automatica
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
