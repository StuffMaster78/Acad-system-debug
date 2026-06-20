import { api, ordersApiPath } from "./client";
import type {
  AdjustmentRequest,
  CreateExtraServicePayload,
  CreateScopeIncrementPayload,
  StaffAdjustmentInboxResponse,
} from "@/types/adjustments";

const adj = (id: number | string) => ordersApiPath(`/orders/adjustments/${id}`);

export const adjustmentsApi = {
  // --- Read ---
  getDetail: (adjustmentId: number | string) =>
    api.get<AdjustmentRequest>(`${adj(adjustmentId)}/`),

  getLatest: (orderId: number | string) =>
    api.get<AdjustmentRequest>(ordersApiPath(`/orders/${orderId}/adjustments/latest/`)),

  inbox: (params?: Record<string, unknown>) =>
    api.get<StaffAdjustmentInboxResponse>(ordersApiPath("/orders/adjustments/inbox/"), { params }),

  // --- Create (writer / staff) ---
  createScopeIncrement: (orderId: number | string, payload: CreateScopeIncrementPayload) =>
    api.post<AdjustmentRequest>(ordersApiPath(`/orders/${orderId}/adjustments/scope-increment/`), payload),

  createExtraService: (orderId: number | string, payload: CreateExtraServicePayload) =>
    api.post<AdjustmentRequest>(ordersApiPath(`/orders/${orderId}/adjustments/extra-service/`), payload),

  // --- Client actions ---
  acceptScope: (adjustmentId: number | string) =>
    api.post<{ message: string; status: string }>(`${adj(adjustmentId)}/accept-scope/`, {}),

  counterScope: (adjustmentId: number | string, countered_quantity: number, countered_note = "") =>
    api.post<{ message: string; status: string }>(
      `${adj(adjustmentId)}/counter-scope/`,
      { countered_quantity, countered_note },
    ),

  acceptExtraService: (adjustmentId: number | string) =>
    api.post<{ message: string; status: string }>(`${adj(adjustmentId)}/accept-extra-service/`, {}),

  decline: (adjustmentId: number | string, reason: string) =>
    api.post<{ message: string; status: string }>(`${adj(adjustmentId)}/decline/`, { reason }),

  cancel: (adjustmentId: number | string, reason: string) =>
    api.post<{ message: string; status: string }>(`${adj(adjustmentId)}/cancel/`, { reason }),

  // --- Writer escalation ---
  escalate: (adjustmentId: number | string, reason: string) =>
    api.post<{ message: string }>(`${adj(adjustmentId)}/escalate/`, { reason }),

  // --- Deadline decrease / rush (client) ---
  createDeadlineDecrease: (
    orderId: number | string,
    payload: { new_deadline: string; reason?: string },
  ) =>
    api.post<{
      id: number;
      status: string;
      adjustment_type: string;
      new_deadline: string;
      surcharge: string;
      surcharge_breakdown: {
        original_multiplier: string;
        new_multiplier: string;
        original_hours: number;
        new_hours: number;
      };
      message: string;
    }>(
      ordersApiPath(`/orders/${orderId}/adjustments/deadline-decrease/`),
      payload,
    ),

  // --- Deadline extension (writer) ---
  createDeadlineExtension: (
    orderId: number | string,
    payload: { requested_deadline: string; reason: string; writer_justification?: string },
  ) =>
    api.post<{ id: number; status: string; requested_deadline: string; hours_requested: number | null }>(
      ordersApiPath(`/orders/${orderId}/adjustments/deadline-extension/`),
      payload,
    ),

  // --- Staff actions ---
  staffOverride: (adjustmentId: number | string, amount: string, notes: string) =>
    api.post<{ message: string; status: string }>(`${adj(adjustmentId)}/staff-override/`, { amount, notes }),

  resolveEscalation: (adjustmentId: number | string, resolution: string, note = "") =>
    api.post<{ message: string; status: string }>(`${adj(adjustmentId)}/resolve-escalation/`, { resolution, note }),
};
