import Link from "next/link";
import { SiteHeader } from "@/components/storefront/SiteHeader";

export default async function PaymentStatusPage({
  searchParams,
}: {
  searchParams: Promise<{ orderId?: string }>;
}) {
  const { orderId } = await searchParams;

  return (
    <div>
      <SiteHeader />
      <div className="min-h-[60vh] flex items-center justify-center px-4 text-center">
        <div className="max-w-md">
          <h1 className="text-xl font-bold text-sb-ink mb-2">
            We&apos;re confirming your payment
          </h1>
          <p className="text-sm text-sb-muted mb-1">
            Check back shortly — this page will show your final status once payment is
            confirmed.
          </p>
          {orderId && (
            <p className="text-xs text-sb-muted mb-6 font-mono">Order: {orderId}</p>
          )}
          {!orderId && <div className="mb-6" />}
          <Link
            href="/skill-bangla"
            className="inline-block bg-sb-red hover:bg-sb-red-hover text-white text-sm font-medium rounded-md px-4 py-2 transition-colors"
          >
            ← Back to all courses
          </Link>
        </div>
      </div>
    </div>
  );
}
