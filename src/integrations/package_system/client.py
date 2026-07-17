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


@dataclass
class Faculty:
    name: str
    image: str | None
    subject: str | None
    experience_years: str | None
    quote: str | None
    demo_url: str | None
    students_mentored: int


@dataclass
class BatchSchedule:
    start_date: str | None
    end_date: str | None
    timings: str | None
    seats: int | None


@dataclass
class Plan:
    title: str
    validity: int | None
    validity_unit: str | None
    validity_title: str | None


@dataclass
class ExamBadge:
    name: str
    thumbnail: str | None


@dataclass
class ContentSection:
    title: str
    html: str


@dataclass
class Faq:
    question: str
    answer: str


@dataclass
class Testimonial:
    name: str
    image: str | None
    rating: int
    description: str


@dataclass
class StorefrontPackage:
    package_id: str
    title: str
    thumbnail_url: str | None
    language: str | None
    live_classes_count: int
    video_count: int
    has_video_content: bool
    schedule: BatchSchedule | None
    plan: Plan | None
    highlights: list[str]
    exam_badges: list[ExamBadge]
    testimonials: list[Testimonial]
    faculties: list[Faculty]
    overview_html: str | None
    sections: list[ContentSection]
    faqs: list[Faq]
    published: bool


def _fetch_entity(package_id: str) -> dict:
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
    return entities[0]


def fetch_package(package_id: str) -> PackageDetails:
    entity = _fetch_entity(package_id)
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


def fetch_storefront_package(package_id: str) -> StorefrontPackage:
    entity = _fetch_entity(package_id)

    languages = entity.get("languages") or []
    primary_language = next((lang.get("name") for lang in languages if lang.get("primary")), None)
    if primary_language is None and languages:
        primary_language = languages[0].get("name")

    category_list = entity.get("categoryList") or []
    video_count = int(entity.get("videoCount") or 0)
    has_video_content = "VIDEOS" in category_list or video_count > 0

    olc_meta = entity.get("olcMetaJson") or {}
    schedule = (
        BatchSchedule(
            start_date=olc_meta.get("start") or entity.get("batchStartingDate"),
            end_date=olc_meta.get("end"),
            timings=olc_meta.get("class"),
            seats=olc_meta.get("seats"),
        )
        if olc_meta or entity.get("batchStartingDate")
        else None
    )

    multi_validity = entity.get("multiValidity") or []
    plan = None
    if multi_validity:
        mv = multi_validity[0]
        plan = Plan(
            title=mv.get("validityTitle") or mv.get("title", ""),
            validity=mv.get("validity"),
            validity_unit=mv.get("validityUnit"),
            validity_title=mv.get("validityTitle"),
        )

    highlights = [h.get("hlsJson", "") for h in (entity.get("hlsJson") or []) if h.get("hlsJson")]

    exam_badges = [
        ExamBadge(name=e.get("name", ""), thumbnail=e.get("thumbnail"))
        for e in (entity.get("examTypes") or [])
        if e.get("name")
    ]

    faculties = [
        Faculty(
            name=f.get("name", ""),
            image=f.get("image"),
            subject=f.get("subject"),
            experience_years=f.get("exp"),
            quote=f.get("highlights"),
            demo_url=f.get("url"),
            students_mentored=int(f.get("studentsMentored") or 0),
        )
        for f in (entity.get("faculties") or [])
    ]

    sections = [
        ContentSection(title=item["title"], html=item["desc"])
        for item in (entity.get("additionalDesc") or [])
        if item.get("title") and item.get("desc")
    ]

    faqs = [
        Faq(question=q, answer=a)
        for raw in (entity.get("faqJson") or [])
        if (q := raw.get("question") or raw.get("q"))
        and (a := raw.get("answer") or raw.get("a") or raw.get("ans"))
    ]

    testimonials = [
        Testimonial(
            name=t.get("name", ""),
            image=t.get("s3URL"),
            rating=int(t.get("rating") or 0),
            description=t.get("description", ""),
        )
        for t in (entity.get("testimonialJson") or [])
        if t.get("name") and t.get("description")
    ]

    return StorefrontPackage(
        package_id=package_id,
        title=entity.get("title", ""),
        thumbnail_url=entity.get("imgUrl"),
        language=primary_language,
        live_classes_count=int(entity.get("olcCount") or 0),
        video_count=video_count,
        has_video_content=has_video_content,
        schedule=schedule,
        plan=plan,
        highlights=highlights,
        exam_badges=exam_badges,
        faculties=faculties,
        overview_html=entity.get("overview") or entity.get("description") or None,
        sections=sections,
        faqs=faqs,
        testimonials=testimonials,
        published=bool(entity.get("published")),
    )
