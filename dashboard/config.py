"""Load dashboard settings from environment variables or Streamlit Cloud secrets."""

from __future__ import annotations

import os
import re

import streamlit as st

PLACEHOLDER_PASSWORDS = {
    "",
    "changeme",
    "your-password",
    "your-supabase-password",
    "your-supabase-database-password",
    "your-db-password",
    "YOUR_SUPABASE_PASSWORD",
    "your password",
}

DEFAULT_REGION = "Bangalore"


def _project_ref(url: str) -> str | None:
    m = re.search(r"https://([a-z0-9]+)\.supabase\.co", url.strip())
    return m.group(1) if m else None


def _from_secrets_flat(key: str) -> str | None:
    try:
        if key in st.secrets:
            val = st.secrets[key]
            return str(val).strip() if val is not None else None
    except Exception:
        pass
    return None


def _from_secrets_nested(key: str) -> str | None:
    """Support optional [database] or [supabase] sections in secrets.toml."""
    aliases: dict[str, list[tuple[str, str]]] = {
        "DB_HOST": [("database", "host"), ("supabase", "db_host"), ("supabase", "host")],
        "DB_PORT": [("database", "port"), ("supabase", "db_port")],
        "DB_NAME": [("database", "name"), ("database", "database"), ("supabase", "db_name")],
        "DB_USER": [("database", "user"), ("database", "username"), ("supabase", "db_user")],
        "DB_PASSWORD": [("database", "password"), ("supabase", "db_password")],
        "SUPABASE_URL": [("supabase", "url")],
        "ORCHESTRATOR_URL": [("orchestrator", "url"), ("services", "orchestrator_url")],
        "ORCHESTRATOR_API_KEY": [("orchestrator", "api_key"), ("services", "orchestrator_api_key")],
        "VEO_MCP_URL": [("services", "veo_mcp_url"), ("veo", "url")],
        "OLLAMA_BASE_URL": [("ollama", "url"), ("services", "ollama_url")],
        "ENABLE_DASHBOARD_SIMULATION": [("dashboard", "simulate"), ("features", "simulate_activity")],
        "AUTO_SYNC_PIPELINE": [("dashboard", "auto_sync"), ("features", "auto_sync_pipeline")],
        "AUTO_SYNC_INTERVAL_MINUTES": [("dashboard", "sync_interval_minutes")],
        "GROQ_API_KEY": [("llm", "groq_api_key"), ("groq", "api_key")],
        "GEMINI_API_KEY": [("llm", "gemini_api_key"), ("gemini", "api_key")],
    }
    for section, field in aliases.get(key, []):
        try:
            block = st.secrets.get(section)
            if block is None:
                continue
            if hasattr(block, field):
                val = getattr(block, field, None)
            elif isinstance(block, dict) and field in block:
                val = block[field]
            else:
                continue
            if val is not None:
                return str(val).strip()
        except Exception:
            continue
    return None


def _get(key: str, default: str = "") -> str:
    env_val = os.environ.get(key)
    if env_val:
        return env_val.strip()

    flat = _from_secrets_flat(key)
    if flat is not None:
        return flat

    nested = _from_secrets_nested(key)
    if nested is not None:
        return nested

    return default


def _secrets_source() -> str:
    if any(os.environ.get(k) for k in ("DB_HOST", "DB_PASSWORD", "DB_USER")):
        return "environment variables"
    try:
        if "DB_PASSWORD" in st.secrets or "database" in st.secrets or "supabase" in st.secrets:
            return "Streamlit Cloud secrets"
    except Exception:
        pass
    return "defaults (not configured)"


_supabase_url = _get("SUPABASE_URL", "")
_ref = _project_ref(_supabase_url)

DB_HOST = _get("DB_HOST", "")
if not DB_HOST or DB_HOST in ("localhost", "db.localhost"):
    DB_HOST = "aws-1-ap-south-1.pooler.supabase.com" if _ref else "localhost"

DB_PORT = int(_get("DB_PORT", "5432") or "5432")
DB_NAME = _get("DB_NAME", "postgres" if _ref else "nivara")

DB_USER = _get("DB_USER", "")
if (not DB_USER or DB_USER == "postgres") and _ref:
    DB_USER = f"postgres.{_ref}"
elif not DB_USER:
    DB_USER = "nivara"

DB_PASSWORD = _get("DB_PASSWORD", "changeme")
ORCH_URL = _get("ORCHESTRATOR_URL", "http://localhost:8000")
VEO_URL = _get("VEO_MCP_URL", "http://localhost:8006")
OLLAMA_URL = _get("OLLAMA_BASE_URL", "http://localhost:11434")
ORCHESTRATOR_API_KEY = _get("ORCHESTRATOR_API_KEY", "")

_sim_flag = _get("ENABLE_DASHBOARD_SIMULATION", "false").strip().lower()
ENABLE_DASHBOARD_SIMULATION = _sim_flag in ("1", "true", "yes", "on")

_auto_flag = _get("AUTO_SYNC_PIPELINE", "true").strip().lower()
AUTO_SYNC_PIPELINE = _auto_flag not in ("0", "false", "no", "off")

AUTO_SYNC_INTERVAL_MINUTES = int(_get("AUTO_SYNC_INTERVAL_MINUTES", "360") or "360")
GROQ_API_KEY = _get("GROQ_API_KEY", "")
GEMINI_API_KEY = _get("GEMINI_API_KEY", "")


def orchestrator_headers() -> dict[str, str]:
    if ORCHESTRATOR_API_KEY.strip():
        return {"X-API-Key": ORCHESTRATOR_API_KEY.strip()}
    return {}


def password_is_placeholder() -> bool:
    return DB_PASSWORD.strip() in PLACEHOLDER_PASSWORDS


def connection_config() -> dict[str, str | int | bool]:
    """Masked diagnostics for the Settings tab."""
    pwd = DB_PASSWORD
    return {
        "source": _secrets_source(),
        "host": DB_HOST,
        "port": DB_PORT,
        "database": DB_NAME,
        "user": DB_USER,
        "password_set": bool(pwd) and not password_is_placeholder(),
        "password_placeholder": password_is_placeholder(),
        "password_preview": ("*" * min(len(pwd), 8)) if pwd and not password_is_placeholder() else "(not set)",
        "supabase_url_set": bool(_supabase_url),
        "project_ref": _ref or "(none)",
    }
