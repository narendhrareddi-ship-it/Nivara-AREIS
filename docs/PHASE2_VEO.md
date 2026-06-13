# Phase 2 — Gemini Veo Integration

Site photo upload → AI video generation → automatic social media posting.

## Overview

When you upload property site photos, NIVARA:

1. Stores the photo as a `media_assets` record
2. Sends image bytes to **Google Gemini Veo** for cinematic image-to-video generation
3. Publishes the resulting video to Instagram, Facebook, and LinkedIn via `social-mcp`

## Setup

### 1. Configure Gemini API key

Get your key at [Google AI Studio](https://aistudio.google.com/apikey):

```bash
# .env
GEMINI_API_KEY=your_key
VEO_MOCK=false
VEO_MODEL=veo-3.1-generate-preview
```

### 2. Start services

```bash
python mcp-servers/veo-mcp/server.py   # :8006
python mcp-servers/social-mcp/server.py # :8003
cd agents && nivara-orchestrator          # :8000
```

## Usage

### Dashboard

1. Open http://localhost:8501 → **MEDIA** tab
2. Upload site photo, enter motion prompt and caption
3. Click **GENERATE VIDEO & POST**

### API

```bash
curl -X POST http://localhost:8006/upload -F "file=@site_photo.jpg"

curl -X POST http://localhost:8006/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "photo_to_video",
    "arguments": {
      "media_asset_id": "ASSET_UUID",
      "prompt": "Cinematic slow pan across luxury apartment, golden hour",
      "auto_publish": true,
      "platforms": ["instagram", "facebook"],
      "post_caption": "Luxury living in OMR Chennai 🏙️"
    }
  }'
```

## Agent pipeline

```
MarketAnalyst → ... → VisualDesigner → SocialMediaManager → ...
```

VisualDesigner calls `veo-mcp` to generate videos from uploaded site photos.

## Mock mode

Set `VEO_MOCK=true` to test without API calls.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Auth error | Verify `GEMINI_API_KEY` at aistudio.google.com |
| Quota exceeded (429) | Enable billing or wait for quota reset at ai.dev/rate-limit |
| Veo access denied | Enable Veo in your Google AI project / billing |
| Timeout | Veo takes 2-10 min; increase client timeout |
| Social post fails | Ensure social-mcp running on :8003 |
