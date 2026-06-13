"""Load dashboard settings from environment variables or Streamlit Cloud secrets."""

from __future__ import annotations

import os

import streamlit as st


def _get(key: str, default: str = "") -> str:
    if os.environ.get(key):
        return os.environ[key]
    try:
        return str(st.secrets[key])
    except Exception:
        return default


DB_HOST = _get("DB_HOST", "localhost")
DB_PORT = int(_get("DB_PORT", "5432"))
DB_NAME = _get("DB_NAME", "nivara")
DB_USER = _get("DB_USER", "nivara")
DB_PASSWORD = _get("DB_PASSWORD", "changeme")
ORCH_URL = _get("ORCHESTRATOR_URL", "http://localhost:8000")
VEO_URL = _get("VEO_MCP_URL", "http://localhost:8006")
OLLAMA_URL = _get("OLLAMA_BASE_URL", "http://localhost:11434")
