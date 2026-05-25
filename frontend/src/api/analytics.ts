import { api, apiPath } from "./client";

export interface ClientAnalytics {
  id: number;
  client?: number;
  client_email?: string;
  client_name?: string;
  period_start: string;
  period_end: string;
  total_spend: string | number;
  average_order_value: string | number;
  total_orders: number;
  on_time_delivery_count: number;
  late_delivery_count: number;
  on_time_delivery_rate: string | number;
  total_revisions: number;
  revision_rate: string | number;
  average_writer_rating: string | number;
}

export interface WriterAnalytics {
  id: number;
  writer?: number;
  writer_email?: string;
  writer_name?: string;
  period_start: string;
  period_end: string;
  total_earnings: string | number;
  effective_hourly_rate: string | number;
  total_orders_completed: number;
  total_orders_in_progress: number;
  average_completion_time_hours: string | number;
  revision_rate: string | number;
  approval_rate: string | number;
  rejection_rate: string | number;
  average_rating: string | number;
  quality_score: string | number;
}

export interface ClassAnalytics {
  id: number;
  class_name: string;
  class_id?: string;
  period_start: string;
  period_end: string;
  total_students: number;
  active_students: number;
  attendance_rate: string | number;
  total_orders: number;
  completed_orders: number;
  completion_rate: string | number;
  average_grade: string | number;
  on_time_submission_rate: string | number;
  reports_count?: number;
}

type ListResponse<T> = T[] | { results: T[] };

export const analyticsApi = {
  clients: (params?: Record<string, unknown>) =>
    api.get<ListResponse<ClientAnalytics>>(apiPath("/analytics/client/"), { params }),
  writers: (params?: Record<string, unknown>) =>
    api.get<ListResponse<WriterAnalytics>>(apiPath("/analytics/writer/"), { params }),
  classes: (params?: Record<string, unknown>) =>
    api.get<ListResponse<ClassAnalytics>>(apiPath("/analytics/class/"), { params }),
};
