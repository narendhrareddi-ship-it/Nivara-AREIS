#!/usr/bin/env python3
"""Run full 20-agent pipeline sync (CLI / cron / GitHub Actions)."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

# Allow importing dashboard helpers
sys.path.insert(0, str(ROOT / "dashboard"))

import psycopg2
from psycopg2.extras import RealDictCursor

from pipeline_sync import (
    PIPELINE_AGENTS,
    auto_sync_pipeline,
    latest_cycle_completed,
    needs_sync,
)


def _query(sql: str, p=None, one: bool = False):
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "nivara"),
        user=os.getenv("DB_USER", "nivara"),
        password=os.getenv("DB_PASSWORD", "changeme"),
        sslmode=os.getenv("DB_SSLMODE", "require"),
        cursor_factory=RealDictCursor,
        connect_timeout=30,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(sql, p)
            return cur.fetchone() if one else cur.fetchall()
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync 20-agent pipeline to Supabase bot_logs")
    parser.add_argument("--force", action="store_true", help="Run even if pipeline looks complete")
    parser.add_argument("--interval", type=int, default=int(os.getenv("AUTO_SYNC_INTERVAL_MINUTES", "360")))
    args = parser.parse_args()

    if not args.force:
        should, reason = needs_sync(_query, interval_minutes=args.interval)
        if not should:
            done = latest_cycle_completed(_query)
            print(f"Pipeline OK: {len(done)}/{len(PIPELINE_AGENTS)} — {reason}")
            return 0
        print(f"Sync needed: {reason}")
    else:
        print("Forced pipeline sync")

    result = auto_sync_pipeline(
        _query,
        db_host=os.getenv("DB_HOST", ""),
        db_port=int(os.getenv("DB_PORT", "5432")),
        db_name=os.getenv("DB_NAME", "postgres"),
        db_user=os.getenv("DB_USER", ""),
        db_password=os.getenv("DB_PASSWORD", ""),
        default_region=os.getenv("DEFAULT_REGION", "Bangalore"),
        orch_url=os.getenv("ORCHESTRATOR_URL", ""),
        orch_headers={"X-API-Key": os.getenv("ORCHESTRATOR_API_KEY", "")}
        if os.getenv("ORCHESTRATOR_API_KEY")
        else {},
        interval_minutes=args.interval,
        prefer_direct=True,
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
    )

    print(
        f"Sync result: synced={result['synced']} mode={result.get('mode')} "
        f"{result['agents_completed']}/{result['agents_expected']} — {result['reason']}"
    )
    if result.get("error"):
        print(f"Error: {result['error']}", file=sys.stderr)
    return 0 if result["synced"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
