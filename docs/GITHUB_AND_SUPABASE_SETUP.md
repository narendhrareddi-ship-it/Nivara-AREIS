# GitHub Repo Change + Supabase Upload Guide

Complete instructions to move NIVARA to a **new GitHub repository** and upload your **local database + files** to **Supabase**.

---

## Part 1 — Create a new GitHub repository

### Step 1: Create the repo on GitHub

1. Go to [github.com/new](https://github.com/new)
2. Set:
   - **Repository name:** e.g. `Nivara-AREIS` (or your preferred name)
   - **Visibility:** Private or Public
   - **Do NOT** initialize with README (you already have code)
3. Click **Create repository**

### Step 2: Push your local project to the new repo

On your computer, in the project folder:

```bash
cd /path/to/your/nivara-project

# Check current remote
git remote -v

# Remove old remote (if pointing to old repo)
git remote remove origin

# Add your NEW repo (replace YOUR_USERNAME and YOUR_REPO)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Push all branches
git push -u origin main

# If your work is on a feature branch, push that too
git push -u origin cursor/phase2-higgsfield-integration-077c
```

### Step 3: Verify on GitHub

Open `https://github.com/YOUR_USERNAME/YOUR_REPO` — you should see:

- `dashboard/`
- `agents/`
- `supabase/migrations/`
- `mcp-servers/`
- `docs/`

### Step 4: Reconnect Streamlit Cloud (if already deployed)

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Open your app → **Settings → General**
3. Change **Repository** to your new GitHub repo
4. Set **Main file path:** `dashboard/app.py`
5. Save → app redeploys from the new repo

---

## Part 2 — Create Supabase project

### Step 1: Create project

1. Go to [supabase.com](https://supabase.com) → **Start your project**
2. **New project:**
   - Name: `nivara-realty`
   - Database password: **save this** — you need it later
   - Region: choose closest to Chennai (e.g. Mumbai / Singapore)
3. Wait ~2 minutes for provisioning

### Step 2: Collect connection details

In Supabase dashboard → **Project Settings**:

| Where to find | What to copy |
|---------------|--------------|
| **Settings → API → Project URL** | `SUPABASE_URL` |
| **Settings → API → anon public** | `SUPABASE_ANON_KEY` |
| **Settings → API → service_role** | `SUPABASE_SERVICE_ROLE_KEY` |
| **Settings → Database → Host** | `DB_HOST` (e.g. `db.xxxxx.supabase.co`) |
| **Settings → Database → Port** | `5432` |
| **Settings → Database → Database name** | `postgres` |
| **Settings → Database → User** | `postgres` |
| **Your chosen password** | `DB_PASSWORD` |

> **Important:** Supabase uses database name `postgres` and user `postgres` — not `nivara`.

---

## Part 3 — Upload schema to Supabase (SQL migrations)

Run these files **in order** in Supabase **SQL Editor** (left menu → SQL Editor → New query).

### Migration 1 — Core schema

1. Open `supabase/migrations/001_initial_schema.sql` from your project
2. Copy entire file → paste into SQL Editor
3. Click **Run**
4. Expected: tables created (projects, leads, campaigns, etc.)

### Migration 2 — Media + bot logs

1. Open `supabase/migrations/002_phase2_media_and_bot_logs.sql`
2. Copy → paste → **Run**
3. Expected: `bot_logs`, `media_assets` tables created

### Migration 3 — Veo provider cleanup

1. Open `supabase/migrations/004_veo_provider.sql`
2. Copy → paste → **Run**
3. Safe even on fresh DB (updates zero rows if no legacy data)

### Seed data (optional sample data)

1. Open `supabase/seed.sql`
2. Copy → paste → **Run**
3. Adds sample projects, leads, campaigns for Chennai/Andhra

### Verify tables exist

Run in SQL Editor:

```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

You should see: `bot_logs`, `campaigns`, `crm_activity`, `leads`, `media_assets`, `projects`, `social_posts`, etc.

---

## Part 4 — Upload local data to Supabase

If you have data on **local PostgreSQL** that you want to move to Supabase:

### Option A — Export specific tables (recommended)

On your local machine (where local Postgres runs):

```bash
# Export leads
pg_dump -h localhost -U nivara -d nivara -t leads --data-only --column-inserts > leads_export.sql

# Export social_posts
pg_dump -h localhost -U nivara -d nivara -t social_posts --data-only --column-inserts > social_posts_export.sql

# Export media_assets
pg_dump -h localhost -U nivara -d nivara -t media_assets --data-only --column-inserts > media_assets_export.sql

# Export bot_logs
pg_dump -h localhost -U nivara -d nivara -t bot_logs --data-only --column-inserts > bot_logs_export.sql

# Export crm_activity
pg_dump -h localhost -U nivara -d nivara -t crm_activity --data-only --column-inserts > crm_activity_export.sql
```

Then in **Supabase SQL Editor**, run each `.sql` file contents **one at a time**.

> Run migrations (Part 3) **before** importing data.

### Option B — Full database dump (advanced)

```bash
pg_dump -h localhost -U nivara -d nivara --no-owner --no-acl -f nivara_full_backup.sql
```

Edit the file to remove `CREATE DATABASE` / schema lines if they conflict, then run in Supabase SQL Editor in sections (large files may need splitting).

### Option C — Fresh start (no local data)

Skip Part 4. Use `supabase/seed.sql` only for demo data.

---

## Part 5 — Upload media files (photos/videos)

Site photos are stored locally in `media_storage/` by `veo-mcp`. To persist them in Supabase:

### Step 1: Create a Storage bucket

1. Supabase → **Storage** → **New bucket**
2. Name: `media`
3. **Public bucket:** ON (so video URLs work for social posting)
4. Create

### Step 2: Upload files manually (small number)

1. Storage → `media` bucket → **Upload files**
2. Upload your `.jpg` / `.mp4` files from `media_storage/`

### Step 3: Update database URLs (if needed)

After upload, each file gets a public URL like:

```
https://YOUR_PROJECT_REF.supabase.co/storage/v1/object/public/media/filename.jpg
```

Update `media_assets` in SQL Editor:

```sql
UPDATE media_assets
SET source_url = 'https://YOUR_PROJECT_REF.supabase.co/storage/v1/object/public/media/YOUR_FILE.jpg'
WHERE filename = 'YOUR_FILE.jpg';
```

### Step 4: Future uploads (production)

Point `veo-mcp` at Supabase Storage instead of local disk — or keep `veo-mcp` on a server with persistent disk. For Streamlit Cloud, `veo-mcp` must run on a host with storage (Render/Railway), not locally.

---

## Part 6 — Update environment files

### Root `.env`

```bash
cp .env.example .env
```

Edit `.env`:

```bash
# Supabase API (for N8N / legacy references)
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Direct Postgres (used by dashboard, agents, MCP servers)
DB_HOST=db.YOUR_PROJECT_REF.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-supabase-db-password

# Gemini Veo
GEMINI_API_KEY=your_gemini_key
VEO_MOCK=false
VEO_MCP_URL=http://localhost:8006

# Other services
ORCHESTRATOR_URL=http://localhost:8000
```

### `agents/.env`

```bash
cp agents/.env.example agents/.env
```

Same `DB_*` and `SUPABASE_*` values as above.

### Streamlit Cloud secrets

In [share.streamlit.io](https://share.streamlit.io) → your app → **Settings → Secrets**:

```toml
DB_HOST = "db.YOUR_PROJECT_REF.supabase.co"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "your-supabase-db-password"

ORCHESTRATOR_URL = "https://your-orchestrator-host"
VEO_MCP_URL = "https://your-veo-mcp-host"
```

Template file: `dashboard/.streamlit/secrets.toml.example`

---

## Part 7 — Test the connection

### Test from terminal

```bash
psql "postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres" -c "SELECT count(*) FROM leads;"
```

### Test dashboard locally

```bash
pip install -r dashboard/requirements.txt
./scripts/start-dashboard.sh
```

Open http://localhost:8501 — leads and stats should load from Supabase.

### Test orchestrator

```bash
cd agents && pip install -e .
nivara-orchestrator
```

```bash
curl http://localhost:8000/health
# Should show supabase_configured: true (Postgres connected)
```

---

## Quick checklist

| Step | Done? |
|------|-------|
| New GitHub repo created | ☐ |
| Local code pushed to new repo | ☐ |
| Supabase project created | ☐ |
| `001_initial_schema.sql` run | ☐ |
| `002_phase2_media_and_bot_logs.sql` run | ☐ |
| `004_veo_provider.sql` run | ☐ |
| `seed.sql` run (optional) | ☐ |
| Local data exported & imported (optional) | ☐ |
| Media bucket created + files uploaded (optional) | ☐ |
| `.env` updated with Supabase credentials | ☐ |
| Streamlit secrets updated | ☐ |
| Dashboard loads data from Supabase | ☐ |

---

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Using `DB_NAME=nivara` | Supabase default is `postgres` |
| Using `DB_USER=nivara` | Supabase default is `postgres` |
| Running migrations out of order | Always: 001 → 002 → 004 |
| Pasting service_role key in frontend | Use only in backend `.env` / secrets |
| Expecting local `media_storage/` on Streamlit Cloud | Upload to Supabase Storage or host veo-mcp separately |

---

## File reference (what goes where)

| Local file / folder | Upload to |
|---------------------|-----------|
| Entire project code | **New GitHub repo** (`git push`) |
| `supabase/migrations/*.sql` | **Supabase SQL Editor** (run in order) |
| `supabase/seed.sql` | **Supabase SQL Editor** |
| Local Postgres table data | **Supabase SQL Editor** (via pg_dump export) |
| `media_storage/*` photos/videos | **Supabase Storage** bucket `media` |
| `.env` secrets | **Never commit** — set in Streamlit Cloud secrets + local `.env` |

---

## Need help?

- Supabase docs: https://supabase.com/docs
- Streamlit deploy: [docs/DEPLOYMENT.md](DEPLOYMENT.md)
- Phase 1 setup: [docs/PHASE1_SETUP.md](PHASE1_SETUP.md)
