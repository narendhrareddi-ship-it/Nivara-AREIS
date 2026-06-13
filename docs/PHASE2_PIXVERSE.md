# Phase 2 — PixVerse Integration

Site photo upload → AI video generation → automatic social media posting.

## Overview

When you upload property site photos, NIVARA:

1. Stores the photo as a `media_assets` record
2. Uploads it directly to **PixVerse** for cinematic image-to-video generation
3. Publishes the resulting video to Instagram, Facebook, and LinkedIn via `social-mcp`

PixVerse accepts image bytes directly — no public URL or ngrok required.

## Setup

### 1. Run Phase 2 migration

```bash
psql -h localhost -p 5433 -U nivara -d nivara -f supabase/migrations/002_phase2_media_and_bot_logs.sql
```

### 2. Configure PixVerse API key

Get your API key at [platform.pixverse.ai](https://platform.pixverse.ai):

```bash
# .env
PIXVERSE_API_KEY=your_api_key
PIXVERSE_MOCK=false
```

### 3. Start services

```bash
docker compose up -d

python mcp-servers/pixverse-mcp/server.py   # :8006
python mcp-servers/social-mcp/server.py       # :8003
cd agents && nivara-orchestrator              # :8000
```

## Usage

### Dashboard (recommended)

1. Open http://localhost:8501
2. Go to **MEDIA** tab
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

```
MarketAnalyst → CompetitorSpy → ContentStrategist → SEOAgent
  → VisualDesigner → SocialMediaManager → LeadQualification → ...
```

## Agents (Phase 2)

| Agent | Role | Status |
|-------|------|--------|
| VisualDesigner | Photo → PixVerse video | ✅ Implemented |
| SocialMediaManager | Publish videos to social | ✅ Updated |
| SEOAgent | Local SEO strategy | ✅ Implemented |
| WhatsAppAgent | Lead nurturing | ✅ Implemented |
| AppointmentScheduler | Site visit scheduling | ✅ Implemented |

## Mock mode

Set `PIXVERSE_MOCK=true` to test the full pipeline without API keys.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| PixVerse auth error | Check `PIXVERSE_API_KEY` from platform.pixverse.ai |
| Video generation timeout | PixVerse takes 20-90s; increase client timeout |
| Social post missing video | Ensure `social-mcp` is running on :8003 |
| `bot_logs` table missing | Run migration `002_phase2_media_and_bot_logs.sql` |
