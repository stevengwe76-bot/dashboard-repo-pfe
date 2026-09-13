"""
CamerTrust — Données de démonstration
Utilisées quand l'API FastAPI n'est pas disponible.
Reproduit des données réalistes du Mobile Money camerounais.
"""
import random
import pandas as pd
from datetime import datetime, timedelta

random.seed(42)

OPERATORS    = ["MTN", "ORANGE", "MTN", "MTN", "ORANGE"]
TX_TYPES     = ["TRANSFER", "CASH_OUT", "PAYMENT", "CASH_IN", "TRANSFER"]
FRAUD_TYPES  = ["SIM_SWAP", "NOCTURNAL", "MULE_ACCOUNT", "UNKNOWN"]
REGIONS      = ["Centre (Yaoundé)", "Littoral (Douala)", "Ouest", "Nord-Ouest", "Sud-Ouest"]
SEVERITIES   = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
STATUSES_TX  = ["COMPLETED", "COMPLETED", "COMPLETED", "BLOCKED", "FLAGGED"]
STATUSES_AL  = ["OPEN", "OPEN", "UNDER_REVIEW", "RESOLVED", "DISMISSED"]

def _phone():
    prefixes = ["677", "699", "655", "688", "670", "696"]
    return f"{random.choice(prefixes)}{random.randint(100000, 999999)}"

def _amount(tx_type, is_fraud):
    if is_fraud:
        return round(random.uniform(200_000, 1_500_000), 2)
    mapping = {"TRANSFER": (5_000, 300_000), "CASH_OUT": (2_000, 150_000),
               "PAYMENT": (500, 50_000), "CASH_IN": (5_000, 200_000)}
    lo, hi = mapping.get(tx_type, (5_000, 100_000))
    return round(random.uniform(lo, hi), 2)

def gen_transactions(n=120, days=7):
    """Génère n transactions sur les derniers `days` jours."""
    rows = []
    now  = datetime.utcnow()
    for i in range(n):
        created = now - timedelta(
            hours=random.uniform(0, days * 24),
            minutes=random.uniform(0, 59)
        )
        tx_type    = random.choice(TX_TYPES)
        is_fraud   = random.random() < 0.15          # 15% de fraudes
        is_night   = created.hour >= 22 or created.hour <= 5
        score      = round(random.uniform(0.65, 0.97), 5) if is_fraud \
                     else round(random.uniform(0.02, 0.45), 5)
        fraud_type = random.choice(FRAUD_TYPES) if is_fraud else None
        status     = "BLOCKED" if is_fraud and score >= 0.85 else \
                     "FLAGGED"  if is_fraud else "COMPLETED"
        amount     = _amount(tx_type, is_fraud)
        severity   = ("CRITICAL" if score >= 0.90 else "HIGH" if score >= 0.75
                       else "MEDIUM" if score >= 0.50 else "LOW")
        rows.append({
            "id":               f"{i+1:04d}-{random.randint(1000,9999)}",
            "user_id":          _phone(),
            "recipient_id":     _phone(),
            "transaction_type": tx_type,
            "amount":           amount,
            "status":           status,
            "fraud_score":      score,
            "is_fraud":         is_fraud,
            "fraud_type":       fraud_type,
            "severity":         severity if is_fraud else "LOW",
            "hour":             created.hour,
            "is_night":         is_night,
            "region":           random.choice(REGIONS),
            "operator":         random.choice(OPERATORS),
            "created_at":       created,
            "action":           "BLOCKED" if is_fraud and score >= 0.85
                                else "FLAGGED" if is_fraud else "ALLOWED",
            "latency_ms":       random.randint(18, 280),
        })
    df = pd.DataFrame(rows)
    df["created_at"] = pd.to_datetime(df["created_at"])
    return df.sort_values("created_at", ascending=False).reset_index(drop=True)

def gen_alerts(transactions_df):
    """Génère les alertes à partir des transactions frauduleuses."""
    fraud_df = transactions_df[transactions_df["is_fraud"]].copy()
    alerts   = []
    statuses = ["OPEN", "OPEN", "OPEN", "UNDER_REVIEW", "RESOLVED", "DISMISSED"]
    titles   = {
        "SIM_SWAP":     "🔴 SIM Swap Détecté",
        "NOCTURNAL":    "🌙 Transaction Nocturne Anormale",
        "MULE_ACCOUNT": "🔀 Compte Mule Suspecté",
        "UNKNOWN":      "⚠️ Activité Frauduleuse Détectée",
    }
    for idx, row in fraud_df.iterrows():
        ftype   = row["fraud_type"] or "UNKNOWN"
        status  = random.choice(statuses)
        alerts.append({
            "id":            idx + 1,
            "transaction_id":row["id"],
            "user_id":       row["user_id"],
            "severity":      row["severity"],
            "alert_type":    ftype,
            "title":         titles.get(ftype, "⚠️ Fraude Détectée"),
            "description":   (f"Transaction de {row['amount']:,.0f} XAF "
                              f"à {row['hour']}h00. Score : {row['fraud_score']*100:.1f}%."),
            "fraud_score":   row["fraud_score"],
            "amount":        row["amount"],
            "status":        status,
            "created_at":    row["created_at"],
            "region":        row["region"],
            "operator":      row["operator"],
        })
    return pd.DataFrame(alerts).sort_values("created_at", ascending=False).reset_index(drop=True)

def gen_hourly_stats(transactions_df):
    """Agrège les transactions par heure pour les graphiques."""
    df = transactions_df.copy()
    df["hour_bucket"] = df["created_at"].dt.floor("h")
    grouped = df.groupby("hour_bucket").agg(
        total_tx      =("id", "count"),
        fraud_count   =("is_fraud", "sum"),
        blocked_count =("status", lambda x: (x == "BLOCKED").sum()),
        total_amount  =("amount", "sum"),
        avg_score     =("fraud_score", "mean"),
        avg_latency   =("latency_ms", "mean"),
    ).reset_index()
    grouped["fraud_rate"] = (grouped["fraud_count"] / grouped["total_tx"] * 100).round(2)
    return grouped.sort_values("hour_bucket")

def gen_global_stats(transactions_df, alerts_df):
    """Calcule les KPIs globaux pour la page Accueil."""
    total    = len(transactions_df)
    frauds   = transactions_df["is_fraud"].sum()
    blocked  = (transactions_df["status"] == "BLOCKED").sum()
    flagged  = (transactions_df["status"] == "FLAGGED").sum()
    amount_blocked = transactions_df.loc[
        transactions_df["status"] == "BLOCKED", "amount"].sum()
    open_alerts    = (alerts_df["status"] == "OPEN").sum()
    avg_latency    = transactions_df["latency_ms"].mean()
    avg_score      = transactions_df[transactions_df["is_fraud"]]["fraud_score"].mean()

    return {
        "total_transactions":  int(total),
        "total_frauds":        int(frauds),
        "total_blocked":       int(blocked),
        "total_flagged":       int(flagged),
        "fraud_rate_pct":      round(frauds / total * 100, 2) if total else 0,
        "amount_blocked_xaf":  round(amount_blocked, 2),
        "open_alerts":         int(open_alerts),
        "avg_latency_ms":      round(avg_latency, 1),
        "avg_fraud_score":     round(avg_score * 100, 1) if not pd.isna(avg_score) else 0,
        "model_version":       "v1.0 (XGBoost + Random Forest)",
        "model_accuracy":      87.3,
    }
