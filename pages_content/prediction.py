"""
CamerTrust Lite - Page Prediction
E3 - Frontend et Coordinateur | S7
"""

import plotly.graph_objects as go
import streamlit as st

from api_client import predict

TRANSACTION_TYPES = ["TRANSFER", "CASH_OUT", "PAYMENT", "CASH_IN", "DEBIT"]


def _render_gauge(score_pct: float, is_fraud: bool):
    color = "#e74c3c" if is_fraud else "#2ecc71"
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score_pct,
            number={"suffix": " %"},
            title={"text": "Score de risque de fraude"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": color},
                "steps": [
                    {"range": [0, 40], "color": "#eafaf1"},
                    {"range": [40, 70], "color": "#fef9e7"},
                    {"range": [70, 100], "color": "#fdedec"},
                ],
                "threshold": {
                    "line": {"color": "black", "width": 3},
                    "thickness": 0.8,
                    "value": score_pct,
                },
            },
        )
    )
    fig.update_layout(height=320, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig, use_container_width=True)


def render():
    st.title("Analyser une transaction")
    st.caption("Saisis les details d'une transaction pour obtenir un score de risque en temps reel")

    with st.form("transaction_form"):
        col1, col2 = st.columns(2)
        with col1:
            amount = st.number_input(
                "Montant (FCFA)", min_value=1.0, value=50000.0, step=1000.0
            )
            tx_type = st.selectbox("Type de transaction", TRANSACTION_TYPES)
        with col2:
            old_balance_org = st.number_input(
                "Solde emetteur avant", min_value=0.0, value=100000.0, step=1000.0
            )
            new_balance_org = st.number_input(
                "Solde emetteur apres", min_value=0.0, value=50000.0, step=1000.0
            )

        with st.expander("Informations destinataire (optionnel)"):
            col3, col4 = st.columns(2)
            with col3:
                old_balance_dest = st.number_input(
                    "Solde destinataire avant", min_value=0.0, value=0.0, step=1000.0
                )
            with col4:
                new_balance_dest = st.number_input(
                    "Solde destinataire apres", min_value=0.0, value=50000.0, step=1000.0
                )

        submitted = st.form_submit_button("Analyser la transaction", type="primary")

    if submitted:
        payload = {
            "amount": amount,
            "type": tx_type,
            "old_balance_org": old_balance_org,
            "new_balance_org": new_balance_org,
            "old_balance_dest": old_balance_dest,
            "new_balance_dest": new_balance_dest,
        }

        with st.spinner("Analyse en cours..."):
            result = predict(payload)

        if result is not None:
            score_pct = result["score"] * 100
            is_fraud = result["is_fraud"]

            _render_gauge(score_pct, is_fraud)

            if is_fraud:
                st.error(
                    f"**Transaction suspecte** — score {score_pct:.1f}% "
                    f"(seuil : {result['threshold'] * 100:.0f}%)"
                )
            else:
                st.success(
                    f"**Transaction consideree comme legitime** — score {score_pct:.1f}% "
                    f"(seuil : {result['threshold'] * 100:.0f}%)"
                )

            st.caption(f"Temps de reponse de l'API : {result['latency_ms']:.0f} ms")
