"use client";

import { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { createAdmin } from "@/lib/api";
import { AdminAccount, ApiError } from "@/lib/types";

interface Props {
  onClose: () => void;
  onCreated: (admin: AdminAccount) => void;
}

export function CreateAdminModal({ onClose, onCreated }: Props) {
  const { token } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!token) return;
    setError(null);
    setIsSaving(true);
    try {
      const admin = await createAdmin(token, { email, password });
      onCreated(admin);
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
        <h2 className="text-lg font-semibold text-navy mb-4">Create admin</h2>

        <label className="block text-sm font-medium text-navy mb-1">Email</label>
        <input
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full border border-border rounded-md px-3 py-2 text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-navy"
        />

        <label className="block text-sm font-medium text-navy mb-1">Initial password</label>
        <input
          type="password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full border border-border rounded-md px-3 py-2 text-sm mb-1 focus:outline-none focus:ring-2 focus:ring-navy"
        />
        <p className="text-xs text-unpublished mb-3">
          New accounts are always created with the ADMIN role.
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
            Create
          </button>
        </div>
      </form>
    </div>
  );
}
