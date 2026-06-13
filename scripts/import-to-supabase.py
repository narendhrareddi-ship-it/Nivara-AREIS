#!/usr/bin/env python3
"""Import local exported SQL data into Supabase."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMPORT_DIR = ROOT / "supabase" / "import"
ORDER = [
    "projects.sql",
    "campaigns.sql",
    "competitors.sql",
    "leads.sql",
    "crm_activity.sql",
    "social_posts.sql",
    "media_assets.sql",
    "bot_logs.sql",
]


def main() -> None:
    from dotenv import load_dotenv
    import psycopg2

    load_dotenv(ROOT / ".env")
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode="require",
        connect_timeout=15,
    )

    for name in ORDER:
        path = IMPORT_DIR / name
        if not path.exists():
            print(f"skip {name}")
            continue
        sql = path.read_text(encoding="utf-8").strip()
        if not sql:
            continue
        # Strip pg_dump psql meta-commands (\restrict etc.)
        lines = [
            ln for ln in sql.splitlines()
            if not ln.strip().startswith("\\")
            and not ln.strip().startswith("SET ")
            and not ln.strip().startswith("SELECT pg_catalog")
        ]
        sql = "\n".join(ln for ln in lines if ln.strip())
        if not sql:
            continue
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()
            print(f"  ✓ {name}")
        except Exception as exc:
            conn.rollback()
            print(f"  ✗ {name}: {exc}")

    with conn.cursor() as cur:
        for table in ["projects", "leads", "social_posts", "media_assets", "bot_logs"]:
            cur.execute(f"SELECT count(*) FROM {table}")
            print(f"  {table}: {cur.fetchone()[0]}")
    conn.close()


if __name__ == "__main__":
    main()
