import type { UserRole } from "@/types/roles";

export interface SuperadminMetric {
  label: string;
  value: string;
  detail: string;
  tone: "neutral" | "good" | "warn" | "risk";
}

export interface SuperadminDashboardStats {
  total_users?: number;
  active_users?: number;
  suspended_users?: number;
  total_admins?: number;
  total_support?: number;
  total_editors?: number;
  total_writers?: number;
  total_clients?: number;
  total_revenue?: string | number;
  completed_payments?: string | number;
  pending_payouts?: string | number;
  failed_payments?: number;
  total_refunds?: string | number;
  total_orders?: number;
  in_progress?: number;
  completed?: number;
  disputed?: number;
  canceled?: number;
  total_disputes?: number;
  pending_disputes?: number;
  resolved_disputes?: number;
  total_tickets?: number;
  open_tickets?: number;
  closed_tickets?: number;
  recent_orders?: Array<Record<string, unknown>>;
  top_writers?: Array<Record<string, unknown>>;
  top_clients?: Array<Record<string, unknown>>;
  website_stats?: TenantSummary[];
  revenue_trends?: Array<{ date?: string | null; revenue?: number | string; order_count?: number }>;
  system_health?: {
    orders_last_24h?: number;
    orders_last_7d?: number;
    new_users_last_24h?: number;
    new_users_last_7d?: number;
    overdue_orders?: number;
    unassigned_orders?: number;
  };
}

export interface TenantSummary {
  id: number;
  name?: string;
  domain?: string;
  slug?: string;
  is_active?: boolean;
  is_deleted?: boolean;
  order_count?: number;
  user_count?: number;
  total_revenue?: string | number;
  recent_orders_30d?: number;
  new_users_30d?: number;
  avg_order_value?: string | number;
  metrics?: {
    users?: { total?: number; new_this_period?: number };
    orders?: { total?: number; completed?: number; completion_rate?: number; avg_order_value?: string | number };
    revenue?: { total?: string | number; avg_per_order?: string | number };
    disputes?: { total?: number; resolution_rate?: number };
    support?: { total_tickets?: number; resolution_rate?: number };
  };
}

export interface TenantListResponse {
  tenants: TenantSummary[];
  count: number;
  summary?: {
    total_tenants?: number;
    active_tenants?: number;
    inactive_tenants?: number;
    deleted_tenants?: number;
  };
}

export interface TenantComparisonResponse {
  tenants: TenantSummary[];
  count: number;
}

export interface CrossTenantAnalyticsResponse {
  summary?: {
    total_tenants?: number;
    active_tenants?: number;
    total_revenue?: string | number;
    total_orders?: number;
    total_users?: number;
    total_disputes?: number;
    total_tickets?: number;
  };
  tenants?: TenantSummary[];
  top_performers?: {
    by_revenue?: TenantSummary[];
    by_orders?: TenantSummary[];
  };
  period?: {
    days?: number;
    from?: string;
    to?: string;
  };
}

export interface SuperadminUser {
  id: number;
  username: string;
  email: string;
  role: UserRole | string;
  is_suspended?: boolean;
  is_on_probation?: boolean;
  date_joined?: string;
}

export interface SuperadminLog {
  id: number;
  superadmin?: string;
  action_type?: string;
  action_details?: string;
  timestamp?: string;
  formatted_timestamp?: string;
}

export interface TenantStaffMember {
  id: number;
  user_id: number;
  username: string;
  email: string;
  role: string;
  joined_at: string;
}

export interface TenantBillingPlan {
  name: string;
  price_per_month: number | null;
  features: string[];
}

export interface TenantDetail extends TenantSummary {
  slug: string;
  billing_email: string | null;
  support_email: string | null;
  writer_count: number;
  client_count: number;
  admin_count: number;
  plan: TenantBillingPlan;
  feature_flags: Record<string, boolean>;
  allowed_subjects: string[];
  staff: TenantStaffMember[];
  recent_orders: Array<Record<string, unknown>>;
  created_at: string;
  updated_at: string;
  suspended_at: string | null;
  suspension_reason: string | null;
}

export interface TenantCreatePayload {
  name: string;
  domain: string;
  slug: string;
  billing_email?: string;
  support_email?: string;
  plan_name?: string;
}

export interface TenantUpdatePayload {
  name?: string;
  domain?: string;
  billing_email?: string;
  support_email?: string;
  feature_flags?: Record<string, boolean>;
  allowed_subjects?: string[];
}

export interface SuperadminAppeal {
  id: number;
  user?: number;
  user_username?: string;
  user_email?: string;
  appeal_type?: string;
  status?: string;
  reason?: string;
  submitted_at?: string;
  reviewed_by_username?: string;
}
