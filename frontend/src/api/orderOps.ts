import { api, ordersApiPath } from "./client";
import type {
  OrderOpsCounts,
  OrderOpsQueueKey,
  OrderOpsQueueResponse,
} from "@/types/orderOps";

export const orderOpsApi = {
  summary: () => api.get<OrderOpsCounts>(ordersApiPath("/orders/ops/summary/")),
  queue: (queueKey: OrderOpsQueueKey) =>
    api.get<OrderOpsQueueResponse>(
      ordersApiPath(`/orders/ops/queues/${queueKey}/`),
    ),
  routeToStaffing: (orderId: number) =>
    api.post(ordersApiPath(`/orders/${orderId}/staffing/route/`), {}),
  assignDirect: (orderId: number, writerId: number, note = "") =>
    api.post(ordersApiPath(`/orders/${orderId}/staffing/assign-direct/`), {
      writer_id: writerId,
      note,
    }),
  releaseToPool: (orderId: number, reason = "") =>
    api.post(ordersApiPath(`/orders/${orderId}/staffing/release-to-pool/`), {
      reason,
    }),
  approveForDelivery: (orderId: number, notes = "") =>
    api.post(ordersApiPath(`/orders/${orderId}/qa/approve/`), { note: notes }),
  returnToWriter: (orderId: number, notes: string) =>
    api.post(ordersApiPath(`/orders/${orderId}/qa/return/`), { reason: notes }),
  requestRevision: (orderId: number, instructions: string) =>
    api.post(ordersApiPath(`/orders/${orderId}/revisions/`), {
      reason: "Staff revision request",
      scope_summary: instructions,
      is_within_original_scope: true,
    }),
  cancel: (orderId: number, reason: string) =>
    api.post(ordersApiPath(`/orders/${orderId}/cancel/`), { reason }),
  archive: (orderId: number) =>
    api.post(ordersApiPath(`/orders/${orderId}/archive/`), {}),
};
