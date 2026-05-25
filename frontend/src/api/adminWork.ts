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

export interface WebsiteRecord {
  id: number;
  name?: string;
  domain?: string;
  slug?: string;
}

type ListResponse<T> = T[] | { results: T[] };

export const adminWorkApi = {
  orders: (params?: Record<string, unknown>) =>
    api.get<ListResponse<OrderSummary>>(apiPath("/orders/"), { params }),
  specialOrders: (params?: Record<string, unknown>) =>
    api.get<ListResponse<SpecialOrderListRecord>>(
      apiPath("/special-orders/"),
      { params },
    ),
  classOrders: (params?: Record<string, unknown>) =>
    api.get<ListResponse<ClassOrderListRecord>>(
      apiPath("/class-management/classes/"),
      { params },
    ),
  websites: () =>
    api.get<ListResponse<WebsiteRecord>>(apiPath("/websites/websites/")),
};
