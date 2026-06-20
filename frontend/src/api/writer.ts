import { api, apiPath, ordersApiPath } from "./client";
import type {
  AvailabilityWindow,
  StaffingActionResponse,
  WriterAvailability,
  WriterBalance,
  WriterCompensationSummary,
  WriterCurrentWindow,
  WriterEvent,
  WriterProfile,
} from "@/types/writer";
import type { OrderSummary } from "@/types/orders";

type ListResponse<T> = T[] | { count: number; next: string | null; previous: string | null; results: T[] };

export interface WriterLevelInfo {
  id: number;
  name: string;
  description: string;
  display_order: number;
}

export interface WriterLevelCriteria {
  min_orders_completed: number;
  min_completion_rate: string;
  min_composite_score: string;
  max_revision_rate: string | null;
  max_lateness_rate: string | null;
}

export interface WriterLevelPerformance {
  completed_orders: number;
  average_rating: string | null;
  completion_rate: string | null;
  on_time_rate: string | null;
  revision_rate: string | null;
}

export interface WriterNextLevel extends WriterLevelInfo {
  criteria: WriterLevelCriteria;
}

export interface WriterLevelProgress {
  current: WriterLevelInfo | null;
  criteria: WriterLevelCriteria;
  performance: WriterLevelPerformance;
  next: WriterNextLevel | null;
}

export interface AdvanceRecord {
  id: number;
  status: string;
  requested_amount: string;
  approved_amount: string | null;
  recovered_amount: string;
  outstanding_balance: string;
  reason: string;
  admin_notes: string;
  reviewed_at: string | null;
  created_at: string;
  recoveries: Array<{ id: number; amount: string; notes: string; recovered_at: string }>;
}

