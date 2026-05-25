import { api, apiPath, ordersApiPath } from "./client";
import type {
  StaffingActionResponse,
  WriterAvailability,
  WriterBalance,
  WriterCompensationSummary,
  WriterCurrentWindow,
  WriterEvent,
  WriterProfile,
} from "@/types/writer";

export const writerApi = {
  profile: () => api.get<WriterProfile>(apiPath("/writer-management/me/profile/")),
  availability: () =>
    api.get<WriterAvailability>(apiPath("/writer-management/me/availability/")),
  toggleAcceptingOrders: (isAcceptingOrders: boolean) =>
    api.post<{ detail: string; is_accepting_orders: boolean }>(
      apiPath("/writer-management/me/availability/toggle/"),
      { is_accepting_orders: isAcceptingOrders },
    ),
  currentWindow: () =>
    api.get<WriterCurrentWindow>(
      apiPath("/writer-compensation/writer/compensation/current-window/"),
    ),
  compensationSummary: () =>
    api.get<WriterCompensationSummary>(
      apiPath("/writer-compensation/writer/compensation/summary/"),
    ),
  balance: () =>
    api.get<WriterBalance>(
      apiPath("/writer-compensation/writer/compensation/balance/"),
    ),
  events: (params?: Record<string, unknown>) =>
    api.get<WriterEvent[]>(
      apiPath("/writer-compensation/writer/compensation/events/"),
      { params },
    ),
  expressInterest: (orderId: number | string, message = "") =>
    api.post<StaffingActionResponse>(
      ordersApiPath(`/orders/${orderId}/staffing/interests/`),
      { message },
    ),
  takeOrder: (orderId: number | string) =>
    api.post<StaffingActionResponse>(
      ordersApiPath(`/orders/${orderId}/staffing/take/`),
      {},
    ),
  withdrawInterest: (interestId: number | string) =>
    api.post<StaffingActionResponse>(
      ordersApiPath(`/staffing/interests/${interestId}/withdraw/`),
      {},
    ),
};
