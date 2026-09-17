"""
CamerTrust — Dashboard de Détection de Fraude Mobile Money
SUP'PTIC · Promotion 2023-2026 · Projet de Fin d'Études

Lancement : streamlit run dashboard/app.py
"""
import streamlit as st
import pandas as pd
from datetime import datetime

from utils.mock_data import (gen_transactions, gen_alerts,
                              gen_hourly_stats, gen_global_stats)
from utils.api_client import check_health

# ── Configuration page ────────────────────────────────────────────────────────
st.set_page_config(
    page_title = "CamerTrust — Détection de Fraude",
    page_icon  = "🛡️",
    layout     = "wide",
    initial_sidebar_state = "expanded",
    timeout = 15,
)

# ── CSS personnalisé ──────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Fond principal */
.main { background-color: #0A2342; }
[data-testid="stAppViewContainer"] { background-color: #0A2342; }
[data-testid="stSidebar"] { background-color: #0F2D52; border-right: 1px solid #028090; }

/* Cartes métriques */
.metric-card {
    background: linear-gradient(135deg, #0F2D52 0%, #1a3a6c 100%);
    border: 1px solid #028090;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    margin-bottom: 12px;
    box-shadow: 0 4px 15px rgba(2, 128, 144, 0.15);
}
.metric-value {
    font-size: 2.2rem;
    font-weight: 800;
    color: #02C39A;
    line-height: 1.1;
    margin: 6px 0 4px 0;
}
.metric-value.danger  { color: #E63946; }
.metric-value.warning { color: #F4A261; }
.metric-value.info    { color: #60A5FA; }
.metric-label {
    font-size: 0.78rem;
    color: #E2E8F0;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
}
.metric-delta {
    font-size: 0.75rem;
    color: #02C39A;
    margin-top: 4px;
}

/* Badge sévérité */
.badge-critical { background:#E63946; color:white; padding:2px 8px; border-radius:12px; font-size:0.72rem; font-weight:700; }
.badge-high     { background:#F4A261; color:white; padding:2px 8px; border-radius:12px; font-size:0.72rem; font-weight:700; }
.badge-medium   { background:#028090; color:white; padding:2px 8px; border-radius:12px; font-size:0.72rem; font-weight:700; }
.badge-low      { background:#64748B; color:white; padding:2px 8px; border-radius:12px; font-size:0.72rem; font-weight:700; }

/* Statut alerte */
.status-open         { color:#E63946; font-weight:700; }
.status-under_review { color:#F4A261; font-weight:700; }
.status-resolved     { color:#02C39A; font-weight:700; }
.status-dismissed    { color:#64748B; font-weight:700; }

/* En-tête section */
.section-header {
    border-left: 4px solid #02C39A;
    padding-left: 12px;
    margin: 20px 0 12px 0;
    font-size: 1.1rem;
    font-weight: 700;
    color: #E2E8F0;
}

/* Bouton prédiction */
.stButton > button {
    background: linear-gradient(135deg, #028090, #02C39A);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 700;
    font-size: 1rem;
    padding: 0.6rem 2rem;
    width: 100%;
    transition: all 0.2s;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(2,195,154,0.4);
}

/* Résultat fraude */
.fraud-alert {
    background: linear-gradient(135deg, #3D0C0E, #5C1A1C);
    border: 2px solid #E63946;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    animation: pulse 2s infinite;
}
.fraud-safe {
    background: linear-gradient(135deg, #0A2E1A, #0D3D22);
    border: 2px solid #02C39A;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(230,57,70,0.4); }
    50%       { box-shadow: 0 0 0 8px rgba(230,57,70,0); }
}

/* Demo mode banner */
.demo-banner {
    background: linear-gradient(135deg, #3D2A00, #5C4000);
    border: 1px solid #F4A261;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 0.8rem;
    color: #F4A261;
    font-weight: 600;
    margin-bottom: 12px;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0A2342; }
::-webkit-scrollbar-thumb { background: #028090; border-radius: 3px; }

/* Hide Streamlit default elements */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Initialisation de la session ──────────────────────────────────────────────
if "demo_mode" not in st.session_state:
    api_ok = check_health()
    st.session_state.demo_mode = not api_ok

if "df_transactions" not in st.session_state or st.session_state.get("refresh_data"):
    df_tx = gen_transactions(n=150, days=7)
    df_al = gen_alerts(df_tx)
    st.session_state.df_transactions  = df_tx
    st.session_state.df_alerts        = df_al
    st.session_state.df_hourly        = gen_hourly_stats(df_tx)
    st.session_state.global_stats     = gen_global_stats(df_tx, df_al)
    st.session_state.refresh_data     = False

df_tx   = st.session_state.df_transactions
df_al   = st.session_state.df_alerts
stats   = st.session_state.global_stats
IS_DEMO = st.session_state.demo_mode


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo + titre
    st.markdown("""
    <div style='text-align:center; padding: 16px 0 8px 0;'>
      <div style='font-size:2.8rem; margin-bottom:4px;'>🛡️</div>
      <div style='font-size:1.4rem; font-weight:900; color:#02C39A; letter-spacing:0.05em;'>
          CamerTrust
      </div>
      <div style='font-size:0.72rem; color:#64748B; margin-top:2px;'>
          Détection de Fraude Mobile Money
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Navigation
    page = st.radio("Navigation",
        ["🏠  Accueil", "🚨  Alertes", "🔮  Prédiction en Direct"],
        label_visibility="collapsed")

    st.markdown("---")

    # Mode / statut API
    if IS_DEMO:
        st.markdown("""
        <div style='background:#3D2A00; border:1px solid #F4A261; border-radius:8px;
                    padding:10px; font-size:0.78rem; color:#F4A261;'>
            ⚡ <b>Mode Démonstration</b><br>
            <span style='color:#94A3B8;'>API non connectée —<br>données simulées réalistes</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background:#0A2E1A; border:1px solid #02C39A; border-radius:8px;
                    padding:10px; font-size:0.78rem; color:#02C39A;'>
            ✅ <b>API Connectée</b><br>
            <span style='color:#94A3B8;'>Données en temps réel</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # Rafraîchir les données
    if st.button("🔄  Actualiser les données"):
        st.session_state.refresh_data = True
        st.rerun()

    # Infos projet
    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.72rem; color:#FFFFFF; text-align:center; line-height:1.6;'>
        SUP'PTIC · Promo 2023-2026<br>
        Ingénierie Informatique & Réseaux, Inspecteur Management<br>
        <span style='color:#FFFFFF;'>v1.0.0</span>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 : ACCUEIL
# ══════════════════════════════════════════════════════════════════════════════
if "Accueil" in page:
    import plotly.express as px
    import plotly.graph_objects as go

    # En-tête
    col_title, col_time = st.columns([3, 1])
    with col_title:
        st.markdown("""
        <h1 style='margin:0; font-size:1.9rem; font-weight:800; color:#E2E8F0;'>
            Tableau de Bord <span style='color:#02C39A;'>CamerTrust</span>
        </h1>
        <p style='color:#64748B; font-size:0.88rem; margin:4px 0 0 0;'>
            Surveillance en temps réel des fraudes Mobile Money au Cameroun
        </p>
        """, unsafe_allow_html=True)
    with col_time:
        st.markdown(f"""
        <div style='text-align:right; padding-top:8px;'>
            <div style='font-size:0.72rem; color:#64748B;'>Dernière mise à jour</div>
            <div style='font-size:0.85rem; color:#02C39A; font-weight:700;'>
                {datetime.now().strftime('%d/%m/%Y %H:%M')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    if IS_DEMO:
        st.markdown('<div class="demo-banner">⚡ Mode démonstration — données simulées sur 7 jours</div>',
                    unsafe_allow_html=True)

    st.markdown("")

    # ── KPIs ──────────────────────────────────────────────────────────────────
    k1, k2, k3, k4, k5, k6 = st.columns(6)

    kpis = [
        (k1, stats["total_transactions"], "Transactions\nAnalysées",     "info",    "7 derniers jours"),
        (k2, f"{stats['total_frauds']}",  "Fraudes\nDétectées",         "danger",  f"{stats['fraud_rate_pct']}% du total"),
        (k3, f"{stats['total_blocked']}", "Transactions\nBloquées",      "danger",  "action auto"),
        (k4, f"{stats['open_alerts']}",   "Alertes\nOuvertes",           "warning", "à traiter"),
        (k5, f"{stats['avg_latency_ms']:.0f} ms", "Latence\nMoyenne IA", "info",    "objectif < 2000ms"),
        (k6, f"{stats['model_accuracy']}%","Précision\nModèle ML",       "info",    "feedback terrain"),
    ]
    for col, val, label, cls, delta in kpis:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value {cls}">{val}</div>
                <div class="metric-delta">{delta}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Graphiques ligne 1 ────────────────────────────────────────────────────

    g1, g2 = st.columns([3, 2])

    with g1:
        st.markdown('<div class="section-header">Évolution des transactions (7 jours)</div>',
                    unsafe_allow_html=True)
        hourly = st.session_state.df_hourly
 
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hourly["hour_bucket"], y=hourly["total_tx"],
            name="Total transactions",
            line=dict(color="#60A5FA", width=2),
            fill="tozeroy", fillcolor="rgba(96,165,250,0.08)"
        ))
        fig.add_trace(go.Scatter(
            x=hourly["hour_bucket"], y=hourly["fraud_count"],
            name="Fraudes détectées",
            line=dict(color="#E63946", width=2.5),
            fill="tozeroy", fillcolor="rgba(230,57,70,0.12)"
        ))
        fig.add_trace(go.Scatter(
            x=hourly["hour_bucket"], y=hourly["blocked_count"],
            name="Bloquées",
            line=dict(color="#F4A261", width=1.5, dash="dot"),
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02,
                        xanchor="right", x=0.525, font=dict(color="#94A3B8", size=11)),
            xaxis=dict(gridcolor="#1E3A5F", color="#94A3B8", tickformat="%d/%m %H:%M",
                       tickangle=-30, tickfont=dict(size=9)),
            yaxis=dict(gridcolor="#1E3A5F", color="#94A3B8"),
            margin=dict(l=0, r=0, t=30, b=0),
            height=280, hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)

    with g2:
        st.markdown('<div class="section-header">Répartition par type de fraude</div>',
                    unsafe_allow_html=True)
        fraud_df = df_al[df_al["alert_type"].notna()]
        type_counts = fraud_df["alert_type"].value_counts()
        labels_map = {
            "SIM_SWAP": "SIM Swap",
            "NOCTURNAL": "Nocturne",
            "MULE_ACCOUNT": "Compte Mule",
            "UNKNOWN": "Inconnue"
        }
        colors_pie = ["#E63946", "#F4A261", "#7C3AED", "#64748B"]

        fig2 = go.Figure(go.Pie(
            labels=[labels_map.get(l, l) for l in type_counts.index],
            values=type_counts.values,
            hole=0.55,
            marker=dict(colors=colors_pie, line=dict(color="#0A2342", width=2)),
            textfont=dict(color="white", size=11),
        ))
        fig2.add_annotation(
            text=f"<b>{len(fraud_df)}</b><br><span style='font-size:10px'>fraudes</span>",
            x=0.5, y=0.5, font=dict(size=14, color="#02C39A"),
            showarrow=False
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(font=dict(color="#94A3B8", size=11),
                        orientation="h", yanchor="top", y=-0.05),
            margin=dict(l=0, r=0, t=30, b=0), height=280,
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Graphiques ligne 2 ────────────────────────────────────────────────────
    g3, g4 = st.columns([2, 3])

    with g3:
        st.markdown('<div class="section-header">Sévérité des alertes</div>',
                    unsafe_allow_html=True)
        sev_order  = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        sev_colors = {"CRITICAL": "#E63946", "HIGH": "#F4A261",
                      "MEDIUM": "#028090", "LOW": "#64748B"}
        sev_counts = df_al["severity"].value_counts().reindex(sev_order, fill_value=0)

        fig3 = go.Figure(go.Bar(
            x=sev_counts.values,
            y=sev_counts.index,
            orientation="h",
            marker=dict(color=[sev_colors[s] for s in sev_counts.index],
                        cornerradius=4),
            text=sev_counts.values,
            textposition="outside",
            textfont=dict(color="#E2E8F0", size=11),
        ))
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor="#1E3A5F", color="#94A3B8", showgrid=True),
            yaxis=dict(color="#E2E8F0", tickfont=dict(size=11)),
            margin=dict(l=0, r=30, t=10, b=0), height=240,
            showlegend=False,
        )
        st.plotly_chart(fig3, use_container_width=True)

    with g4:
        st.markdown('<div class="section-header">Montants par heure (XAF)</div>',
                    unsafe_allow_html=True)
        hourly_grp = df_tx.groupby(df_tx["created_at"].dt.hour).agg(
            legit  =("amount", lambda x: x[df_tx.loc[x.index,"is_fraud"] == False].sum()),
            fraud  =("amount", lambda x: x[df_tx.loc[x.index,"is_fraud"] == True].sum()),
        ).reset_index()
        hourly_grp.columns = ["heure", "Légitimes", "Frauduleuses"]

        fig4 = go.Figure()
        fig4.add_trace(go.Bar(
            x=hourly_grp["heure"], y=hourly_grp["Légitimes"] / 1000,
            name="Légitimes (k XAF)", marker_color="#028090", marker_cornerradius=3))
        fig4.add_trace(go.Bar(
            x=hourly_grp["heure"], y=hourly_grp["Frauduleuses"] / 1000,
            name="Frauduleuses (k XAF)", marker_color="#E63946", marker_cornerradius=3))
        fig4.update_layout(
            barmode="stack",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor="#1E3A5F", color="#94A3B8", title="Heure"),
            yaxis=dict(gridcolor="#1E3A5F", color="#94A3B8", title="Montant (k XAF)"),
            legend=dict(font=dict(color="#94A3B8", size=10),
                        orientation="h", yanchor="bottom", y=1.02),
            margin=dict(l=0, r=0, t=30, b=0), height=240, hovermode="x unified",
        )
        st.plotly_chart(fig4, use_container_width=True)

    # ── Dernières transactions ─────────────────────────────────────────────────
    st.markdown('<div class="section-header">Dernières transactions analysées</div>',
                unsafe_allow_html=True)

    display_df = df_tx.head(8)[[
        "id","user_id","transaction_type","amount","status",
        "fraud_score","severity","created_at"
    ]].copy()

    display_df["fraud_score"]  = (display_df["fraud_score"] * 100).map("{:.1f}%".format)
    display_df["amount"]       = display_df["amount"].map("{:,.0f} XAF".format)
    display_df["created_at"]   = display_df["created_at"].dt.strftime("%d/%m %H:%M")
    display_df.columns = ["ID", "Émetteur", "Type", "Montant", "Statut",
                           "Score Fraude", "Sévérité", "Date/Heure"]

    def color_status(val):
        colors = {"BLOCKED": "color:#E63946;font-weight:700",
                  "FLAGGED": "color:#F4A261;font-weight:700",
                  "COMPLETED": "color:#02C39A",
                  "FAILED": "color:#64748B"}
        return colors.get(val, "")

    styled = display_df.style\
        .apply(lambda col: [color_status(v) for v in col]
               if col.name == "Statut" else [""] * len(col), axis=0)\
        .set_properties(**{"font-size": "0.82rem"})\
        .set_table_styles([
            {"selector": "th", "props": [("background-color","#0F2D52"),
                                          ("color","#94A3B8"),
                                          ("font-size","0.78rem")]},
            {"selector": "td", "props": [("padding","6px 10px")]},
        ])
    st.dataframe(display_df, use_container_width=True, hide_index=True,
                 column_config={
                     "Score Fraude": st.column_config.TextColumn(),
                     "Statut": st.column_config.TextColumn(),
                 })


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 : ALERTES
# ══════════════════════════════════════════════════════════════════════════════
elif "Alertes" in page:
    import plotly.graph_objects as go

    st.markdown("""
    <h1 style='margin:0 0 4px 0; font-size:1.9rem; font-weight:800; color:#E2E8F0;'>
        🚨 Gestion des <span style='color:#E63946;'>Alertes</span>
    </h1>
    <p style='color:#64748B; font-size:0.88rem; margin:0 0 16px 0;'>
        Toutes les alertes de fraude générées — cycle de vie : Ouverte → En examen → Résolue
    </p>
    """, unsafe_allow_html=True)

    if IS_DEMO:
        st.markdown('<div class="demo-banner">⚡ Mode démonstration — données simulées</div>',
                    unsafe_allow_html=True)

    # ── KPIs alertes ──────────────────────────────────────────────────────────
    a1, a2, a3, a4 = st.columns(4)
    open_n   = (df_al["status"] == "OPEN").sum()
    review_n = (df_al["status"] == "UNDER_REVIEW").sum()
    res_n    = (df_al["status"] == "RESOLVED").sum()
    dis_n    = (df_al["status"] == "DISMISSED").sum()
    crit_n   = (df_al["severity"] == "CRITICAL").sum()

    for col, val, label, cls in [
        (a1, open_n,   f"Ouvertes\n({crit_n} critiques)", "danger"),
        (a2, review_n, "En cours\nd'examen",              "warning"),
        (a3, res_n,    "Résolues\n(fraude confirmée)",    "info"),
        (a4, dis_n,    "Rejetées\n(faux positifs)",       ""),
    ]:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value {cls}">{val}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Filtres ───────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Filtres</div>', unsafe_allow_html=True)
    f1, f2, f3, f4, f5 = st.columns(5)
    with f1:
        filt_status = st.selectbox("Statut", ["Tous", "OPEN", "UNDER_REVIEW",
                                               "RESOLVED", "DISMISSED"])
    with f2:
        filt_sev = st.selectbox("Sévérité", ["Toutes", "CRITICAL", "HIGH",
                                              "MEDIUM", "LOW"])
    with f3:
        filt_type = st.selectbox("Type de fraude", ["Tous", "SIM_SWAP",
                                  "NOCTURNAL", "MULE_ACCOUNT", "UNKNOWN"])
    with f4:
        filt_op = st.selectbox("Opérateur", ["Tous", "MTN", "ORANGE"])
    with f5:
        filt_min = st.number_input("Montant min (XAF)", value=0, step=10000,
                                    format="%d")

    # Appliquer les filtres
    filtered = df_al.copy()
    if filt_status != "Tous":
        filtered = filtered[filtered["status"] == filt_status]
    if filt_sev != "Toutes":
        filtered = filtered[filtered["severity"] == filt_sev]
    if filt_type != "Tous":
        filtered = filtered[filtered["alert_type"] == filt_type]
    if filt_op != "Tous":
        filtered = filtered[filtered["operator"] == filt_op]
    if filt_min > 0:
        filtered = filtered[filtered["amount"] >= filt_min]

    st.markdown(f"""
    <div class="section-header">
        {len(filtered)} alerte(s) trouvée(s)
        <span style='font-size:0.8rem; color:#64748B; margin-left:8px;'>
            sur {len(df_al)} total
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Export CSV ─────────────────────────────────────────────────────────────
    col_exp, _ = st.columns([1, 3])
    with col_exp:
        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥  Exporter CSV",
            data=csv, file_name=f"alertes_camertrust_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

    # ── Tableau des alertes ────────────────────────────────────────────────────
    severity_icons = {"CRITICAL":"🔴","HIGH":"🟠","MEDIUM":"🟡","LOW":"⚪"}
    status_icons   = {"OPEN":"🔔","UNDER_REVIEW":"🔍","RESOLVED":"✅","DISMISSED":"❌"}

    for _, row in filtered.head(25).iterrows():
        sev_i  = severity_icons.get(row["severity"], "⚪")
        stat_i = status_icons.get(row["status"], "❓")
        is_crit = row["severity"] == "CRITICAL"
        border_color = "#E63946" if is_crit else ("#F4A261" if row["severity"]=="HIGH" else "#028090")

        with st.expander(
            f"{sev_i} {row['title']}  ·  {row['amount']:,.0f} XAF  ·  "
            f"Score: {row['fraud_score']*100:.1f}%  ·  {stat_i} {row['status']}",
            expanded=is_crit and row["status"] == "OPEN"
        ):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"<span stype = 'color :#E2E8F0;'>**Abonné :** `{row['user_id']}`</span>",
                            unsafe_allow_html=True)
                st.markdown(f"<span stype = 'color :#E2E8F0;'>**Type fraude :** `{row['alert_type']}`</span>",
                            unsafe_allow_html=True)
                st.markdown(f"<span stype = 'color :#E2E8F0;'>**Opérateur :** {row['operator']}</span>",
                            unsafe_allow_html=True)
            with c2:
                st.markdown(f"<span stype = 'color :#E2E8F0;'>**Montant :** `{row['amount']:,.0f} XAF`</span>",
                            unsafe_allow_html=True)
                st.markdown(f"<span stype = 'color :#E2E8F0;'>**Sévérité :** `{row['severity']}`</span>",
                            unsafe_allow_html=True)
                st.markdown(f"<span stype = 'color :#E2E8F0;'>**Région :** {row['region']}</span>",
                            unsafe_allow_html=True)
            with c3:
                st.markdown(f"<span stype = 'color :#E2E8F0;'>**ID Alerte :** `{row['id']}`</span>",
                            unsafe_allow_html=True)
                st.markdown(f"<span stype = 'color :#E2E8F0;'>**ID Transaction :** `{row['transaction_id']}`</span>",
                            unsafe_allow_html=True)
                st.markdown(f"<span stype = 'color :#E2E8F0;'>**Date :** {row['created_at'].strftime('%d/%m/%Y %H:%M')}</span>",
                            unsafe_allow_html=True)

            st.markdown(f"<p style='color :#CBD5E1;font-style:italic;'>📝 *{row['description']}*</p>",
                        unsafe_allow_html=True)

            # Score gauge
            score_pct = int(row["fraud_score"] * 100)
            gauge_color = "#E63946" if score_pct >= 85 else "#F4A261" if score_pct >= 60 else "#02C39A"
            st.markdown(f"""
            <div style='background:#0F2D52; border-radius:8px; padding:10px 14px; margin:8px 0;'>
                <div style='font-size:0.78rem; color:#E2E8F0; margin-bottom:4px;'>
                    Score de fraude : <b style='color:{gauge_color};'>{score_pct}%</b>
                </div>
                <div style='background:#1E3A5F; border-radius:6px; height:10px;'>
                    <div style='background:{gauge_color}; width:{score_pct}%;
                                border-radius:6px; height:10px;
                                box-shadow: 0 0 8px {gauge_color}60;'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Action si alerte OPEN ou UNDER_REVIEW
            if row["status"] in ("OPEN", "UNDER_REVIEW"):
                st.markdown("---")
                act_col1, act_col2 = st.columns(2)
                with act_col1:
                    note = st.text_input("Note (optionnel)", key=f"note_{row['id']}",
                                         placeholder="Ex: Appel client confirmé...")
                with act_col2:
                    agent = st.text_input("Agent ID", value="agent_001",
                                           key=f"agent_{row['id']}")
                btn1, btn2 = st.columns(2)
                with btn1:
                    if st.button("✅  Confirmer la fraude", key=f"res_{row['id']}",
                                 use_container_width=True):
                        st.success("✅ Fraude confirmée — feedback enregistré")
                with btn2:
                    if st.button("❌  Faux positif", key=f"dis_{row['id']}",
                                 use_container_width=True):
                        st.info("ℹ️ Alerte rejetée — transaction légitime")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 : PRÉDICTION EN DIRECT
# ══════════════════════════════════════════════════════════════════════════════
elif "Prédiction" in page:
    import plotly.graph_objects as go
    import random as rnd
    import time

    st.markdown("""
    <h1 style='margin:0 0 4px 0; font-size:1.9rem; font-weight:800; color:#E2E8F0;'>
        🔮 Prédiction <span style='color:#02C39A;'>en Direct</span>
    </h1>
    <p style='color:#64748B; font-size:0.88rem; margin:0 0 16px 0;'>
        Soumettez une transaction et obtenez un score de fraude en temps réel
    </p>
    """, unsafe_allow_html=True)

    if IS_DEMO:
        st.markdown('<div class="demo-banner">⚡ Mode démonstration — prédiction simulée par heuristiques</div>',
                    unsafe_allow_html=True)

    # ── Formulaire ────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Données de la Transaction</div>',
                unsafe_allow_html=True)

    with st.form("predict_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            user_id     = st.text_input("📱 Numéro émetteur (6XXXXXXXX)",
                                         value="677123456", max_chars=15)
            tx_type     = st.selectbox("🔄 Type de transaction",
                                        ["TRANSFER","CASH_OUT","CASH_IN","PAYMENT","DEBIT"])
            old_balance = st.number_input("💰 Solde avant (XAF)", value=500000,
                                           min_value=0, step=10000, format="%d")
        with c2:
            recipient   = st.text_input("📱 Numéro destinataire (6XXXXXXXX)",
                                         value="699987654", max_chars=15)
            amount      = st.number_input("💵 Montant (XAF)", value=150000,
                                           min_value=100, max_value=5000000,
                                           step=5000, format="%d")
            new_balance = st.number_input("💰 Solde après (XAF)",
                                           value=max(0, 500000 - 150000),
                                           min_value=0, step=10000, format="%d")

        st.markdown("**Contexte de la transaction**")
        cx1, cx2, cx3, cx4 = st.columns(4)
        with cx1:
            hour = st.slider("🕐 Heure", 0, 23, 14)
        with cx2:
            is_night = st.toggle("🌙 Transaction nocturne", value=(hour >= 22 or hour <= 5))
        with cx3:
            is_new_device = st.toggle("📱 Nouvel appareil", value=False)
        with cx4:
            network = st.selectbox("📶 Réseau", ["4G","3G","2G","WIFI"])

        # Scénarios prédéfinis
        st.markdown("---")
        st.markdown("**Ou utiliser un scénario prédéfini :**")
        sc1, sc2, sc3, sc4 = st.columns(4)
        scenario = None
        with sc1:
            if st.form_submit_button("✅ Transaction normale",
                                      use_container_width=True):
                scenario = "normal"
        with sc2:
            if st.form_submit_button("🌙 Transaction nocturne",
                                      use_container_width=True):
                scenario = "nocturnal"
        with sc3:
            if st.form_submit_button("🔴 SIM Swap simulé",
                                      use_container_width=True):
                scenario = "sim_swap"
        with sc4:
            if st.form_submit_button("🔀 Compte mule",
                                      use_container_width=True):
                scenario = "mule"

        # Bouton principal
        st.markdown("")
        submitted = st.form_submit_button("🔍  ANALYSER CETTE TRANSACTION",
                                           use_container_width=True)

    # ── Résultat ───────────────────────────────────────────────────────────────
    if submitted or scenario:
        # Construire le payload
        scenarios_data = {
            "normal":    {"amount": 25000, "old_balance": 150000, "new_balance": 125000,
                          "tx_type": "TRANSFER", "hour": 14, "is_night": False,
                          "is_new_device": False},
            "nocturnal": {"amount": 750000, "old_balance": 800000, "new_balance": 50000,
                          "tx_type": "CASH_OUT", "hour": 3, "is_night": True,
                          "is_new_device": True},
            "sim_swap":  {"amount": 980000, "old_balance": 980000, "new_balance": 0,
                          "tx_type": "TRANSFER", "hour": 2, "is_night": True,
                          "is_new_device": True},
            "mule":      {"amount": 500000, "old_balance": 500000, "new_balance": 0,
                          "tx_type": "CASH_OUT", "hour": 5, "is_night": True,
                          "is_new_device": False},
        }

        params = scenarios_data.get(scenario, {
            "amount": amount, "old_balance": old_balance, "new_balance": new_balance,
            "tx_type": tx_type, "hour": hour, "is_night": is_night,
            "is_new_device": is_new_device
        })

        payload = {
            "user_id":          user_id if scenario is None else "677111000",
            "recipient_id":     recipient if scenario is None else "699222000",
            "transaction_type": params["tx_type"],
            "amount":           params["amount"],
            "old_balance":      params["old_balance"],
            "new_balance":      params["new_balance"],
            "context": {
                "hour_of_day":    params["hour"],
                "is_night":       params["is_night"],
                "is_new_device":  params["is_new_device"],
                "network_type":   network,
            }
        }

        # Barre de progression
        with st.spinner("🤖 Modèle ML en cours d'analyse..."):
            time.sleep(0.8)

        # Calcul du score (démo ou API)
        from utils.api_client import predict as api_predict
        api_result = api_predict(payload) if not IS_DEMO else None

        if api_result:
            score   = api_result["fraud_score"]
            action  = api_result["action"]
            ftype   = api_result.get("fraud_type") or "UNKNOWN"
            latency = api_result["latency_ms"]
        else:
            # Calcul heuristique démo
            h       = params["hour"]
            amt     = params["amount"]
            new_b   = params["new_balance"]
            is_n    = params["is_night"]
            new_dev = params["is_new_device"]
            err_o   = abs(params["old_balance"] - new_b - amt)

            base = 0.05
            if is_n:        base += 0.30
            if amt > 500_000: base += 0.25
            if new_b == 0:  base += 0.20
            if new_dev:     base += 0.15
            if err_o > 1000: base += 0.10
            score   = min(0.97, round(base + rnd.uniform(-0.03, 0.03), 5))
            action  = ("BLOCKED" if score >= 0.85 else "FLAGGED"
                       if score >= 0.50 else "ALLOWED")
            if new_dev and is_n:       ftype = "SIM_SWAP"
            elif is_n and amt > 300_000: ftype = "NOCTURNAL"
            elif new_b == 0:             ftype = "MULE_ACCOUNT"
            else:                        ftype = "UNKNOWN" if score >= 0.50 else None
            latency = rnd.randint(20, 180)

        score_pct = int(score * 100)
        is_fraud  = score >= 0.50
        severity  = ("CRITICAL" if score >= 0.90 else "HIGH" if score >= 0.75
                     else "MEDIUM" if score >= 0.50 else "LOW")
        action_labels = {
            "BLOCKED": ("🚫 TRANSACTION BLOQUÉE", "#E63946"),
            "FLAGGED": ("⚠️ TRANSACTION SIGNALÉE", "#F4A261"),
            "ALLOWED": ("✅ TRANSACTION AUTORISÉE", "#02C39A"),
        }
        action_txt, action_col = action_labels.get(action, ("❓", "#64748B"))

        fraud_type_labels = {
            "SIM_SWAP":     "🔴 SIM Swap",
            "NOCTURNAL":    "🌙 Transaction Nocturne",
            "MULE_ACCOUNT": "🔀 Compte Mule",
            "UNKNOWN":      "⚠️ Type Inconnu",
        }

        st.markdown("---")
        st.markdown('<div class="section-header">Résultat de l\'analyse</div>',
                    unsafe_allow_html=True)

        r1, r2 = st.columns([2, 3])

        with r1:
            # Carte résultat
            bg_class = "fraud-alert" if is_fraud else "fraud-safe"
            icon     = "🚨" if is_fraud else "✅"
            st.markdown(f"""
            <div class="{bg_class}">
                <div style='font-size:2.8rem; margin-bottom:8px;'>{icon}</div>
                <div style='font-size:1.5rem; font-weight:800; color:{action_col};'>
                    {action_txt}
                </div>
                <div style='font-size:3.5rem; font-weight:900;
                            color:{"#E63946" if score_pct >= 85 else "#F4A261" if score_pct >= 50 else "#02C39A"};
                            margin:12px 0 4px 0;'>
                    {score_pct}%
                </div>
                <div style='font-size:0.82rem; color:#94A3B8;'>Score de fraude</div>
                <div style='margin-top:10px; font-size:0.85rem; color:#E2E8F0;'>
                    Sévérité : <b style='color:{action_col};'>{severity}</b>
                </div>
                {"<div style='font-size:0.85rem; color:#E2E8F0; margin-top:4px;'>Type : <b>" + fraud_type_labels.get(ftype, ftype or "—") + "</b></div>" if ftype else ""}
                <div style='font-size:0.78rem; color:#64748B; margin-top:8px;'>
                    ⚡ Latence : {latency} ms · Seuil : 50%
                </div>
            </div>
            """, unsafe_allow_html=True)

        with r2:
            # Jauge
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score_pct,
                number={"suffix": "%", "font": {"size": 36, "color": "#E2E8F0"}},
                gauge={
                    "axis": {"range": [0, 100], "tickwidth": 1,
                             "tickcolor": "#475569", "tickfont": {"color":"#94A3B8"}},
                    "bar":  {"color": "#E63946" if score_pct >= 85
                             else "#F4A261" if score_pct >= 50 else "#02C39A",
                             "thickness": 0.25},
                    "bgcolor": "#0F2D52",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0, 50],  "color": "rgba(2,195,154,0.12)"},
                        {"range": [50, 75], "color": "rgba(244,162,97,0.15)"},
                        {"range": [75, 100],"color": "rgba(230,57,70,0.18)"},
                    ],
                    "threshold": {
                        "line": {"color": "#E2E8F0", "width": 2},
                        "thickness": 0.75, "value": 50
                    }
                }
            ))
            fig_gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", height=260,
                margin=dict(l=20, r=20, t=20, b=20),
                font={"color": "#E2E8F0"}
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

            # Détails de la transaction
            st.markdown(f"""
            <div style='background:#0F2D52; border-radius:8px; padding:14px;
                        font-size:0.82rem; line-height:2.0;'>
                <span style='color:#FFFFFF;'>Émetteur</span>
                <span style='float:right; color:#E2E8F0; font-family:monospace;'>
                    {payload["user_id"]}</span><br>
                <span style='color:#FFFFFF;'>Type</span>
                <span style='float:right; color:#E2E8F0;'>
                    {payload["transaction_type"]}</span><br>
                <span style='color:#FFFFFF;'>Montant</span>
                <span style='float:right; color:#02C39A; font-weight:700;'>
                    {params["amount"]:,.0f} XAF</span><br>
                <span style='color:#FFFFFF;'>Heure</span>
                <span style='float:right; color:{"#E63946" if params["is_night"] else "#E2E8F0"};'>
                    {params["hour"]}:00{"  🌙" if params["is_night"] else ""}</span><br>
                <span style='color:#FFFFFF;'>Réseau</span>
                <span style='float:right; color:#E2E8F0;'>{network}</span>
            </div>
            """, unsafe_allow_html=True)

        # Explication du résultat
        st.markdown("")
        if is_fraud:
            reasons = []
            if params["is_night"] and params["amount"] > 200_000:
                reasons.append("💡 Gros montant effectué entre 22h et 5h — pattern fraude nocturne")
            if params["new_balance"] == 0:
                reasons.append("💡 Compte émetteur vidé complètement — pattern fraude typique")
            if params["is_new_device"]:
                reasons.append("💡 Transaction depuis un appareil jamais vu — possible SIM Swap")
            if params["amount"] > 500_000:
                reasons.append(f"💡 Montant de {params['amount']:,.0f} XAF — au-dessus du seuil habituel")
            if reasons:
                st.markdown('<div class="section-header">Pourquoi cette alerte ?</div>',
                            unsafe_allow_html=True)
                for r in reasons:
                    st.markdown(f"""
                    <div style='background:#1E0A0C; border-left:3px solid #E63946;
                                border-radius:4px; padding:8px 12px; margin-bottom:6px;
                                font-size:0.85rem; color:#E2E8F0;'>
                        {r}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background:#0A1F0F; border-left:3px solid #02C39A;
                        border-radius:4px; padding:10px 14px; font-size:0.85rem; color:#E2E8F0;'>
                ✅ Aucun pattern suspect détecté. La transaction respecte le comportement habituel
                de l'abonné. Score de fraude inférieur au seuil de 50%.
            </div>
            """, unsafe_allow_html=True)
