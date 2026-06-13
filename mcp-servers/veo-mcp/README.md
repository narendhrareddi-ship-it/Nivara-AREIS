# Gemini Veo MCP Server

Site photo upload, Google Gemini Veo image-to-video generation, and social media publishing.

## Port

`8006` (configurable via `VEO_MCP_PORT`)

## Environment

```bash
GEMINI_API_KEY=your_key          # or VEO_API_KEY
VEO_MODEL=veo-3.1-generate-preview
VEO_MOCK=true
VEO_MCP_PORT=8006
SOCIAL_MCP_URL=http://localhost:8003
```

Get API key at https://aistudio.google.com/apikey

## Quick Start

```bash
python mcp-servers/veo-mcp/server.py
```

## Photo → Video → Social

1. Upload via `POST /upload`
2. Call `photo_to_video` with `media_asset_id` and `auto_publish: true`
3. Veo generates video from image bytes; social-mcp publishes
