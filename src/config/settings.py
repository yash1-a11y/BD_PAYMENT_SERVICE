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

    # Guest Checkout integration — intentionally a separate namespace from
    # package_system_base_url/package_system_src above, which belong to
    # the unrelated storefront/catalogue package-lookup integration and
    # must never be reused here. All fields default to empty so the app
    # starts and behaves identically whether or not the backend team's
    # Guest Checkout API has been configured — this integration is being
    # prepared, not enabled (see src/integrations/guest_checkout/ and
    # docs/guest_checkout_integration.md). Only guest_checkout_base_url is
    # expected to change between staging and production; the endpoint
    # path stays independently configurable via guest_checkout_endpoint
    # rather than hardcoded anywhere.
    guest_checkout_base_url: str = ""
    guest_checkout_endpoint: str = ""
    guest_checkout_jwt_token: str = ""
    guest_checkout_basic_auth: str = ""
    guest_checkout_cp_origin: str = ""

    app_env: str = "production"
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
