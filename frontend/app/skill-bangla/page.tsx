import Link from "next/link";
import { SiteHeader } from "@/components/storefront/SiteHeader";
import { listPackages } from "@/lib/storefront-api";
import { formatTaka, listingMetaLine } from "@/lib/storefront-format";

export default async function SkillBanglaListingPage() {
  const packages = await listPackages();

  return (
    <div>
      <SiteHeader />

      <section
        className="px-6 py-10"
        style={{ background: "linear-gradient(180deg, #1A2B4A 0%, #10203C 100%)" }}
      >
        <h1 className="text-2xl md:text-3xl font-bold text-white">
          Skill courses in Bangla, taught live
        </h1>
      </section>

      <main className="px-6 py-8">
        <p className="mb-4 text-sm text-sb-muted">
          {packages.length} course{packages.length === 1 ? "" : "s"} live now
        </p>

        {packages.length === 0 ? (
          <div className="text-center py-20 text-sb-muted">
            No courses are live right now — check back soon.
          </div>
        ) : (
          <div
            className="grid gap-5"
            style={{ gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))" }}
          >
            {packages.map((pkg) => (
              <Link
                key={pkg.package_id}
                href={`/skill-bangla/${encodeURIComponent(pkg.package_id)}`}
                className="block bg-sb-card border border-sb-border rounded-[14px] overflow-hidden hover:shadow-md transition-shadow"
              >
                <div className="relative aspect-square bg-sb-gray-pill">
                  {pkg.thumbnail_url && (
                    // eslint-disable-next-line @next/next/no-img-element -- hotlinked external CDN thumbnails, no local optimization possible
                    <img
                      src={pkg.thumbnail_url}
                      alt={pkg.title}
                      className="absolute inset-0 w-full h-full object-cover"
                    />
                  )}
                </div>
                <div className="p-4">
                  <div className="flex gap-2 mb-2">
                    {pkg.language && (
                      <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-sb-gray-pill text-sb-gray-pill-ink">
                        {pkg.language}
                      </span>
                    )}
                    <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-sb-blue-bg text-sb-blue">
                      {pkg.batch_type}
                    </span>
                  </div>
                  <h2 className="font-bold text-sb-ink line-clamp-2 mb-1">{pkg.title}</h2>
                  <p className="text-xs text-sb-muted mb-3">{listingMetaLine(pkg)}</p>
                  <p className="text-right font-bold text-sb-ink">{formatTaka(pkg.price_bdt)}</p>
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
