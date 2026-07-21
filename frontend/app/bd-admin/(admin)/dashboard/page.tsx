"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { getDashboardStats } from "@/lib/api";
import { DashboardStats } from "@/lib/types";

function formatBdt(value: string): string {
  return `${Number(value).toLocaleString("en-BD")} BDT`;
}

function StatTile({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-card border border-border rounded-lg p-5">
      <p className="text-sm text-unpublished">{label}</p>
      <p className="text-2xl font-semibold text-navy mt-2">{value}</p>
    </div>
  );
}

export default function DashboardPage() {
  const { token, role } = useAuth();
  const router = useRouter();

  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchStats = useCallback(async () => {
    if (!token) return;
    setIsLoading(true);
    try {
      setStats(await getDashboardStats(token));
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (role && role !== "SUPER_ADMIN") {
      router.replace("/bd-admin/landing-pages");
      return;
    }
    // eslint-disable-next-line react-hooks/set-state-in-effect -- initial stats fetch on mount
    fetchStats();
  }, [role, router, fetchStats]);

  if (role && role !== "SUPER_ADMIN") return null;

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-navy">Dashboard</h1>
        <p className="text-sm text-unpublished mt-1">Order and webhook activity at a glance</p>
      </div>

      {isLoading && !stats ? (
        <p className="text-sm text-unpublished">Loading...</p>
      ) : stats ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          <StatTile label="Total Orders" value={stats.total_orders} />
          <StatTile label="Paid" value={stats.paid} />
          <StatTile label="Pending" value={stats.pending} />
          <StatTile label="Failed" value={stats.failed} />
          <StatTile label="Cancelled" value={stats.cancelled} />
          <StatTile label="Guest Checkout Success" value={stats.guest_checkout_success_count} />
          <StatTile label="Guest Checkout Failure" value={stats.guest_checkout_failure_count} />
          <StatTile label="Webhook Success" value={stats.webhook_success_count} />
          <StatTile label="Webhook Failure" value={stats.webhook_failure_count} />
          <StatTile label="Revenue Today (Paid Orders Only)" value={formatBdt(stats.revenue_today_bdt)} />
          <StatTile label="Orders Today" value={stats.orders_today} />
        </div>
      ) : null}
    </div>
  );
}
