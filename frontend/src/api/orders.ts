import { api, apiPath, ordersApiPath } from "./client";
import type {
  CancelOrderPayload,
  CreateOrderPayload,
  CreateOrderResponse,
  OrderActionResponse,
  OrderInterestRecord,
  OrderLifecycle,
  OrderSummary,
  RevisionRequest,
  RevisionRequestPayload,
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
    api.post<OrderActionResponse>(ordersApiPath(`/orders/${id}/revisions/`), payload),
  cancel: (id: number | string, payload: CancelOrderPayload) =>
    api.post<OrderActionResponse>(ordersApiPath(`/orders/${id}/cancel/`), payload),
  archive: (id: number | string, payload: Record<string, unknown>) =>
    api.post<OrderActionResponse>(ordersApiPath(`/orders/${id}/archive/`), payload),
  raiseDispute: (id: number | string, reason: string) =>
    api.post<OrderActionResponse>(ordersApiPath(`/orders/${id}/dispute/`), { reason }),
  revisions: (id: number | string) =>
    api.get<RevisionRequest[] | { count: number; results: RevisionRequest[] }>(ordersApiPath(`/orders/${id}/revisions/`)),
  // QA actions
  qaSubmit: (id: number | string) =>
    api.post<OrderActionResponse>(ordersApiPath(`/orders/${id}/qa/submit/`), {}),
  qaApprove: (id: number | string) =>
    api.post<OrderActionResponse>(ordersApiPath(`/orders/${id}/qa/approve/`), {}),
  qaReturn: (id: number | string, notes?: string) =>
    api.post<OrderActionResponse>(ordersApiPath(`/orders/${id}/qa/return/`), { notes }),
  // Staffing
  interests: (id: number | string) =>
    api.get<OrderInterestRecord[]>(ordersApiPath(`/orders/${id}/staffing/interests/`)),
  assignFromInterest: (interestId: number | string) =>
    api.post<OrderActionResponse>(ordersApiPath(`/staffing/interests/${interestId}/assign/`), {}),
};
