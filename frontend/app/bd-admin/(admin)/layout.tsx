"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { Topbar } from "@/components/Topbar";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const { token, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !token) router.replace("/bd-admin/login");
  }, [isLoading, token, router]);

  if (isLoading || !token) return null;

  return (
    <div className="min-h-screen bg-page flex flex-col">
      <Topbar />
      <main className="flex-1 max-w-6xl mx-auto w-full px-6 py-8">{children}</main>
    </div>
  );
}
