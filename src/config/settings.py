from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    jwt_secret: str
    jwt_expire_minutes: int = 60 * 24
    package_system_base_url: str = "https://search.adda247.com/v13/packages/info"
    package_system_src: str = "aweb"
    allowed_origins: list[str] = ["http://localhost:3001"]

    transfi_base_url: str
    transfi_public_key: str
    transfi_secret_key: str
    transfi_payment_link_id: str
    transfi_success_url: str
    transfi_failure_url: str
    transfi_webhook_secret: str


@lru_cache
def get_settings() -> Settings:
    return Settings()
