import { api, ordersApiPath } from "./client";
import type { CancellationRequest } from "@/types/cancellation";

const base = (orderId: number | string) =>
  ordersApiPath(`/orders/${orderId}/cancellation-request`);

export const cancellationRequestsApi = {
  getCurrent: (orderId: number | string) =>
    api.get<CancellationRequest>(`${base(orderId)}/`),

  create: (orderId: number | string, reason: string) =>
    api.post<CancellationRequest>(`${base(orderId)}/`, { reason }),

  approve: (
    orderId: number | string,
    reqId: number,
    payload: {
      refund_destination: "wallet" | "external_gateway";
      forfeiture_pct_override?: string | number | null;
      notes?: string;
    },
  ) =>
    api.post<{ message: string }>(`${base(orderId)}/${reqId}/approve/`, payload),

  reject: (orderId: number | string, reqId: number, notes = "") =>
    api.post<{ message: string }>(`${base(orderId)}/${reqId}/reject/`, { notes }),
};
