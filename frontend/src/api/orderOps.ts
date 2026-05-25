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
  archive: (orderId: number) =>
    api.post(ordersApiPath(`/orders/${orderId}/archive/`), {}),
};
