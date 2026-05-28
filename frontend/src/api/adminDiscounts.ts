import { api, apiPath } from "./client";

const base = (path: string) => apiPath(`/discounts${path}`);

// ── Interfaces ──────────────────────────────────────────────────────────────

export interface DiscountCampaign {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  starts_at: string | null;
  ends_at: string | null;
  is_active: boolean;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface Discount {
  id: number;
  campaign: DiscountCampaign | null;
  campaign_id: number | null;
  is_campaign_managed: boolean;
  discount_code: string;
  name: string;
  description: string | null;
  discount_type: string;
  discount_value: string;
  max_discount_amount: string | null;
  min_payable_amount: string;
  starts_at: string | null;
  ends_at: string | null;
  usage_limit: number | null;
  per_client_usage_limit: number | null;
  first_order_only: boolean;
  origin: string;
  is_active: boolean;
  is_archived: boolean;
  is_deleted: boolean;
  usage_count: number;
  distinct_clients: number;
  total_discount_given: string;
  created_at: string;
  updated_at: string;
}

export interface AdminCampaign {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  starts_at: string | null;
  ends_at: string | null;
  is_active: boolean;
  is_archived: boolean;
  discount_count: number;
  usage_count: number;
  distinct_clients: number;
  total_discount_given: string;
  created_at: string;
  updated_at: string;
}

export interface SpendTier {
  id: number;
  name: string;
  minimum_lifetime_spend: string;
  is_active: boolean;
  discount: Discount;
  created_at: string;
  updated_at: string;
}

export interface DiscountSettings {
  id: number;
  allow_manual_codes: boolean;
  auto_apply_first_order_discount: boolean;
  allow_code_to_replace_first_order: boolean;
  auto_apply_best_discount: boolean;
  allow_discounts_on_orders: boolean;
  allow_discounts_on_special_orders: boolean;
  allow_discounts_on_class_bundles: boolean;
  require_admin_approval_for_campaigns: boolean;
  notify_admins_on_large_discount: boolean;
  large_discount_threshold: string;
  created_at: string;
  updated_at: string;
}

export interface FirstOrderConfig {
  id: number;
  is_enabled: boolean;
  discount_type: string;
  discount_value: string;
  max_discount_amount: string | null;
  min_payable_amount: string;
  applies_to_orders: boolean;
  applies_to_special_orders: boolean;
  applies_to_class_bundles: boolean;
  created_at: string;
  updated_at: string;
}

export interface DashboardSummary {
  total_discounts: number;
  working_discounts: number;
  scheduled_discounts: number;
  expired_discounts: number;
  archived_discounts: number;
  total_redemptions: number;
  total_discount_given: string;
  distinct_clients: number;
}

export interface DiscountOriginGroup {
  origin: string;
  total: number;
}

// ── API ─────────────────────────────────────────────────────────────────────

export const adminDiscountsApi = {
  // ── Dashboard ───────────────────────────────────────────────────────────────
  dashboardSummary: () =>
    api.get<DashboardSummary>(base("/admin/dashboard/summary/")),
  dashboardWorking: () =>
    api.get<Discount[]>(base("/admin/dashboard/working/")),
  dashboardExpiringSoon: (days = 7) =>
    api.get<Discount[]>(base("/admin/dashboard/expiring-soon/"), { params: { days } }),
  dashboardTopPerforming: (limit = 10) =>
    api.get<Discount[]>(base("/admin/dashboard/top-performing/"), { params: { limit } }),
  dashboardUnused: () =>
    api.get<Discount[]>(base("/admin/dashboard/unused/")),
  dashboardByOrigin: () =>
    api.get<DiscountOriginGroup[]>(base("/admin/dashboard/by-origin/")),

  // ── Discounts ────────────────────────────────────────────────────────────────
  discounts: (params?: Record<string, unknown>) =>
    api.get<Discount[]>(base("/admin/discounts/"), { params }),
  createDiscount: (payload: Record<string, unknown>) =>
    api.post<Discount>(base("/admin/discounts/"), payload),
  discountDetail: (id: number) =>
    api.get<Discount>(base(`/admin/discounts/${id}/`)),
  updateDiscount: (id: number, payload: Record<string, unknown>) =>
    api.patch<Discount>(base(`/admin/discounts/${id}/`), payload),
  archiveDiscount: (id: number) =>
    api.post<Discount>(base(`/admin/discounts/${id}/archive/`), {}),
  restoreDiscount: (id: number) =>
    api.post<Discount>(base(`/admin/discounts/${id}/restore/`), {}),

  // ── Campaigns ───────────────────────────────────────────────────────────────
  campaigns: () =>
    api.get<{ campaigns: AdminCampaign[] }>(base("/admin/campaigns/")),
  createCampaign: (payload: Record<string, unknown>) =>
    api.post<AdminCampaign>(base("/admin/campaigns/"), payload),
  campaignDetail: (id: number) =>
    api.get<AdminCampaign>(base(`/admin/campaigns/${id}/`)),
  updateCampaign: (id: number, payload: Record<string, unknown>) =>
    api.patch<AdminCampaign>(base(`/admin/campaigns/${id}/`), payload),
  activateCampaign: (id: number) =>
    api.post<AdminCampaign>(base(`/admin/campaigns/${id}/activate/`), {}),
  deactivateCampaign: (id: number) =>
    api.post<AdminCampaign>(base(`/admin/campaigns/${id}/deactivate/`), {}),
  archiveCampaign: (id: number) =>
    api.post<AdminCampaign>(base(`/admin/campaigns/${id}/archive/`), {}),
  restoreCampaign: (id: number) =>
    api.post<AdminCampaign>(base(`/admin/campaigns/${id}/restore/`), {}),

  // ── Spend tiers ─────────────────────────────────────────────────────────────
  spendTiers: () =>
    api.get<{ spend_tiers: SpendTier[] }>(base("/admin/spend-tiers/")),
  createSpendTier: (payload: Record<string, unknown>) =>
    api.post<SpendTier>(base("/admin/spend-tiers/"), payload),
  updateSpendTier: (id: number, payload: Record<string, unknown>) =>
    api.patch<SpendTier>(base(`/admin/spend-tiers/${id}/`), payload),

  // ── Clone ───────────────────────────────────────────────────────────────────
  cloneDiscount: (payload: { source_discount_id: number; target_website_id: number; new_code?: string; target_campaign_id?: number }) =>
    api.post<Discount>(base("/admin/clone/discount/"), payload),
  cloneCampaign: (payload: { source_campaign_id: number; target_website_id: number; new_name?: string; new_slug?: string }) =>
    api.post<DiscountCampaign>(base("/admin/clone/campaign/"), payload),

  // ── Settings ────────────────────────────────────────────────────────────────
  settings: () =>
    api.get<DiscountSettings>(base("/admin/settings/")),
  updateSettings: (payload: Partial<DiscountSettings>) =>
    api.patch<DiscountSettings>(base("/admin/settings/"), payload),
  firstOrderConfig: () =>
    api.get<FirstOrderConfig>(base("/admin/first-order-config/")),
  updateFirstOrderConfig: (payload: Partial<FirstOrderConfig>) =>
    api.patch<FirstOrderConfig>(base("/admin/first-order-config/"), payload),
};
