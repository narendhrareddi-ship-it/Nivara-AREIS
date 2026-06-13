#!/usr/bin/env bash
# Export local PostgreSQL data to SQL files for importing into Supabase.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${ROOT}/supabase/import"
mkdir -p "$OUT"

source "${ROOT}/.env" 2>/dev/null || true

HOST="${DB_HOST:-localhost}"
PORT="${DB_PORT:-5432}"
DB="${DB_NAME:-nivara}"
USER="${DB_USER:-nivara}"
export PGPASSWORD="${DB_PASSWORD:-changeme}"

TABLES=(projects campaigns leads social_posts media_assets bot_logs crm_activity competitors)

echo "Exporting from ${HOST}:${PORT}/${DB} → ${OUT}/"

for t in "${TABLES[@]}"; do
  if pg_dump -h "$HOST" -p "$PORT" -U "$USER" -d "$DB" -t "$t" \
      --data-only --column-inserts --no-owner --no-acl \
      -f "${OUT}/${t}.sql" 2>/dev/null; then
    echo "  ✓ ${t}.sql"
  else
    echo "  - ${t} (skipped or empty)"
    rm -f "${OUT}/${t}.sql"
  fi
done

echo ""
echo "Import into Supabase: SQL Editor → run each file in supabase/import/ after migrations."
