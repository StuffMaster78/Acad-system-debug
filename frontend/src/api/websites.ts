import { api, apiPath } from "./client";

type PageResponse<T> = { count: number; next: string | null; previous: string | null; results: T[] } | T[];

export interface Website {
  id: number;
  name: string;
  domain: string;
  slug: string;
  is_active: boolean;
  logo: string | null;
  theme_color: string | null;
  contact_email: string | null;
  contact_phone: string | null;
  meta_title: string | null;
  meta_description: string | null;
  admin_notifications_email: string | null;
  allow_registration: boolean;
  allow_guest_checkout: boolean;
  guest_requires_email_verification: boolean;
  guest_max_order_amount: string | null;
  guest_block_urgent_before_hours: number | null;
  guest_magic_link_ttl_hours: number | null;
  google_analytics_id: string | null;
  google_search_console_id: string | null;
  bing_webmaster_id: string | null;
  enable_live_chat: boolean;
  tawkto_widget_id: string | null;
  tawkto_property_id: string | null;
  communication_widget_type: string | null;
  communication_widget_config: Record<string, unknown> | null;
  is_deleted: boolean;
  deleted_at: string | null;
}

export interface WebsiteActionLog {
  id: number;
  website: string;
  user: string;
  action: string;
  details: string | null;
  timestamp: string;
}

export interface WebsiteStaticPage {
  title: string;
  slug: string;
  content: string;
  meta_title: string | null;
  meta_description: string | null;
  language: string;
  version: number;
  scheduled_publish_date: string | null;
  views: number;
  last_updated: string;
  previous_versions: Record<string, unknown>[];
}

export interface TenantBranding {
  id: number;
  website: number;
  website_name: string | null;
  email_subject_prefix: string | null;
  email_reply_to: string | null;
  email_from_name: string | null;
  email_from_address: string | null;
  notification_subject_prefix: string | null;
  email_logo_url: string | null;
  email_header_color: string | null;
  email_footer_text: string | null;
  created_at: string;
  updated_at: string;
}

export interface TenantFeatureToggle {
  id: number;
  website: number;
  website_name: string | null;
  magic_link_enabled: boolean;
  two_factor_required: boolean;
  password_reset_enabled: boolean;
  messaging_enabled: boolean;
  messaging_types_allowed: string[] | null;
  max_order_size_pages: number | null;
  max_order_size_slides: number | null;
  allow_order_drafts: boolean;
  allow_order_presets: boolean;
  allow_writer_portfolios: boolean;
  allow_writer_feedback: boolean;
  allow_wallet: boolean;
  allow_advance_payments: boolean;
  allow_class_orders: boolean;
  allow_disputes: boolean;
  allow_escalations: boolean;
  created_at: string;
  updated_at: string;
}

export interface WebsiteIntegrationConfig {
  id: number;
  website: number;
  integration_type: string;
  is_active: boolean;
  api_key: string | null;
  secret_key: string | null;
  access_token: string | null;
  config: Record<string, unknown> | null;
  name: string | null;
  description: string | null;
  created_at: string;
  updated_at: string;
  created_by: number | null;
}

export interface PaymentDisclosureConfig {
  id: number;
  website: number;
  website_name: string | null;
  website_domain: string | null;
  brand_name: string;
  processor_display_name: string;
  statement_descriptor: string;
  client_disclosure_text: string;
  support_contact: string;
  requires_acknowledgement: boolean;
  updated_at: string;
}

export interface PaymentDisclosureAckPayload {
  event: "shown" | "acknowledged";
  context?: string;
  reference_type?: string;
  reference_id?: string | number;
}

