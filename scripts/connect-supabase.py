#!/usr/bin/env python3
"""Connect NIVARA to a Supabase Postgres database and apply migrations."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = sorted((ROOT / "supabase" / "migrations").glob("*.sql"))
SEED = ROOT / "supabase" / "seed.sql"


def load_env() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        print(f"Missing {env_path}. Copy .env.example and add your Supabase credentials.")
        sys.exit(1)
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
    except ImportError:
        pass


def project_ref_from_url(url: str) -> str | None:
    m = re.search(r"https://([a-z0-9]+)\.supabase\.co", url.strip())
    return m.group(1) if m else None


def resolve_db_settings() -> dict[str, str]:
    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    ref = project_ref_from_url(supabase_url)

    host = os.getenv("DB_HOST", "").strip()
    user = os.getenv("DB_USER", "postgres").strip()
    if (not host or host == "localhost") and ref:
        host = "aws-1-ap-south-1.pooler.supabase.com"
        if "." not in user or user == "postgres":
            user = f"postgres.{ref}"

    return {
        "host": host,
        "port": os.getenv("DB_PORT", "5432"),
        "dbname": os.getenv("DB_NAME", "postgres"),
        "user": user,
        "password": os.getenv("DB_PASSWORD", ""),
    }


def validate_settings(cfg: dict[str, str]) -> None:
    missing = [k for k, v in cfg.items() if not v and k != "port"]
    if missing:
        print("Missing required values in .env:")
        for key in missing:
            print(f"  - {key.upper() if key != 'dbname' else 'DB_NAME'}")
        print("\nGet these from Supabase → Project Settings → Database / API")
        sys.exit(1)

    if cfg["host"] in ("localhost", "127.0.0.1"):
        print("DB_HOST is still localhost. Set SUPABASE_URL and DB_PASSWORD in .env first.")
        sys.exit(1)

    if "your-project-ref" in os.getenv("SUPABASE_URL", ""):
        print("SUPABASE_URL is still a placeholder. Update .env with your real Supabase project URL.")
        sys.exit(1)


def connect(cfg: dict[str, str]):
    import psycopg2
    return psycopg2.connect(
        host=cfg["host"],
        port=cfg["port"],
        dbname=cfg["dbname"],
        user=cfg["user"],
        password=cfg["password"],
        connect_timeout=15,
        sslmode="require",
    )


def run_sql_file(conn, path: Path) -> None:
    sql = path.read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    print(f"  ✓ {path.name}")


def list_tables(conn) -> list[str]:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_name"
        )
        return [r[0] for r in cur.fetchall()]


def main() -> None:
    load_env()
    cfg = resolve_db_settings()
    validate_settings(cfg)

    print(f"Connecting to {cfg['host']}:{cfg['port']}/{cfg['dbname']} as {cfg['user']}...")

    try:
        conn = connect(cfg)
    except Exception as exc:
        print(f"Connection failed: {exc}")
        print("\nCheck DB_PASSWORD and that your IP is allowed (Supabase → Database → Network).")
        sys.exit(1)

    print("Connected.\n")

    existing = list_tables(conn)
    if "projects" in existing:
        print(f"Database already has {len(existing)} tables. Skipping migrations.")
        print("Tables:", ", ".join(existing[:12]), "..." if len(existing) > 12 else "")
    else:
        print("Running migrations...")
        for path in MIGRATIONS:
            try:
                run_sql_file(conn, path)
            except Exception as exc:
                print(f"  ✗ {path.name}: {exc}")
                conn.rollback()
                sys.exit(1)

        if SEED.exists() and (
        "--seed" in sys.argv
        or input("\nRun seed.sql for sample data? [y/N]: ").strip().lower() == "y"
    ):
            run_sql_file(conn, SEED)
            print("  ✓ seed.sql")

    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM leads")
        leads = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM projects")
        projects = cur.fetchone()[0]
    conn.close()

    print(f"\nDone. leads={leads}, projects={projects}")
    print("\nNext steps:")
    print("  1. Copy same DB_* values to agents/.env")
    print("  2. Copy to dashboard/.streamlit/secrets.toml (local) or Streamlit Cloud secrets")
    print("  3. Restart services: ./scripts/start-dashboard.sh")
    print("  4. Import local data: run SQL files in supabase/import/ if needed")


if __name__ == "__main__":
    main()
