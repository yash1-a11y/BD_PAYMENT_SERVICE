"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

export default function BdAdminRootPage() {
  const { token, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isLoading) return;
    router.replace(token ? "/bd-admin/landing-pages" : "/bd-admin/login");
  }, [isLoading, token, router]);

  return null;
}
