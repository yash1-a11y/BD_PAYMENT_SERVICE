"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { listLandingPages } from "@/lib/api";
import { CatalogueEntry } from "@/lib/types";
import { LandingPageForm } from "@/components/LandingPageForm";

export default function EditLandingPagePage() {
  const { token } = useAuth();
  const params = useParams<{ id: string }>();
  const router = useRouter();

  const [entry, setEntry] = useState<CatalogueEntry | null>(null);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    if (!token) return;
    listLandingPages(token).then((entries) => {
      const found = entries.find((e) => e.id === params.id);
      if (!found) {
        setNotFound(true);
      } else {
        setEntry(found);
      }
    });
  }, [token, params.id]);

  useEffect(() => {
    if (notFound) router.replace("/bd-admin/landing-pages");
  }, [notFound, router]);

  if (!entry) return null;

  return (
    <LandingPageForm
      mode="edit"
      entryId={entry.id}
      displayCode={entry.display_code}
      initialPackageId={entry.package_id}
      initialPriceBdt={entry.price_bdt}
      initialPublished={entry.published}
    />
  );
}
