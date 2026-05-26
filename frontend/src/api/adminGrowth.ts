import { api, apiPath } from "./client";

export type ListResponse<T> = T[] | { results?: T[]; items?: T[]; data?: T[]; count?: number } | Record<string, unknown>;

export interface GrowthApiRecord {
  id?: number | string;
  name?: string;
  title?: string;
  code?: string;
  status?: string;
  is_active?: boolean;
  active?: boolean;
  campaign_type?: string;
  discount_type?: string;
  value?: string | number;
  percentage?: string | number;
  amount?: string | number;
  starts_at?: string | null;
  start_date?: string | null;
  ends_at?: string | null;
  end_date?: string | null;
  date?: string | null;
  created_at?: string;
  updated_at?: string;
  [key: string]: unknown;
}

export interface DiscountSummaryResponse {
  active_discounts?: number;
  total_discounts?: number;
  expiring_soon?: number;
  unused_discounts?: number;
  total_redemptions?: number;
  revenue_impact?: string | number;
  [key: string]: unknown;
}

export interface DiscountCreatePayload {
  name: string;
  discount_code?: string;
  generate_code?: boolean;
  code_prefix?: string;
  campaign_id?: number | null;
  is_campaign_managed?: boolean;
  description?: string;
  discount_type: "percentage" | "fixed_amount";
  discount_value: string | number;
  max_discount_amount?: string | number | null;
  min_payable_amount?: string | number;
  starts_at?: string | null;
  ends_at?: string | null;
  usage_limit?: number | null;
  per_client_usage_limit?: number | null;
  first_order_only?: boolean;
  origin?: "manual" | "first_order" | "holiday" | "loyalty" | "referral" | "campaign" | "spend_tier" | "system";
  is_active?: boolean;
  eligible_client_ids?: number[];
}

export interface CampaignCreatePayload {
  name: string;
  slug?: string;
  description?: string;
  starts_at?: string | null;
  ends_at?: string | null;
  is_active?: boolean;
}

export interface DiscountClonePayload {
  source_discount_id: number;
  target_website_id: number;
  new_code?: string;
  target_campaign_id?: number | null;
}

export interface CampaignClonePayload {
  source_campaign_id: number;
  target_website_id: number;
  new_name?: string;
  new_slug?: string;
}

export const adminGrowthApi = {
  discountSummary: () =>
    api.get<DiscountSummaryResponse>(
      apiPath("/discounts/admin/dashboard/summary/"),
    ),
  workingDiscounts: () =>
    api.get<ListResponse<GrowthApiRecord>>(
      apiPath("/discounts/admin/dashboard/working/"),
    ),
  expiringDiscounts: () =>
    api.get<ListResponse<GrowthApiRecord>>(
      apiPath("/discounts/admin/dashboard/expiring-soon/"),
    ),
  topDiscounts: () =>
    api.get<ListResponse<GrowthApiRecord>>(
      apiPath("/discounts/admin/dashboard/top-performing/"),
    ),
  unusedDiscounts: () =>
    api.get<ListResponse<GrowthApiRecord>>(
      apiPath("/discounts/admin/dashboard/unused/"),
    ),
  campaigns: () =>
    api.get<ListResponse<GrowthApiRecord>>(
      apiPath("/discounts/admin/campaigns/"),
    ),
  createDiscount: (payload: DiscountCreatePayload) =>
    api.post<GrowthApiRecord>(
      apiPath("/discounts/admin/discounts/"),
      payload,
    ),
  createCampaign: (payload: CampaignCreatePayload) =>
    api.post<GrowthApiRecord>(
      apiPath("/discounts/admin/campaigns/"),
      payload,
    ),
  cloneDiscount: (payload: DiscountClonePayload) =>
    api.post<GrowthApiRecord>(
      apiPath("/discounts/admin/clone/discount/"),
      payload,
    ),
  cloneCampaign: (payload: CampaignClonePayload) =>
    api.post<GrowthApiRecord>(
      apiPath("/discounts/admin/clone/campaign/"),
      payload,
    ),
  activateCampaign: (id: number | string) =>
    api.post(apiPath(`/discounts/admin/campaigns/${id}/activate/`)),
  deactivateCampaign: (id: number | string) =>
    api.post(apiPath(`/discounts/admin/campaigns/${id}/deactivate/`)),
  referralReports: () =>
    api.get<Record<string, unknown>>(
      apiPath("/referrals/referral-reports/"),
    ),
  referralConfigs: () =>
    api.get<ListResponse<GrowthApiRecord>>(
      apiPath("/referrals/referral-bonus-configs/"),
    ),
  referralStats: () =>
    api.get<ListResponse<GrowthApiRecord>>(
      apiPath("/referrals/referral-stats/"),
    ),
  loyaltyAnalytics: () =>
    api.get<Record<string, unknown>>(
      apiPath("/loyalty-management/analytics/"),
    ),
  loyaltyTiers: () =>
    api.get<ListResponse<GrowthApiRecord>>(
      apiPath("/loyalty-management/loyalty-tiers/"),
    ),
  redemptionRequests: () =>
    api.get<ListResponse<GrowthApiRecord>>(
      apiPath("/loyalty-management/redemption-requests/"),
    ),
  holidayCampaigns: () =>
    api.get<ListResponse<GrowthApiRecord>>(
      apiPath("/holidays/campaigns/"),
    ),
  specialDays: () =>
    api.get<ListResponse<GrowthApiRecord>>(
      apiPath("/holidays/special-days/"),
    ),
};
