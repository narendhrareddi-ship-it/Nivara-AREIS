# Phase 2 — Higgsfield Integration

Site photo upload → AI video generation → automatic social media posting.

## Overview

When you upload property site photos, NIVARA:

1. Stores the photo as a `media_assets` record
2. Sends it to **Higgsfield AI** for cinematic image-to-video generation
3. Publishes the resulting video to Instagram, Facebook, and LinkedIn via `social-mcp`

## Setup

### 1. Run Phase 2 migration

```bash
# In Supabase SQL Editor or local Postgres:
psql -h localhost -p 5433 -U nivara -d nivara -f supabase/migrations/002_phase2_media_and_bot_logs.sql
```

### 2. Configure Higgsfield credentials

Get API keys at [cloud.higgsfield.ai](https://cloud.higgsfield.ai):

```bash
# .env
HIGGSFIELD_CREDENTIALS=your_key_id:your_key_secret
HIGGSFIELD_MOCK=false   # set true for dev without API keys
```

### 3. Start services

```bash
docker compose up -d

# MCP servers (separate terminals or use docker higgsfield-mcp service)
python mcp-servers/higgsfield-mcp/server.py   # :8006
python mcp-servers/social-mcp/server.py       # :8003
cd agents && nivara-orchestrator              # :8000
```

### 4. Public image URL (production)

Higgsfield requires a publicly accessible HTTPS image URL. Options:

- Set `MEDIA_PUBLIC_BASE_URL` to your domain or ngrok URL
- Example: `MEDIA_PUBLIC_BASE_URL=https://your-domain.com/media`

## Usage

### Dashboard (recommended)

1. Open http://localhost:8501
2. Go to **🎬 MEDIA** tab
3. Upload a site photo, select project
4. Enter motion prompt and caption
5. Click **GENERATE VIDEO & POST**

### API

```bash
# Upload photo
curl -X POST http://localhost:8006/upload \
  -F "file=@site_photo.jpg" \
  -F "project_id=YOUR_PROJECT_UUID"

# Generate video + auto-post
curl -X POST http://localhost:8006/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "photo_to_video",
    "arguments": {
      "media_asset_id": "ASSET_UUID",
      "prompt": "Cinematic slow pan, golden hour, luxury property",
      "auto_publish": true,
      "platforms": ["instagram", "facebook"],
      "post_caption": "Luxury living in OMR Chennai 🏙️ #NivaraRealty"
    }
  }'
```

### Agent pipeline

The full pipeline now includes:

```
MarketAnalyst → CompetitorSpy → ContentStrategist → SEOAgent
  → VisualDesigner → SocialMediaManager → LeadQualification → ...
```

Trigger with uploaded media:

```bash
curl -X POST http://localhost:8000/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "task": "social_video_campaign",
    "region": "Chennai",
    "project_id": "PROJECT_UUID",
    "media_assets": [{"id": "ASSET_UUID", "source_url": "http://..."}],
    "auto_publish_social": true
  }'
```

### N8N workflow

Import `n8n/workflows/social_video_publish.json` — runs daily at 10 AM IST to publish completed videos.

## Agents (Phase 2)

| Agent | Role | Status |
|-------|------|--------|
| VisualDesigner | Photo → Higgsfield video | ✅ Implemented |
| SocialMediaManager | Publish videos to social | ✅ Updated |
| SEOAgent | Local SEO strategy | ✅ Implemented |
| WhatsAppAgent | Lead nurturing | ✅ Implemented |
| AppointmentScheduler | Site visit scheduling | ✅ Implemented |

## Mock mode

Set `HIGGSFIELD_MOCK=true` to test the full pipeline without API keys. Returns placeholder video URLs.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Higgsfield auth error | Check `HIGGSFIELD_CREDENTIALS` format: `KEY_ID:KEY_SECRET` |
| Image URL not accessible | Use ngrok or public domain for `MEDIA_PUBLIC_BASE_URL` |
| Video generation timeout | Increase timeout; Higgsfield takes 20-60s |
| Social post missing video | Ensure `social-mcp` is running on :8003 |
| `bot_logs` table missing | Run migration `002_phase2_media_and_bot_logs.sql` |
