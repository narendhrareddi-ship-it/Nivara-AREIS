# WhatsApp MCP Server (Mock)

Phase 1 mock WhatsApp handler with rule-based lead scoring.

> **Note:** The real WhatsApp Business API requires Meta Business verification.
> Cloud API has per-conversation pricing after free tier. This server simulates
> webhooks for development only.

## Setup

```bash
pip install fastapi uvicorn python-dotenv httpx
python server.py
```

Port: **8004** (`WHATSAPP_MCP_PORT`)

## Webhook (used by N8N lead intake)

```bash
curl -X POST http://localhost:8004/webhook/message \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+919876543210",
    "message": "Looking for 3BHK in OMR, budget 80 lakhs, want site visit",
    "lead_id": "optional-uuid"
  }'
```

## Lead Scoring Rules (Phase 1)

- Budget/price keywords: +25
- Site visit/property keywords: +20
- Location keywords (OMR, Amaravati, etc.): +15
- Urgency keywords: +15
- Low intent phrases: -20

## Phase 2+

Integrate Meta WhatsApp Cloud API or Twilio (paid) for production messaging.

Tool descriptors: `tools.json`
