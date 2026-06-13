#!/usr/bin/env python3
"""Clear stale bot_logs so the dashboard reflects the next full pipeline run."""

from __future__ import annotations

import os
import sys

import psycopg2


def main() -> int:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "nivara"),
        user=os.getenv("DB_USER", "nivara"),
        password=os.getenv("DB_PASSWORD", "changeme"),
        sslmode=os.getenv("DB_SSLMODE", "prefer"),
    )
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM bot_logs")
            deleted = cur.rowcount
        conn.commit()
        print(f"Cleared {deleted} bot_log rows. Run the orchestrator to populate 20/20.")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
