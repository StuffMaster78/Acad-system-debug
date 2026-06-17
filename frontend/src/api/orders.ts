import { api, apiPath, ordersApiPath } from "./client";

export interface ClientLookupResult {
  id: number;
  email: string;
  username: string;
  full_name: string;
  role: string | null;
  is_active: boolean;
}

import type {
  CancelOrderPayload,
  CreateOrderPayload,
  CreateOrderResponse,
  OrderActionResponse,
  OrderInterestRecord,
  OrderLifecycle,
  OrderNote,
  OrderPaymentSummary,
  OrderSummary,
  RevisionRequest,
  RevisionRequestPayload,
  RevisionRouteResponse,
  UpdateOrderPayload,
} from "@/types/orders";

export const ordersApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<OrderSummary[] | { count: number; next: string | null; previous: string | null; results: OrderSummary[] }>(ordersApiPath("/orders/"), { params }),
  get: (id: number | string) => api.get<OrderSummary>(ordersApiPath(`/orders/${id}/`)),
  update: (id: number | string, payload: UpdateOrderPayload) =>
    api.patch<OrderSummary>(ordersApiPath(`/orders/${id}/`), payload),
  create: (payload: CreateOrderPayload) =>
    api.post<CreateOrderResponse>(ordersApiPath("/orders/create/"), payload),
  lifecycle: (id: number | string) =>
    api.get<OrderLifecycle>(ordersApiPath(`/orders/${id}/lifecycle/`)),
  dashboard: (params?: Record<string, unknown>) =>
    api.get(ordersApiPath("/orders/dashboard/"), { params }),
  submit: (id: number | string, payload: Record<string, unknown>) =>
    api.post(ordersApiPath(`/orders/${id}/submit/`), payload),
  approve: (id: number | string, payload: Record<string, unknown>) =>
    api.post<OrderActionResponse>(ordersApiPath(`/orders/${id}/approve/`), payload),
  requestRevision: (id: number | string, payload: RevisionRequestPayload) =>
    api.post<RevisionRouteResponse | RevisionRequest>(ordersApiPath(`/orders/${id}/revisions/`), payload),
  cancel: (id: number | string, payload: CancelOrderPayload) =>
    api.post<OrderActionResponse>(ordersApiPath(`/orders/${id}/cancel/`), payload),
  archive: (id: number | string, payload: Record<string, unknown>) =>
    api.post<OrderActionResponse>(ordersApiPath(`/orders/${id}/archive/`), payload),
  raiseDispute: (id: number | string, reason: string) =>
    api.post<OrderActionResponse>(ordersApiPath(`/orders/${id}/disputes/`), { reason }),
  holdRequest: (id: number | string, reason: string) =>
    api.post<OrderActionResponse>(ordersApiPath(`/orders/${id}/holds/`), { reason }),
  holdRelease: (holdId: number, reason?: string) =>
    api.post<OrderActionResponse>(ordersApiPath(`/holds/${holdId}/release/`), { reason: reason ?? "" }),
  reassignmentRequest: (id: number | string, reason: string) =>
    api.post<OrderActionResponse>(ordersApiPath(`/orders/${id}/reassignments/`), { reason }),
  revisions: (id: number | string) =>
    api.get<RevisionRequest[]>(ordersApiPath(`/orders/${id}/revisions/`)),
  approveRevision: (orderId: number | string, revId: number) =>
    api.post<RevisionRequest>(ordersApiPath(`/orders/${orderId}/revisions/${revId}/approve/`), {}),
  rejectRevision: (orderId: number | string, revId: number) =>
    api.post<RevisionRequest>(ordersApiPath(`/orders/${orderId}/revisions/${revId}/reject/`), {}),
  completeRevision: (orderId: number | string, revId: number, writerNotes?: string) =>
    api.post<RevisionRequest>(ordersApiPath(`/orders/${orderId}/revisions/${revId}/complete/`), { writer_notes: writerNotes ?? "" }),
  acceptRevision: (orderId: number | string, revId: number) =>
    api.post<RevisionRequest>(ordersApiPath(`/orders/${orderId}/revisions/${revId}/accept/`), {}),
  // QA actions
  qaSubmit: (id: number | string) =>
    api.post<OrderActionResponse>(ordersApiPath(`/orders/${id}/qa/submit/`), {}),
  qaApprove: (id: number | string) =>
    api.post<OrderActionResponse>(ordersApiPath(`/orders/${id}/qa/approve/`), {}),
  qaReturn: (id: number | string, reason: string) =>
    api.post<OrderActionResponse>(ordersApiPath(`/orders/${id}/qa/return/`), { reason }),
  // Staffing
  interests: (id: number | string) =>
    api.get<OrderInterestRecord[]>(ordersApiPath(`/orders/${id}/staffing/interests/`)),
  assignFromInterest: (interestId: number | string) =>
    api.post<OrderActionResponse>(ordersApiPath(`/staffing/interests/${interestId}/assign/`), {}),
  lookupClient: (q: string) =>
    api.get<ClientLookupResult[]>(ordersApiPath(`/client-lookup/?q=${encodeURIComponent(q)}`)),
  lookupPreferredWriter: (registrationId: string) =>
    api.get<{ id: number; registration_id: string; display_name: string }>(
      ordersApiPath(`/preferred-writer-lookup/${registrationId}/`),
    ),
  invitePreferredWriter: (orderId: number | string, writerRegistrationId: string) =>
    api.post<{ message: string; preferred_writer_status: string }>(
      ordersApiPath(`/orders/${orderId}/staffing/invite-preferred/`),
      { writer_registration_id: writerRegistrationId },
    ),
  // Operational notes (staff-only)
  notes: (id: number | string) =>
    api.get<OrderNote[]>(ordersApiPath(`/orders/${id}/notes/`)),
  createNote: (id: number | string, body: string) =>
    api.post<OrderNote>(ordersApiPath(`/orders/${id}/notes/`), { body }),
  patchNote: (orderId: number | string, noteId: number, patch: { is_pinned?: boolean }) =>
    api.patch<OrderNote>(ordersApiPath(`/orders/${orderId}/notes/${noteId}/`), patch),
  deleteNote: (orderId: number | string, noteId: number) =>
    api.delete(ordersApiPath(`/orders/${orderId}/notes/${noteId}/`)),
  paymentSummary: (id: number | string) =>
    api.get<OrderPaymentSummary>(ordersApiPath(`/orders/${id}/payment-summary/`)),

  payFromWallet: (id: number | string) =>
    api.post<{ message: string; amount_charged: string; new_balance: string }>(
      ordersApiPath(`/orders/${id}/pay/wallet/`),
      {},
    ),
};
