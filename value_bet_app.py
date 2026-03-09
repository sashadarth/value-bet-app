import streamlit as st
import requests
import pandas as pd

# 🔴 CAMBIA LA PRIMA VOLTA: metti la tua API key gratuita
API_KEY = "4c5aadfe776d4975d63720c8acd38b9b"

# 🔴 PASSWORD DEL MESE (da cambiare ogni mese)
PASSWORD_MESE = "negri"

# --- Login ---
pw = st.text_input("Inserisci la password del mese", type="password")
if pw != PASSWORD_MESE:
    st.error("Password errata!")
    st.stop()

st.title("Calcolo Value Bet")

# --- Scegli la lega ---
lega = st.selectbox("Scegli la lega", [
    "PD", "SA", "PL", "BL1", "FL1", "DED", "PPL",
    "CL", "EL", "CLF", "FAC", "CI", "SC", "CUP"
])  # PD=La Liga, SA=Serie A, PL=Premier League, ecc.

# --- Prendi squadre dall'API ---
def get_teams(lega):
    url = f"https://api.football-data.org/v4/competitions/{lega}/teams"
    headers = {"X-Auth-Token": API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        st.error("Errore nel recupero dati")
        st.stop()
    teams = [team['name'] for team in response.json().get('teams', [])]
    return teams

squadre = get_teams(lega)
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

# --- Inserisci le quote dei bookmaker ---
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
        prob = 0.5  # esempio di probabilità automatica dall'API
        dati_matematici.append({
            "mercato": mercato,
            "prob_matematica": prob,
            "quota_book": quote_input[mercato]
        })
    df_value = calcola_value(dati_matematici)
    
    # Evidenzia verde/rosso
    def coloriza(row):
        return ["background-color: lightgreen" if v > 0 else "background-color: salmon" 
                for v in row if isinstance(v, (int,float))]
    
    st.subheader("Value Bet Positive")
    st.dataframe(df_value.style.apply(coloriza, axis=1))
