export function formatTaka(amount: string | number): string {
  const value = Math.round(Number(amount));
  return `৳ ${value.toLocaleString("en-IN")}`;
}

export function formatShortDate(iso: string): string {
  const date = new Date(`${iso}T00:00:00`);
  return date.toLocaleDateString("en-GB", { day: "numeric", month: "long" });
}

export function listingMetaLine(pkg: {
  batch_type: string;
  start_date: string | null;
  live_classes_count: number;
  video_count: number;
}): string {
  if (pkg.start_date) {
    return `${pkg.batch_type} · Starts ${formatShortDate(pkg.start_date)}`;
  }
  const parts: string[] = [];
  if (pkg.live_classes_count > 0) parts.push(`${pkg.live_classes_count} Live Classes`);
  if (pkg.video_count > 0) parts.push(`${pkg.video_count} Videos`);
  return parts.length > 0 ? parts.join(" · ") : pkg.batch_type;
}
