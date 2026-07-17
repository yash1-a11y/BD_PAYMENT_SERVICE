import Link from "next/link";

export default function SkillBanglaNotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4 text-center">
      <div>
        <h1 className="text-xl font-bold text-sb-ink mb-2">
          This course isn&apos;t available right now
        </h1>
        <p className="text-sm text-sb-muted mb-6">
          It may have been unpublished or the link may be incorrect.
        </p>
        <Link
          href="/skill-bangla"
          className="inline-block bg-sb-red hover:bg-sb-red-hover text-white text-sm font-medium rounded-md px-4 py-2 transition-colors"
        >
          ← Back to all courses
        </Link>
      </div>
    </div>
  );
}
