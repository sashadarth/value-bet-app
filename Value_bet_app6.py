import pandas as pd
import streamlit as st

# 🔴 PASSWORD DEL MESE (cambia ogni mese)
PASSWORD_MESE = "negri"

# --- Funzione di login ---
def login():
    pw = st.text_input("Inserisci la password del mese", type="password")
    if pw != PASSWORD_MESE:
        st.error("Password errata!")
        st.stop()

# --- Menu competizioni ---
competizioni = [
    "Serie A", "Premier League", "La Liga", "Bundesliga", "Ligue 1",
    "Eredivisie", "Liga Portoghese", "Champions League", "Europa League", "FA Cup"
]

st.title("Calcolo Value Bet - Tutti i mercati di squadra")
login()  # login con password

competizione = st.selectbox("Scegli la competizione", competizioni)

# 🔴 Inserisci qui il percorso CSV per ogni competizione
csv_per_competizione = {
    "Serie A": "Percorso/SerieA.csv",
    "Premier League": "Percorso/Premier.csv",
    "La Liga": "Percorso/LaLiga.csv",
    "Bundesliga": "Percorso/Bundesliga.csv",
    "Ligue 1": "Percorso/Ligue1.csv",
    "Eredivisie": "Percorso/Eredivisie.csv",
    "Liga Portoghese": "Percorso/LigaPortoghese.csv",
    "Champions League": "Percorso/Champions.csv",
    "Europa League": "Percorso/Europa.csv",
    "FA Cup": "Percorso/FAcup.csv"
}

file_csv = csv_per_competizione[competizione]

# --- Leggi CSV ---
df = pd.read_csv(file_csv)

# --- Funzione Value Bet ---
def value(prob, quota):
    return (prob*100/quota)-100

def colore(val):
    return "POSITIVO ✅" if val>0 else "NEGATIVO ❌"

# --- Lista mercati principali di squadra ---
mercati = [
    "1X2_Home", "1X2_Draw", "1X2_Away",
    "Over2.5", "Under2.5",
    "Gol_Casa", "Gol_Ospite",
    "Corner_Totali", "Corner_Casa", "Corner_Ospite", "Corner_Primo_Tempo", "Corner_Secondo_Tempo",
    "Primo_3_Corner", "Primo_5_Corner", "Primo_7_Corner", "Almeno_X_Corner", "Corner_Handicap",
    "Cartellini_Totali", "Cartellini_Casa", "Cartellini_Ospite", "Cartellini_Primo_Tempo", "Cartellini_Handicap",
    "Falli_Totali", "Falli_Casa", "Falli_Ospite", "Falli_Primo_Tempo", "Falli_Secondo_Tempo",
    "Tiri_Totali", "Tiri_Casa", "Tiri_Ospite", "Tiri_in_Porta_Totali", "Tiri_in_Porta_Casa", "Tiri_in_Porta_Ospite"
]

# --- Input quote bookmaker ---
st.subheader("Inserisci le quote dei bookmaker")
quote_input = {}
for mercato in mercati:
    quote_input[mercato] = st.number_input(f"Inserisci quota {mercato}", min_value=1.0, step=0.01)

# --- Bottone per calcolo value ---
if st.button("Calcola Value Bet"):
    dati_matematici = []
    for mercato in mercati:
        # 🔹 qui puoi calcolare probabilità reali dal CSV se disponibili
        # altrimenti inserire un placeholder 0.5
        prob = df[mercato].iloc[0] if mercato in df.columns else 0.5
        dati_matematici.append({
            "mercato": mercato,
            "prob_matematica": prob,
            "quota_book": quote_input[mercato]
        })

    # Calcolo value
    df_value = pd.DataFrame(dati_matematici)
    df_value["value"] = (df_value["prob_matematica"] * 100 / df_value["quota_book"]) - 100
    # Mostra colori
    df_value["colore"] = df_value["value"].apply(lambda x: "POSITIVO ✅" if x>0 else "NEGATIVO ❌")
    st.subheader("Value Bet per tutti i mercati di squadra")
    st.dataframe(df_value)
