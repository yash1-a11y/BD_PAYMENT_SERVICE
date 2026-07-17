"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { useToast } from "@/components/Toast";
import { ConfirmModal } from "@/components/ConfirmModal";
import { CreateAdminModal } from "@/components/CreateAdminModal";
import { EditAdminModal } from "@/components/EditAdminModal";
import { ResetPasswordModal } from "@/components/ResetPasswordModal";
import { deleteAdmin, disableAdmin, enableAdmin, listAdmins } from "@/lib/api";
import { AdminAccount } from "@/lib/types";

function formatDate(iso: string | null): string {
  if (!iso) return "Never";
  return new Date(iso).toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function StatusPill({ isActive }: { isActive: boolean }) {
  if (isActive) {
    return (
      <span className="inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full bg-published-bg text-published">
        <span className="w-1.5 h-1.5 rounded-full bg-published" />
        Active
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full bg-unpublished-bg text-unpublished">
      <span className="w-1.5 h-1.5 rounded-full bg-unpublished" />
      Disabled
    </span>
  );
}

export default function AdminUsersPage() {
  const { token, role, email: currentEmail } = useAuth();
  const { showToast } = useToast();
  const router = useRouter();

  const [admins, setAdmins] = useState<AdminAccount[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [editTarget, setEditTarget] = useState<AdminAccount | null>(null);
  const [resetTarget, setResetTarget] = useState<AdminAccount | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<AdminAccount | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const fetchAdmins = useCallback(async () => {
    if (!token) return;
    setIsLoading(true);
    try {
      setAdmins(await listAdmins(token));
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (role && role !== "SUPER_ADMIN") {
      router.replace("/bd-admin/landing-pages");
      return;
    }
    // eslint-disable-next-line react-hooks/set-state-in-effect -- initial admin list fetch on mount
    fetchAdmins();
  }, [role, router, fetchAdmins]);

  async function handleToggleActive(admin: AdminAccount) {
    if (!token) return;
    if (admin.is_active) {
      await disableAdmin(token, admin.id);
      showToast("Admin disabled");
    } else {
      await enableAdmin(token, admin.id);
      showToast("Admin enabled");
    }
    fetchAdmins();
  }

  async function handleDelete() {
    if (!token || !deleteTarget) return;
    setIsDeleting(true);
    try {
      await deleteAdmin(token, deleteTarget.id);
      showToast("Admin deleted");
      setDeleteTarget(null);
      fetchAdmins();
    } finally {
      setIsDeleting(false);
    }
  }

  if (role && role !== "SUPER_ADMIN") return null;

  return (
    <div>
      <div className="flex items-start justify-between mb-6 gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-semibold text-navy">Admin users</h1>
          <p className="text-sm text-unpublished mt-1">
            {admins.length} admin{admins.length === 1 ? "" : "s"}
          </p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="bg-accent hover:bg-accent-hover text-white text-sm font-medium rounded-md px-4 py-2 whitespace-nowrap transition-colors"
        >
          + Create admin
        </button>
      </div>

      <div className="bg-card border border-border rounded-lg overflow-hidden">
        {!isLoading && admins.length === 0 ? (
          <div className="text-center py-16">
            <p className="text-navy font-medium">No admins yet</p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-page text-xs text-unpublished uppercase">
              <tr>
                <th className="text-left px-4 py-3">Email</th>
                <th className="text-left px-4 py-3">Role</th>
                <th className="text-left px-4 py-3">Status</th>
                <th className="text-left px-4 py-3">Last login</th>
                <th className="text-right px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {admins.map((admin) => {
                const isSelf = admin.email === currentEmail;
                return (
                  <tr key={admin.id} className="border-t border-border">
                    <td className="px-4 py-3 font-mono">{admin.email}</td>
                    <td className="px-4 py-3">{admin.role}</td>
                    <td className="px-4 py-3">
                      <StatusPill isActive={admin.is_active} />
                    </td>
                    <td className="px-4 py-3">{formatDate(admin.last_login_at)}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => setResetTarget(admin)}
                          className="border border-border rounded-md px-3 py-1.5 text-xs font-medium text-navy hover:bg-page transition-colors"
                        >
                          Reset password
                        </button>
                        <button
                          onClick={() => setEditTarget(admin)}
                          className="border border-border rounded-md px-3 py-1.5 text-xs font-medium text-navy hover:bg-page transition-colors"
                        >
                          Edit
                        </button>
                        {!isSelf && (
                          <>
                            <button
                              onClick={() => handleToggleActive(admin)}
                              className="border border-border rounded-md px-3 py-1.5 text-xs font-medium text-navy hover:bg-page transition-colors"
                            >
                              {admin.is_active ? "Disable" : "Enable"}
                            </button>
                            <button
                              onClick={() => setDeleteTarget(admin)}
                              className="border border-accent text-accent rounded-md px-3 py-1.5 text-xs font-medium hover:bg-red-50 transition-colors"
                            >
                              Delete
                            </button>
                          </>
                        )}
                        {isSelf && <span className="text-xs text-unpublished px-2">(you)</span>}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {showCreate && (
        <CreateAdminModal
          onClose={() => setShowCreate(false)}
          onCreated={() => {
            showToast("Admin created");
            fetchAdmins();
          }}
        />
      )}

      {editTarget && (
        <EditAdminModal
          admin={editTarget}
          onClose={() => setEditTarget(null)}
          onUpdated={() => {
            showToast("Changes saved");
            fetchAdmins();
          }}
        />
      )}

      {resetTarget && (
        <ResetPasswordModal
          admin={resetTarget}
          onClose={() => setResetTarget(null)}
          onReset={() => showToast("Password reset")}
        />
      )}

      {deleteTarget && (
        <ConfirmModal
          title="Delete admin?"
          body={<>{deleteTarget.email} will lose access immediately. This cannot be undone.</>}
          onCancel={() => setDeleteTarget(null)}
          onConfirm={handleDelete}
          isBusy={isDeleting}
        />
      )}
    </div>
  );
}
