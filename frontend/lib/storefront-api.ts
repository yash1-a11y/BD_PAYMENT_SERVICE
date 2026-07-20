import { Order, OrderCreatePayload, PackageListing, PackagePdp } from "@/lib/storefront-types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class StorefrontApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(
  path: string,
  options: { method?: string; body?: unknown } = {}
): Promise<T> {
  const headers: Record<string, string> = {};
  if (options.body !== undefined) headers["Content-Type"] = "application/json";

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method ?? "GET",
    headers,
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    cache: "no-store",
  });

  if (!response.ok) {
    let message = "Something went wrong. Please try again.";
    try {
      const data = await response.json();
      if (typeof data.detail === "string") message = data.detail;
    } catch {
      // response had no JSON body
    }
    throw new StorefrontApiError(response.status, message);
  }

  return response.json() as Promise<T>;
}

export function listPackages() {
  return request<PackageListing[]>("/api/bd/packages");
}

export function getPackage(packageId: string) {
  return request<PackagePdp>(`/api/bd/packages/${encodeURIComponent(packageId)}`);
}

export function initiateCheckout(payload: OrderCreatePayload) {
  return request<Order>("/api/bd/checkout/initiate", { method: "POST", body: payload });
}
