import { api, apiPath } from "./client";

export interface GatewayConfig {
  id: number;
  website: number;
  website_name: string;
  website_domain: string;
  website_slug: string;
  gateway: string;
  webhook_endpoint: string;
  callback_base_url: string;
  effective_callback_base_url: string;
  mode: "live" | "test";
  is_active: boolean;
  statement_descriptor: string;
  secret_key_env_var: string;
  webhook_secret_env_var: string;
  secret_key_configured: boolean;
  webhook_secret_configured: boolean;
  updated_at: string;
}

export interface GatewayConfigPayload {
  website?: number;
  gateway?: string;
  webhook_endpoint?: string;
  callback_base_url?: string;
  mode?: "live" | "test";
  is_active?: boolean;
  statement_descriptor?: string;
  secret_key_env_var?: string;
  webhook_secret_env_var?: string;
}

export interface NotificationEmail {
  id: number;
  website: number;
  website_name: string;
  website_domain: string;
  email: string;
  label: string;
  is_active: boolean;
  created_at: string;
}

export interface NotificationEmailPayload {
  website: number;
  email: string;
  label?: string;
  is_active?: boolean;
}

export const adminGatewayApi = {
  // Gateway configs
  listConfigs: () =>
    api.get<GatewayConfig[]>(apiPath("/payments/gateway/configs/")),
  getConfig: (id: number) =>
    api.get<GatewayConfig>(apiPath(`/payments/gateway/configs/${id}/`)),
  createConfig: (payload: GatewayConfigPayload) =>
    api.post<GatewayConfig>(apiPath("/payments/gateway/configs/create/"), payload),
  updateConfig: (id: number, payload: GatewayConfigPayload) =>
    api.patch<GatewayConfig>(apiPath(`/payments/gateway/configs/${id}/`), payload),

  // Notification emails
  listNotificationEmails: () =>
    api.get<NotificationEmail[]>(apiPath("/payments/gateway/notification-emails/")),
  createNotificationEmail: (payload: NotificationEmailPayload) =>
    api.post<NotificationEmail>(apiPath("/payments/gateway/notification-emails/"), payload),
  updateNotificationEmail: (id: number, payload: Partial<NotificationEmailPayload>) =>
    api.patch<NotificationEmail>(apiPath(`/payments/gateway/notification-emails/${id}/`), payload),
  deleteNotificationEmail: (id: number) =>
    api.delete(apiPath(`/payments/gateway/notification-emails/${id}/`)),
};
