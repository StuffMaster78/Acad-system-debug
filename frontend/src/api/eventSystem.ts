import { api, apiPath } from "./client";

const base = (path = "") => apiPath(`/events${path}`);

export type EventStatus =
  | "pending"
  | "processing"
  | "processed"
  | "failed"
  | "ignored"
  | "dead_letter";

export interface OutboxEvent {
  id: string;
  event_type: string;
  domain: string;
  version: number;
  payload: Record<string, unknown>;
  routing_key: string;
  idempotency_key: string;
  status: EventStatus;
  attempts: number;
  max_attempts: number;
  correlation_id: string | null;
  causation_id: string | null;
  last_error: string | null;
  processed_at: string | null;
  ignored_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface EventMetrics {
  total_events: number;
  processed: number;
  failed: number;
  dead_letter: number;
  ignored: number;
  processing_rate: number;
  failure_rate: number;
  avg_processing_time_ms: number | null;
  last_updated: string | null;
}

export interface EventFailure {
  event_id: string;
  attempts: number;
  last_error: string | null;
  status: string;
  updated_at: string | null;
}

export interface EventTimelineEntry {
  stage: string;
  event_status: string;
  duration_ms?: number;
  created_at: string;
}

export interface EventDetail {
  event: OutboxEvent;
  timeline: EventTimelineEntry[];
}

export const eventSystemApi = {
  list: () =>
    api.get<OutboxEvent[]>(base("/")),

  metrics: () =>
    api.get<EventMetrics>(base("/metrics/")),

  detail: (id: string) =>
    api.get<EventDetail>(base(`/${id}/`)),

  failures: (id: string) =>
    api.get<EventFailure[]>(base(`/${id}/failures/`)),

  replay: (eventId: string, reason?: string) =>
    api.post<{ status: string; event_id: string }>(
      base(`/${eventId}/replay/`),
      { event_id: eventId, reason: reason ?? "" },
    ),

  timeline: (params: { event_id?: string; correlation_id?: string }) =>
    api.get<EventTimelineEntry[]>(base("/timeline/"), { params }),
};
