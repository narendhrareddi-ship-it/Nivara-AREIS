"""Application configuration from environment variables."""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_storage_bucket: str = "media"
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "nivara"
    db_password: str = "changeme"
    db_name: str = "nivara"
    db_sslmode: str = "require"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    llm_provider: str = "auto"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    gemini_api_key: str = ""
    gemini_llm_model: str = "gemini-2.0-flash"
    openrouter_api_key: str = ""
    openrouter_model: str = "meta-llama/llama-3.3-70b-instruct"
    whatsapp_mcp_url: str = "http://localhost:8004"
    orchestrator_api_key: str = ""
    agent_log_level: str = "INFO"
    default_region: str = "Bangalore"
    default_state: str = "Karnataka"
    orchestrator_host: str = "0.0.0.0"
    orchestrator_port: int = 8000

    @property
    def listen_port(self) -> int:
        return int(os.getenv("PORT", str(self.orchestrator_port)))


settings = Settings()
