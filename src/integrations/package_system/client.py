from dataclasses import dataclass

import httpx

from src.config.settings import get_settings


class PackageNotFoundError(Exception):
    pass


@dataclass
class PackageDetails:
    package_id: str
    title: str
    category: str
    validity_months: int | None
    thumbnail_url: str | None
    india_mrp: float | None
    published: bool

    @property
    def is_eligible(self) -> bool:
        return self.published


def fetch_package(package_id: str) -> PackageDetails:
    settings = get_settings()
    response = httpx.get(
        settings.package_system_base_url,
        params={"packageId": package_id, "src": settings.package_system_src},
        timeout=10,
    )
    if response.status_code == 400:
        raise PackageNotFoundError(package_id)
    response.raise_for_status()
    entities = response.json().get("data", {}).get("packageEsEntity", [])
    if not entities:
        raise PackageNotFoundError(package_id)

    entity = entities[0]
    val_months = entity.get("valMonths") or []
    primary_category = entity.get("primaryCategory")
    package_category = entity.get("packagePrimaryCategory")
    category = " · ".join(filter(None, [primary_category, package_category]))

    return PackageDetails(
        package_id=package_id,
        title=entity.get("title", ""),
        category=category,
        validity_months=min(val_months) if val_months else None,
        thumbnail_url=entity.get("imgUrl"),
        india_mrp=entity.get("maxPrice"),
        published=bool(entity.get("published")),
    )
