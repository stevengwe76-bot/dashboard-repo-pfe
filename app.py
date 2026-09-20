"""
CamerTrust Lite - Dashboard
E3 - Frontend et Coordinateur | S2, S5, S6, S7, S9

Lancer en local :
  streamlit run dashboard/app.py

Deployer sur Streamlit Cloud :
  https://share.streamlit.io -> New app -> pointer sur ce fichier
  Puis configurer .streamlit/secrets.toml dans Settings -> Secrets
  (SEUL endroit a modifier pour relier ce dashboard a l'API deployee).
"""

import streamlit as st

from api_client import check_health, get_api_url
from pages_content import accueil, alertes, prediction

st.set_page_config(
    page_title="CamerTrust Lite",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Sidebar : navigation + statut de connexion a l'API
# ---------------------------------------------------------------------------
st.sidebar.title("🛡️ CamerTrust Lite")
st.sidebar.caption("Detection de fraude Mobile Money")

page = st.sidebar.radio("Page", ["Accueil", "Alertes", "Prediction"])

st.sidebar.divider()

api_ok, api_message = check_health()
if api_ok:
    st.sidebar.success(f"● {api_message}")
else:
    st.sidebar.error(f"● {api_message}")
st.sidebar.caption(f"API : `{get_api_url()}`")

st.sidebar.divider()
st.sidebar.caption(
    "CamerTrust protege votre argent, pas vos habitudes.\n\n"
    "Aucune donnee personnelle n'est conservee au-dela de la transaction analysee."
)

# ---------------------------------------------------------------------------
# Routage vers la page selectionnee
# ---------------------------------------------------------------------------
if page == "Accueil":
    accueil.render()
elif page == "Alertes":
    alertes.render()
elif page == "Prediction":
    prediction.render()
