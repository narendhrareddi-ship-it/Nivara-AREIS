# Browser MCP Server

Stub/browser MCP for competitor scraping and listing research.

## Phase 1 Behavior

- Default: **httpx** fetch (no browser install needed)
- Optional: set `BROWSER_USE_PLAYWRIGHT=true` and install Playwright

## Setup

```bash
pip install fastapi uvicorn httpx

# Optional Playwright (free, open source)
pip install playwright
playwright install chromium
export BROWSER_USE_PLAYWRIGHT=true

python server.py
```

Port: **8002** (`BROWSER_MCP_PORT`)

## Tools

- `scrape_url` — Fetch page title and excerpt
- `scrape_competitor` — Competitor site scrape wrapper
- `search_listings` — Mock listing search (Chennai/Andhra)

Tool descriptors: `tools.json`
