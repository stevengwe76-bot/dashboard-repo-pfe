"""
CamerTrust Lite - Client API pour le dashboard
E3 - Frontend et Coordinateur

Centralise tous les appels vers l'API de E2 : gestion du token JWT,
timeouts, messages d'erreur clairs a afficher dans Streamlit.

Rien ici ne depend de l'URL de l'API : elle est lue depuis
st.secrets["api_url"] (voir .streamlit/secrets.toml). Aucun changement de
code n'est necessaire pour pointer vers l'API deployee -- seul le fichier
secrets.toml doit etre complete.
"""

from typing import Optional

import requests
import streamlit as st

TIMEOUT = 10  # secondes - l'API Render peut etre lente au reveil (cold start)


def get_api_url() -> str:
    return st.secrets.get("api_url", "http://localhost:8000").rstrip("/")


def check_health() -> tuple[bool, str]:
    """Retourne (ok, message) pour affichage dans la sidebar."""
    try:
        response = requests.get(f"{get_api_url()}/health", timeout=TIMEOUT)
        if response.status_code == 200:
            return True, "API connectee"
        return False, f"API a repondu avec le code {response.status_code}"
    except requests.exceptions.Timeout:
        return False, "API ne repond pas (timeout — reveil en cours si Render vient de dormir ?)"
    except requests.exceptions.ConnectionError:
        return False, "Impossible de joindre l'API (verifie api_url dans secrets.toml)"
    except Exception as exc:  # noqa: BLE001
        return False, f"Erreur inattendue : {exc}"


@st.cache_data(ttl=300, show_spinner=False)
def _get_token() -> Optional[str]:
    """Recupere un token JWT et le met en cache 5 minutes."""
    try:
        response = requests.post(
            f"{get_api_url()}/auth/token",
            data={
                "username": st.secrets.get("api_username", "camertrust"),
                "password": st.secrets.get("api_password", "changeme123"),
            },
            timeout=TIMEOUT,
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        return None
    except Exception:  # noqa: BLE001
        return None


def _auth_headers() -> dict:
    token = _get_token()
    if token is None:
        return {}
    return {"Authorization": f"Bearer {token}"}


def predict(transaction: dict) -> Optional[dict]:
    """Appelle POST /predict. Retourne None en cas d'erreur (message affiche via st.error)."""
    try:
        response = requests.post(
            f"{get_api_url()}/predict", json=transaction, timeout=TIMEOUT
        )
        if response.status_code == 200:
            return response.json()
        st.error(f"Erreur API ({response.status_code}) : {response.text}")
        return None
    except requests.exceptions.Timeout:
        st.error("L'API met trop de temps a repondre. Reessaie dans quelques secondes.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("Impossible de joindre l'API. Verifie que le service est bien deploye.")
        return None


def get_transactions(limit: int = 50, skip: int = 0) -> list[dict]:
    try:
        response = requests.get(
            f"{get_api_url()}/transactions",
            params={"limit": limit, "skip": skip},
            headers=_auth_headers(),
            timeout=TIMEOUT,
        )
        if response.status_code == 200:
            return response.json()
        st.warning(f"Impossible de charger les transactions ({response.status_code})")
        return []
    except Exception as exc:  # noqa: BLE001
        st.warning(f"Erreur de connexion a l'API : {exc}")
        return []


def get_alerts(
    limit: int = 100,
    date_from: Optional[str] = None,
    min_amount: Optional[float] = None,
) -> list[dict]:
    params = {"limit": limit}
    if date_from:
        params["date_from"] = date_from
    if min_amount is not None:
        params["min_amount"] = min_amount

    try:
        response = requests.get(
            f"{get_api_url()}/alerts",
            params=params,
            headers=_auth_headers(),
            timeout=TIMEOUT,
        )
        if response.status_code == 200:
            return response.json()
        st.warning(f"Impossible de charger les alertes ({response.status_code})")
        return []
    except Exception as exc:  # noqa: BLE001
        st.warning(f"Erreur de connexion a l'API : {exc}")
        return []
