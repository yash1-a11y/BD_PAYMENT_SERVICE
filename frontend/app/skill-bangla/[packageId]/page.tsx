import Link from "next/link";
import { notFound } from "next/navigation";
import { FacultyCarousel } from "@/components/storefront/FacultyCarousel";
import { FaqAccordion } from "@/components/storefront/FaqAccordion";
import { PdpStickyChrome } from "@/components/storefront/PdpStickyChrome";
import { SiteHeader } from "@/components/storefront/SiteHeader";
import { TestimonialCarousel } from "@/components/storefront/TestimonialCarousel";
import { getPackage, StorefrontApiError } from "@/lib/storefront-api";
import { formatShortDate, formatTaka } from "@/lib/storefront-format";
import { PackagePdp } from "@/lib/storefront-types";

const SALIENT_FEATURES = [
  "Expert Faculties",
  "Interactive Classes",
  "Recorded Videos",
  "Limited Batch Size",
];

// Generic, storefront-level FAQs — not package data. Every real package
// checked returns an empty faqJson, so these always render; any real
// per-package FAQs are shown first.
const GENERIC_FAQS = [
  {
    question: "How to attend Live Classes after purchase?",
    answer:
      "After your purchase is confirmed, you'll get access details for the live classes on the Adda247 app or website using the same phone number you checked out with.",
  },
  {
    question: "How to check the study plan?",
    answer:
      "The Study Plan tab on this page lists the topic-wise plan for this course, with links to the detailed schedule.",
  },
  {
    question: "How to get class notifications?",
    answer:
      "Enable notifications in the Adda247 app, or check the class schedule under My Courses — you'll be notified before each live class starts.",
  },
  {
    question: "How to access PDF/Handouts of live class?",
    answer:
      "Handouts and PDFs shared during live classes are available under the class's resources section in the Adda247 app or website.",
  },
  {
    question: "What if I miss my live classes?",
    answer:
      "No problem — recorded videos of every live class are available so you can catch up at your convenience.",
  },
  {
    question: "Will I get topic wise test / daily quizzes in the package?",
    answer:
      "Yes, if this course includes test series access, topic-wise tests and daily quizzes are available as part of it.",
  },
  {
    question: "Can I re-attempt the test?",
    answer: "Yes, tests included in this course can be re-attempted to help you track improvement.",
  },
  {
    question: "How can test series help me?",
    answer:
      "Test series help you practice with the latest exam pattern, identify weak areas, and track your progress with detailed solutions.",
  },
  {
    question: "When will the mock be live in my account?",
    answer:
      "Mocks included in this course are activated in your account as per the schedule shown under Test Series — check My Courses for exact dates.",
  },
  {
    question: "How to access the test series?",
    answer: "Go to My Courses on the Adda247 app or website and open the Test Series section for this course.",
  },
  {
    question: "How to access video course?",
    answer: "Recorded videos are available under My Courses in the Adda247 app or website, playable anytime.",
  },
  {
    question: "How is a video course different from a live class?",
    answer:
      "A video course is pre-recorded content you can watch anytime, while live classes happen at a scheduled time with real-time interaction.",
  },
  {
    question: "Can I download videos?",
    answer: "Videos are available for streaming within the Adda247 app; offline download availability depends on this course's plan.",
  },
  {
    question: "Is the video course updated with the latest content?",
    answer: "Yes, video content is kept current with the latest exam pattern and syllabus updates.",
  },
  {
    question: "Can I access videos after the subscription expires?",
    answer: "No, video access is tied to your course validity period and ends once it expires.",
  },
  {
    question: "Can I download or print Ebook?",
    answer: "Ebooks included in this course are available to download and print from My Courses.",
  },
  {
    question: "How can I check/know the language of the ebook?",
    answer: "The ebook's language is listed alongside it under the Ebooks section in My Courses.",
  },
  {
    question: "How to access ebooks?",
    answer: "Go to My Courses on the Adda247 app or website and open the Ebooks section for this course.",
  },
  {
    question: "Will I get ebooks immediately after purchase?",
    answer: "Yes, ebooks included in this course are available in your account immediately after purchase.",
  },
];

function includesChips(pkg: PackagePdp): string[] {
  const chips: string[] = [];
  if (pkg.live_classes_count > 0) chips.push(`${pkg.live_classes_count} Online Live Classes`);
  if (pkg.video_count > 0) chips.push(`${pkg.video_count} Videos`);
  return chips;
}

