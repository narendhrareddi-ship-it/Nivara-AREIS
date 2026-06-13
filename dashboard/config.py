"""Load dashboard settings from environment variables or Streamlit Cloud secrets."""

from __future__ import annotations

import os
import re

import streamlit as st


def _get(key: str, default: str = "") -> str:
    if os.environ.get(key):
        return os.environ[key]
    try:
        return str(st.secrets[key])
    except Exception:
        return default


def _project_ref(url: str) -> str | None:
    m = re.search(r"https://([a-z0-9]+)\.supabase\.co", url.strip())
    return m.group(1) if m else None


_supabase_url = _get("SUPABASE_URL", "")
_ref = _project_ref(_supabase_url)

DB_HOST = _get("DB_HOST", "")
if not DB_HOST or DB_HOST in ("localhost", "db.localhost"):
    DB_HOST = "aws-1-ap-south-1.pooler.supabase.com" if _ref else "localhost"

DB_PORT = int(_get("DB_PORT", "5432"))
DB_NAME = _get("DB_NAME", "postgres" if _ref else "nivara")

DB_USER = _get("DB_USER", "")
if not DB_USER or DB_USER == "postgres" and _ref:
    DB_USER = f"postgres.{_ref}" if _ref else "nivara"
elif not DB_USER:
    DB_USER = "nivara"

DEFAULT_REGION = "Bangalore"

DB_PASSWORD = _get("DB_PASSWORD", "changeme")
ORCH_URL = _get("ORCHESTRATOR_URL", "http://localhost:8000")
VEO_URL = _get("VEO_MCP_URL", "http://localhost:8006")
OLLAMA_URL = _get("OLLAMA_BASE_URL", "http://localhost:11434")
