#!/usr/bin/env python3
"""Bootstrap NIVARA production: DB sync, health checks, secrets template."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "dashboard"))
sys.path.insert(0, str(ROOT / "agents" / "src"))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

import psycopg2
from psycopg2.extras import RealDictCursor
import requests

REPORT: dict = {"ok": True, "steps": []}


def step(name: str, ok: bool, detail: str = "") -> None:
    REPORT["steps"].append({"name": name, "ok": ok, "detail": detail})
    if not ok:
        REPORT["ok"] = False
    mark = "OK" if ok else "FAIL"
    print(f"[{mark}] {name}" + (f" — {detail}" if detail else ""))


def db_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode="require",
        connect_timeout=15,
        cursor_factory=RealDictCursor,
    )


def check_database() -> None:
    try:
        conn = db_conn()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.execute("SELECT count(*) c FROM bot_logs")
        logs = cur.fetchone()["c"]
        cur.execute(
            """
            SELECT count(DISTINCT agent_name) c FROM bot_logs
            WHERE action = 'Task completed'
            AND timestamp >= COALESCE(
                (SELECT MAX(timestamp) FROM bot_logs
                 WHERE agent_name = 'MarketAnalyst' AND action = 'Starting task'),
                NOW() - INTERVAL '1 hour'
            )
            """
        )
        agents = cur.fetchone()["c"]
        cur.execute("SELECT count(*) c FROM social_posts")
        posts = cur.fetchone()["c"]
        conn.close()
        step("Database", True, f"{logs} bot_logs, {agents}/20 agents, {posts} posts")
    except Exception as exc:
        step("Database", False, str(exc))


def run_pipeline_sync() -> None:
    try:
        from pipeline_sync import auto_sync_pipeline, PIPELINE_AGENTS

        def q(sql, p=None, one=False):
            conn = db_conn()
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, p)
                    return cur.fetchone() if one else cur.fetchall()
            finally:
                conn.close()

        result = auto_sync_pipeline(
            q,
            db_host=os.getenv("DB_HOST", ""),
            db_port=int(os.getenv("DB_PORT", "5432")),
            db_name=os.getenv("DB_NAME", ""),
            db_user=os.getenv("DB_USER", ""),
            db_password=os.getenv("DB_PASSWORD", ""),
            default_region=os.getenv("DEFAULT_REGION", "Bangalore"),
            orch_url=os.getenv("ORCHESTRATOR_URL", "https://nivara-orchestrator.onrender.com"),
            interval_minutes=360,
            prefer_direct=True,
            groq_api_key=os.getenv("GROQ_API_KEY", ""),
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        )
        synced = result.get("synced", False)
        reason = result.get("reason", "")
        ok = synced or "up to date" in reason.lower()
        step(
            "Pipeline sync",
            ok,
            f"{result.get('agents_completed', 0)}/{len(PIPELINE_AGENTS)} mode={result.get('mode')} — {reason}",
        )
    except Exception as exc:
        step("Pipeline sync", False, str(exc))


def check_render_services() -> None:
    services = {
        "orchestrator": "https://nivara-orchestrator.onrender.com/health",
        "veo-mcp": "https://nivara-veo-mcp.onrender.com/health",
        "social-mcp": "https://nivara-social-mcp.onrender.com/health",
        "dashboard": "https://nivara-dashboard.onrender.com/",
    }
    for name, url in services.items():
        try:
            r = requests.get(url, timeout=20)
            if name == "dashboard":
                ok = r.status_code == 200 and "do not have access" not in r.text.lower()
                detail = f"HTTP {r.status_code}" + (" — deploy nivara-dashboard on Render" if not ok else "")
            else:
                data = r.json() if r.ok else {}
                ok = r.ok
                if name == "orchestrator":
                    detail = f"agents={data.get('agent_count')} db={data.get('db_connected')}"
                else:
                    detail = f"HTTP {r.status_code}"
            step(f"Render {name}", ok, detail)
        except Exception as exc:
            step(f"Render {name}", False, str(exc))


def write_secrets_templates() -> None:
    pwd = os.getenv("DB_PASSWORD", "YOUR_REAL_SUPABASE_PASSWORD")
    gemini = os.getenv("GEMINI_API_KEY", "")
    groq = os.getenv("GROQ_API_KEY", "")

    streamlit = f'''# Paste into Streamlit Cloud → Settings → Secrets
SUPABASE_URL = "https://mxjhwjxxqtkwsrwtqwuc.supabase.co"
DB_HOST = "aws-1-ap-south-1.pooler.supabase.com"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "postgres.mxjhwjxxqtkwsrwtqwuc"
DB_PASSWORD = "{pwd}"
ORCHESTRATOR_URL = "https://nivara-orchestrator.onrender.com"
VEO_MCP_URL = "https://nivara-veo-mcp.onrender.com"
AUTO_SYNC_ON_LOAD = "false"
GEMINI_API_KEY = "{gemini}"
GROQ_API_KEY = "{groq}"
'''
    out = ROOT / "generated" / "streamlit-secrets.toml"
    out.parent.mkdir(exist_ok=True)
    out.write_text(streamlit, encoding="utf-8")
    step("Secrets template", True, str(out))


def main() -> int:
    print("NIVARA bootstrap\n")
    check_database()
    run_pipeline_sync()
    check_render_services()
    write_secrets_templates()
    print()
    print("Primary dashboard URL: https://nivara-dashboard.onrender.com")
    print("Streamlit (optional):  https://nivara-areis.streamlit.app")
    print()
    report_path = ROOT / "generated" / "bootstrap-report.json"
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(json.dumps(REPORT, indent=2), encoding="utf-8")
    print(f"Report: {report_path}")
    return 0 if REPORT["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
