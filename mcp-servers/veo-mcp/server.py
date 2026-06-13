"""NIVARA Gemini Veo MCP Server — site photo upload + image-to-video + social publish."""

from __future__ import annotations

import base64
import json
import logging
import os
import sys
import uuid
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
from nivara.integrations.storage_client import SupabaseStorage
from nivara.integrations.veo_client import VeoClient

app = FastAPI(title="NIVARA Gemini Veo MCP", version="0.1.0")

MEDIA_DIR = Path(os.getenv("MEDIA_STORAGE_PATH", "media_storage"))
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
MEDIA_PUBLIC_BASE = os.getenv("MEDIA_PUBLIC_BASE_URL", "http://localhost:8006/media")
SOCIAL_MCP_URL = os.getenv("SOCIAL_MCP_URL", "http://localhost:8003")
USE_SUPABASE_STORAGE = os.getenv("USE_SUPABASE_STORAGE", "true").lower() in ("1", "true", "yes")


def _get_crm() -> SupabaseCRM:
    return SupabaseCRM()


def _get_veo() -> VeoClient:
    return VeoClient()


def _get_storage() -> SupabaseStorage:
    return SupabaseStorage()


def _public_url(filename: str) -> str:
    return f"{MEDIA_PUBLIC_BASE.rstrip('/')}/{filename}"


def _save_file(content: bytes, filename: str, content_type: str = "application/octet-stream") -> tuple[str, str, str]:
    """Returns (stored_name, public_url, provider)."""
    storage = _get_storage()
    if USE_SUPABASE_STORAGE and storage.is_configured():
        uploaded = storage.upload(content, filename, content_type=content_type, folder="photos")
        return uploaded["filename"], uploaded["public_url"], "supabase"

    safe_name = f"{uuid.uuid4().hex[:12]}_{filename}"
    path = MEDIA_DIR / safe_name
    path.write_bytes(content)
    return safe_name, _public_url(safe_name), "local"


def _read_image_asset(asset: dict[str, Any]) -> tuple[bytes, str] | None:
    mime = asset.get("mime_type") or "image/jpeg"
    storage_path = (asset.get("metadata") or {}).get("storage_path")
    if storage_path:
        storage = _get_storage()
        if storage.is_configured():
            data = storage.download(storage_path)
            if data:
                return data, mime

    filename = asset.get("filename")
    if filename:
        return _read_local_image(filename)
    return None


