"""Visual Designer Agent — transforms site photos into cinematic videos via Gemini Veo."""

from __future__ import annotations

import os
from typing import Any

import httpx

from nivara.agents.base import AgentState, BaseAgent


class VisualDesignerAgent(BaseAgent):
    name = "VisualDesigner"
    role = "Creates cinematic video content from site photos using Google Gemini Veo"

    def __init__(self, llm: Any, crm: Any) -> None:
        super().__init__(llm, crm)
        self.mcp_url = os.getenv("VEO_MCP_URL", "http://localhost:8006")

    async def run(self, state: AgentState) -> dict[str, Any]:
        region = state.get("region", "Chennai")
        content_strategy = state.get("agent_outputs", {}).get("ContentStrategist", "")
        media_assets = state.get("media_assets") or []
        project_id = state.get("project_id")

        if not media_assets and self.crm.is_configured():
            pending = self.crm.get_media_by_project(project_id, asset_type="photo") if project_id else []
            media_assets = [dict(a) for a in pending[:3]]

        if not media_assets:
            brief = await self.llm.generate(
                f"Write a cinematic video motion prompt for a {region} luxury real estate site photo. "
                "Describe camera movement, lighting, and atmosphere in 1-2 sentences.",
                system=self.system_prompt(region),
            )
            return {
                "agent_outputs": {
                    **state.get("agent_outputs", {}),
                    self.name: f"No site photos uploaded. Suggested prompt for next upload: {brief}",
                },
                "next_agent": "SocialMediaManager",
            }

        results = []
        generated_videos: list[dict[str, Any]] = []

        async with httpx.AsyncClient(timeout=900.0) as client:
            for asset in media_assets[:3]:
                asset_id = str(asset.get("id", ""))
                prompt = asset.get("prompt") or (
                    f"Cinematic slow pan across this {region} real estate property, "
                    "golden hour lighting, luxury atmosphere, smooth camera movement"
                )

                if content_strategy:
                    brief_prompt = await self.llm.generate(
                        f"Based on this content strategy, write a 1-sentence Veo video motion prompt "
                        f"for a {region} property photo:\n{content_strategy[:600]}",
                        system=self.system_prompt(region),
                    )
                    prompt = brief_prompt.strip() or prompt

                try:
                    response = await client.post(
                        f"{self.mcp_url}/call",
                        json={
                            "name": "photo_to_video",
                            "arguments": {
                                "media_asset_id": asset_id,
                                "prompt": prompt,
                                "project_id": project_id or asset.get("project_id"),
                            },
                        },
                    )
                    if response.status_code == 200:
                        data = response.json().get("result", {})
                        video_url = data.get("video_url", "")
                        generated_videos.append({
                            "source_asset_id": asset_id,
                            "video_url": video_url,
                            "media_asset": data.get("media_asset", {}),
                        })
                        results.append(f"Generated video from {asset_id}: {video_url}")
                    else:
                        results.append(f"Failed for {asset_id}: {response.text[:200]}")
                except Exception as exc:
                    results.append(f"Error for {asset_id}: {exc}")

        summary = "\n".join(results) if results else "No videos generated."

        return {
            "media_videos": generated_videos,
            "agent_outputs": {**state.get("agent_outputs", {}), self.name: summary},
            "next_agent": "SocialMediaManager",
        }