export default async function PackagePdpPage({
  params,
}: {
  params: Promise<{ packageId: string }>;
}) {
  const { packageId } = await params;

  let pkg: PackagePdp;
  try {
    pkg = await getPackage(packageId);
  } catch (err) {
    if (err instanceof StorefrontApiError && err.status === 404) notFound();
    throw err;
  }

  const chips = includesChips(pkg);
  const faqs = [...pkg.faqs, ...GENERIC_FAQS];

  const tabs: { id: string; label: string }[] = [];
  if (pkg.overview_html) tabs.push({ id: "overview", label: "Overview" });
  for (const section of pkg.sections) {
    tabs.push({ id: section.title.toLowerCase().replace(/\s+/g, "-"), label: section.title });
  }
  tabs.push({ id: "faqs", label: "FAQs" });
  if (pkg.testimonials.length > 0) tabs.push({ id: "testimonials", label: "Testimonials" });

  return (
    <div className="pb-24 md:pb-0">
      <SiteHeader />

      <div className="max-w-6xl mx-auto px-6 py-6">
        <Link href="/skill-bangla" className="text-sm text-sb-muted hover:underline">
          ← All courses
        </Link>

        <div className="grid md:grid-cols-[minmax(0,1fr)_360px] gap-8 mt-4">
          {/* Left column */}
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-sb-ink mb-3">{pkg.title}</h1>

            {(pkg.start_date || pkg.seats || pkg.timings) && (
              <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-sb-muted mb-4 divide-x divide-sb-border [&>*:not(:first-child)]:pl-4">
                {pkg.start_date && <span>Starts: {formatShortDate(pkg.start_date)}</span>}
                {pkg.seats && <span>Seats: {pkg.seats}</span>}
                {pkg.timings && <span>Timings: {pkg.timings}</span>}
              </div>
            )}

            {chips.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-6">
                {chips.map((chip) => (
                  <span
                    key={chip}
                    className="text-xs font-medium px-3 py-1.5 rounded-[11px] border border-sb-border bg-sb-card"
                  >
                    {chip}
                  </span>
                ))}
              </div>
            )}

            {pkg.plan && (
              <section className="mb-8">
                <h2 className="font-bold text-sb-ink mb-3">
                  Our <span className="text-sb-red">Plan</span>
                </h2>
                <div className="relative border-2 border-sb-blue rounded-[12px] p-4 max-w-xs">
                  <span className="absolute -top-3 left-4 bg-sb-blue text-white text-xs font-medium px-2 py-0.5 rounded-full">
                    Recommended
                  </span>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-bold text-sb-ink">{pkg.plan.title}</p>
                      {pkg.plan.validity_title && (
                        <p className="text-xs text-sb-muted">
                          Valid for {pkg.plan.validity_title.toUpperCase()}
                        </p>
                      )}
                      <p className="font-bold text-sb-ink mt-1">{formatTaka(pkg.price_bdt)}</p>
                    </div>
                    <span className="w-4 h-4 rounded-full border-2 border-sb-blue flex items-center justify-center">
                      <span className="w-2 h-2 rounded-full bg-sb-blue" />
                    </span>
                  </div>
                </div>
              </section>
            )}

            <section className="mb-8">
              <h2 className="font-bold text-sb-ink mb-3">
                Salient <span className="text-sb-red">Features</span>
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {SALIENT_FEATURES.map((feature) => (
                  <div
                    key={feature}
                    className="border border-sb-border rounded-[11px] p-3 text-sm font-medium text-sb-ink"
                  >
                    {feature}
                  </div>
                ))}
              </div>
            </section>

            {pkg.highlights.length > 0 && (
              <section className="mb-8">
                <h2 className="font-bold text-sb-ink mb-3">
                  Product <span className="text-sb-red">Highlights</span>
                </h2>
                <ul className="grid md:grid-cols-2 gap-2">
                  {pkg.highlights.map((highlight) => (
                    <li key={highlight} className="flex gap-2 text-sm text-sb-ink">
                      <span className="text-sb-green shrink-0">✓</span>
                      <span>{highlight}</span>
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {pkg.exam_badges.length > 0 && (
              <section className="mb-8">
                <h2 className="font-bold text-sb-ink mb-3">
                  Exams <span className="text-sb-red">Covered</span>
                </h2>
                <div className="flex flex-wrap gap-4">
                  {pkg.exam_badges.map((badge) => (
                    <div key={badge.name} className="flex flex-col items-center gap-1 text-center w-24">
                      {badge.thumbnail && (
                        // eslint-disable-next-line @next/next/no-img-element -- hotlinked external CDN image
                        <img
                          src={badge.thumbnail}
                          alt=""
                          className="w-10 h-10 rounded-full object-cover bg-sb-gray-pill"
                        />
                      )}
                      <span className="text-xs text-sb-muted">{badge.name}</span>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {chips.length > 0 && (
              <section className="mb-8">
                <h2 className="font-bold text-sb-ink mb-3">
                  This Course <span className="text-sb-red">Includes</span>
                </h2>
                <div className="flex flex-wrap gap-2">
                  {chips.map((chip) => (
                    <span
                      key={chip}
                      className="text-xs font-medium px-3 py-1.5 rounded-[11px] border border-sb-border bg-sb-card"
                    >
                      {chip}
                    </span>
                  ))}
                </div>
              </section>
            )}

            {pkg.faculties.length > 0 && (
              <section className="mb-8">
                <h2 className="font-bold text-sb-ink mb-3">
                  Faculty <span className="text-sb-red">Profile</span>
                </h2>
                <FacultyCarousel faculties={pkg.faculties} />
              </section>
            )}
          </div>

          {/* Right column — buy card (desktop only; mobile uses sticky bottom bar) */}
          <div className="hidden md:block">
            <div className="sticky top-6 bg-sb-card border border-sb-border rounded-[16px] p-4">
              <div className="relative aspect-video bg-sb-gray-pill rounded-lg overflow-hidden mb-3">
                {pkg.thumbnail_url && (
                  // eslint-disable-next-line @next/next/no-img-element -- hotlinked external CDN image
                  <img
                    src={pkg.thumbnail_url}
                    alt={pkg.title}
                    className="absolute inset-0 w-full h-full object-cover"
                  />
                )}
                {pkg.demo_url && (
                  <a
                    href={pkg.demo_url}
                    target="_blank"
                    rel="noreferrer"
                    className="absolute inset-0 flex items-center justify-center"
                    aria-label="Play demo video"
                  >
                    <span className="w-12 h-12 rounded-full bg-black/50 text-white flex items-center justify-center text-xl">
                      ▶
                    </span>
                  </a>
                )}
              </div>
              <div className="flex gap-2 mb-3">
                {pkg.language && (
                  <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-sb-gray-pill text-sb-gray-pill-ink">
                    {pkg.language}
                  </span>
                )}
                <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-sb-blue-bg text-sb-blue">
                  {pkg.batch_type}
                </span>
              </div>
              <p className="text-2xl font-bold text-sb-ink mb-1">{formatTaka(pkg.price_bdt)}</p>
              <p className="text-xs text-sb-muted mb-4">
                Paid once in BDT via secure Transfi checkout
              </p>
              <Link
                href={`/skill-bangla/checkout?packageId=${encodeURIComponent(pkg.package_id)}`}
                className="block text-center bg-sb-red hover:bg-sb-red-hover text-white font-medium rounded-md py-2.5 transition-colors"
              >
                BUY NOW
              </Link>
            </div>
          </div>
        </div>

      </div>

      {/* Sticky compact buy bar + tab bar (client component: scroll-tracked) */}
      <PdpStickyChrome
        tabs={tabs}
        buyBar={{
          packageId: pkg.package_id,
          title: pkg.title,
          thumbnailUrl: pkg.thumbnail_url,
          priceBdt: pkg.price_bdt,
          planTitle: pkg.plan?.validity_title ?? null,
        }}
      />

      <div className="max-w-6xl mx-auto px-6">
        <div className="py-6 space-y-10">
          {pkg.overview_html && (
            <section id="overview" className="scroll-mt-32">
              <h2 className="font-bold text-sb-ink mb-3 text-lg">Overview</h2>
              <div
                className="sb-html-content text-sm text-sb-ink"
                dangerouslySetInnerHTML={{ __html: pkg.overview_html }}
              />
            </section>
          )}

          {pkg.sections.map((section) => {
            const id = section.title.toLowerCase().replace(/\s+/g, "-");
            return (
              <section key={id} id={id} className="scroll-mt-32">
                <h2 className="font-bold text-sb-ink mb-3 text-lg">{section.title}</h2>
                <div
                  className="sb-html-content text-sm text-sb-ink"
                  dangerouslySetInnerHTML={{ __html: section.html }}
                />
              </section>
            );
          })}

          <section id="faqs" className="scroll-mt-32">
            <h2 className="font-bold text-sb-ink mb-3 text-lg">
              Frequently Asked <span className="text-sb-red">Questions</span>
            </h2>
            <FaqAccordion faqs={faqs} />
          </section>

          {pkg.testimonials.length > 0 && (
            <section id="testimonials" className="scroll-mt-32">
              <h2 className="font-bold text-sb-ink mb-3 text-lg">Testimonials</h2>
              <TestimonialCarousel testimonials={pkg.testimonials} />
            </section>
          )}
        </div>
      </div>

      {/* Mobile sticky bottom bar */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 bg-sb-card border-t border-sb-border p-3 flex items-center justify-between gap-4">
        <p className="text-lg font-bold text-sb-ink">{formatTaka(pkg.price_bdt)}</p>
        <Link
          href={`/skill-bangla/checkout?packageId=${encodeURIComponent(pkg.package_id)}`}
          className="bg-sb-red hover:bg-sb-red-hover text-white font-medium rounded-md px-6 py-2.5 transition-colors"
        >
          BUY NOW
        </Link>
      </div>
    </div>
  );
}
