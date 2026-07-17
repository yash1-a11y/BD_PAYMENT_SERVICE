export function SiteHeader() {
  return (
    <header className="border-b border-sb-border bg-sb-card px-6 py-4 flex flex-col items-center">
      {/* eslint-disable-next-line @next/next/no-img-element -- static local asset, next/image is overkill for a tiny fixed logo */}
      <img src="/adda247-logo.png" alt="Adda247" className="h-6 w-auto" />
      <div className="text-xs font-semibold tracking-wide text-sb-muted mt-1">SKILL BANGLA</div>
    </header>
  );
}
