export interface CatalogueEntry {
  id: string;
  display_code: string;
  package_id: string;
  price_bdt: string;
  published: boolean;
  display_order: number;
  created_at: string;
  updated_at: string;
  title: string | null;
  category: string | null;
  validity_months: number | null;
}

export interface PackageLookupResult {
  package_id: string;
  title: string;
  category: string;
  validity_months: number | null;
  thumbnail_url: string | null;
  india_mrp: number | null;
  source_published: boolean;
}

export interface FieldError {
  field: string;
  message: string;
}

export interface AdminAccount {
  id: string;
  email: string;
  role: "SUPER_ADMIN" | "ADMIN";
  is_active: boolean;
  created_at: string;
  last_login_at: string | null;
}

export interface DashboardStats {
  total_orders: number;
  paid: number;
  pending: number;
  failed: number;
  cancelled: number;
  guest_checkout_success_count: number;
  guest_checkout_failure_count: number;
  webhook_success_count: number;
  webhook_failure_count: number;
  orders_today: number;
  revenue_today_bdt: string;
}

export class ApiError extends Error {
  status: number;
  fieldErrors: FieldError[];

  constructor(status: number, message: string, fieldErrors: FieldError[] = []) {
    super(message);
    this.status = status;
    this.fieldErrors = fieldErrors;
  }

  fieldMessage(field: string): string | undefined {
    return this.fieldErrors.find((e) => e.field === field)?.message;
  }
}
