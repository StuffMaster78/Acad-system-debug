import { api, apiPath } from "./client";
import type { OrderSummary } from "@/types/orders";

export interface SpecialOrderListRecord {
  id: number;
  title: string;
  pricing_mode?: string;
  status: string;
  origin?: string;
  priority?: string;
  currency?: string;
  duration_days?: number | null;
  client?: number | null;
  client_name?: string;
  writer?: number | null;
  writer_name?: string;
  predefined_config_name?: string;
  budget?: string | number | null;
  created_at?: string;
  updated_at?: string;
}

export interface SpecialOrderDetailRecord extends SpecialOrderListRecord {
  inquiry_details?: string;
  admin_notes?: string;
  predefined_config?: number | null;
  predefined_duration?: number | null;
  writer_pay_rule?: number | null;
  accepted_quote?: number | null;
  converted_order?: number | null;
  assigned_at?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  cancelled_at?: string | null;
}

export interface ClassOrderListRecord {
  id: number;
  title: string;
  client?: number | null;
  client_name?: string;
  assigned_writer?: number | null;
  assigned_writer_name?: string;
  status: string;
  payment_status?: string;
  institution_name?: string;
  class_name?: string;
  class_subject?: string;
  academic_level?: string;
  final_amount?: string | number | null;
  paid_amount?: string | number | null;
  balance_amount?: string | number | null;
  currency?: string;
  is_work_paused?: boolean;
  pause_reason?: string;
  created_at?: string;
  updated_at?: string;
}

export interface ClassOrderDetailRecord extends ClassOrderListRecord {
  website?: number | null;
  institution_state?: string;
  class_code?: string;
  starts_on?: string | null;
  ends_on?: string | null;
  complexity_level?: string;
  initial_client_notes?: string;
  writer_visible_notes?: string;
  admin_internal_notes?: string;
  quoted_amount?: string | number | null;
  accepted_amount?: string | number | null;
  discount_amount?: string | number | null;
  pricing_snapshot?: Record<string, unknown>;
  discount_snapshot?: Record<string, unknown>;
  paused_at?: string | null;
  submitted_at?: string | null;
  accepted_at?: string | null;
  completed_at?: string | null;
  cancelled_at?: string | null;
  archived_at?: string | null;
  created_by?: number | null;
  updated_by?: number | null;
}

export interface AdminWorkDetailBundle {
  detail?: SpecialOrderDetailRecord | ClassOrderDetailRecord | Record<string, unknown>;
  tasks?: Array<Record<string, unknown>>;
  milestones?: Array<Record<string, unknown>>;
  assignments?: Array<Record<string, unknown>>;
  timeline?: Array<Record<string, unknown>>;
  accessLogs?: Array<Record<string, unknown>>;
  portalWorkLogs?: Array<Record<string, unknown>>;
  writerCompensation?: Array<Record<string, unknown>>;
}

export interface WebsiteRecord {
  id: number;
  name?: string;
  domain?: string;
  slug?: string;
}

type ListResponse<T> = T[] | { results: T[] };

export const adminWorkApi = {
  orders: (params?: Record<string, unknown>) =>
    api.get<ListResponse<OrderSummary>>(apiPath("/orders/orders/"), { params }),
  forceOrderStatus: (orderId: number, newStatus: string, note?: string) =>
    api.post<{ detail: string; old_status: string; new_status: string }>(
      apiPath(`/admin-management/orders/${orderId}/force-status/`),
      { status: newStatus, note: note ?? "Admin force-transition" },
    ),
  specialOrders: (params?: Record<string, unknown>) =>
    api.get<ListResponse<SpecialOrderListRecord>>(
      apiPath("/special-orders/"),
      { params },
    ),
  specialOrder: (id: number | string) =>
    api.get<SpecialOrderDetailRecord>(apiPath(`/special-orders/${id}/`)),
  specialDeliverables: (id: number | string) =>
    api.get<Array<Record<string, unknown>>>(apiPath(`/special-orders/${id}/deliverables/`)),
  specialDeliveryCheckpoints: (id: number | string) =>
    api.get<Array<Record<string, unknown>>>(apiPath(`/special-orders/${id}/delivery-checkpoints/`)),
  classOrders: (params?: Record<string, unknown>) =>
    api.get<ListResponse<ClassOrderListRecord>>(
      apiPath("/class-management/classes/"),
      { params },
    ),
  classOrder: (id: number | string) =>
    api.get<ClassOrderDetailRecord>(apiPath(`/class-management/classes/${id}/`)),
  classTasks: (id: number | string) =>
    api.get<Array<Record<string, unknown>>>(apiPath(`/class-management/classes/${id}/tasks/`)),
  classPaymentMilestones: (id: number | string) =>
    api.get<Array<Record<string, unknown>>>(apiPath(`/class-management/classes/${id}/payments/milestones/`)),
  classAssignments: (id: number | string) =>
    api.get<Array<Record<string, unknown>>>(apiPath(`/class-management/classes/${id}/assignments/`)),
  classTimeline: (id: number | string) =>
    api.get<Array<Record<string, unknown>>>(apiPath(`/class-management/classes/${id}/timeline/`)),
  classAccessLogs: (id: number | string) =>
    api.get<Array<Record<string, unknown>>>(apiPath(`/class-management/classes/${id}/access/logs/`)),
  classPortalWorkLogs: (id: number | string) =>
    api.get<Array<Record<string, unknown>>>(apiPath(`/class-management/classes/${id}/portal-work-logs/`)),
  classWriterCompensation: (id: number | string) =>
    api.get<Array<Record<string, unknown>>>(apiPath(`/class-management/classes/${id}/writer-compensation/`)),
  websites: () =>
    api.get<ListResponse<WebsiteRecord>>(apiPath("/websites/websites/")),
};
