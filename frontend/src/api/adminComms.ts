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
};
