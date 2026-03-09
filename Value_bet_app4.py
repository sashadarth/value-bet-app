import streamlit as st
import requests
import pandas as pd

# 🔴 CAMBIA LA PRIMA VOLTA: inserisci la tua API Key di SportDB.dev
API_KEY = "hQ0vz3tXDrZm7vmsY7n4chWNch9jHUY8dtWGq0Ot"

# 🔴 PASSWORD DEL MESE (cambia ogni mese)
PASSWORD_MESE = "negri"

# --- Login ---
pw = st.text_input("Inserisci la password del mese", type="password")
if pw != PASSWORD_MESE:
    st.error("Password errata!")
    st.stop()

st.title("Calcolo Value Bet 2025/2026 - SportDB.dev")

# --- Stagione ---
SEASON = "2025-2026"  # puoi usare la stagione corrente disponibile

# --- Leghe con slug SportDB.dev ---
lega_slug = {
    "Serie A": "italy/serie-a",
    "Premier League": "england/premier-league",
    "La Liga": "spain/la-liga",
    "Bundesliga": "germany/bundesliga",
    "Ligue 1": "france/ligue-1",
    "Eredivisie": "netherlands/eredivisie",
    "Liga Portoghese": "portugal/liga-portugal"
}

# --- Seleziona lega ---
lega = st.selectbox("Scegli la lega", list(lega_slug.keys()))
slug_lega = lega_slug[lega]

# --- Funzione per ottenere squadre ---
def get_teams(slug_lega):
    url = f"https://api.sportdb.dev/api/football/{slug_lega}/{SEASON}/standings"
    headers = {"X-API-Key": API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        teams = [team['team']['name'] for team in data.get('data', [])]
        if not teams:
            st.error("Nessuna squadra trovata per questa lega/stagione. Controlla la tua API Key e la stagione.")
            st.stop()
        return teams
    except requests.exceptions.RequestException as e:
        st.error(f"Errore nel recupero dati: {e}")
        st.stop()

squadre = get_teams(slug_lega)
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
        prob = 0.5  # Placeholder probabilità automatica: sostituire con logica reale se vuoi
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
