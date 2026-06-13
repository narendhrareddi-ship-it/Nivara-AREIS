#!/usr/bin/env python3
"""Create the Supabase Storage bucket for NIVARA media (idempotent)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agents" / "src"))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")
load_dotenv(ROOT / "agents" / ".env")

url = os.getenv("SUPABASE_URL", "")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
bucket = os.getenv("SUPABASE_STORAGE_BUCKET", "media")


def main() -> int:
    if not url or not key:
        print("SKIP: Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY to create storage bucket.")
        return 0

    from supabase import create_client

    client = create_client(url, key)
    buckets = [b.name for b in client.storage.list_buckets()]

    if bucket in buckets:
        print(f"OK: Bucket '{bucket}' already exists.")
        return 0

    try:
        client.storage.create_bucket(bucket, options={"public": True})
        print(f"OK: Created public bucket '{bucket}'.")
    except Exception as exc:
        if "already exists" in str(exc).lower():
            print(f"OK: Bucket '{bucket}' already exists.")
            return 0
        print(f"ERROR: Could not create bucket: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
