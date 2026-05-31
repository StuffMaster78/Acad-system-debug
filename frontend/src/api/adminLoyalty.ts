import { api, apiPath } from "./client";

type PageResponse<T> = { count: number; next: string | null; previous: string | null; results: T[] } | T[];

export interface LoyaltyTier {
  id: number;
  name: string;
  min_points: number;
  max_points: number | null;
  multiplier: number;
  benefits: string | null;
  is_active: boolean;
  [key: string]: unknown;
}

export interface LoyaltyTransaction {
  id: number;
  client: number;
  client_username: string | null;
  points: number;
  transaction_type: string;
  reason: string | null;
  timestamp: string;
}

export interface Milestone {
  id: number;
  name: string;
  description: string | null;
  points_required: number;
  reward_points: number;
  is_active: boolean;
  [key: string]: unknown;
}

export interface ClientBadge {
  id: number;
  client: number;
  client_username: string | null;
  badge_name: string;
  description: string | null;
  awarded_at: string;
}

export interface LoyaltyConversionConfig {
  id: number;
  website: number | null;
  conversion_rate: string;
  min_conversion_points: number;
  max_conversion_limit: number | null;
  active: boolean;
}

export interface RedemptionCategory {
  id: number;
  name: string;
  description: string | null;
  is_active: boolean;
  sort_order: number;
  created_at: string;
  items_count: number;
}

export interface RedemptionItem {
  id: number;
  category: number;
  category_name: string | null;
  name: string;
  description: string | null;
  points_required: number;
  redemption_type: string;
  discount_code: string | null;
  discount_amount: string | null;
  discount_percentage: string | null;
  stock_quantity: number | null;
  total_redemptions: number;
  max_per_client: number | null;
  min_tier_level: number | null;
  is_active: boolean;
  image_url: string | null;
  is_available: boolean;
  created_at: string;
  updated_at: string;
}

export interface RedemptionRequest {
  id: number;
  item: number;
  item_name: string | null;
  item_points: number | null;
  client: number;
  client_username: string | null;
  points_used: number;
  status: string;
  fulfillment_code: string | null;
  fulfillment_details: Record<string, unknown> | null;
  approved_by: number | null;
  approved_by_username: string | null;
  fulfilled_by: number | null;
  fulfilled_by_username: string | null;
  rejection_reason: string | null;
  requested_at: string;
  approved_at: string | null;
  fulfilled_at: string | null;
  rejected_at: string | null;
}

