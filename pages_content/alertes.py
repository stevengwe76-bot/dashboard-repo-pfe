"""
CamerTrust Lite - Page Alertes
E3 - Frontend et Coordinateur | S6
"""

from datetime import date, datetime

import pandas as pd
import streamlit as st

from api_client import get_alerts


def render():
    st.title("Alertes de fraude")
    st.caption("Transactions detectees comme frauduleuses par le modele")

    col1, col2 = st.columns(2)
    with col1:
        date_filter = st.date_input("Depuis le", value=None, format="YYYY-MM-DD")
    with col2:
        min_amount = st.number_input(
            "Montant minimum (FCFA)", min_value=0, value=0, step=1000
        )

    date_from_str = None
    if isinstance(date_filter, date):
        date_from_str = datetime.combine(date_filter, datetime.min.time()).isoformat()

    alerts = get_alerts(
        limit=500,
        date_from=date_from_str,
        min_amount=min_amount if min_amount > 0 else None,
    )

    if not alerts:
        st.success("Aucune alerte pour les criteres selectionnes. Bon signe !")
        return

    df = pd.DataFrame(alerts)
    df["created_at"] = pd.to_datetime(df["created_at"])
    df = df.sort_values("created_at", ascending=False)

    st.metric("Nombre d'alertes", len(df))

    display_df = df[["created_at", "type", "amount", "score", "latency_ms"]].rename(
        columns={
            "created_at": "Date",
            "type": "Type",
            "amount": "Montant (FCFA)",
            "score": "Score de fraude",
            "latency_ms": "Latence (ms)",
        }
    )

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    csv_bytes = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Exporter en CSV",
        data=csv_bytes,
        file_name=f"alertes_camertrust_{date.today().isoformat()}.csv",
        mime="text/csv",
    )
