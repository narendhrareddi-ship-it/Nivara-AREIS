# PixVerse MCP Server

Site photo upload, PixVerse image-to-video generation, and social media publishing for NIVARA REALTY.

## Port

`8006` (configurable via `PIXVERSE_MCP_PORT`)

## Tools

| Tool | Purpose |
|------|---------|
| `upload_site_photo` | Store uploaded site photo as media asset |
| `photo_to_video` | Generate cinematic video from photo via PixVerse |
| `get_media_status` | Check generation job status |
| `list_project_media` | List photos/videos for a project |
| `publish_video_to_social` | Publish completed video to social platforms |

## Environment

```bash
PIXVERSE_API_KEY=your_api_key          # from platform.pixverse.ai
PIXVERSE_MODEL=v5.5
PIXVERSE_QUALITY=720p
PIXVERSE_MOCK=true                       # dev without API keys
MEDIA_STORAGE_PATH=media_storage
MEDIA_PUBLIC_BASE_URL=http://localhost:8006/media
SOCIAL_MCP_URL=http://localhost:8003
```

## Quick Start

```bash
pip install fastapi uvicorn python-dotenv httpx psycopg2-binary python-multipart

python mcp-servers/pixverse-mcp/server.py
```

## Photo → Video → Social Flow

1. Upload site photo via `POST /upload` or `upload_site_photo` tool
2. Call `photo_to_video` with prompt and `auto_publish: true`
3. PixVerse uploads image directly (no public URL needed), generates video, social-mcp publishes

### Example

```bash
curl -X POST http://localhost:8006/upload \
  -F "file=@site_photo.jpg" \
  -F "project_id=YOUR_PROJECT_UUID"

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
