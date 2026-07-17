from decimal import Decimal

from pydantic import BaseModel


class FacultyOut(BaseModel):
    name: str
    image: str | None
    subject: str | None
    experience_years: str | None
    quote: str | None
    demo_url: str | None
    students_mentored: int

    model_config = {"from_attributes": True}


class PlanOut(BaseModel):
    title: str
    validity: int | None
    validity_unit: str | None
    validity_title: str | None

    model_config = {"from_attributes": True}


class ExamBadgeOut(BaseModel):
    name: str
    thumbnail: str | None

    model_config = {"from_attributes": True}


class SectionOut(BaseModel):
    title: str
    html: str

    model_config = {"from_attributes": True}


class FaqOut(BaseModel):
    question: str
    answer: str

    model_config = {"from_attributes": True}


class TestimonialOut(BaseModel):
    name: str
    image: str | None
    rating: int
    description: str

    model_config = {"from_attributes": True}


class PackageListingOut(BaseModel):
    package_id: str
    display_code: str
    title: str
    thumbnail_url: str | None
    price_bdt: Decimal
    language: str | None
    batch_type: str
    live_classes_count: int
    video_count: int
    start_date: str | None
    display_order: int


class PackagePdpOut(BaseModel):
    package_id: str
    display_code: str
    title: str
    thumbnail_url: str | None
    price_bdt: Decimal
    language: str | None
    batch_type: str
    live_classes_count: int
    video_count: int
    start_date: str | None
    end_date: str | None
    seats: int | None
    timings: str | None
    plan: PlanOut | None
    highlights: list[str]
    exam_badges: list[ExamBadgeOut]
    faculties: list[FacultyOut]
    overview_html: str | None
    sections: list[SectionOut]
    faqs: list[FaqOut]
    testimonials: list[TestimonialOut]
