export function HowThisWorksPanel() {
  return (
    <div className="space-y-4">
      <div className="bg-card border border-border rounded-lg p-5">
        <h2 className="font-semibold text-navy mb-3">How this works</h2>
        <ol className="space-y-3 text-sm text-unpublished">
          <li>
            <span className="font-semibold text-navy">1.</span> Fetch the package by ID —
            content comes from the package system, nothing is authored here.
          </li>
          <li>
            <span className="font-semibold text-navy">2.</span> Set the BDT price — this
            exact amount is passed to Transfi at checkout.
          </li>
          <li>
            <span className="font-semibold text-navy">3.</span> Publish when the product
            should go live for the month; unpublish to delist it.
          </li>
        </ol>
      </div>
      <div className="bg-amber-bg text-amber-text rounded-lg p-5">
        <h3 className="font-semibold mb-1">Monthly catalogue changes</h3>
        <p className="text-sm">
          Products rotate every month. Unpublish outgoing packages and create or publish
          incoming ones — changes reflect on the live page within ~15 minutes (cache).
        </p>
      </div>
    </div>
  );
}
