# Higgsfield MCP Server

Site photo upload, Higgsfield image-to-video generation, and social media publishing for NIVARA REALTY.

## Port

`8006` (configurable via `HIGGSFIELD_MCP_PORT`)

## Tools

| Tool | Purpose |
|------|---------|
| `upload_site_photo` | Store uploaded site photo as media asset |
| `photo_to_video` | Generate cinematic video from photo via Higgsfield |
| `get_media_status` | Check generation job status |
| `list_project_media` | List photos/videos for a project |
| `publish_video_to_social` | Publish completed video to social platforms |

## Environment

```bash
HIGGSFIELD_CREDENTIALS=KEY_ID:KEY_SECRET   # from cloud.higgsfield.ai
# OR
HIGGSFIELD_API_KEY=your_key_id
HIGGSFIELD_API_SECRET=your_key_secret

HIGGSFIELD_VIDEO_MODEL=higgsfield-ai/dop/standard
HIGGSFIELD_MOCK=true                        # dev without API keys
MEDIA_STORAGE_PATH=media_storage
MEDIA_PUBLIC_BASE_URL=http://localhost:8006/media
SOCIAL_MCP_URL=http://localhost:8003
```

## Quick Start

```bash
pip install fastapi uvicorn python-dotenv httpx supabase psycopg2-binary

python mcp-servers/higgsfield-mcp/server.py
```

## Photo → Video → Social Flow

1. Upload site photo via `POST /upload` or `upload_site_photo` tool
2. Call `photo_to_video` with prompt and `auto_publish: true`
3. Higgsfield generates video; social-mcp publishes to selected platforms

### Example

```bash
# Upload
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
      "prompt": "Smooth cinematic pan across luxury apartment, golden hour lighting",
      "auto_publish": true,
      "platforms": ["instagram", "facebook"],
      "post_caption": "Experience luxury living in OMR Chennai 🏙️ #NivaraRealty"
    }
  }'
```

## Production Note

Higgsfield requires a **publicly accessible HTTPS image URL**. For local dev, use `MEDIA_PUBLIC_BASE_URL` with ngrok or deploy behind a public domain.
