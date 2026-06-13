# Free Tier Limits & Paid Upgrade Path

NIVARA REALTY Phase 1 uses **zero paid services**. This document maps what's free, what's mocked, and what to add in later phases.

## Currently Free (Phase 1)

| Service | Free Tier Limits | Our Usage |
|---------|-----------------|-----------|
| **Supabase** | 500 MB DB, 50K MAU, 2 projects | CRM schema, RLS, REST API |
| **N8N** | Self-hosted, unlimited (OSS) | 4 workflows, webhooks |
| **Ollama** | Local, unlimited | Llama 3.2 / Mistral inference |
| **LangGraph** | Open source | Agent orchestration |
| **Playwright** | Open source | Optional browser scraping |
| **Docker** | Free for personal use | n8n + ollama containers |

## Mocked in Phase 1 (No Cost)

| Feature | Mock Implementation | Why |
|---------|-------------------|-----|
| WhatsApp | whatsapp-mcp webhook | Meta Business API requires verification; per-conversation pricing |
| Facebook/Instagram | social-mcp mock publish | Meta Graph API needs Business account + app review |
| LinkedIn/X/YouTube | social-mcp mock | API access restricted/paid |
| Google Ads | analytics_collector mock data | Google Ads API needs developer token + spend |
| Ad performance | Random mock metrics in N8N | No ad platform connected |
| Image/video generation | Not implemented | DALL-E, Midjourney, Runway are paid |

## Supabase Free Tier Watchouts

- **500 MB storage** — sufficient for Phase 1-2 CRM data
- **Edge Functions** — 500K invocations/month (unused in Phase 1)
- **Realtime** — 200 concurrent connections (optional for Phase 3 dashboard)
- **Upgrade trigger**: >50K monthly active users or need for daily backups beyond 7 days

## Ollama Hardware Notes

- **Minimum**: 8 GB RAM for Llama 3.2 3B
- **Recommended**: 16 GB RAM + GPU for Llama 3.2 8B or Mistral 7B
- No API costs; runs entirely local

## Paid Services to Add (By Phase)

### Phase 2 (~$0-50/month)

| Service | Purpose | Est. Cost |
|---------|---------|-----------|
| Domain + hosting | Landing page | $10-15/mo |
| Resend or Mailgun free tier | Email campaigns | Free up to limits |
| Meta WhatsApp Cloud API | Real WhatsApp | Free tier: 1000 conversations/mo, then ~$0.05-0.15/conversation |

### Phase 3 (~$100-300/month)

| Service | Purpose | Est. Cost |
|---------|---------|-----------|
| Google Ads | Paid search/display | Ad spend variable |
| Meta Ads Manager | FB/IG campaigns | Ad spend variable |
| Canva Pro | Creative assets | ~$13/mo |
| Supabase Pro | If DB exceeds free tier | $25/mo |

### Phase 4 (~$300+/month)

| Service | Purpose | Est. Cost |
|---------|---------|-----------|
| OpenAI/Anthropic API (optional) | Higher quality LLM fallback | Usage-based |
| Twilio | SMS/voice backup | Usage-based |
| Cloud hosting (Railway/Fly.io) | Production deployment | $20-50/mo |
| Sentry | Error monitoring | Free tier available |

## Recommendation

Stay on the free stack through Phase 2. Evaluate paid LLM APIs only if Ollama quality is insufficient for client-facing copy. Prioritize WhatsApp Business API and Google/Meta ad integrations when ready for live lead generation.
