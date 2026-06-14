"""Fast database access — one persistent connection and short-lived read cache."""

from __future__ import annotations

import json
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st

from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

_last_db_error: str | None = None


@st.cache_resource(show_spinner=False)
def _open_connection() -> psycopg2.extensions.connection:
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor,
        sslmode="require",
        connect_timeout=10,
        keepalives=1,
        keepalives_idle=30,
        keepalives_interval=10,
        keepalives_count=3,
    )


def _reset_connection() -> psycopg2.extensions.connection:
    st.cache_resource.clear()
    return _open_connection()


def get_conn() -> psycopg2.extensions.connection | None:
    global _last_db_error
    try:
        conn = _open_connection()
        if conn.closed:
            conn = _reset_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        return conn
    except Exception as exc:
        _last_db_error = str(exc)
        try:
            return _reset_connection()
        except Exception as exc2:
            _last_db_error = str(exc2)
            return None


def _execute(sql: str, params: tuple[Any, ...] | list[Any] | None, *, one: bool) -> Any:
    conn = get_conn()
    if not conn:
        return None if one else []
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            if cur.description is None:
                conn.commit()
                invalidate_reads()
                return None if one else []
            return cur.fetchone() if one else cur.fetchall()
    except Exception:
        conn.rollback()
        return None if one else []


def invalidate_reads() -> None:
    st.cache_data.clear()


@st.cache_data(ttl=20, show_spinner=False)
def _cached_read(sql: str, params_key: str, one: bool) -> Any:
    params: tuple[Any, ...] | None = None
    if params_key:
        decoded = json.loads(params_key)
        if decoded is not None:
            params = tuple(decoded)
    return _execute(sql, params, one=one)


def q(
    sql: str,
    params: tuple[Any, ...] | list[Any] | None = None,
    *,
    one: bool = False,
    write: bool = False,
) -> Any:
    """Run a query. Reads are cached ~20s; writes clear the cache."""
    normalized = sql.strip().upper()
    is_write = write or normalized.startswith(("INSERT", "UPDATE", "DELETE", "TRUNCATE"))
    if is_write:
        p = tuple(params) if params else None
        return _execute(sql, p, one=one)

    params_key = json.dumps(list(params) if params else None, default=str)
    return _cached_read(sql, params_key, one)


@st.cache_data(ttl=300, show_spinner=False)
def check_db() -> tuple[bool, str | None]:
    global _last_db_error
    conn = get_conn()
    if not conn:
        return False, _last_db_error
    return True, None


@st.cache_data(ttl=15, show_spinner=False)
def load_performance_stats() -> dict[str, Any]:
    row = _execute(
        """
        SELECT
          (SELECT count(*)::int FROM leads) AS total_leads,
          (SELECT count(*)::int FROM leads WHERE score >= 70) AS hot_leads,
          (SELECT COALESCE(AVG(score), 0)::int FROM leads) AS avg_score,
          (SELECT count(*)::int FROM leads WHERE status = 'converted') AS converted,
          (SELECT count(*)::int FROM social_posts) AS posts,
          (SELECT COALESCE(SUM(reach), 0)::bigint FROM social_posts) AS total_reach,
          (SELECT count(*)::int FROM bot_logs) AS agent_runs,
          (SELECT count(*)::int FROM crm_activity) AS crm_actions
        """,
        None,
        one=True,
    )
    return dict(row) if row else {}


@st.cache_data(ttl=60, show_spinner=False)
def pipeline_cycle_status() -> tuple[int, set[str]]:
    rows = q(
        """
        SELECT agent_name, action
        FROM bot_logs
        WHERE timestamp >= COALESCE(
            (SELECT MAX(timestamp) FROM bot_logs
             WHERE agent_name = 'MarketAnalyst' AND action = 'Starting task'),
            NOW() - INTERVAL '1 hour'
        )
        ORDER BY timestamp ASC
        """,
    )
    done: set[str] = set()
    if rows:
        for row in rows:
            if row.get("action") == "Task completed":
                done.add(row["agent_name"])
    return len(done), done


@st.cache_data(ttl=45, show_spinner=False)
def fetch_orchestrator_health(orch_url: str) -> dict[str, Any]:
    try:
        import requests

        response = requests.get(f"{orch_url.rstrip('/')}/health", timeout=5)
        if response.ok:
            return response.json()
    except Exception:
        pass
    return {}

