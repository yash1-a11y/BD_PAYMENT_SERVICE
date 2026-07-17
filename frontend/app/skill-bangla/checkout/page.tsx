import Link from "next/link";

export default async function CheckoutPlaceholderPage({
  searchParams,
}: {
  searchParams: Promise<{ packageId?: string }>;
}) {
  const { packageId } = await searchParams;

  return (
    <div className="min-h-screen flex items-center justify-center px-4 text-center">
      <div>
        <h1 className="text-xl font-bold text-sb-ink mb-2">Checkout coming soon</h1>
        <p className="text-sm text-sb-muted mb-1">
          Secure payment via Transfi is on its way.
        </p>
        {packageId && (
          <p className="text-xs text-sb-muted mb-6">Package: {packageId}</p>
        )}
        {!packageId && <div className="mb-6" />}
        <Link
          href="/skill-bangla"
          className="inline-block bg-sb-red hover:bg-sb-red-hover text-white text-sm font-medium rounded-md px-4 py-2 transition-colors"
        >
          ← Back to all courses
        </Link>
      </div>
    </div>
  );
}
