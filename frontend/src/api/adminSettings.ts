import { api, apiPath } from "./client";

export interface GatewayKeyStatus {
  configured: boolean;
  masked: string | null;
}

export interface GatewayStatusResponse {
  provider: string;
  mode: "live" | "test" | "unknown";
  secret_key: GatewayKeyStatus;
  publishable_key: GatewayKeyStatus;
  webhook_secret: GatewayKeyStatus;
  note: string;
}

export interface WebhookConfigRecord {
  retry_attempts: number;
  timeout_seconds: number;
  signature_verification_enabled: boolean;
  updated_at: string | null;
}

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

export interface ScreenedWordRecord {
  id?: number;
  word: string;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
  [key: string]: unknown;
}

export interface ScreenedWordBulkResponse {
  created?: ScreenedWordRecord[];
  errors?: string[];
  created_count?: number;
  error_count?: number;
}

export interface AdminActivityLogRecord {
  id: number;
  admin?: string | null;
  admin_id?: number | null;
  admin_username?: string | null;
  action: string;
  timestamp?: string;
}

export interface SystemHealthResponse {
  status?: string;
  timestamp?: string;
  alerts?: Array<Record<string, unknown> | string>;
  recommendations?: string[];
  database?: Record<string, unknown>;
  order_metrics?: Record<string, unknown>;
  user_metrics?: Record<string, unknown>;
  performance_metrics?: Record<string, unknown>;
  financial_health?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface SystemAlertsResponse {
  alerts?: Array<Record<string, unknown> | string>;
  recommendations?: string[];
}

export interface SpecialDayRecord {
  id?: number;
  name: string;
  description?: string;
  event_type?: string;
  date: string;
  is_annual?: boolean;
  is_international?: boolean;
  countries?: string[];
  priority?: string;
  reminder_days_before?: number;
  send_broadcast_reminder?: boolean;
  auto_generate_discount?: boolean;
  discount_percentage?: string | number | null;
  is_active?: boolean;
  days_until?: number;
  is_upcoming?: boolean;
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
  screenedWords: () =>
    api.get<ListResponse<ScreenedWordRecord>>(
      apiPath("/admin-management/configs/screened-words/"),
    ),
  bulkCreateScreenedWords: (words: string[]) =>
    api.post<ScreenedWordBulkResponse>(
      apiPath("/admin-management/configs/screened-words/bulk_create/"),
      { words },
    ),
  systemHealth: () =>
    api.get<SystemHealthResponse>(
      apiPath("/admin-management/system-health/health/"),
    ),
  systemAlerts: () =>
    api.get<SystemAlertsResponse>(
      apiPath("/admin-management/system-health/alerts/"),
    ),
  activityLogs: (params?: Record<string, unknown>) =>
    api.get<ListResponse<AdminActivityLogRecord>>(
      apiPath("/admin-management/activity-logs/"),
      { params },
    ),
  specialDays: (params?: Record<string, unknown>) =>
    api.get<ListResponse<SpecialDayRecord>>(
      apiPath("/holidays/special-days/"),
      { params },
    ),
  createSpecialDay: (payload: Partial<SpecialDayRecord>) =>
    api.post<SpecialDayRecord>(
      apiPath("/holidays/special-days/"),
      payload,
    ),

  // Payment gateway status (read-only masked keys + connectivity test)
  gatewayStatus: () =>
    api.get<GatewayStatusResponse>(apiPath("/payments/gateway/status/")),
  testGatewayConnection: () =>
    api.post<{ success: boolean; detail: string }>(apiPath("/payments/gateway/status/")),

  // Webhook runtime config
  webhookConfig: () =>
    api.get<WebhookConfigRecord>(apiPath("/payments/gateway/webhook-config/")),
  updateWebhookConfig: (payload: Partial<WebhookConfigRecord>) =>
    api.patch<WebhookConfigRecord>(apiPath("/payments/gateway/webhook-config/"), payload),
};
