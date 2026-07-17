"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { useToast } from "@/components/Toast";
import { StatusPill } from "@/components/StatusPill";
import { ConfirmModal } from "@/components/ConfirmModal";
import {
  deleteLandingPage,
  listLandingPages,
  publishLandingPage,
  reorderLandingPages,
  unpublishLandingPage,
} from "@/lib/api";
import { CatalogueEntry } from "@/lib/types";

function formatPrice(price: string): string {
  const value = Number(price);
  return `৳ ${value.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

export default function LandingPagesListPage() {
  const { token } = useAuth();
  const { showToast } = useToast();

  const [entries, setEntries] = useState<CatalogueEntry[]>([]);
  const [search, setSearch] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [pendingDelete, setPendingDelete] = useState<CatalogueEntry | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const fetchEntries = useCallback(
    async (searchTerm: string) => {
      if (!token) return;
      setIsLoading(true);
      try {
        const data = await listLandingPages(token, searchTerm || undefined);
        setEntries(data);
      } finally {
        setIsLoading(false);
      }
    },
    [token]
  );

  useEffect(() => {
    const timeout = setTimeout(() => fetchEntries(search), 250);
    return () => clearTimeout(timeout);
  }, [search, fetchEntries]);

  async function handleTogglePublish(entry: CatalogueEntry) {
    if (!token) return;
    if (entry.published) {
      await unpublishLandingPage(token, entry.id);
      showToast("Unpublished — removed from the BD landing page");
    } else {
      await publishLandingPage(token, entry.id);
      showToast("Published — live on the BD landing page");
    }
    fetchEntries(search);
  }

  async function handleDelete() {
    if (!token || !pendingDelete) return;
    setIsDeleting(true);
    try {
      await deleteLandingPage(token, pendingDelete.id);
      showToast("Landing page deleted");
      setPendingDelete(null);
      fetchEntries(search);
    } finally {
      setIsDeleting(false);
    }
  }

  async function handleMove(index: number, direction: -1 | 1) {
    if (!token) return;
    const targetIndex = index + direction;
    if (targetIndex < 0 || targetIndex >= entries.length) return;

    const reordered = [...entries];
    [reordered[index], reordered[targetIndex]] = [reordered[targetIndex], reordered[index]];
    setEntries(reordered);
    await reorderLandingPages(token, reordered.map((e) => e.id));
    fetchEntries(search);
  }

  const liveCount = entries.filter((e) => e.published).length;

  return (
    <div>
      <div className="flex items-start justify-between mb-6 gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-semibold text-navy">Landing pages</h1>
          <p className="text-sm text-unpublished mt-1">
            {entries.length} landing page{entries.length === 1 ? "" : "s"} · {liveCount} live
            on the BD page
          </p>
        </div>
        <div className="flex items-center gap-3">
          <input
            type="text"
            placeholder="Search by package ID or title"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="border border-border rounded-md px-3 py-2 text-sm w-64 focus:outline-none focus:ring-2 focus:ring-navy"
          />
          <Link
            href="/bd-admin/landing-pages/new"
            className="bg-accent hover:bg-accent-hover text-white text-sm font-medium rounded-md px-4 py-2 whitespace-nowrap transition-colors"
          >
            + Create landing page
          </Link>
        </div>
      </div>

      <div className="bg-card border border-border rounded-lg overflow-hidden">
        {!isLoading && entries.length === 0 ? (
          <div className="text-center py-16">
            <p className="text-navy font-medium">No landing pages yet</p>
            <p className="text-sm text-unpublished mt-1">
              Create your first landing page to list a package for Bangladesh.
            </p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-page text-xs text-unpublished uppercase">
              <tr>
                <th className="text-left px-4 py-3">LP ID</th>
                <th className="text-left px-4 py-3">Package ID</th>
                <th className="text-left px-4 py-3">Package</th>
                <th className="text-left px-4 py-3">Price (BDT)</th>
                <th className="text-left px-4 py-3">Status</th>
                <th className="text-left px-4 py-3">Last updated</th>
                <th className="text-right px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry, index) => (
                <tr key={entry.id} className="border-t border-border">
                  <td className="px-4 py-3 font-mono">{entry.display_code}</td>
                  <td className="px-4 py-3 font-mono">{entry.package_id}</td>
                  <td className="px-4 py-3">
                    <div className="font-semibold text-navy">
                      {entry.title ?? entry.package_id}
                    </div>
                    {entry.category && (
                      <div className="text-xs text-unpublished mt-0.5">
                        {entry.category}
                        {entry.validity_months ? ` · Validity ${entry.validity_months} months` : ""}
                      </div>
                    )}
                  </td>
                  <td className="px-4 py-3 font-mono">{formatPrice(entry.price_bdt)}</td>
                  <td className="px-4 py-3">
                    <StatusPill published={entry.published} />
                  </td>
                  <td className="px-4 py-3">{formatDate(entry.updated_at)}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-end gap-2">
                      <div className="flex flex-col mr-1">
                        <button
                          aria-label="Move up"
                          onClick={() => handleMove(index, -1)}
                          disabled={index === 0}
                          className="text-unpublished disabled:opacity-30 leading-none"
                        >
                          ▲
                        </button>
                        <button
                          aria-label="Move down"
                          onClick={() => handleMove(index, 1)}
                          disabled={index === entries.length - 1}
                          className="text-unpublished disabled:opacity-30 leading-none"
                        >
                          ▼
                        </button>
                      </div>
                      <button
                        onClick={() => handleTogglePublish(entry)}
                        className="border border-border rounded-md px-3 py-1.5 text-xs font-medium text-navy hover:bg-page transition-colors"
                      >
                        {entry.published ? "Unpublish" : "Publish"}
                      </button>
                      <Link
                        href={`/bd-admin/landing-pages/${entry.id}/edit`}
                        className="border border-border rounded-md px-3 py-1.5 text-xs font-medium text-navy hover:bg-page transition-colors"
                      >
                        Edit
                      </Link>
                      <button
                        onClick={() => setPendingDelete(entry)}
                        className="border border-accent text-accent rounded-md px-3 py-1.5 text-xs font-medium hover:bg-red-50 transition-colors"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {pendingDelete && (
        <ConfirmModal
          title="Delete landing page?"
          body={
            <>
              {pendingDelete.display_code} — &quot;{pendingDelete.title ?? pendingDelete.package_id}
              &quot; (package {pendingDelete.package_id}) will be removed from the admin and
              delisted from the BD landing page. Customers who already purchased keep their
              course access. This cannot be undone.
            </>
          }
          onCancel={() => setPendingDelete(null)}
          onConfirm={handleDelete}
          isBusy={isDeleting}
        />
      )}
    </div>
  );
}
