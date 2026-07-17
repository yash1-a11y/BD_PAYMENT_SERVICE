"use client";

import { useRef, useState } from "react";
import { Faculty } from "@/lib/storefront-types";

export function FacultyCarousel({ faculties }: { faculties: Faculty[] }) {
  const scrollerRef = useRef<HTMLDivElement>(null);
  const [atStart, setAtStart] = useState(true);
  const [atEnd, setAtEnd] = useState(faculties.length <= 3);

  function updateEdges() {
    const el = scrollerRef.current;
    if (!el) return;
    setAtStart(el.scrollLeft <= 0);
    setAtEnd(el.scrollLeft + el.clientWidth >= el.scrollWidth - 1);
  }

  function scrollByOnePage(direction: 1 | -1) {
    const el = scrollerRef.current;
    if (!el) return;
    el.scrollBy({ left: direction * el.clientWidth, behavior: "smooth" });
  }

  return (
    <div className="relative">
      <div
        ref={scrollerRef}
        onScroll={updateEdges}
        className="flex gap-4 overflow-x-auto scroll-smooth snap-x snap-mandatory [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]"
      >
        {faculties.map((faculty) => (
          <div
            key={faculty.name}
            className="shrink-0 grow-0 basis-full sm:basis-[calc((100%-2rem)/3)] snap-start border border-sb-border rounded-[14px] p-4"
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="w-12 h-12 rounded-full bg-sb-gray-pill overflow-hidden shrink-0">
                {faculty.image && (
                  // eslint-disable-next-line @next/next/no-img-element -- hotlinked external CDN image
                  <img
                    src={faculty.image}
                    alt={faculty.name}
                    className="w-full h-full object-cover"
                  />
                )}
              </div>
              <div>
                <p className="font-bold text-sb-ink text-sm">{faculty.name}</p>
                {faculty.subject && (
                  <p className="text-xs text-sb-muted uppercase">{faculty.subject}</p>
                )}
              </div>
            </div>
            {faculty.demo_url && (
              <a
                href={faculty.demo_url}
                target="_blank"
                rel="noreferrer"
                className="text-xs font-medium text-sb-blue hover:underline"
              >
                ▶ Play Demo
              </a>
            )}
            <ul className="mt-2 space-y-1">
              {faculty.experience_years && (
                <li className="flex gap-2 text-xs text-sb-ink">
                  <span className="text-sb-green shrink-0">✓</span>
                  <span>{faculty.experience_years}+ years of Experience</span>
                </li>
              )}
              {faculty.students_mentored > 0 && (
                <li className="flex gap-2 text-xs text-sb-ink">
                  <span className="text-sb-green shrink-0">✓</span>
                  <span>
                    More than {faculty.students_mentored.toLocaleString("en-IN")} Aspirants Mentored
                  </span>
                </li>
              )}
              {faculty.quote && (
                <li className="flex gap-2 text-xs text-sb-ink">
                  <span className="text-sb-green shrink-0">✓</span>
                  <span>{faculty.quote}</span>
                </li>
              )}
            </ul>
          </div>
        ))}
      </div>

      {!atStart && (
        <button
          onClick={() => scrollByOnePage(-1)}
          aria-label="Previous faculty"
          className="hidden md:flex absolute top-1/2 -left-5 -translate-y-1/2 w-9 h-9 rounded-full border border-sb-blue bg-sb-card text-sb-blue items-center justify-center shadow-sm hover:bg-sb-blue-bg"
        >
          ‹
        </button>
      )}
      {!atEnd && (
        <button
          onClick={() => scrollByOnePage(1)}
          aria-label="More faculty"
          className="hidden md:flex absolute top-1/2 -right-5 -translate-y-1/2 w-9 h-9 rounded-full border border-sb-blue bg-sb-card text-sb-blue items-center justify-center shadow-sm hover:bg-sb-blue-bg"
        >
          ›
        </button>
      )}
    </div>
  );
}
