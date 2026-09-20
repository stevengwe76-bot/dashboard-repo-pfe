"""
CamerTrust Lite - Page Accueil
E3 - Frontend et Coordinateur | S5
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from api_client import get_transactions


def render():
    st.title("Vue d'ensemble")
    st.caption("Metriques en temps reel issues des transactions analysees par l'API")

    transactions = get_transactions(limit=500)

    if not transactions:
        st.info(
            "Aucune transaction analysee pour le moment. "
            "Rends-toi sur la page **Prediction** pour tester une transaction."
        )
        return

    df = pd.DataFrame(transactions)
    df["created_at"] = pd.to_datetime(df["created_at"])

    total = len(df)
    nb_fraudes = int(df["is_fraud"].sum())
    taux_fraude = (nb_fraudes / total * 100) if total else 0
    latence_moy = df["latency_ms"].mean() if "latency_ms" in df else None

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Transactions analysees", f"{total:,}".replace(",", " "))
    col2.metric("Fraudes detectees", nb_fraudes)
    col3.metric("Taux de fraude", f"{taux_fraude:.1f} %")
    col4.metric(
        "Latence moyenne",
        f"{latence_moy:.0f} ms" if latence_moy is not None and pd.notna(latence_moy) else "N/A",
    )

    st.divider()

    st.subheader("Transactions par heure")
    df["heure"] = df["created_at"].dt.floor("h")
    par_heure = df.groupby(["heure", "is_fraud"]).size().reset_index(name="nombre")
    par_heure["statut"] = par_heure["is_fraud"].map({True: "Fraude", False: "Legitime"})

    fig = px.bar(
        par_heure,
        x="heure",
        y="nombre",
        color="statut",
        color_discrete_map={"Fraude": "#e74c3c", "Legitime": "#2ecc71"},
        title="Volume de transactions par heure",
        labels={"heure": "Heure", "nombre": "Nombre de transactions", "statut": "Statut"},
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Repartition par type de transaction")
    fig2 = px.pie(df, names="type", title="Types de transactions analysees")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Dernieres transactions")
    st.dataframe(
        df[["created_at", "type", "amount", "score", "is_fraud"]]
        .sort_values("created_at", ascending=False)
        .head(10),
        use_container_width=True,
        hide_index=True,
    )
