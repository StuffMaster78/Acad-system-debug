import { api, apiPath } from "./client";

export interface ConfigSummaryResponse {
  pricing_configs?: unknown[];
  writer_configs?: unknown[];
  discount_configs?: unknown[];
  notification_profiles?: unknown[];
}

export interface ScreenedWordStats {
  total_screened_words: number;
  total_flagged_messages: number;
  flagged_last_7_days: number;
}

export interface OrderConfigAnalytics {
  summary?: {
    total_configs?: number;
    used_configs?: number;
    unused_configs?: number;
    usage_percentage?: number;
  };
  [key: string]: unknown;
}

export interface DefaultSetResponse {
  default_sets?: string[];
  available_sets?: string[];
  sets?: string[];
  [key: string]: unknown;
}

export interface ConfigItem {
  id?: number;
  name?: string;
  title?: string;
  is_active?: boolean;
  website?: number | string | null;
  created_at?: string;
  updated_at?: string;
  [key: string]: unknown;
}

type ListResponse<T> = T[] | { results: T[] };

export const adminSettingsApi = {
  configSummary: () =>
    api.get<ConfigSummaryResponse>(
      apiPath("/admin-management/configs/list_all_configs/"),
    ),
  pricingConfigs: () =>
    api.get<ListResponse<ConfigItem>>(
      apiPath("/admin-management/configs/pricing/"),
    ),
  writerConfigs: () =>
    api.get<ListResponse<ConfigItem>>(
      apiPath("/admin-management/configs/writer/"),
    ),
  discountConfigs: () =>
    api.get<ListResponse<ConfigItem>>(
      apiPath("/admin-management/configs/discount/"),
    ),
  notificationProfiles: () =>
    api.get<ListResponse<ConfigItem>>(
      apiPath("/admin-management/configs/notifications/"),
    ),
  screenedWordStats: () =>
    api.get<ScreenedWordStats>(
      apiPath("/admin-management/configs/screened-words/stats/"),
    ),
  orderConfigUsage: () =>
    api.get<OrderConfigAnalytics>(
      apiPath("/order-configs/management/usage-analytics/"),
    ),
  defaultSets: () =>
    api.get<DefaultSetResponse>(
      apiPath("/order-configs/management/available-default-sets/"),
    ),
  checkDefaults: () =>
    api.get(apiPath("/order-configs/management/check-defaults/")),
  populateDefaults: (website_id: number, default_set?: string) =>
    api.post(apiPath("/order-configs/management/populate-defaults/"), {
      website_id,
      default_set,
    }),
};
