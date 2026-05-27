import { api, apiPath } from "./client";

export interface AuditEvent {
  id: string;
  website: number | null;
  occurred_at: string;
  actor_id: string | null;
  action: string;
  object_type: string | null;
  object_id: string | null;
  status: string;
  processed_at: string | null;
  processing_attempts: number;
  correlation_id: string | null;
  span_id: string | null;
  severity: string;
  is_sensitive: boolean;
  sensitivity_level: string | null;
  service_name: string | null;
  metadata: Record<string, unknown> | null;
  // sensitive fields (staff with elevated perms)
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
  action?: string;
  actor_id?: string;
  object_type?: string;
  service_name?: string;
  occurred_after?: string;
  occurred_before?: string;
  page_size?: number;
}

export const auditLogsApi = {
  events: (params?: AuditEventFilters) =>
    api.get<AuditCursorPage>(apiPath("/audit-logs/v1/events/"), { params }),
  eventsFromUrl: (url: string) =>
    api.get<AuditCursorPage>(url),
};
