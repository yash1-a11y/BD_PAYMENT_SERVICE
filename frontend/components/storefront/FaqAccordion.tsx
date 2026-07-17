"use client";

import { useState } from "react";
import { Faq } from "@/lib/storefront-types";

export function FaqAccordion({ faqs }: { faqs: Faq[] }) {
  const [openIndexes, setOpenIndexes] = useState<Set<number>>(new Set());

  function toggle(index: number) {
    setOpenIndexes((prev) => {
      const next = new Set(prev);
      if (next.has(index)) next.delete(index);
      else next.add(index);
      return next;
    });
  }

  function expandAll() {
    setOpenIndexes(new Set(faqs.map((_, i) => i)));
  }

  return (
    <div>
      <div className="flex justify-end mb-3">
        <button
          onClick={expandAll}
          className="text-sm font-medium text-sb-blue hover:underline"
        >
          Expand All Questions
        </button>
      </div>
      <div className="border border-sb-border rounded-lg divide-y divide-sb-border">
        {faqs.map((faq, index) => {
          const isOpen = openIndexes.has(index);
          return (
            <div key={index}>
              <button
                onClick={() => toggle(index)}
                className="w-full flex justify-between items-center gap-4 px-4 py-3 text-left"
              >
                <span className="text-sm font-medium text-sb-ink">
                  {index + 1}. {faq.question}
                </span>
                <span className="text-sb-muted shrink-0">{isOpen ? "▲" : "▼"}</span>
              </button>
              {isOpen && (
                <div className="px-4 pb-4 text-sm text-sb-muted">{faq.answer}</div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
