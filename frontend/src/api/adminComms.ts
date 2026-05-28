import { api, apiPath } from "./client";
import type { UserRole } from "@/types/roles";

export interface CommunicationThreadRecord {
  id: number;
  website?: number | null;
  target_type?: string;
  target_id?: number;
  kind: string;
  status: string;
  subject: string;
  reference?: string;
  last_message_at?: string | null;
  locked_at?: string | null;
  closed_at?: string | null;
  archived_at?: string | null;
  metadata?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
}

export interface CommunicationQueueRecord {
  id: number;
  thread?: number;
  status?: string;
  reason?: string;
  severity?: string;
  created_at?: string;
  updated_at?: string;
  [key: string]: unknown;
}

export interface BroadcastRecord {
  id: number;
  title: string;
  message: string;
  event_type?: string;
  website?: number | null;
  channels?: string[];
  target_roles?: UserRole[];
  show_to_all?: boolean;
  is_blocking?: boolean;
  require_acknowledgement?: boolean;
  is_active?: boolean;
  is_expired?: boolean;
  scheduled_for?: string | null;
  sent_at?: string | null;
  expires_at?: string | null;
  acknowledgement_count?: number;
  created_at?: string;
}

export interface EmailCampaignRecord {
  id: number;
  title: string;
  subject: string;
  status: string;
  email_type?: string;
  scheduled_time?: string | null;
  sent_time?: string | null;
  website?: string | number | null;
  created_by?: string;
  created_at?: string;
}

export interface CreateEmailCampaignPayload {
  title: string;
  subject: string;
  body: string;
  website?: number | null;
  email_type: string;
  target_roles: UserRole[];
  scheduled_time?: string | null;
}

export interface EmailTemplate {
  id: number;
  name: string;
  subject: string;
  body: string;
  is_global: boolean;
  created_by: number | null;
  created_at: string;
}

export interface CreateEmailTemplatePayload {
  name: string;
  subject: string;
  body: string;
  is_global?: boolean;
}

export interface EmailProvider {
  id: number;
  website: number;
  provider_name: "smtp" | "sendgrid" | "mailgun";
  api_key: string;
  sender_email: string;
  sender_name: string;
  is_active: boolean;
  created_at: string;
}

export interface CreateEmailProviderPayload {
  website: number;
  provider_name: "smtp" | "sendgrid" | "mailgun";
  api_key: string;
  sender_email: string;
  sender_name: string;
  is_active?: boolean;
}

export interface CampaignRecipient {
  id: number;
  email: string;
  status: string;
  campaign: {
    id: number;
    title: string;
    subject: string;
    status: string;
    email_type: string;
    sent_time: string | null;
  } | null;
  sent_at: string | null;
  opened_at: string | null;
  error_message: string | null;
}

export interface CampaignAnalyticsRow {
  campaign_id: number;
  title: string;
  sent_time: string | null;
  recipients: number;
  opens: number;
  clicks: number;
  unsubscribes: number;
  open_rate: number;
  click_rate: number;
  unsubscribe_rate: number;
}

export interface SendBroadcastPayload {
  event_key: string;
  title: string;
  message: string;
  channels: string[];
  target_roles: UserRole[];
  priority: "low" | "normal" | "high" | "critical";
  show_to_all?: boolean;
  is_critical?: boolean;
  is_blocking?: boolean;
  require_acknowledgement?: boolean;
}

type ListResponse<T> = T[] | { results: T[] };

export const adminCommsApi = {
  threads: (params?: Record<string, unknown>) =>
    api.get<ListResponse<CommunicationThreadRecord>>(
      apiPath("/communications/threads/"),
      { params },
    ),
  escalations: () =>
    api.get<ListResponse<CommunicationQueueRecord>>(
      apiPath("/communications/escalations/"),
    ),
  moderationFlags: () =>
    api.get<ListResponse<CommunicationQueueRecord>>(
      apiPath("/communications/moderation-flags/"),
    ),
  broadcasts: () =>
    api.get<ListResponse<BroadcastRecord>>(
      apiPath("/notifications/admin/broadcasts/list_all/"),
    ),
  sendBroadcast: (payload: SendBroadcastPayload) =>
    api.post(apiPath("/notifications/admin/broadcasts/send/"), payload),
  campaigns: () =>
    api.get<ListResponse<EmailCampaignRecord>>(
      apiPath("/mass-emails/campaigns/"),
    ),
  createCampaign: (payload: CreateEmailCampaignPayload) =>
    api.post<EmailCampaignRecord>(
      apiPath("/mass-emails/campaigns/"),
      payload,
    ),
  syncCampaignRecipients: (campaignId: number) =>
    api.post(apiPath(`/mass-emails/campaigns/${campaignId}/sync-recipients/`), {}),
  sendCampaignNow: (campaignId: number) =>
    api.post(apiPath(`/mass-emails/campaigns/${campaignId}/send_now/`), {}),
  sendCampaignTest: (campaignId: number) =>
    api.post(apiPath(`/mass-emails/campaigns/${campaignId}/send_test/`), {}),

  // Email templates
  templates: () =>
    api.get<ListResponse<EmailTemplate>>(apiPath("/mass-emails/templates/")),
  createTemplate: (payload: CreateEmailTemplatePayload) =>
    api.post<EmailTemplate>(apiPath("/mass-emails/templates/"), payload),
  deleteTemplate: (id: number) =>
    api.delete(apiPath(`/mass-emails/templates/${id}/`)),

  // Campaign analytics
  campaignAnalytics: (params?: { start?: string; end?: string }) =>
    api.get<CampaignAnalyticsRow[]>(apiPath("/mass-emails/analytics/campaigns/"), { params }),
  campaignTrending: () =>
    api.get<Record<string, unknown>>(apiPath("/mass-emails/analytics/trending/")),

  // Email providers
  providers: () =>
    api.get<ListResponse<EmailProvider>>(apiPath("/mass-emails/providers/")),
  createProvider: (payload: CreateEmailProviderPayload) =>
    api.post<EmailProvider>(apiPath("/mass-emails/providers/"), payload),
  updateProvider: (id: number, payload: Partial<CreateEmailProviderPayload>) =>
    api.patch<EmailProvider>(apiPath(`/mass-emails/providers/${id}/`), payload),
  deleteProvider: (id: number) =>
    api.delete(apiPath(`/mass-emails/providers/${id}/`)),

  // Campaign recipients
  recipients: (params?: Record<string, unknown>) =>
    api.get<ListResponse<CampaignRecipient>>(apiPath("/mass-emails/recipients/"), { params }),

  // Admin email history (lookup by user_id)
  adminEmailHistory: (userId: number, params?: { status?: string; email_type?: string }) =>
    api.get<ListResponse<CampaignRecipient>>(apiPath("/mass-emails/admin/email-history/"), {
      params: { user_id: userId, ...params },
    }),
};
