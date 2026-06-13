"""Social Media Manager Agent — coordinates FB/IG/LinkedIn posting with Higgsfield videos."""

from __future__ import annotations

from typing import Any

import httpx

from nivara.agents.base import AgentState, BaseAgent

DEFAULT_PLATFORMS = ["instagram", "facebook", "linkedin"]


class SocialMediaManagerAgent(BaseAgent):
    name = "SocialMediaManager"
    role = "Manages social media presence, posting schedules, and engagement tracking"

    def __init__(self, llm: Any, crm: Any) -> None:
        super().__init__(llm, crm)
        self.mcp_url = os.getenv("SOCIAL_MCP_URL", "http://localhost:8003")
        self.higgsfield_url = os.getenv("HIGGSFIELD_MCP_URL", "http://localhost:8006")

    def _parse_platform_posts(self, social_plan: str) -> list[dict[str, str]]:
        posts = []
        platform_map = {
            "fb": "facebook", "facebook": "facebook",
            "ig": "instagram", "instagram": "instagram",
            "linkedin": "linkedin", "li": "linkedin",
            "x": "twitter", "twitter": "twitter",
        }
        for line in social_plan.splitlines():
            lower = line.lower()
            for key, platform in platform_map.items():
                if key in lower and len(line) > 20:
                    copy = re.sub(r"^[\s\|\-\d\.]+", "", line).strip()
                    if copy:
                        posts.append({"platform": platform, "content": copy[:500]})
                    break
        return posts[:4]

    async def _publish_video(
        self,
        client: httpx.AsyncClient,
        video: dict[str, Any],
        caption: str,
        platforms: list[str],
        project_id: str | None,
    ) -> list[str]:
        published = []
        video_url = video.get("video_url", "")
        media_asset_id = str(video.get("media_asset", {}).get("id", video.get("source_asset_id", "")))

        if media_asset_id:
            try:
                response = await client.post(
                    f"{self.higgsfield_url}/call",
                    json={
                        "name": "publish_video_to_social",
                        "arguments": {
                            "media_asset_id": media_asset_id,
                            "caption": caption,
                            "platforms": platforms,
                            "project_id": project_id,
                        },
                    },
                )
                if response.status_code == 200:
                    published.append(f"Published video {media_asset_id} via higgsfield-mcp")
                    return published
            except Exception:
                pass

        for platform in platforms:
            try:
                response = await client.post(
                    f"{self.mcp_url}/call",
                    json={
                        "name": "publish_post",
                        "arguments": {
                            "platform": platform,
                            "content": caption,
                            "project_id": project_id,
                            "media_urls": [video_url] if video_url else [],
                            "media_type": "video",
                            "media_asset_id": media_asset_id or None,
                        },
                    },
                )
                if response.status_code == 200:
                    published.append(f"Published to {platform}")
            except Exception as exc:
                published.append(f"Failed {platform}: {exc}")

        return published

    async def run(self, state: AgentState) -> dict[str, Any]:
        region = state.get("region", "Chennai")
        content_strategy = state.get("agent_outputs", {}).get("ContentStrategist", "")
        media_videos = state.get("media_videos") or []
        project_id = state.get("project_id")
        auto_publish = state.get("auto_publish_social", True)

        if not content_strategy and not media_videos:
            return {
                "agent_outputs": {
                    **state.get("agent_outputs", {}),
                    self.name: "No content strategy or videos available to publish.",
                },
                "next_agent": "LeadQualification",
            }

        caption_base = ""
        if content_strategy:
            prompt = (
                f"Translate this content strategy for {region} into 3 social media post captions. "
                f"Include emojis and hashtags for real estate:\n\n{content_strategy[:1500]}\n\n"
                "Return JSON array: [{\"platform\": \"instagram\", \"caption\": \"...\"}]"
            )
            raw = await self.llm.generate(prompt, system=self.system_prompt(region))
            caption_base = raw

        publish_log: list[str] = []

        async with httpx.AsyncClient(timeout=120.0) as client:
            if media_videos and auto_publish:
                default_caption = (
                    f"Discover luxury living in {region} with NIVARA REALTY 🏙️ "
                    "#ChennaiRealEstate #LuxuryLiving #NivaraRealty"
                )
                for video in media_videos:
                    logs = await self._publish_video(
                        client,
                        video,
                        default_caption,
                        DEFAULT_PLATFORMS,
                        project_id,
                    )
                    publish_log.extend(logs)

            elif content_strategy:
                social_plan = await self.llm.generate(
                    f"Create social media posts for {region}:\n{content_strategy[:1500]}\n\n"
                    "Format: Platform | Post Copy | Image Brief | Posting Time",
                    system=self.system_prompt(region),
                )

                parsed = self._parse_platform_posts(social_plan)
                for post in parsed:
                    try:
                        response = await client.post(
                            f"{self.mcp_url}/call",
                            json={
                                "name": "publish_post",
                                "arguments": {
                                    "platform": post["platform"],
                                    "content": post["content"],
                                    "project_id": project_id,
                                },
                            },
                        )
                        if response.status_code == 200:
                            publish_log.append(f"Published text post to {post['platform']}")
                    except Exception as exc:
                        publish_log.append(f"Failed {post['platform']}: {exc}")

                caption_base = social_plan

        if self.crm.is_configured():
            self.crm.log_activity({
                "activity_type": "ai_action",
                "title": "Social media posts published",
                "description": "; ".join(publish_log)[:500] if publish_log else caption_base[:500],
                "performed_by": "ai",
                "agent_name": self.name,
            })

        summary = caption_base
        if publish_log:
            summary += f"\n\nPublished:\n" + "\n".join(publish_log)

        return {
            "agent_outputs": {**state.get("agent_outputs", {}), self.name: summary},
            "next_agent": "LeadQualification",
        }
