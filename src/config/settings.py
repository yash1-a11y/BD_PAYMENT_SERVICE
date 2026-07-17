from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://bd_payment:bd_payment@localhost:5432/bd_payment_service"
    jwt_secret: str = "change-me"
    jwt_expire_minutes: int = 60 * 24
    package_system_base_url: str = "https://search.adda247.com/v13/packages/info"
    package_system_src: str = "aweb"
    allowed_origins: list[str] = ["http://localhost:3001"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
