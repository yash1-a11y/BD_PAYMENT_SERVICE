"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { formatTaka } from "@/lib/storefront-format";

const COMPACT_BAR_HEIGHT = 96;

interface Tab {
  id: string;
  label: string;
}

interface CompactBarInfo {
  packageId: string;
  title: string;
  thumbnailUrl: string | null;
  priceBdt: string;
  planTitle: string | null;
}

export function PdpStickyChrome({ tabs, buyBar }: { tabs: Tab[]; buyBar: CompactBarInfo }) {
  const [compactVisible, setCompactVisible] = useState(false);
  const [activeTab, setActiveTab] = useState(tabs[0]?.id);
  const sentinelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = sentinelRef.current;
    if (!el) return;
    // isIntersecting is false both "not yet scrolled to" (below the fold) and
    // "scrolled past" (above the viewport) — only the latter should show the
    // compact bar, so also check that the sentinel's top has gone negative.
    const observer = new IntersectionObserver(([entry]) => {
      setCompactVisible(!entry.isIntersecting && entry.boundingClientRect.top < 0);
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (tabs.length === 0) return;
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter((e) => e.isIntersecting);
        if (visible.length > 0) {
          const topMost = visible.reduce((a, b) => (a.boundingClientRect.top < b.boundingClientRect.top ? a : b));
          setActiveTab(topMost.target.id);
        }
      },
      { rootMargin: "-120px 0px -70% 0px", threshold: 0 }
    );
    tabs.forEach((tab) => {
      const el = document.getElementById(tab.id);
      if (el) observer.observe(el);
    });
    return () => observer.disconnect();
  }, [tabs]);

  return (
    <>
      <div ref={sentinelRef} />

      {compactVisible && (
        <div
          className="hidden md:flex fixed top-0 left-0 right-0 z-30 bg-sb-card border-b border-sb-border items-center gap-4 px-6"
          style={{ height: COMPACT_BAR_HEIGHT }}
        >
          <div className="w-16 h-16 rounded-md bg-sb-gray-pill overflow-hidden shrink-0">
            {buyBar.thumbnailUrl && (
              // eslint-disable-next-line @next/next/no-img-element -- hotlinked external CDN image
              <img
                src={buyBar.thumbnailUrl}
                alt={buyBar.title}
                className="w-full h-full object-cover"
              />
            )}
          </div>
          <div className="min-w-0 flex-1">
            <p className="font-bold text-sb-ink text-lg truncate">{buyBar.title}</p>
            {buyBar.planTitle && (
              <p className="text-sm text-sb-muted">
                Plan Selected: <span className="font-medium">{buyBar.planTitle}</span>
              </p>
            )}
          </div>
          <p className="text-2xl font-bold text-sb-ink shrink-0">{formatTaka(buyBar.priceBdt)}</p>
          <Link
            href={`/skill-bangla/checkout?packageId=${encodeURIComponent(buyBar.packageId)}`}
            className="shrink-0 bg-sb-red hover:bg-sb-red-hover text-white font-medium rounded-md px-6 py-3 transition-colors"
          >
            BUY NOW
          </Link>
        </div>
      )}

      {tabs.length > 0 && (
        <div
          className="sticky z-20 bg-sb-card border-y border-sb-border overflow-x-auto"
          style={{ top: compactVisible ? COMPACT_BAR_HEIGHT : 0 }}
        >
          <div className="flex justify-start md:justify-center gap-6 px-1 max-w-6xl mx-auto">
            {tabs.map((tab) => {
              const isActive = activeTab === tab.id;
              return (
                <a
                  key={tab.id}
                  href={`#${tab.id}`}
                  className={`py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
                    isActive
                      ? "text-sb-red border-sb-red"
                      : "text-sb-muted border-transparent hover:text-sb-red hover:border-sb-red"
                  }`}
                >
                  {tab.label}
                </a>
              );
            })}
          </div>
        </div>
      )}
    </>
  );
}
