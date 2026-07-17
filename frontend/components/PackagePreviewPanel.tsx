import { PackageLookupResult } from "@/lib/types";

interface Props {
  preview: PackageLookupResult | null;
  errorMessage: string | null;
}

export function PackagePreviewPanel({ preview, errorMessage }: Props) {
  if (errorMessage) {
    return (
      <div className="border border-dashed border-border rounded-lg p-5 text-sm text-accent">
        {errorMessage}
      </div>
    );
  }

  if (!preview) {
    return (
      <div className="border border-dashed border-border rounded-lg p-5 text-sm text-unpublished">
        Enter a package ID and fetch to preview what will appear on the landing page.
      </div>
    );
  }

  return (
    <div className="border border-border rounded-lg p-5">
      <div className="font-semibold text-navy">{preview.title}</div>
      <div className="text-sm text-unpublished mt-1">
        {preview.category}
        {preview.validity_months ? ` · Validity ${preview.validity_months} months` : ""}
      </div>
      {preview.india_mrp != null && (
        <div className="text-sm text-unpublished mt-2 font-mono">
          India MRP (reference): ₹{preview.india_mrp.toLocaleString("en-IN")}
        </div>
      )}
      <p className="text-xs text-unpublished mt-3">
        This content is fetched from the package system and will render on the PDP. Edit
        content in the package system, not here.
      </p>
    </div>
  );
}