def _read_local_image(filename: str) -> tuple[bytes, str] | None:
    path = MEDIA_DIR / filename
    if not path.exists():
        return None
    suffix = path.suffix.lower()
    mime = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}.get(
        suffix, "image/jpeg"
    )
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
    veo = _get_veo()
    storage = _get_storage()
    return {
        "status": "ok",
        "server": "veo-mcp",
        "veo_configured": veo.is_configured(),
        "veo_mock": veo.mock_mode,
        "veo_model": veo.model,
        "media_storage": str(MEDIA_DIR),
        "supabase_storage": storage.is_configured(),
        "storage_bucket": storage.bucket if storage.is_configured() else None,
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
async def upload_photo(file: UploadFile = File(...), project_id: str | None = None) -> dict[str, Any]:
    content = await file.read()
    mime = file.content_type or "image/jpeg"
    stored_name, public_url, provider = _save_file(content, file.filename or "photo.jpg", content_type=mime)

    crm = _get_crm()
    metadata: dict[str, Any] = {"original_filename": file.filename}
    if provider == "supabase":
        metadata["storage_path"] = f"photos/{stored_name}"

    record: dict[str, Any] = {
        "asset_type": "photo",
        "status": "uploaded",
        "source_url": public_url,
        "filename": stored_name,
        "mime_type": mime,
        "file_size_bytes": len(content),
        "provider": provider,
        "metadata": metadata,
    }
    if project_id:
        record["project_id"] = project_id

    stored = crm.create_media_asset(record) if crm.is_configured() else {**record, "id": str(uuid.uuid4())}
    return {"result": stored, "public_url": public_url}


@app.post("/call")
async def call_tool(request: ToolCallRequest) -> dict[str, Any]:
    args = request.arguments
    crm = _get_crm()
    veo = _get_veo()

    match request.name:
        case "upload_site_photo":
            content_b64 = args["content_base64"]
            if "," in content_b64:
                content_b64 = content_b64.split(",", 1)[1]
            content = base64.b64decode(content_b64)
            mime = args.get("mime_type", "image/jpeg")
            stored_name, public_url, provider = _save_file(content, args["filename"], content_type=mime)
            metadata: dict[str, Any] = {}
            if provider == "supabase":
                metadata["storage_path"] = f"photos/{stored_name}"
            record: dict[str, Any] = {
                "asset_type": "photo",
                "status": "uploaded",
                "source_url": public_url,
                "filename": stored_name,
                "mime_type": mime,
                "file_size_bytes": len(content),
                "provider": provider,
                "metadata": metadata,
            }
            if args.get("project_id"):
                record["project_id"] = args["project_id"]
            stored = crm.create_media_asset(record) if crm.is_configured() else record
            return {"result": stored, "public_url": public_url}

        case "photo_to_video":
            prompt = args["prompt"]
            media_asset_id = args.get("media_asset_id")
            project_id = args.get("project_id")
            image_content: bytes | None = None
            mime_type = "image/jpeg"
            asset: dict[str, Any] | None = None

            if media_asset_id and crm.is_configured():
                asset = crm.get_media_asset(media_asset_id)
                if not asset:
                    raise HTTPException(404, f"Media asset not found: {media_asset_id}")
                project_id = project_id or asset.get("project_id")
                local = _read_image_asset(asset)
                if local:
                    image_content, mime_type = local

            if not image_content:
                raise HTTPException(400, "media_asset_id with local file required for Veo generation")

            video_record: dict[str, Any] = {
                "asset_type": "video",
                "status": "generating",
                "source_url": asset.get("source_url") if asset else None,
                "prompt": prompt,
                "provider": "veo",
                "metadata": {"source_asset_id": media_asset_id},
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
                result = await veo.generate_video(
                    image_content=image_content,
                    prompt=prompt,
                    mime_type=mime_type,
                )
                video_url = result.get("video_url", "")
                update_data = {
                    "status": "completed",
                    "output_url": video_url,
                    "provider_job_id": result.get("operation_name"),
                    "metadata": {
                        "source_asset_id": media_asset_id,
                        "veo_response": result.get("raw", {}),
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
                        "operation_name": result.get("operation_name"),
                        "publish_results": publish_results,
                    }
                }
            except Exception as exc:
                if crm.is_configured() and video_asset_id:
                    crm.update_media_asset(video_asset_id, {"status": "failed", "metadata": {"error": str(exc)}})
                raise HTTPException(500, f"Video generation failed: {exc}") from exc

        case "get_media_status":
            if args.get("media_asset_id") and crm.is_configured():
                asset = crm.get_media_asset(args["media_asset_id"])
                if not asset:
                    raise HTTPException(404, "Media asset not found")
                op_name = asset.get("provider_job_id")
                if op_name and asset.get("status") == "generating":
                    status = await veo.get_operation_status(op_name)
                    return {"result": {"asset": asset, "job_status": status}}
                return {"result": {"asset": asset}}
            if args.get("operation_name"):
                status = await veo.get_operation_status(args["operation_name"])
                return {"result": status}
            raise HTTPException(400, "media_asset_id or operation_name required")

        case "list_project_media":
            if not crm.is_configured():
                return {"result": []}
            return {"result": crm.get_media_by_project(args["project_id"], asset_type=args.get("asset_type"))}

        case "publish_video_to_social":
            if not crm.is_configured():
                raise HTTPException(503, "Database not configured")
            asset = crm.get_media_asset(args["media_asset_id"])
            if not asset:
                raise HTTPException(404, "Media asset not found")
            video_url = asset.get("output_url")
            if not video_url:
                raise HTTPException(400, "Video not ready — no output_url")
            publish_results = await _publish_to_social(
                video_url=video_url,
                caption=args["caption"],
                platforms=args.get("platforms", ["instagram", "facebook"]),
                project_id=args.get("project_id") or asset.get("project_id"),
                media_asset_id=args["media_asset_id"],
            )
            crm.update_media_asset(args["media_asset_id"], {"status": "published"})
            return {"result": {"published": publish_results}}

        case _:
            raise HTTPException(400, f"Unknown tool: {request.name}")


if __name__ == "__main__":
    port = int(os.getenv("PORT", os.getenv("VEO_MCP_PORT", "8006")))
    uvicorn.run(app, host="0.0.0.0", port=port)
