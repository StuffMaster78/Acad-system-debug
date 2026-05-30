import { api, apiPath, ordersApiPath } from "./client";
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
} from "@/types/orders";

export const ordersApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<OrderSummary[] | { count: number; next: string | null; previous: string | null; results: OrderSummary[] }>(apiPath("/orders/"), { params }),
  get: (id: number | string) => api.get<OrderSummary>(apiPath(`/orders/${id}/`)),
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
    api.post<OrderActionResponse>(ordersApiPath(`/orders/${id}/dispute/`), { reason }),
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