export interface ExitPopupConfig {
  id: number;
  website: number;
  website_name: string | null;
  is_enabled: boolean;
  trigger: "exit_intent" | "delay" | "scroll_depth";
  title: string;
  body: string;
  primary_cta_label: string;
  primary_cta_url: string;
  secondary_cta_label: string;
  image_url: string;
  show_on_paths: string[];
  suppress_on_paths: string[];
  delay_seconds: number;
  scroll_depth_percent: number;
  cooldown_hours: number;
  max_shows_per_session: number;
  requires_marketing_consent: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateIntegrationPayload {
  website: number;
  integration_type: string;
  name?: string;
  description?: string;
  is_active?: boolean;
  api_key?: string;
  secret_key?: string;
  access_token?: string;
  config?: Record<string, unknown>;
}

export const websitesApi = {
  // ── Websites ──────────────────────────────────────────────────────────────
  list: (params?: Record<string, unknown>) =>
    api.get<PageResponse<Website>>(apiPath("/websites/websites/"), { params }),
  get: (id: number) =>
    api.get<Website>(apiPath(`/websites/websites/${id}/`)),
  update: (id: number, payload: Partial<Website>) =>
    api.patch<Website>(apiPath(`/websites/websites/${id}/`), payload),
  updateSeoSettings: (id: number, payload: Partial<Website>) =>
    api.patch<{ message: string; data: Partial<Website> }>(
      apiPath(`/websites/websites/${id}/update_seo_settings/`),
      payload,
    ),
  softDelete: (id: number) =>
    api.post<{ message: string }>(apiPath(`/websites/websites/${id}/soft_delete/`), {}),
  restore: (id: number) =>
    api.post<{ message: string }>(apiPath(`/websites/websites/${id}/restore/`), {}),
  updateTerms: (id: number, payload: { title?: string; content: string; language?: string; meta_title?: string; meta_description?: string }) =>
    api.post(apiPath(`/websites/websites/${id}/update_terms/`), payload),

  // ── Action logs ───────────────────────────────────────────────────────────
  actionLogs: (params?: Record<string, unknown>) =>
    api.get<PageResponse<WebsiteActionLog>>(apiPath("/websites/website-logs/"), { params }),

  // ── Static pages ──────────────────────────────────────────────────────────
  staticPages: (params?: Record<string, unknown>) =>
    api.get<PageResponse<WebsiteStaticPage>>(apiPath("/websites/static-pages/"), { params }),
  staticPage: (slug: string) =>
    api.get<WebsiteStaticPage>(apiPath(`/websites/static-pages/${slug}/`)),

  // ── Branding ──────────────────────────────────────────────────────────────
  branding: (params?: Record<string, unknown>) =>
    api.get<PageResponse<TenantBranding>>(apiPath("/websites/branding/"), { params }),
  currentBranding: () =>
    api.get<TenantBranding>(apiPath("/websites/branding/current/")),
  updateBranding: (id: number, payload: Partial<TenantBranding>) =>
    api.patch<TenantBranding>(apiPath(`/websites/branding/${id}/`), payload),

  // ── Feature toggles ───────────────────────────────────────────────────────
  featureToggles: (params?: Record<string, unknown>) =>
    api.get<PageResponse<TenantFeatureToggle>>(apiPath("/websites/feature-toggles/"), { params }),
  currentFeatureToggle: () =>
    api.get<TenantFeatureToggle>(apiPath("/websites/feature-toggles/current/")),
  updateFeatureToggle: (id: number, payload: Partial<TenantFeatureToggle>) =>
    api.patch<TenantFeatureToggle>(apiPath(`/websites/feature-toggles/${id}/`), payload),

  // ── Integrations ──────────────────────────────────────────────────────────
  integrations: (params?: Record<string, unknown>) =>
    api.get<PageResponse<WebsiteIntegrationConfig>>(apiPath("/websites/integrations/"), { params }),
  createIntegration: (payload: CreateIntegrationPayload) =>
    api.post<WebsiteIntegrationConfig>(apiPath("/websites/integrations/"), payload),
  updateIntegration: (id: number, payload: Partial<CreateIntegrationPayload>) =>
    api.patch<WebsiteIntegrationConfig>(apiPath(`/websites/integrations/${id}/`), payload),
  deleteIntegration: (id: number) =>
    api.delete(apiPath(`/websites/integrations/${id}/`)),

  paymentDisclosure: (params?: Record<string, unknown>) =>
    api.get<PaymentDisclosureConfig>(apiPath("/websites/payment-disclosure/"), { params }),
  updatePaymentDisclosure: (payload: Partial<PaymentDisclosureConfig>, params?: Record<string, unknown>) =>
    api.patch<PaymentDisclosureConfig>(apiPath("/websites/payment-disclosure/"), payload, { params }),
  acknowledgePaymentDisclosure: (payload: PaymentDisclosureAckPayload) =>
    api.post(apiPath("/websites/payment-disclosure/acknowledge/"), payload),

  exitPopup: (params?: Record<string, unknown>) =>
    api.get<ExitPopupConfig>(apiPath("/privacy/admin/exit-popup/"), { params }),
  updateExitPopup: (payload: Partial<ExitPopupConfig>, params?: Record<string, unknown>) =>
    api.patch<ExitPopupConfig>(apiPath("/privacy/admin/exit-popup/"), payload, { params }),
};
