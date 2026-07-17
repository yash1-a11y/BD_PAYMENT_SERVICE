"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { useToast } from "@/components/Toast";
import { createLandingPage, lookupPackage, updateLandingPage } from "@/lib/api";
import { ApiError, PackageLookupResult } from "@/lib/types";
import { PackagePreviewPanel } from "@/components/PackagePreviewPanel";
import { HowThisWorksPanel } from "@/components/HowThisWorksPanel";

interface Props {
  mode: "create" | "edit";
  entryId?: string;
  displayCode?: string;
  initialPackageId?: string;
  initialPriceBdt?: string;
  initialPublished?: boolean;
}

export function LandingPageForm({
  mode,
  entryId,
  displayCode,
  initialPackageId = "",
  initialPriceBdt = "",
  initialPublished = false,
}: Props) {
  const { token } = useAuth();
  const { showToast } = useToast();
  const router = useRouter();

  const [packageId, setPackageId] = useState(initialPackageId);
  const [priceBdt, setPriceBdt] = useState(initialPriceBdt);
  const [published, setPublished] = useState(initialPublished);

  const [preview, setPreview] = useState<PackageLookupResult | null>(null);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [isFetching, setIsFetching] = useState(false);

  const [priceError, setPriceError] = useState<string | null>(null);
  const [packageIdError, setPackageIdError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  async function handleFetch() {
    if (!token || !packageId) return;
    setIsFetching(true);
    setFetchError(null);
    try {
      const result = await lookupPackage(token, packageId);
      setPreview(result);
      if (!result.source_published) {
        setFetchError(
          "This package exists but isn't published in the package system yet. Publish it there first, then fetch again."
        );
      }
    } catch (err) {
      setPreview(null);
      if (err instanceof ApiError) {
        setFetchError(err.message);
      } else {
        setFetchError("Something went wrong. Please try again.");
      }
    } finally {
      setIsFetching(false);
    }
  }

  useEffect(() => {
    if (mode === "edit" && initialPackageId) {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- initial preview fetch from the package system on mount for edit mode
      handleFetch();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode]);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setPriceError(null);
    setPackageIdError(null);

    const price = Number(priceBdt);
    if (!price || price <= 0) {
      setPriceError("Enter a price greater than 0.");
      return;
    }
    if (mode === "create" && (!preview || !preview.source_published)) {
      setFetchError("Fetch a published package before saving.");
      return;
    }
    if (!token) return;

    setIsSaving(true);
    try {
      if (mode === "create") {
        await createLandingPage(token, { package_id: packageId, price_bdt: price, published });
        showToast(published ? `Created and published · ${displayCode ?? ""}` : "Changes saved");
      } else if (entryId) {
        await updateLandingPage(token, entryId, { price_bdt: price, published });
        showToast("Changes saved");
      }
      router.push("/bd-admin/landing-pages");
    } catch (err) {
      if (err instanceof ApiError) {
        setPriceError(err.fieldMessage("price_bdt") ?? null);
        setPackageIdError(err.fieldMessage("package_id") ?? null);
        if (err.fieldMessage("package_id")) {
          showToast(err.fieldMessage("package_id")!);
        }
      }
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div>
      <div className="text-sm text-unpublished mb-6">
        <span>Landing pages / </span>
        {mode === "create" ? (
          <span>Create landing page · LP ID assigned on save</span>
        ) : (
          <span>Edit landing page · {displayCode}</span>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-6">
        <form onSubmit={handleSave} className="space-y-6">
          <div className="bg-card border border-border rounded-lg p-5">
            <h2 className="font-semibold text-navy mb-3">Package</h2>
            <label className="block text-sm font-medium text-navy mb-1">Package ID</label>
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="e.g. 109216"
                value={packageId}
                disabled={mode === "edit"}
                onChange={(e) => setPackageId(e.target.value)}
                className="flex-1 font-mono border border-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-navy disabled:bg-page disabled:text-unpublished"
              />
              <button
                type="button"
                onClick={handleFetch}
                disabled={isFetching || !packageId || mode === "edit"}
                className="bg-navy hover:bg-navy-hover text-white text-sm font-medium rounded-md px-4 py-2 whitespace-nowrap disabled:opacity-60 transition-colors"
              >
                Fetch details
              </button>
            </div>
            {packageIdError && <p className="text-xs text-accent mt-1">{packageIdError}</p>}
            <p className="text-xs text-unpublished mt-2">
              All page content (title, description, inclusions, imagery) is pulled from the
              internal package system using this ID.
            </p>

            <div className="mt-4">
              <PackagePreviewPanel preview={preview} errorMessage={fetchError} />
            </div>
          </div>

          <div className="bg-card border border-border rounded-lg p-5">
            <h2 className="font-semibold text-navy mb-3">Pricing</h2>
            <label className="block text-sm font-medium text-navy mb-1">
              Selling price (BDT)
            </label>
            <input
              type="number"
              placeholder="e.g. 1499"
              min={1}
              value={priceBdt}
              onChange={(e) => setPriceBdt(e.target.value)}
              className="w-full font-mono border border-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-navy"
            />
            {priceError && <p className="text-xs text-accent mt-1">{priceError}</p>}
            <p className="text-xs text-unpublished mt-2">
              This amount is passed to the Transfi widget and charged to the customer in
              Bangladeshi Taka.
            </p>
          </div>

          <div className="bg-card border border-border rounded-lg p-5">
            <h2 className="font-semibold text-navy mb-3">Status</h2>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setPublished(true)}
                className={`text-left border rounded-lg p-4 transition-colors ${
                  published ? "border-navy ring-2 ring-navy" : "border-border"
                }`}
              >
                <div className="font-medium text-published mb-1">Published</div>
                <p className="text-xs text-unpublished">
                  Listed on the BD landing page. Customers can view the PDP and buy.
                </p>
              </button>
              <button
                type="button"
                onClick={() => setPublished(false)}
                className={`text-left border rounded-lg p-4 transition-colors ${
                  !published ? "border-navy ring-2 ring-navy" : "border-border"
                }`}
              >
                <div className="font-medium text-unpublished mb-1">Unpublished</div>
                <p className="text-xs text-unpublished">
                  Hidden from the landing page. Existing owners keep course access.
                </p>
              </button>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              type="submit"
              disabled={isSaving}
              className="bg-accent hover:bg-accent-hover text-white text-sm font-medium rounded-md px-5 py-2.5 disabled:opacity-60 transition-colors"
            >
              Save landing page
            </button>
            <button
              type="button"
              onClick={() => router.push("/bd-admin/landing-pages")}
              className="border border-border text-navy text-sm font-medium rounded-md px-5 py-2.5 hover:bg-page transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>

        <HowThisWorksPanel />
      </div>
    </div>
  );
}
