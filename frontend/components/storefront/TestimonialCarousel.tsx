"use client";

import { useRef, useState } from "react";
import { Testimonial } from "@/lib/storefront-types";

export function TestimonialCarousel({ testimonials }: { testimonials: Testimonial[] }) {
  const scrollerRef = useRef<HTMLDivElement>(null);
  const [atStart, setAtStart] = useState(true);
  const [atEnd, setAtEnd] = useState(testimonials.length <= 2);

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
        {testimonials.map((testimonial) => (
          <div
            key={testimonial.name}
            className="shrink-0 grow-0 basis-full sm:basis-[calc((100%-1rem)/2)] snap-start border border-sb-border rounded-[14px] p-4"
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-full bg-sb-gray-pill overflow-hidden shrink-0">
                {testimonial.image && (
                  // eslint-disable-next-line @next/next/no-img-element -- hotlinked external CDN image
                  <img
                    src={testimonial.image}
                    alt={testimonial.name}
                    className="w-full h-full object-cover"
                  />
                )}
              </div>
              <div>
                <p className="font-bold text-sb-ink text-sm">{testimonial.name}</p>
                {testimonial.rating > 0 && (
                  <p
                    className="text-amber-500 text-sm"
                    aria-label={`${testimonial.rating} out of 5 stars`}
                  >
                    {"★".repeat(testimonial.rating)}
                    {"☆".repeat(Math.max(0, 5 - testimonial.rating))}
                  </p>
                )}
              </div>
            </div>
            <p className="text-sm text-sb-ink">{testimonial.description}</p>
          </div>
        ))}
      </div>

      {!atStart && (
        <button
          onClick={() => scrollByOnePage(-1)}
          aria-label="Previous testimonials"
          className="hidden md:flex absolute top-1/2 -left-5 -translate-y-1/2 w-9 h-9 rounded-full border border-sb-blue bg-sb-card text-sb-blue items-center justify-center shadow-sm hover:bg-sb-blue-bg"
        >
          ‹
        </button>
      )}
      {!atEnd && (
        <button
          onClick={() => scrollByOnePage(1)}
          aria-label="More testimonials"
          className="hidden md:flex absolute top-1/2 -right-5 -translate-y-1/2 w-9 h-9 rounded-full border border-sb-blue bg-sb-card text-sb-blue items-center justify-center shadow-sm hover:bg-sb-blue-bg"
        >
          ›
        </button>
      )}
    </div>
  );
}
