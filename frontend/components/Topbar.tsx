"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

export function Topbar() {
  const { email, role, logout } = useAuth();
  const pathname = usePathname();

  const navLinkClass = (href: string) =>
    `text-sm px-2 py-1 rounded-md transition-colors ${
      pathname.startsWith(href) ? "bg-white/15" : "hover:bg-white/10"
    }`;

  return (
    <header className="bg-navy text-white">
      <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <span className="font-bold">adda247</span>
            <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-white/10">
              BD ADMIN
            </span>
          </div>
          <nav className="flex items-center gap-1">
            <Link href="/bd-admin/landing-pages" className={navLinkClass("/bd-admin/landing-pages")}>
              Catalogue
            </Link>
            {role === "SUPER_ADMIN" && (
              <Link href="/bd-admin/admin-users" className={navLinkClass("/bd-admin/admin-users")}>
                Admin Users
              </Link>
            )}
            {role === "SUPER_ADMIN" && (
              <Link href="/bd-admin/dashboard" className={navLinkClass("/bd-admin/dashboard")}>
                Dashboard
              </Link>
            )}
          </nav>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <span className="text-white/80">{email}</span>
          <button
            onClick={logout}
            className="border border-white/30 rounded-md px-3 py-1 text-sm hover:bg-white/10 transition-colors"
          >
            Log out
          </button>
        </div>
      </div>
    </header>
  );
}
