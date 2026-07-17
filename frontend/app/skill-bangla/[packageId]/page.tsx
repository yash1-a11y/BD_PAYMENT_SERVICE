import Link from "next/link";
import { notFound } from "next/navigation";
import { FaqAccordion } from "@/components/storefront/FaqAccordion";
import { getPackage, StorefrontApiError } from "@/lib/storefront-api";
import { formatShortDate, formatTaka } from "@/lib/storefront-format";
import { PackagePdp } from "@/lib/storefront-types";

const SALIENT_FEATURES = [
  "Expert Faculties",
  "Interactive Classes",
  "Recorded Videos",
  "Limited Batch Size",
];

function includesChips(pkg: PackagePdp): string[] {
  const chips: string[] = [];
  if (pkg.live_classes_count > 0) chips.push(`${pkg.live_classes_count} Online Live Classes`);
  if (pkg.video_count > 0) chips.push(`${pkg.video_count} Videos`);
  return chips;
}

const SECTION_ORDER = ["This Package Includes", "Subjects Covered", "Note", "Study Plan"];

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
  const sectionsByTitle = new Map(pkg.sections.map((s) => [s.title, s.html]));

  const tabs: { id: string; label: string }[] = [];
  if (pkg.overview_html) tabs.push({ id: "overview", label: "Overview" });
  for (const title of SECTION_ORDER) {
    if (sectionsByTitle.has(title)) {
      tabs.push({ id: title.toLowerCase().replace(/\s+/g, "-"), label: title });
    }
  }
  if (pkg.faqs.length > 0) tabs.push({ id: "faqs", label: "FAQs" });

  return (
    <div className="pb-24 md:pb-0">
      <header className="border-b border-sb-border bg-sb-card px-6 py-4">
        <span className="text-xl font-extrabold text-sb-red">adda247</span>
        <div className="text-xs font-semibold tracking-wide text-sb-muted">SKILL BANGLA</div>
      </header>

      <div className="max-w-6xl mx-auto px-6 py-6">
        <Link href="/skill-bangla" className="text-sm text-sb-muted hover:underline">
          ← All courses
        </Link>

        <div className="grid md:grid-cols-[1fr_360px] gap-8 mt-4">
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
                <div className="grid md:grid-cols-3 gap-4">
                  {pkg.faculties.map((faculty) => (
                    <div
                      key={faculty.name}
                      className="border border-sb-border rounded-[14px] p-4"
                    >
                      <div className="flex items-center gap-3 mb-2">
                        <div className="w-12 h-12 rounded-full bg-sb-gray-pill overflow-hidden shrink-0">
                          {faculty.image && (
                            // eslint-disable-next-line @next/next/no-img-element -- hotlinked external CDN image
                            <img
                              src={faculty.image}
                              alt={faculty.name}
                              className="w-full h-full object-cover"
                            />
                          )}
                        </div>
                        <div>
                          <p className="font-bold text-sb-ink text-sm">{faculty.name}</p>
                          {faculty.subject && (
                            <p className="text-xs text-sb-muted uppercase">{faculty.subject}</p>
                          )}
                        </div>
                      </div>
                      {faculty.demo_url && (
                        <a
                          href={faculty.demo_url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-xs font-medium text-sb-blue hover:underline"
                        >
                          ▶ Play Demo
                        </a>
                      )}
                      <ul className="mt-2 space-y-1">
                        {faculty.experience_years && (
                          <li className="flex gap-2 text-xs text-sb-ink">
                            <span className="text-sb-green shrink-0">✓</span>
                            <span>{faculty.experience_years}+ years of Experience</span>
                          </li>
                        )}
                        {faculty.students_mentored > 0 && (
                          <li className="flex gap-2 text-xs text-sb-ink">
                            <span className="text-sb-green shrink-0">✓</span>
                            <span>
                              More than {faculty.students_mentored.toLocaleString("en-IN")} Aspirants
                              Mentored
                            </span>
                          </li>
                        )}
                        {faculty.quote && (
                          <li className="flex gap-2 text-xs text-sb-ink">
                            <span className="text-sb-green shrink-0">✓</span>
                            <span>{faculty.quote}</span>
                          </li>
                        )}
                      </ul>
                    </div>
                  ))}
                </div>
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
                <span className="absolute inset-0 flex items-center justify-center">
                  <span className="w-12 h-12 rounded-full bg-black/50 text-white flex items-center justify-center text-xl">
                    ▶
                  </span>
                </span>
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

        {/* Tabs + content sections */}
        {tabs.length > 0 && (
          <div className="mt-10">
            <div className="sticky top-0 z-10 bg-sb-card border-y border-sb-border flex gap-6 px-1 overflow-x-auto">
              {tabs.map((tab) => (
                <a
                  key={tab.id}
                  href={`#${tab.id}`}
                  className="py-3 text-sm font-medium text-sb-muted hover:text-sb-red whitespace-nowrap border-b-2 border-transparent hover:border-sb-red"
                >
                  {tab.label}
                </a>
              ))}
            </div>

            <div className="py-6 space-y-10">
              {pkg.overview_html && (
                <section id="overview" className="scroll-mt-16">
                  <h2 className="font-bold text-sb-ink mb-3 text-lg">Overview</h2>
                  <div
                    className="sb-html-content text-sm text-sb-ink"
                    dangerouslySetInnerHTML={{ __html: pkg.overview_html }}
                  />
                </section>
              )}

              {SECTION_ORDER.map((title) => {
                const html = sectionsByTitle.get(title);
                if (!html) return null;
                const id = title.toLowerCase().replace(/\s+/g, "-");
                return (
                  <section key={id} id={id} className="scroll-mt-16">
                    <h2 className="font-bold text-sb-ink mb-3 text-lg">{title}</h2>
                    <div
                      className="sb-html-content text-sm text-sb-ink"
                      dangerouslySetInnerHTML={{ __html: html }}
                    />
                  </section>
                );
              })}

              {pkg.faqs.length > 0 && (
                <section id="faqs" className="scroll-mt-16">
                  <h2 className="font-bold text-sb-ink mb-3 text-lg">
                    Frequently Asked <span className="text-sb-red">Questions</span>
                  </h2>
                  <FaqAccordion faqs={pkg.faqs} />
                </section>
              )}
            </div>
          </div>
        )}
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
