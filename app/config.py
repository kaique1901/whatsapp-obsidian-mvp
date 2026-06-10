from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = Field(
        default="postgresql+psycopg://whatsapp:change-me@postgres:5432/whatsapp_obsidian",
        alias="DATABASE_URL",
    )
    webhook_token: str = Field(default="change-this-token", alias="WEBHOOK_TOKEN")
    ollama_base_url: str = Field(default="http://ollama:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="qwen2.5:3b", alias="OLLAMA_MODEL")
    obsidian_daily_dir: str = Field(default="/obsidian/WhatsApp/Daily", alias="OBSIDIAN_DAILY_DIR")
    summary_time: str = Field(default="23:55", alias="SUMMARY_TIME")
    timezone: str = Field(default="America/Sao_Paulo", alias="TZ")


@lru_cache
def get_settings() -> Settings:
    return Settings()
