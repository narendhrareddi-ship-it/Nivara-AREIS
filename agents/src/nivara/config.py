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
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    agent_log_level: str = "INFO"
    default_region: str = "Bangalore"
    default_state: str = "Karnataka"
    orchestrator_host: str = "0.0.0.0"
    orchestrator_port: int = 8000

    @property
    def listen_port(self) -> int:
        return int(os.getenv("PORT", str(self.orchestrator_port)))


settings = Settings()
