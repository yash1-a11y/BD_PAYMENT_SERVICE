import Link from "next/link";
import { SiteHeader } from "@/components/storefront/SiteHeader";

// We don't yet know the exact query param name Transfi appends on redirect
// (never observed a real completed payment) — check the likely candidates
// defensively rather than assuming one specific name.
const LIKELY_ORDER_PARAM_KEYS = [
  "orderId",
  "order_id",
  "customerOrderId",
  "invoiceId",
  "invoice_id",
  "id",
];

function firstValue(value: string | string[] | undefined): string | null {
  if (Array.isArray(value)) return value[0] ?? null;
  return value ?? null;
}

export default async function PaymentStatusPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const entries = Object.entries(params).filter(([, v]) => v !== undefined);

  const orderIdKey = LIKELY_ORDER_PARAM_KEYS.find((key) => params[key] !== undefined);
  const orderId = orderIdKey ? firstValue(params[orderIdKey]) : null;

  return (
    <div>
      <SiteHeader />
      <div className="min-h-[60vh] flex items-center justify-center px-4 text-center">
        <div className="max-w-md w-full">
          <h1 className="text-xl font-bold text-sb-ink mb-2">
            We&apos;re confirming your payment
          </h1>
          <p className="text-sm text-sb-muted mb-1">
            Check back shortly — this page will show your final status once payment is
            confirmed.
          </p>
          {orderId && (
            <p className="text-xs text-sb-muted mt-4 font-mono">Order: {orderId}</p>
          )}

          {entries.length > 0 && (
            <div className="mt-6 text-left bg-sb-card border border-sb-border rounded-[14px] p-4">
              <p className="text-xs font-medium text-sb-muted mb-2">
                Data received from redirect (shown for verification while the real
                param names are unconfirmed):
              </p>
              <dl className="text-xs font-mono space-y-1">
                {entries.map(([key, value]) => (
                  <div key={key} className="flex gap-2">
                    <dt className="text-sb-muted shrink-0">{key}:</dt>
                    <dd className="text-sb-ink break-all">{firstValue(value)}</dd>
                  </div>
                ))}
              </dl>
            </div>
          )}

          <Link
            href="/skill-bangla"
            className="inline-block bg-sb-red hover:bg-sb-red-hover text-white text-sm font-medium rounded-md px-4 py-2 transition-colors mt-6"
          >
            ← Back to all courses
          </Link>
        </div>
      </div>
    </div>
  );
}
