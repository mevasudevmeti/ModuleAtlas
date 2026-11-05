from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ModuleAtlas API"
    environment: str = "local"

    llm_provider: str = "mock"

    aws_region: str = "eu-west-2"
    aws_profile: str = "moduleatlas"

    bedrock_model_id: str = "amazon.nova-lite-v1:0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()