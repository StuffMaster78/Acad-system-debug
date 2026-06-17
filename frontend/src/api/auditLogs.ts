import { api, apiPath } from "./client";

export interface AuditEvent {
  id: string;
  website: number | null;
  occurred_at: string;
  // Actor
  actor_id: string | null;
  actor_role: string | null;
  actor_display: string | null;
  // Action
  action: string;
  // Object
  object_type: string | null;
  object_id: string | null;
  object_label: string | null;
  // Request context
  portal_surface: string | null;
  request_path: string | null;
  http_method: string | null;
  session_id: string | null;
  // Lifecycle
  status: string;
  processed_at: string | null;
  processing_attempts: number;
  // Tracing
  correlation_id: string | null;
  span_id: string | null;
  // Classification
  severity: string;
  is_sensitive: boolean;
  sensitivity_level: string | null;
  service_name: string | null;
  // State diff
  before_state: Record<string, unknown> | null;
  after_state: Record<string, unknown> | null;
  // Payload
  metadata: Record<string, unknown> | null;
  // Sensitive fields (staff with elevated perms only)
  ip_address?: string | null;
  user_agent?: string | null;
  last_error?: string | null;
}

export interface AuditCursorPage {
  next: string | null;
  previous: string | null;
  results: AuditEvent[];
}

export interface AuditEventFilters {
  search?: string;
  status?: string;
  severity?: string;
  is_sensitive?: boolean;
  action?: string;
  actor_id?: string;
  object_type?: string;
  object_id?: string;
  service_name?: string;
  occurred_after?: string;
  occurred_before?: string;
  page_size?: number;
}

export interface AuditSensitiveSummary {
  window_days: number;
  total_events: number;
  sensitive_events: number;
  by_severity: Record<string, number>;
  by_sensitivity_level: Record<string, number>;
  top_actions: { action: string; count: number }[];
  recent_critical: {
    id: string; action: string; object_type: string | null; object_id: string | null;
    actor_id: string | null; severity: string; occurred_at: string;
    metadata: Record<string, unknown> | null;
  }[];
}

export interface AuditObjectTimeline {
  object_type: string;
  object_id: string;
  events: AuditEvent[];
}

export const auditLogsApi = {
  events: (params?: AuditEventFilters) =>
    api.get<AuditCursorPage>(apiPath("/audit-logs/v1/events/"), { params }),
  eventsFromUrl: (url: string) =>
    api.get<AuditCursorPage>(url),
  sensitiveSummary: (params?: { days?: number; website?: number }) =>
    api.get<AuditSensitiveSummary>(apiPath("/audit-logs/v1/events/sensitive-summary/"), { params }),
  objectTimeline: (objectType: string, objectId: string | number) =>
    api.get<AuditObjectTimeline>(apiPath("/audit-logs/v1/events/object-timeline/"), {
      params: { object_type: objectType, object_id: String(objectId) },
    }),
  exportUrl(params?: AuditEventFilters): string {
    const base = apiPath("/audit-logs/v1/events/export/");
    if (!params) return base;
    const q = new URLSearchParams(
      Object.fromEntries(
        Object.entries(params)
          .filter(([, v]) => v !== undefined && v !== "")
          .map(([k, v]) => [k, String(v)])
      )
    ).toString();
    return q ? `${base}?${q}` : base;
  },
};
