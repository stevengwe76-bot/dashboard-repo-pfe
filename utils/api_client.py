"""
CamerTrust — Client API
Gère les appels à FastAPI avec fallback automatique en mode démo.
"""
import requests
import streamlit as st

def get_api_url():
    try:
        return st.secrets.get("api_url", "http://localhost:8000")
    except Exception:
        return "http://localhost:8000"

def get_token():
    try:
        return st.session_state.get("jwt_token")
    except Exception:
        return None

def _headers():
    token = get_token()
    if token:
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    return {"Content-Type": "application/json"}

def login(username: str, password: str) -> dict:
    try:
        r = requests.post(
            f"{get_api_url()}/auth/token",
            data={"username": username, "password": password},
            timeout=5
        )
        if r.status_code == 200:
            return {"ok": True, "token": r.json()["access_token"],
                    "role": r.json().get("role", "ANALYST")}
        return {"ok": False, "error": r.json().get("detail", "Erreur de connexion")}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def get_stats(hours=24) -> dict | None:
    try:
        r = requests.get(f"{get_api_url()}/dashboard/stats?hours={hours}",
                         headers=_headers(), timeout=5)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

def get_transactions(page=1, per_page=20, **filters) -> dict | None:
    try:
        params = {"page": page, "per_page": per_page, **filters}
        r = requests.get(f"{get_api_url()}/transactions",
                         headers=_headers(), params=params, timeout=5)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

def get_alerts(**filters) -> dict | None:
    try:
        r = requests.get(f"{get_api_url()}/alerts",
                         headers=_headers(), params=filters, timeout=5)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

def predict(payload: dict) -> dict | None:
    try:
        r = requests.post(f"{get_api_url()}/predict",
                          json=payload, headers=_headers(), timeout=10)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

def resolve_alert(alert_id: int, status: str, resolved_by: str, note: str = "") -> bool:
    try:
        r = requests.patch(
            f"{get_api_url()}/alerts/{alert_id}/resolve",
            json={"status": status, "resolved_by": resolved_by, "resolution_note": note},
            headers=_headers(), timeout=5
        )
        return r.status_code == 200
    except Exception:
        return False

def check_health() -> bool:
    try:
        r = requests.get(f"{get_api_url()}/dashboard/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False
