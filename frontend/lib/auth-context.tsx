"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import * as api from "@/lib/api";

interface AuthContextValue {
  token: string | null;
  email: string | null;
  role: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const TOKEN_KEY = "bd_admin_token";
const EMAIL_KEY = "bd_admin_email";
const ROLE_KEY = "bd_admin_role";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [email, setEmail] = useState<string | null>(null);
  const [role, setRole] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- hydration-safe read of localStorage, unavailable during SSR
    setToken(localStorage.getItem(TOKEN_KEY));
    setEmail(localStorage.getItem(EMAIL_KEY));
    setRole(localStorage.getItem(ROLE_KEY));
    setIsLoading(false);
  }, []);

  useEffect(() => {
    api.setUnauthorizedHandler(() => {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(EMAIL_KEY);
      localStorage.removeItem(ROLE_KEY);
      setToken(null);
      setEmail(null);
      setRole(null);
      router.replace("/bd-admin/login");
    });
  }, [router]);

  async function login(loginEmail: string, password: string) {
    const result = await api.login(loginEmail, password);
    localStorage.setItem(TOKEN_KEY, result.access_token);
    localStorage.setItem(EMAIL_KEY, loginEmail);
    localStorage.setItem(ROLE_KEY, result.role);
    setToken(result.access_token);
    setEmail(loginEmail);
    setRole(result.role);
  }

  function logout() {
    if (token) {
      api.logout(token).catch(() => {});
    }
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(EMAIL_KEY);
    localStorage.removeItem(ROLE_KEY);
    setToken(null);
    setEmail(null);
    setRole(null);
    router.replace("/bd-admin/login");
  }

  return (
    <AuthContext.Provider value={{ token, email, role, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