export const adminLoyaltyApi = {
  // ── Tiers ─────────────────────────────────────────────────────────────────
  tiers: (params?: Record<string, unknown>) =>
    api.get<PageResponse<LoyaltyTier>>(apiPath("/loyalty-management/loyalty-tiers/"), { params }),
  createTier: (payload: Partial<LoyaltyTier>) =>
    api.post<LoyaltyTier>(apiPath("/loyalty-management/loyalty-tiers/"), payload),
  updateTier: (id: number, payload: Partial<LoyaltyTier>) =>
    api.patch<LoyaltyTier>(apiPath(`/loyalty-management/loyalty-tiers/${id}/`), payload),
  deleteTier: (id: number) =>
    api.delete(apiPath(`/loyalty-management/loyalty-tiers/${id}/`)),

  // ── Transactions ───────────────────────────────────────────────────────────
  transactions: (params?: Record<string, unknown>) =>
    api.get<PageResponse<LoyaltyTransaction>>(apiPath("/loyalty-management/loyalty-transactions/"), { params }),

  // ── Milestones ─────────────────────────────────────────────────────────────
  milestones: (params?: Record<string, unknown>) =>
    api.get<PageResponse<Milestone>>(apiPath("/loyalty-management/milestones/"), { params }),
  createMilestone: (payload: Partial<Milestone>) =>
    api.post<Milestone>(apiPath("/loyalty-management/milestones/"), payload),
  updateMilestone: (id: number, payload: Partial<Milestone>) =>
    api.patch<Milestone>(apiPath(`/loyalty-management/milestones/${id}/`), payload),
  deleteMilestone: (id: number) =>
    api.delete(apiPath(`/loyalty-management/milestones/${id}/`)),

  // ── Conversion config ──────────────────────────────────────────────────────
  conversionConfigs: () =>
    api.get<PageResponse<LoyaltyConversionConfig>>(apiPath("/loyalty-management/loyalty-points-conversion-config/")),
  updateConversionConfig: (id: number, payload: Partial<LoyaltyConversionConfig>) =>
    api.patch<LoyaltyConversionConfig>(apiPath(`/loyalty-management/loyalty-points-conversion-config/${id}/`), payload),
  adminConversionConfig: () =>
    api.get<LoyaltyConversionConfig>(apiPath("/loyalty-management/admin/loyalty-conversion-config/")),
  updateAdminConversionConfig: (payload: Partial<LoyaltyConversionConfig>) =>
    api.patch<LoyaltyConversionConfig>(apiPath("/loyalty-management/admin/loyalty-conversion-config/"), payload),

  // ── Redemption catalog ─────────────────────────────────────────────────────
  redemptionCategories: (params?: Record<string, unknown>) =>
    api.get<PageResponse<RedemptionCategory>>(apiPath("/loyalty-management/redemption-categories/"), { params }),
  createCategory: (payload: Partial<RedemptionCategory>) =>
    api.post<RedemptionCategory>(apiPath("/loyalty-management/redemption-categories/"), payload),
  updateCategory: (id: number, payload: Partial<RedemptionCategory>) =>
    api.patch<RedemptionCategory>(apiPath(`/loyalty-management/redemption-categories/${id}/`), payload),
  deleteCategory: (id: number) =>
    api.delete(apiPath(`/loyalty-management/redemption-categories/${id}/`)),

  redemptionItems: (params?: Record<string, unknown>) =>
    api.get<PageResponse<RedemptionItem>>(apiPath("/loyalty-management/redemption-items/"), { params }),
  createItem: (payload: Partial<RedemptionItem>) =>
    api.post<RedemptionItem>(apiPath("/loyalty-management/redemption-items/"), payload),
  updateItem: (id: number, payload: Partial<RedemptionItem>) =>
    api.patch<RedemptionItem>(apiPath(`/loyalty-management/redemption-items/${id}/`), payload),
  deleteItem: (id: number) =>
    api.delete(apiPath(`/loyalty-management/redemption-items/${id}/`)),

  // ── Redemption requests ────────────────────────────────────────────────────
  redemptionRequests: (params?: Record<string, unknown>) =>
    api.get<PageResponse<RedemptionRequest>>(apiPath("/loyalty-management/redemption-requests/"), { params }),
  approveRedemption: (id: number) =>
    api.post<RedemptionRequest>(apiPath(`/loyalty-management/redemption-requests/${id}/approve/`), {}),
  rejectRedemption: (id: number, reason: string) =>
    api.post<RedemptionRequest>(apiPath(`/loyalty-management/redemption-requests/${id}/reject/`), { reason }),
  cancelRedemption: (id: number) =>
    api.post<RedemptionRequest>(apiPath(`/loyalty-management/redemption-requests/${id}/cancel/`), {}),

  // ── Admin point operations ─────────────────────────────────────────────────
  awardPoints: (clientId: number, points: number, reason: string, websiteId: number) =>
    api.post<{ message: string }>(apiPath("/loyalty-management/admin/award-loyalty/"), {
      client_id: clientId, points, reason, website_id: websiteId,
    }),
  deductPoints: (clientId: number, points: number, reason: string, websiteId: number) =>
    api.post<{ message: string }>(apiPath("/loyalty-management/admin/deduct-loyalty/"), {
      client_id: clientId, points, reason, website_id: websiteId,
    }),
  transferPoints: (fromClientId: number, toClientId: number, points: number, reason: string, websiteId: number) =>
    api.post<{ message: string }>(apiPath("/loyalty-management/admin/transfer-loyalty/"), {
      from_client_id: fromClientId, to_client_id: toClientId, points, reason, website_id: websiteId,
    }),
  forceConvert: (clientId: number, points: number, websiteId: number) =>
    api.post<{ message: string }>(apiPath(`/loyalty-management/admin/force-convert/${clientId}/`), {
      points, website_id: websiteId,
    }),

  // ── Analytics ──────────────────────────────────────────────────────────────
  analytics: () =>
    api.get<Record<string, unknown>>(apiPath("/loyalty-management/analytics/")),
};
