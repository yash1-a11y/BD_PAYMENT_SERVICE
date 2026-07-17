"use client";

import { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { resetAdminPassword } from "@/lib/api";
import { AdminAccount, ApiError } from "@/lib/types";

interface Props {
  admin: AdminAccount;
  onClose: () => void;
  onReset: () => void;
}

export function ResetPasswordModal({ admin, onClose, onReset }: Props) {
  const { token } = useAuth();
  const [newPassword, setNewPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!token) return;
    setError(null);
    setIsSaving(true);
    try {
      await resetAdminPassword(token, admin.id, newPassword);
      onReset();
      onClose();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-40 px-4">
      <form onSubmit={handleSubmit} className="bg-card rounded-lg max-w-md w-full p-6">
        <h2 className="text-lg font-semibold text-navy mb-1">Reset password</h2>
        <p className="text-sm text-unpublished mb-4">{admin.email}</p>

        <label className="block text-sm font-medium text-navy mb-1">New password</label>
        <input
          type="password"
          required
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          className="w-full border border-border rounded-md px-3 py-2 text-sm mb-1 focus:outline-none focus:ring-2 focus:ring-navy"
        />
        <p className="text-xs text-unpublished mb-3">
          Relay this password to the admin out-of-band (Slack, in person, etc).
        </p>

        {error && <p className="text-sm text-accent mb-3">{error}</p>}

        <div className="flex justify-end gap-3 mt-3">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm rounded-md border border-border text-navy hover:bg-page transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSaving}
            className="px-4 py-2 text-sm rounded-md bg-accent hover:bg-accent-hover text-white transition-colors disabled:opacity-60"
          >
            Reset password
          </button>
        </div>
      </form>
    </div>
  );
}