export const writerApi = {
  poolOrders: (params?: Record<string, unknown>) =>
    api.get<ListResponse<OrderSummary>>(ordersApiPath("/orders/"), {
      params: { status: "ready_for_staffing", ...params },
    }),
  assignments: (params?: Record<string, unknown>) =>
    api.get<ListResponse<OrderSummary>>(ordersApiPath("/orders/"), { params }),
  submitOrder: (orderId: number | string, payload: Record<string, unknown>) =>
    api.post<{ message: string; status?: string }>(
      ordersApiPath(`/orders/${orderId}/submit/`),
      payload,
    ),
  profile: () => api.get<WriterProfile>(apiPath("/writer-management/me/profile/")),
  updateProfile: (payload: Partial<Pick<WriterProfile, "display_name"> & { bio?: string }>) =>
    api.patch<WriterProfile>(apiPath("/writer-management/me/profile/"), payload),
  availability: () =>
    api.get<WriterAvailability>(apiPath("/writer-management/me/availability/")),
  toggleAcceptingOrders: (isAcceptingOrders: boolean) =>
    api.post<{ detail: string; is_accepting_orders: boolean }>(
      apiPath("/writer-management/me/availability/toggle/"),
      { is_accepting_orders: isAcceptingOrders },
    ),
  createAvailabilityWindow: (payload: { start_at: string; end_at?: string | null; reason?: string; note?: string }) =>
    api.post<AvailabilityWindow>(apiPath("/writer-management/me/availability/"), payload),
  cancelAvailabilityWindow: (windowId: number | string) =>
    api.delete(apiPath(`/writer-management/me/availability/${windowId}/`)),
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
    api.get<ListResponse<WriterEvent>>(
      apiPath("/writer-compensation/writer/compensation/events/"),
      { params },
    ),
  orderEligibility: (orderId: number | string) =>
    api.get<{
      can_take: boolean;
      can_bid: boolean;
      has_capacity: boolean;
      reason: string;
      suggested_bid_price: string | null;
      rate_breakdown: {
        per_page: string;
        per_slide: string;
        per_chart: string;
        urgent_surcharge: string;
        urgent_multiplier: string;
        earning_mode: string;
      };
    }>(ordersApiPath(`/orders/${orderId}/eligibility/`)),
  eventsForOrder: (orderId: number | string) =>
    api.get<WriterEvent[]>(
      apiPath("/writer-compensation/writer/compensation/events/"),
      { params: { source_type: "order", source_id: orderId } },
    ),
  orderRateCard: (orderId: number | string) =>
    api.get<{
      order_id: number;
      level_name: string;
      earning_mode: string;
      currency: string;
      rates: {
        base_pay_per_page: string;
        base_pay_per_slide: string;
        base_pay_per_chart: string;
        additional_page_pay: string;
        additional_slide_pay: string;
        additional_chart_pay: string;
      };
      urgency: {
        urgent_time_threshold_hours: number;
        urgent_order_surcharge: string;
        urgent_multiplier: string;
      };
      tip_percentage: string;
      snapshotted_at: string;
    }>(apiPath(`/writer-compensation/writer/compensation/orders/${orderId}/rate-card/`)),
  payoutHistory: () =>
    api.get<{ id: number; total_amount: string; status: string; window_label: string; paid_at: string | null }[]>(
      apiPath("/writer-compensation/writer/compensation/payouts/"),
    ),
  payoutPreference: () =>
    api.get<{ id: number; cycle_type: string; locked: boolean; created_at: string; updated_at: string }>(
      apiPath("/writer-compensation/writer/compensation/preference/"),
    ),
  setPayoutPreference: (cycleType: string) =>
    api.post<{ id: number; cycle_type: string; locked: boolean }>(
      apiPath("/writer-compensation/writer/compensation/preference/"),
      { cycle_type: cycleType },
    ),
  requestCycleChange: (requestedCycle: string, reason: string) =>
    api.post<{ id: number; requested_cycle: string; status: string }>(
      apiPath("/writer-compensation/writer/compensation/cycle-change/"),
      { requested_cycle: requestedCycle, reason },
    ),
  pendingCycleChange: () =>
    api.get<{ id: number; requested_cycle: string; status: string; reason: string; created_at: string }>(
      apiPath("/writer-compensation/writer/compensation/cycle-change/"),
    ),
  bonuses: (params?: { limit?: number }) =>
    api.get<WriterEvent[]>(
      apiPath("/writer-compensation/writer/compensation/bonuses/"),
      { params },
    ),
  advances: () =>
    api.get<AdvanceRecord[]>(apiPath("/writer-compensation/advances/")),
  requestAdvance: (amount: string, reason: string) =>
    api.post<AdvanceRecord>(apiPath("/writer-compensation/advances/"), { amount, reason }),
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
  myLevel: () =>
    api.get<WriterLevelProgress>(apiPath("/writer-management/me/level/")),

  // Preferred-writer invitation responses
  acceptPreferredInvitation: (interestId: number | string) =>
    api.post<{ message: string; assignment_id: number; order_id: number }>(
      ordersApiPath(`/staffing/interests/${interestId}/preferred-accept/`),
      {},
    ),
  declinePreferredInvitation: (interestId: number | string) =>
    api.post<{ message: string; order_id: number }>(
      ordersApiPath(`/staffing/interests/${interestId}/preferred-decline/`),
      {},
    ),

  // Direct-assignment acceptance gate
  getAssignmentGate: (orderId: number | string) =>
    api.get<{ gate_id: number; order_id: number; status: string; assigned_at: string; assigned_by_id: number | null }>(
      ordersApiPath(`/orders/${orderId}/assignment/`),
    ),
  acceptAssignment: (orderId: number | string, reason = "") =>
    api.post<{ message: string; order_id: number }>(
      ordersApiPath(`/orders/${orderId}/assignment/accept/`),
      { reason },
    ),
  rejectAssignment: (orderId: number | string, reason: string) =>
    api.post<{ message: string; order_id: number }>(
      ordersApiPath(`/orders/${orderId}/assignment/reject/`),
      { reason },
    ),
};
