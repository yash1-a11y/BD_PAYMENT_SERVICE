import {
  AdminAccount,
  ApiError,
  CatalogueEntry,
  FieldError,
  PackageLookupResult,
} from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8001";

let unauthorizedHandler: (() => void) | null = null;

export function setUnauthorizedHandler(fn: () => void) {
  unauthorizedHandler = fn;
}

async function request<T>(
  path: string,
  options: { method?: string; token?: string | null; body?: unknown } = {}
): Promise<T> {
  const headers: Record<string, string> = {};
  if (options.body !== undefined) headers["Content-Type"] = "application/json";
  if (options.token) headers["Authorization"] = `Bearer ${options.token}`;

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method ?? "GET",
    headers,
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
  });

  if (response.status === 401) {
    unauthorizedHandler?.();
  }

  if (!response.ok) {
    let message = "Something went wrong. Please try again.";
    let fieldErrors: FieldError[] = [];
    try {
      const data = await response.json();
      if (Array.isArray(data.detail)) {
        fieldErrors = data.detail;
        message = fieldErrors[0]?.message ?? message;
      } else if (typeof data.detail === "string") {
        message = data.detail;
      }
    } catch {
      // response had no JSON body
    }
    throw new ApiError(response.status, message, fieldErrors);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export function login(email: string, password: string) {
  return request<{ access_token: string; token_type: string; role: string }>(
    "/bd-admin/api/auth/login",
    { method: "POST", body: { email, password } }
  );
}

export function logout(token: string) {
  return request<{ success: boolean }>("/bd-admin/api/auth/logout", {
    method: "POST",
    token,
  });
}

export function listLandingPages(token: string, search?: string) {
  const query = search ? `?search=${encodeURIComponent(search)}` : "";
  return request<CatalogueEntry[]>(`/bd-admin/api/landing-pages${query}`, { token });
}

export function lookupPackage(token: string, packageId: string) {
  return request<PackageLookupResult>(
    `/bd-admin/api/package-lookup/${encodeURIComponent(packageId)}`,
    { token }
  );
}

export function createLandingPage(
  token: string,
  payload: { package_id: string; price_bdt: number; published: boolean }
) {
  return request<CatalogueEntry>("/bd-admin/api/landing-pages", {
    method: "POST",
    token,
    body: payload,
  });
}

export function updateLandingPage(
  token: string,
  id: string,
  payload: { price_bdt: number; published: boolean }
) {
  return request<CatalogueEntry>(`/bd-admin/api/landing-pages/${id}`, {
    method: "PUT",
    token,
    body: payload,
  });
}

export function deleteLandingPage(token: string, id: string) {
  return request<void>(`/bd-admin/api/landing-pages/${id}`, { method: "DELETE", token });
}

export function publishLandingPage(token: string, id: string) {
  return request<CatalogueEntry>(`/bd-admin/api/landing-pages/${id}/publish`, {
    method: "PUT",
    token,
  });
}

export function unpublishLandingPage(token: string, id: string) {
  return request<CatalogueEntry>(`/bd-admin/api/landing-pages/${id}/unpublish`, {
    method: "PUT",
    token,
  });
}

export function reorderLandingPages(token: string, orderedIds: string[]) {
  return request<{ success: boolean }>("/bd-admin/api/landing-pages/reorder", {
    method: "PUT",
    token,
    body: { orderedIds },
  });
}

export function listAdmins(token: string) {
  return request<AdminAccount[]>("/bd-admin/api/admins", { token });
}

export function createAdmin(token: string, payload: { email: string; password: string }) {
  return request<AdminAccount>("/bd-admin/api/admins", { method: "POST", token, body: payload });
}

export function updateAdmin(token: string, id: string, payload: { email: string }) {
  return request<AdminAccount>(`/bd-admin/api/admins/${id}`, {
    method: "PUT",
    token,
    body: payload,
  });
}

export function enableAdmin(token: string, id: string) {
  return request<AdminAccount>(`/bd-admin/api/admins/${id}/enable`, { method: "PATCH", token });
}

export function disableAdmin(token: string, id: string) {
  return request<AdminAccount>(`/bd-admin/api/admins/${id}/disable`, { method: "PATCH", token });
}

export function resetAdminPassword(token: string, id: string, newPassword: string) {
  return request<AdminAccount>(`/bd-admin/api/admins/${id}/reset-password`, {
    method: "POST",
    token,
    body: { new_password: newPassword },
  });
}

export function deleteAdmin(token: string, id: string) {
  return request<void>(`/bd-admin/api/admins/${id}`, { method: "DELETE", token });
}
