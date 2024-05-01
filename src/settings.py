from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = Field(
        default="prod",
        description="Current environment",
    )
    postgres_url: str = Field(
        default="postgresql://fastapi_app:fastapi_app@localhost:5432/fastapi_app",
        description="URL of postgresql",
    )
    nats_urls: str = Field(
        default="nats://localhost:4222/",
        description="List of nats urls, separated by comma",
    )
    redis_url: str = Field(
        default="redis://localhost",
        description="Redis DB url",
    )
    PROFILE: bool = Field(default=False)

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
