import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from datetime import datetime
from yfinance import Ticker, download, Market

# Configuration de la page
st.set_page_config(page_title="Dashboard Financier", layout="wide")

# Menu latéral
st.sidebar.title("📈 Navigation")
page = st.sidebar.radio("Aller à", ["Calculateur d'Intérêts", "Portefeuille", "Watchlist", "Marchés", "Informations Financières"])

# Fonction pour calculer intérêts composés
def calculer_capital(montant, taux, duree, type_invest="Actions"):
    capital = 0
    evolution = []
    for annee in range(1, duree + 1):
        taux_ajuste = taux / 100 * (1.2 if type_invest == "Actions" else 0.8)
        capital = (capital + montant) * (1 + taux_ajuste)
        evolution.append((annee, round(capital, 2)))
    return pd.DataFrame(evolution, columns=["Année", "Capital accumulé"])

# Fonction pour calculer la volatilité et la VaR
def calculer_risque(data_close):
    rendements = data_close.pct_change().dropna()
    if len(rendements) < 2:
        return "N/A", "N/A"
    volatilite = rendements.std() * np.sqrt(252)
    var = np.percentile(rendements, 5)
    return volatilite, var

# Pages
if page == "Calculateur d'Intérêts":
    st.title("💰 Calculateur d'Intérêts Composés")
    montant = st.number_input("Montant investi par an ($)", 1000.0)
    taux = st.number_input("Taux d'intérêt (%)", 5.0)
    duree = st.number_input("Durée (années)", 10)
    type_invest = st.selectbox("Type d'investissement", ["Actions", "Obligations"])

    if st.button("Calculer"):
        df = calculer_capital(montant, taux, int(duree), type_invest)
        st.line_chart(df.set_index("Année"))
        st.dataframe(df)
        st.success(f"Capital final : ${df['Capital accumulé'].iloc[-1]:,.2f}")

elif page == "Portefeuille":
    st.title("📊 Mon Portefeuille")
    if "portefeuille" not in st.session_state:
        st.session_state.portefeuille = pd.DataFrame(columns=["Symbole", "Quantité", "Prix Achat", "Prix Actuel"])

    symbole = st.text_input("Symbole à ajouter")
    quantite = st.number_input("Quantité", 0.0)
    if st.button("Ajouter"):
        if symbole:
            info = Ticker(symbole).history(period="1d")
            if not info.empty:
                prix_actuel = info["Close"].iloc[-1]
                new_row = {"Symbole": symbole.upper(), "Quantité": quantite, "Prix Achat": prix_actuel, "Prix Actuel": prix_actuel}
                st.session_state.portefeuille = pd.concat([st.session_state.portefeuille, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"{symbole.upper()} ajouté !")

    if not st.session_state.portefeuille.empty:
        st.subheader("Détails du portefeuille")
        st.session_state.portefeuille["Valeur Totale"] = st.session_state.portefeuille["Quantité"] * st.session_state.portefeuille["Prix Actuel"]
        st.dataframe(st.session_state.portefeuille)

elif page == "Watchlist":
    st.title("👀 Ma Watchlist")
    if "watchlist" not in st.session_state:
        st.session_state.watchlist = []

    symbole_watch = st.text_input("Ajouter à la watchlist")
    if st.button("Ajouter à Watchlist"):
        if symbole_watch:
            st.session_state.watchlist.append(symbole_watch.upper())
            st.success(f"{symbole_watch.upper()} ajouté à la watchlist !")

    if st.session_state.watchlist:
        st.subheader("Prix actuel des actions")
        prix = {}
        for symb in st.session_state.watchlist:
            data = Ticker(symb).history(period="1d")
            prix[symb] = data["Close"].iloc[-1] if not data.empty else "N/A"
        st.dataframe(pd.DataFrame.from_dict(prix, orient='index', columns=["Prix Actuel"]))

elif page == "Marchés":
    st.title("🌍 Marchés Financiers")
    st.subheader("Indices Principaux")
    indices = ["^GSPC", "^DJI", "^IXIC", "^RUT"]
    data = download(indices, period="1d")
    if not data.empty:
        cours = data["Close"].iloc[-1]
        st.dataframe(cours)

elif page == "Informations Financières":
    st.title("ℹ️ Détails Financiers")
    symbole_info = st.text_input("Entrez un symbole pour voir les informations")
    if symbole_info:
        try:
            actif = Ticker(symbole_info)
            info = actif.info
            st.header(f"{info.get('longName', symbole_info.upper())}")

            st.write(f"**Secteur** : {info.get('sector', 'N/A')}")
            st.write(f"**Prix Actuel** : ${info.get('currentPrice', 'N/A')}")
            st.write(f"**PER** : {info.get('trailingPE', 'N/A')}")
            st.write(f"**Dividende** : {info.get('dividendYield', 'N/A')}")
            st.write(f"**Market Cap** : ${info.get('marketCap', 'N/A'):,}")

            historique = actif.history(period="1y")
            if not historique.empty:
                st.line_chart(historique["Close"])
        except Exception as e:
            st.error(f"Erreur : {e}")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption(f"Mis à jour le : {datetime.now().strftime('%d/%m/%Y')}")