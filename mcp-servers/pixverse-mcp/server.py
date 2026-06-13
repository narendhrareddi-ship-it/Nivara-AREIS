"""NIVARA PixVerse MCP Server — site photo upload + image-to-video + social publish."""

from __future__ import annotations

import base64
import json
import logging
import os
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

load_dotenv()
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "agents", "src"))
from nivara.db.supabase_client import SupabaseCRM
from nivara.integrations.pixverse_client import PixverseClient

app = FastAPI(title="NIVARA PixVerse MCP", version="0.1.0")

MEDIA_DIR = Path(os.getenv("MEDIA_STORAGE_PATH", "media_storage"))
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
MEDIA_PUBLIC_BASE = os.getenv("MEDIA_PUBLIC_BASE_URL", "http://localhost:8006/media")
SOCIAL_MCP_URL = os.getenv("SOCIAL_MCP_URL", "http://localhost:8003")


def _get_crm() -> SupabaseCRM:
    return SupabaseCRM()


def _get_pixverse() -> PixverseClient:
    return PixverseClient()


def _public_url(filename: str) -> str:
    return f"{MEDIA_PUBLIC_BASE.rstrip('/')}/{filename}"


def _save_file(content: bytes, filename: str) -> str:
    safe_name = f"{uuid.uuid4().hex[:12]}_{filename}"
    path = MEDIA_DIR / safe_name
    path.write_bytes(content)
    return safe_name


def _read_local_image(filename: str) -> tuple[bytes, str] | None:
    path = MEDIA_DIR / filename
    if not path.exists():
        return None
    suffix = path.suffix.lower()
    mime = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(suffix, "image/jpeg")
    return path.read_bytes(), mime


