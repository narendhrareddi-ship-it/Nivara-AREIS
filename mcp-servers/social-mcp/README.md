# Social MCP Server

Mock social media integration for Phase 1. Logs actions and stores posts in Supabase.

## Supported Platforms (Mock)

Facebook, Instagram, LinkedIn, X (Twitter), YouTube

## Setup

```bash
pip install fastapi uvicorn python-dotenv httpx
export SUPABASE_URL=...
export SUPABASE_SERVICE_ROLE_KEY=...
python server.py
```

Port: **8003** (`SOCIAL_MCP_PORT`)

## Webhook Endpoints

```
POST /webhook/facebook
POST /webhook/instagram
POST /webhook/linkedin
```

## Phase 2+

Replace mock publish with Meta Graph API, LinkedIn API, etc. (paid/developer accounts required).

Tool descriptors: `tools.json`
