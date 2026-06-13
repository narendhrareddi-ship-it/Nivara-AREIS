"""Application configuration from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    supabase_url: str = ""
    supabase_service_role_key: str = ""
    db_host: str = "localhost"
    db_port: int = 5433
    db_user: str = "nivara"
    db_password: str = "changeme"
    db_name: str = "nivara"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    agent_log_level: str = "INFO"
    default_region: str = "Chennai"
    default_state: str = "Tamil Nadu"
    orchestrator_host: str = "0.0.0.0"
    orchestrator_port: int = 8000


settings = Settings()
