export function StatusPill({ published }: { published: boolean }) {
  if (published) {
    return (
      <span className="inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full bg-published-bg text-published">
        <span className="w-1.5 h-1.5 rounded-full bg-published" />
        Published
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full bg-unpublished-bg text-unpublished">
      <span className="w-1.5 h-1.5 rounded-full bg-unpublished" />
      Unpublished
    </span>
  );
}
