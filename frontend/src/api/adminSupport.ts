import { api, apiPath } from "./client";

export interface SupportTicketRecord {
  id: number;
  title: string;
  description?: string;
  created_by?: number | null;
  created_by_name?: string;
  assigned_to?: number | null;
  assigned_to_name?: string;
  website?: number | null;
  status: string;
  priority: string;
  category?: string;
  is_escalated?: boolean;
  has_sla?: boolean;
  resolution_time?: string | null;
  content_type?: number | null;
  object_id?: number | null;
  created_at?: string;
  updated_at?: string;
}

export interface SupportQueueResponse {
  unassigned_tickets?: SupportTicketRecord[];
  my_assigned_tickets?: SupportTicketRecord[];
  high_priority_tickets?: SupportTicketRecord[];
  overdue_tickets?: SupportTicketRecord[];
  counts?: {
    unassigned?: number;
    my_assigned?: number;
    high_priority?: number;
    overdue?: number;
  };
}

export interface SupportWorkloadResponse {
  current_ticket_load?: number;
  average_response_time_hours?: number | null;
  resolution_rate_percent?: number;
  tickets_resolved_today?: number;
  tickets_resolved_this_week?: number;
  tickets_resolved_this_month?: number;
  sla_compliance_rate_percent?: number;
  workload_tracker?: {
    tickets_handled?: number;
    disputes_handled?: number;
    orders_managed?: number;
    last_activity?: string | null;
  };
}

export interface CommunicationEscalationRecord {
  id: number;
  website?: number | null;
  thread?: number;
  status: string;
  reason: string;
  resolution_note?: string;
  escalated_by?: number | null;
  escalated_by_display?: string;
  resolved_by?: number | null;
  resolved_by_display?: string;
  escalated_at?: string;
  resolved_at?: string | null;
  metadata?: Record<string, unknown>;
}

export interface SavedReplyRecord {
  id: number;
  website?: number | null;
  title: string;
  body: string;
  category?: string;
  is_active?: boolean;
  created_by?: number | null;
  created_at?: string;
  updated_at?: string;
}

export interface CreateSavedReplyPayload {
  title: string;
  body: string;
  category?: string;
}

type ListResponse<T> = T[] | { results: T[] };

export const adminSupportApi = {
  tickets: (params?: Record<string, unknown>) =>
    api.get<ListResponse<SupportTicketRecord>>(
      apiPath("/tickets/tickets/"),
      { params },
    ),
  closeTicket: (ticketId: number, reason = "") =>
    api.post(apiPath(`/tickets/tickets/${ticketId}/close/`), { reason }),
  reopenTicket: (ticketId: number, reason = "") =>
    api.post(apiPath(`/tickets/tickets/${ticketId}/reopen/`), {
      status: "open",
      reason,
    }),
  escalateTicket: (ticketId: number) =>
    api.post(apiPath(`/tickets/tickets/${ticketId}/escalate/`), {}),
  queue: () =>
    api.get<SupportQueueResponse>(apiPath("/support-management/dashboard/queue/")),
  workload: () =>
    api.get<SupportWorkloadResponse>(apiPath("/support-management/dashboard/workload/")),
  escalations: () =>
    api.get<ListResponse<CommunicationEscalationRecord>>(
      apiPath("/communications/escalations/"),
    ),
  resolveEscalation: (escalationId: number, resolution_note = "") =>
    api.post(apiPath(`/communications/escalations/${escalationId}/resolve/`), {
      resolution_note,
    }),
  savedReplies: () =>
    api.get<ListResponse<SavedReplyRecord>>(
      apiPath("/communications/saved-replies/"),
    ),
  createSavedReply: (payload: CreateSavedReplyPayload) =>
    api.post<SavedReplyRecord>(
      apiPath("/communications/saved-replies/"),
      payload,
    ),
};
