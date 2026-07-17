from sqlalchemy import select
from sqlalchemy.orm import Session

from src.integrations.package_system.client import (
    PackageNotFoundError,
    StorefrontPackage,
    fetch_storefront_package,
)
from src.modules.catalogue.models import BDLandingPage
from src.modules.storefront.exceptions import PackageUnavailableError
from src.modules.storefront.schemas import (
    ExamBadgeOut,
    FacultyOut,
    FaqOut,
    PackageListingOut,
    PackagePdpOut,
    PlanOut,
    SectionOut,
    TestimonialOut,
)


def _batch_type(storefront: StorefrontPackage) -> str:
    return "Live + Recorded" if storefront.has_video_content else "Live Batch"


def _to_listing_out(entry: BDLandingPage, storefront: StorefrontPackage) -> PackageListingOut:
    return PackageListingOut(
        package_id=entry.package_id,
        display_code=entry.display_code,
        title=storefront.title or entry.package_id,
        thumbnail_url=storefront.thumbnail_url,
        price_bdt=entry.price_bdt,
        language=storefront.language,
        batch_type=_batch_type(storefront),
        live_classes_count=storefront.live_classes_count,
        video_count=storefront.video_count,
        start_date=storefront.schedule.start_date if storefront.schedule else None,
        display_order=entry.display_order,
    )


def _to_pdp_out(entry: BDLandingPage, storefront: StorefrontPackage) -> PackagePdpOut:
    schedule = storefront.schedule
    return PackagePdpOut(
        package_id=entry.package_id,
        display_code=entry.display_code,
        title=storefront.title or entry.package_id,
        thumbnail_url=storefront.thumbnail_url,
        price_bdt=entry.price_bdt,
        language=storefront.language,
        batch_type=_batch_type(storefront),
        live_classes_count=storefront.live_classes_count,
        video_count=storefront.video_count,
        start_date=schedule.start_date if schedule else None,
        end_date=schedule.end_date if schedule else None,
        seats=schedule.seats if schedule else None,
        timings=schedule.timings if schedule else None,
        plan=PlanOut.model_validate(storefront.plan) if storefront.plan else None,
        highlights=storefront.highlights,
        exam_badges=[ExamBadgeOut.model_validate(b) for b in storefront.exam_badges],
        faculties=[FacultyOut.model_validate(f) for f in storefront.faculties],
        overview_html=storefront.overview_html,
        sections=[SectionOut.model_validate(s) for s in storefront.sections],
        faqs=[FaqOut.model_validate(f) for f in storefront.faqs],
        testimonials=[TestimonialOut.model_validate(t) for t in storefront.testimonials],
    )


def list_storefront_packages(db: Session) -> list[PackageListingOut]:
    query = (
        select(BDLandingPage)
        .where(BDLandingPage.published.is_(True))
        .order_by(BDLandingPage.display_order.asc())
    )
    listings = []
    for entry in db.scalars(query):
        try:
            storefront = fetch_storefront_package(entry.package_id)
        except PackageNotFoundError:
            continue
        listings.append(_to_listing_out(entry, storefront))
    return listings


def get_storefront_package(db: Session, package_id: str) -> PackagePdpOut:
    entry = db.scalar(select(BDLandingPage).where(BDLandingPage.package_id == package_id))
    if entry is None or not entry.published:
        raise PackageUnavailableError(package_id)

    try:
        storefront = fetch_storefront_package(package_id)
    except PackageNotFoundError:
        raise PackageUnavailableError(package_id)

    return _to_pdp_out(entry, storefront)
