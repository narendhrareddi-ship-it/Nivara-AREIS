#!/usr/bin/env python3
"""Configure all Render services via API — set secrets, trigger deploys, verify health."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
load_dotenv(ROOT / ".env.render")

API_BASE = "https://api.render.com/v1"
SERVICES = [
    "nivara-dashboard",
    "nivara-orchestrator",
    "nivara-veo-mcp",
    "nivara-social-mcp",
]

SECRET_KEYS = [
    "DB_PASSWORD",
    "GEMINI_API_KEY",
    "GROQ_API_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "SUPABASE_URL",
    "MEDIA_PUBLIC_BASE_URL",
    "ORCHESTRATOR_API_KEY",
    "OPENROUTER_API_KEY",
]

HEALTH_URLS = {
    "nivara-dashboard": "https://nivara-dashboard.onrender.com/_stcore/health",
    "nivara-orchestrator": "https://nivara-orchestrator.onrender.com/health",
    "nivara-veo-mcp": "https://nivara-veo-mcp.onrender.com/health",
    "nivara-social-mcp": "https://nivara-social-mcp.onrender.com/health",
}


def api_key() -> str:
    key = os.getenv("RENDER_API_KEY", "").strip()
    if not key:
        print("ERROR: RENDER_API_KEY not set.")
        print("  1. Open https://dashboard.render.com/u/settings#api-keys")
        print("  2. Create API key → add to .env.render as RENDER_API_KEY=rnd_...")
        print("  3. Re-run: python3 scripts/render-setup.py")
        sys.exit(1)
    return key


def headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key()}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def list_services() -> list[dict]:
    out: list[dict] = []
    cursor: str | None = None
    while True:
        params = {"limit": 100}
        if cursor:
            params["cursor"] = cursor
        r = requests.get(f"{API_BASE}/services", headers=headers(), params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        out.extend(data if isinstance(data, list) else [])
        cursor = r.headers.get("X-Next-Cursor") or r.headers.get("x-next-cursor")
        if not cursor:
            break
    return out


def find_service(services: list[dict], name: str) -> dict | None:
    for svc in services:
        if svc.get("name") == name or svc.get("service", {}).get("name") == name:
            return svc.get("service", svc)
        if svc.get("service", {}).get("name") == name:
            return svc["service"]
    for svc in services:
        s = svc if "id" in svc else svc.get("service", {})
        if s.get("name") == name:
            return s
    return None


def get_env_vars(service_id: str) -> list[dict]:
    r = requests.get(f"{API_BASE}/services/{service_id}/env-vars", headers=headers(), timeout=30)
    r.raise_for_status()
    data = r.json()
    return data if isinstance(data, list) else data.get("envVars", [])


def merge_env_vars(existing: list[dict], updates: dict[str, str]) -> list[dict]:
    by_key = {}
    for item in existing:
        ev = item.get("envVar", item)
        key = ev.get("key")
        if key:
            by_key[key] = ev.get("value", "")
    for key, value in updates.items():
        if value:
            by_key[key] = value
    return [{"key": k, "value": v} for k, v in sorted(by_key.items())]


def set_env_vars(service_id: str, updates: dict[str, str]) -> None:
    existing = get_env_vars(service_id)
    payload = merge_env_vars(existing, updates)
    r = requests.put(
        f"{API_BASE}/services/{service_id}/env-vars",
        headers=headers(),
        json=payload,
        timeout=60,
    )
    r.raise_for_status()


def trigger_deploy(service_id: str) -> None:
    r = requests.post(
        f"{API_BASE}/services/{service_id}/deploys",
        headers=headers(),
        json={"clearCache": "clear"},
        timeout=60,
    )
    if r.status_code not in (200, 201, 202):
        r = requests.post(
            f"{API_BASE}/services/{service_id}/deploys",
            headers=headers(),
            json={},
            timeout=60,
        )
    r.raise_for_status()


def secret_values() -> dict[str, str]:
    values = {
        "DB_PASSWORD": os.getenv("DB_PASSWORD", ""),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY", ""),
        "SUPABASE_URL": os.getenv("SUPABASE_URL", ""),
        "SUPABASE_SERVICE_ROLE_KEY": os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
        "MEDIA_PUBLIC_BASE_URL": "https://nivara-veo-mcp.onrender.com/media",
    }
    return {k: v for k, v in values.items() if v}


def wait_health(name: str, timeout: int = 180) -> bool:
    url = HEALTH_URLS.get(name)
    if not url:
        return False
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(url, timeout=25)
            if name == "nivara-dashboard":
                if r.status_code == 200 and "ok" in r.text.lower():
                    return True
            elif r.status_code == 200:
                if name == "nivara-orchestrator":
                    data = r.json()
                    if data.get("db_connected"):
                        return True
                else:
                    return True
        except Exception:
            pass
        time.sleep(10)
    return False


def main() -> int:
    print("NIVARA Render setup\n")
    secrets = secret_values()
    if not secrets.get("DB_PASSWORD"):
        print("ERROR: DB_PASSWORD missing from .env")
        return 1

    services = list_services()
    found = {}
    for name in SERVICES:
        svc = find_service(services, name)
        if svc:
            found[name] = svc["id"]
            print(f"[found] {name} → {svc['id']}")
        else:
            print(f"[missing] {name} — sync blueprint on Render first")

    if not found:
        print("\nNo services found. Connect repo on Render → Blueprints → Sync.")
        return 1

    for name, sid in found.items():
        print(f"\nUpdating env vars: {name}")
        updates = dict(secrets)
        if name == "nivara-veo-mcp":
            updates["MEDIA_PUBLIC_BASE_URL"] = secrets.get("MEDIA_PUBLIC_BASE_URL", "")
        set_env_vars(sid, updates)
        print(f"Deploying: {name}")
        trigger_deploy(sid)

    print("\nWaiting for health checks...")
    ok = True
    for name in found:
        healthy = wait_health(name, timeout=120 if name == "nivara-dashboard" else 60)
        mark = "OK" if healthy else "PENDING"
        print(f"  [{mark}] {name}")
        if not healthy and name in ("nivara-dashboard", "nivara-orchestrator"):
            ok = False

    print(f"\nDashboard: https://nivara-dashboard.onrender.com")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
