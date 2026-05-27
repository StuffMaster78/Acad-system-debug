import { api, apiPath } from "./client";
import type {
  CommunicationEscalationRecord,
  SavedReplyRecord,
  SupportOrdersDashboard,
  SupportQueueResponse,
  SupportSlaDashboard,
  SupportTicketRecord,
  SupportWorkloadResponse,
} from "@/types/support";
import type { CreateSavedReplyPayload } from "@/api/adminSupport";

type ListResponse<T> = T[] | { results: T[] };

export const supportApi = {
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
  orders: () =>
    api.get<SupportOrdersDashboard>(apiPath("/support-management/dashboard/orders/")),
  slaDashboard: () =>
    api.get<SupportSlaDashboard>(apiPath("/support-management/dashboard/sla/dashboard/")),
  performance: (days = 30) =>
    api.get<Record<string, unknown>>(
      apiPath("/support-management/dashboard/performance/metrics/"),
      { params: { days } },
    ),
  trends: (days = 30) =>
    api.get<{ trends: Array<Record<string, unknown>> }>(
      apiPath("/support-management/dashboard/performance/trends/"),
      { params: { days } },
    ),
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
  createTicket: (payload: { title: string; description: string; category?: string; object_id?: number | string }) =>
    api.post<SupportTicketRecord>(apiPath("/tickets/tickets/"), payload),
  getTicket: (id: number | string) =>
    api.get<SupportTicketRecord>(apiPath(`/tickets/tickets/${id}/`)),
  ticketMessages: (id: number | string) =>
    api.get<ListResponse<Record<string, unknown>>>(apiPath(`/tickets/tickets/${id}/messages/`)),
  addMessage: (id: number | string, body: string) =>
    api.post<Record<string, unknown>>(apiPath(`/tickets/tickets/${id}/messages/`), { body }),
};
