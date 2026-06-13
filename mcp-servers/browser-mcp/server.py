"""NIVARA Browser MCP Server — stub scraper (Playwright-ready for Phase 2)."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from typing import Any

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="NIVARA Browser MCP", version="0.1.0")

USE_PLAYWRIGHT = os.getenv("BROWSER_USE_PLAYWRIGHT", "false").lower() == "true"


class ToolCallRequest(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


async def _fetch_url(url: str) -> dict[str, Any]:
    if USE_PLAYWRIGHT:
        return await _playwright_scrape(url)
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        try:
            response = await client.get(url, headers={"User-Agent": "NIVARA-Bot/0.1"})
            text = response.text[:5000]
            title_start = text.lower().find("<title>")
            title_end = text.lower().find("</title>")
            title = text[title_start + 7 : title_end] if title_start >= 0 and title_end > title_start else ""
            return {
                "url": str(response.url),
                "status_code": response.status_code,
                "title": title.strip(),
                "excerpt": text[:1000],
                "method": "httpx",
            }
        except httpx.HTTPError as exc:
            return {"url": url, "error": str(exc), "method": "httpx", "stub": True}


async def _playwright_scrape(url: str) -> dict[str, Any]:
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        return {"url": url, "error": "playwright not installed", "stub": True}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=30000)
        title = await page.title()
        text = await page.inner_text("body")
        await browser.close()
        return {"url": url, "title": title, "excerpt": text[:1000], "method": "playwright"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "server": "browser-mcp", "playwright": str(USE_PLAYWRIGHT)}


@app.get("/tools")
async def list_tools() -> dict[str, Any]:
    with open(os.path.join(os.path.dirname(__file__), "tools.json"), encoding="utf-8") as f:
        return json.load(f)


@app.post("/call")
async def call_tool(request: ToolCallRequest) -> dict[str, Any]:
    args = request.arguments

    match request.name:
        case "scrape_url":
            return {"result": await _fetch_url(args["url"])}
        case "scrape_competitor":
            scrape = await _fetch_url(args["url"])
            return {
                "result": {
                    "competitor": args["competitor_name"],
                    "scraped_at": datetime.now(UTC).isoformat(),
                    "data": scrape,
                    "projects_detected": [],
                    "note": "Phase 1 stub — add parsing rules in Phase 2",
                }
            }
        case "search_listings":
            location = args.get("location", "Chennai OMR")
            return {
                "result": {
                    "location": location,
                    "property_type": args.get("property_type", "apartment"),
                    "listings": [
                        {"title": f"2BHK in {location}", "price": "₹65L", "source": "mock"},
                        {"title": f"3BHK in {location}", "price": "₹95L", "source": "mock"},
                    ],
                    "is_mock": True,
                }
            }
        case _:
            raise HTTPException(400, f"Unknown tool: {request.name}")


if __name__ == "__main__":
    port = int(os.getenv("BROWSER_MCP_PORT", "8002"))
    uvicorn.run(app, host="0.0.0.0", port=port)