class ToolCallRequest(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


async def _publish_to_social(
    video_url: str,
    caption: str,
    platforms: list[str],
    project_id: str | None = None,
    media_asset_id: str | None = None,
) -> list[dict[str, Any]]:
    results = []
    async with httpx.AsyncClient(timeout=30.0) as client:
        for platform in platforms:
            try:
                response = await client.post(
                    f"{SOCIAL_MCP_URL}/call",
                    json={
                        "name": "publish_post",
                        "arguments": {
                            "platform": platform,
                            "content": caption,
                            "project_id": project_id,
                            "media_urls": [video_url],
                            "media_type": "video",
                            "media_asset_id": media_asset_id,
                        },
                    },
                )
                if response.status_code == 200:
                    results.append({"platform": platform, "success": True, "result": response.json()})
                else:
                    results.append({"platform": platform, "success": False, "error": response.text})
            except Exception as exc:
                results.append({"platform": platform, "success": False, "error": str(exc)})
    return results


@app.get("/health")
async def health() -> dict[str, Any]:
    pv = _get_pixverse()
    return {
        "status": "ok",
        "server": "pixverse-mcp",
        "pixverse_configured": pv.is_configured(),
        "pixverse_mock": pv.mock_mode,
        "media_storage": str(MEDIA_DIR),
    }


@app.get("/tools")
async def list_tools() -> dict[str, Any]:
    with open(os.path.join(os.path.dirname(__file__), "tools.json"), encoding="utf-8") as f:
        return json.load(f)


@app.get("/media/{filename}")
async def serve_media(filename: str) -> FileResponse:
    path = MEDIA_DIR / filename
    if not path.exists():
        raise HTTPException(404, "Media not found")
    return FileResponse(path)


@app.post("/upload")
async def upload_photo(
    file: UploadFile = File(...),
    project_id: str | None = None,
) -> dict[str, Any]:
    content = await file.read()
    stored_name = _save_file(content, file.filename or "photo.jpg")
    public_url = _public_url(stored_name)

    crm = _get_crm()
    record: dict[str, Any] = {
        "asset_type": "photo",
        "status": "uploaded",
        "source_url": public_url,
        "filename": stored_name,
        "mime_type": file.content_type or "image/jpeg",
        "file_size_bytes": len(content),
        "provider": "local",
        "metadata": {"original_filename": file.filename},
    }
    if project_id:
        record["project_id"] = project_id

    if crm.is_configured():
        stored = crm.create_media_asset(record)
    else:
        stored = {**record, "id": str(uuid.uuid4()), "stored": False}

    return {"result": stored, "public_url": public_url}


@app.post("/call")
async def call_tool(request: ToolCallRequest) -> dict[str, Any]:
    args = request.arguments
    crm = _get_crm()
    pv = _get_pixverse()

    match request.name:
        case "upload_site_photo":
            content_b64 = args["content_base64"]
            if "," in content_b64:
                content_b64 = content_b64.split(",", 1)[1]
            content = base64.b64decode(content_b64)
            stored_name = _save_file(content, args["filename"])
            public_url = _public_url(stored_name)

            record: dict[str, Any] = {
                "asset_type": "photo",
                "status": "uploaded",
                "source_url": public_url,
                "filename": stored_name,
                "mime_type": args.get("mime_type", "image/jpeg"),
                "file_size_bytes": len(content),
                "provider": "local",
            }
            if args.get("project_id"):
                record["project_id"] = args["project_id"]

            stored = crm.create_media_asset(record) if crm.is_configured() else record
            return {"result": stored, "public_url": public_url}

        case "photo_to_video":
            prompt = args["prompt"]
            image_url = args.get("image_url")
            media_asset_id = args.get("media_asset_id")
            project_id = args.get("project_id")
            image_content: bytes | None = None
            mime_type = "image/jpeg"
            filename = "photo.jpg"

            if media_asset_id and crm.is_configured():
                asset = crm.get_media_asset(media_asset_id)
                if not asset:
                    raise HTTPException(404, f"Media asset not found: {media_asset_id}")
                image_url = asset.get("source_url")
                project_id = project_id or asset.get("project_id")
                if asset.get("filename"):
                    local = _read_local_image(asset["filename"])
                    if local:
                        image_content, mime_type = local
                        filename = asset["filename"]

            if not image_content and not image_url:
                raise HTTPException(400, "image_url or media_asset_id required")

            video_record: dict[str, Any] = {
                "asset_type": "video",
                "status": "generating",
                "source_url": image_url,
                "prompt": prompt,
                "provider": "pixverse",
                "metadata": {"source_image": image_url},
            }
            if project_id:
                video_record["project_id"] = project_id

            if crm.is_configured():
                video_asset = crm.create_media_asset(video_record)
                video_asset_id = str(video_asset.get("id", ""))
            else:
                video_asset = {**video_record, "id": str(uuid.uuid4())}
                video_asset_id = video_asset["id"]

            try:
                result = await pv.generate_video(
                    image_content=image_content,
                    image_url=image_url if not image_content else None,
                    filename=filename,
                    mime_type=mime_type,
                    prompt=prompt,
                    duration=args.get("duration", 5),
                )
                video_url = result.get("video_url", "")
                update_data = {
                    "status": "completed",
                    "output_url": video_url,
                    "provider_job_id": str(result.get("video_id", "")),
                    "metadata": {
                        "source_image": image_url,
                        "pixverse_response": result.get("raw", {}),
                        "img_id": result.get("img_id"),
                        "mock": result.get("mock", False),
                    },
                }
                if crm.is_configured() and video_asset_id:
                    video_asset = crm.update_media_asset(video_asset_id, update_data)

                publish_results = []
                if args.get("auto_publish") and video_url:
                    platforms = args.get("platforms", ["instagram", "facebook"])
                    caption = args.get("post_caption") or prompt
                    publish_results = await _publish_to_social(
                        video_url=video_url,
                        caption=caption,
                        platforms=platforms,
                        project_id=project_id,
                        media_asset_id=video_asset_id,
                    )
                    if crm.is_configured() and video_asset_id:
                        crm.update_media_asset(video_asset_id, {"status": "published"})

                return {
                    "result": {
                        "media_asset": video_asset,
                        "video_url": video_url,
                        "video_id": result.get("video_id"),
                        "publish_results": publish_results,
                    }
                }
            except Exception as exc:
                if crm.is_configured() and video_asset_id:
                    crm.update_media_asset(
                        video_asset_id,
                        {"status": "failed", "metadata": {"error": str(exc)}},
                    )
                raise HTTPException(500, f"Video generation failed: {exc}") from exc

        case "get_media_status":
            if args.get("media_asset_id") and crm.is_configured():
                asset = crm.get_media_asset(args["media_asset_id"])
                if not asset:
                    raise HTTPException(404, "Media asset not found")
                job_id = asset.get("provider_job_id")
                if job_id and asset.get("status") == "generating":
                    status = await pv.get_video_status(int(job_id))
                    return {"result": {"asset": asset, "job_status": status}}
                return {"result": {"asset": asset}}

            if args.get("video_id"):
                status = await pv.get_video_status(int(args["video_id"]))
                return {"result": status}

            raise HTTPException(400, "media_asset_id or video_id required")

        case "list_project_media":
            if not crm.is_configured():
                return {"result": []}
            assets = crm.get_media_by_project(
                args["project_id"],
                asset_type=args.get("asset_type"),
            )
            return {"result": assets}

        case "publish_video_to_social":
            if not crm.is_configured():
                raise HTTPException(503, "Database not configured")

            asset = crm.get_media_asset(args["media_asset_id"])
            if not asset:
                raise HTTPException(404, "Media asset not found")

            video_url = asset.get("output_url")
            if not video_url:
                raise HTTPException(400, "Video not ready — no output_url")

            platforms = args.get("platforms", ["instagram", "facebook"])
            publish_results = await _publish_to_social(
                video_url=video_url,
                caption=args["caption"],
                platforms=platforms,
                project_id=args.get("project_id") or asset.get("project_id"),
                media_asset_id=args["media_asset_id"],
            )
            crm.update_media_asset(args["media_asset_id"], {"status": "published"})
            return {"result": {"published": publish_results}}

        case _:
            raise HTTPException(400, f"Unknown tool: {request.name}")


if __name__ == "__main__":
    port = int(os.getenv("PIXVERSE_MCP_PORT", "8006"))
    uvicorn.run(app, host="0.0.0.0", port=port)
