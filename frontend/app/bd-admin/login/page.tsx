"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { ApiError } from "@/lib/types";

export default function LoginPage() {
  const { token, isLoading, login } = useAuth();
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [emailError, setEmailError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (!isLoading && token) router.replace("/bd-admin/landing-pages");
  }, [isLoading, token, router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setFormError(null);

    let hasError = false;
    if (!/^\S+@\S+\.\S+$/.test(email)) {
      setEmailError("Enter a valid email address.");
      hasError = true;
    } else {
      setEmailError(null);
    }
    if (!password) {
      setPasswordError("Password is required.");
      hasError = true;
    } else {
      setPasswordError(null);
    }
    if (hasError) return;

    setIsSubmitting(true);
    try {
      await login(email, password);
      router.replace("/bd-admin/landing-pages");
    } catch (err) {
      if (err instanceof ApiError) {
        setFormError("Email or password is incorrect. Contact the developer team if you need access.");
      } else {
        setFormError("Something went wrong. Please try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div
      className="min-h-screen flex items-center justify-center px-4"
      style={{
        background: "linear-gradient(180deg, #1A2B4A 0%, #10203C 55%, #0C1830 100%)",
      }}
    >
      <div className="w-full max-w-[400px] bg-card rounded-lg p-8">
        <div className="flex items-center gap-2 mb-2">
          <span className="font-bold text-lg text-accent">adda247</span>
          <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-unpublished-bg text-unpublished">
            BD ADMIN
          </span>
        </div>
        <p className="text-sm text-unpublished mb-6">
          Bangladesh landing page &amp; payment administration
        </p>

        <form onSubmit={handleSubmit} noValidate>
          <label className="block text-sm font-medium text-navy mb-1" htmlFor="email">
            Email
          </label>
          <input
            id="email"
            type="email"
            placeholder="you@adda247.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full border border-border rounded-md px-3 py-2 mb-1 text-sm focus:outline-none focus:ring-2 focus:ring-navy"
          />
          {emailError && <p className="text-xs text-accent mb-3">{emailError}</p>}
          {!emailError && <div className="mb-3" />}

          <label className="block text-sm font-medium text-navy mb-1" htmlFor="password">
            Password
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full border border-border rounded-md px-3 py-2 mb-1 text-sm focus:outline-none focus:ring-2 focus:ring-navy"
          />
          {passwordError && <p className="text-xs text-accent mb-3">{passwordError}</p>}
          {!passwordError && <div className="mb-3" />}

          {formError && (
            <div className="mb-4 text-sm text-accent bg-red-50 border border-red-200 rounded-md px-3 py-2">
              {formError}
            </div>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-accent hover:bg-accent-hover text-white font-medium rounded-md py-2 text-sm transition-colors disabled:opacity-60"
          >
            Sign in
          </button>
        </form>

        <div className="mt-4 text-xs text-amber-text bg-amber-bg rounded-md px-3 py-3">
          Accounts are provisioned by the developer team (manual DB entry). There is no
          self sign-up or password reset in v1 — contact tech to add a user or change a
          password.
        </div>
      </div>
    </div>
  );
}
