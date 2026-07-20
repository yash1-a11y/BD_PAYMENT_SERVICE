"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { SiteHeader } from "@/components/storefront/SiteHeader";
import { getPackage, initiateCheckout, StorefrontApiError } from "@/lib/storefront-api";
import { formatTaka } from "@/lib/storefront-format";
import { PackagePdp } from "@/lib/storefront-types";

const LOCAL_PHONE_PATTERN = /^1\d{9}$/;

export default function CheckoutPage() {
  return (
    <Suspense fallback={<CheckoutFallback />}>
      <CheckoutForm />
    </Suspense>
  );
}

function CheckoutFallback() {
  return (
    <div>
      <SiteHeader />
      <div className="min-h-[60vh] flex items-center justify-center px-4 text-center text-sm text-sb-muted">
        Loading…
      </div>
    </div>
  );
}

function CheckoutForm() {
  const searchParams = useSearchParams();
  const packageId = searchParams.get("packageId");

  const [pkg, setPkg] = useState<PackagePdp | null>(null);
  const [pkgError, setPkgError] = useState<string | null>(null);
  const [isLoadingPkg, setIsLoadingPkg] = useState(Boolean(packageId));

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [nameError, setNameError] = useState<string | null>(null);
  const [emailError, setEmailError] = useState<string | null>(null);
  const [phoneError, setPhoneError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRedirecting, setIsRedirecting] = useState(false);

  useEffect(() => {
    if (!packageId) return;
    getPackage(packageId)
      .then(setPkg)
      .catch(() => setPkgError("This course isn't available right now."))
      .finally(() => setIsLoadingPkg(false));
  }, [packageId]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setFormError(null);

    let hasError = false;
    if (!name.trim()) {
      setNameError("Name is required.");
      hasError = true;
    } else {
      setNameError(null);
    }
    if (!/^\S+@\S+\.\S+$/.test(email)) {
      setEmailError("Enter a valid email address.");
      hasError = true;
    } else {
      setEmailError(null);
    }
    if (!LOCAL_PHONE_PATTERN.test(phone)) {
      setPhoneError("Enter a valid 10-digit number starting with 1 (e.g. 1712345678).");
      hasError = true;
    } else {
      setPhoneError(null);
    }
    if (hasError || !packageId) return;

    setIsSubmitting(true);
    try {
      const created = await initiateCheckout({ package_id: packageId, name, email, phone });
      setIsRedirecting(true);
      window.location.href = created.payment_url;
    } catch (err) {
      setFormError(
        err instanceof StorefrontApiError ? err.message : "Something went wrong. Please try again."
      );
      setIsSubmitting(false);
    }
  }

  if (!packageId) {
    return (
      <div>
        <SiteHeader />
        <div className="min-h-[60vh] flex items-center justify-center px-4 text-center">
          <div>
            <h1 className="text-xl font-bold text-sb-ink mb-2">No course selected</h1>
            <Link
              href="/skill-bangla"
              className="inline-block bg-sb-red hover:bg-sb-red-hover text-white text-sm font-medium rounded-md px-4 py-2 transition-colors mt-4"
            >
              ← Back to all courses
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (isRedirecting) {
    return (
      <div>
        <SiteHeader />
        <div className="min-h-[60vh] flex items-center justify-center px-4 text-center text-sm text-sb-muted">
          Redirecting you to payment…
        </div>
      </div>
    );
  }

  return (
    <div>
      <SiteHeader />
      <div className="max-w-md mx-auto px-4 py-10">
        <Link href="/skill-bangla" className="text-sm text-sb-muted hover:underline">
          ← All courses
        </Link>

        <h1 className="text-xl font-bold text-sb-ink mt-4 mb-4">Checkout</h1>

        {isLoadingPkg && <p className="text-sm text-sb-muted">Loading course details…</p>}
        {pkgError && <p className="text-sm text-sb-red">{pkgError}</p>}
        {pkg && (
          <div className="bg-sb-card border border-sb-border rounded-[14px] p-4 mb-6 flex items-center justify-between gap-4">
            <p className="font-medium text-sb-ink text-sm">{pkg.title}</p>
            <p className="font-bold text-sb-ink shrink-0">{formatTaka(pkg.price_bdt)}</p>
          </div>
        )}

        {pkg && (
          <form onSubmit={handleSubmit} noValidate>
            <label className="block text-sm font-medium text-sb-ink mb-1" htmlFor="name">
              Full Name
            </label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full border border-sb-border rounded-md px-3 py-2 mb-1 text-sm focus:outline-none focus:ring-2 focus:ring-sb-blue"
            />
            {nameError && <p className="text-xs text-sb-red mb-3">{nameError}</p>}
            {!nameError && <div className="mb-3" />}

            <label className="block text-sm font-medium text-sb-ink mb-1" htmlFor="email">
              Email Address
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-sb-border rounded-md px-3 py-2 mb-1 text-sm focus:outline-none focus:ring-2 focus:ring-sb-blue"
            />
            {emailError && <p className="text-xs text-sb-red mb-3">{emailError}</p>}
            {!emailError && <div className="mb-3" />}

            <label className="block text-sm font-medium text-sb-ink mb-1" htmlFor="phone">
              Phone Number
            </label>
            <div className="flex mb-1">
              <span className="inline-flex items-center px-3 border border-r-0 border-sb-border rounded-l-md bg-sb-gray-pill text-sm text-sb-gray-pill-ink">
                +880
              </span>
              <input
                id="phone"
                type="tel"
                inputMode="numeric"
                placeholder="1712345678"
                value={phone}
                onChange={(e) => setPhone(e.target.value.replace(/\D/g, "").slice(0, 10))}
                className="w-full border border-sb-border rounded-r-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sb-blue"
              />
            </div>
            {phoneError && <p className="text-xs text-sb-red mb-3">{phoneError}</p>}
            {!phoneError && <div className="mb-3" />}

            {formError && (
              <div className="mb-4 text-sm text-sb-red bg-red-50 border border-red-200 rounded-md px-3 py-2">
                {formError}
              </div>
            )}

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-sb-red hover:bg-sb-red-hover text-white font-medium rounded-md py-2.5 text-sm transition-colors disabled:opacity-60"
            >
              {isSubmitting ? "Processing…" : "Proceed to Payment"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
