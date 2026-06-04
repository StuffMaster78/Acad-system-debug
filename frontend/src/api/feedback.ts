import { api, apiPath } from "./client";

export type FeedbackStatus =
  | "new" | "triaging" | "planned" | "in_progress"
  | "released" | "declined" | "duplicate";

export type FeedbackPriority = "low" | "medium" | "high" | "critical";
export type FeedbackType = "feature_request" | "improvement" | "bug_report" | "question";
export type FeedbackSurface = "client" | "writer" | "staff";

export interface FeedbackStatusEvent {
  id: number;
  from_status: string;
  to_status: string;
  changed_by_name: string | null;
  note: string;
  created_at: string;
}

export interface FeedbackItem {
  id: number;
  title: string;
  description?: string;
  request_type: FeedbackType;
  category: string;
  priority: FeedbackPriority;
  status: FeedbackStatus;
  portal_surface: FeedbackSurface;
  requester_display: string;
  requester_role: string;
  upvote_count: number;
  has_voted: boolean;
  staff_owner_name: string | null;
  public_response: string;
  public_response_at?: string | null;
  responded_by_name?: string | null;
  duplicate_of: number | null;
  duplicate_of_title: string | null;
  internal_notes?: string;
  linked_order_id?: number | null;
  linked_ticket_id?: number | null;
  status_history?: FeedbackStatusEvent[];
  created_at: string;
  updated_at: string;
}

export interface FeedbackCategory {
  value: string;
  label: string;
}

export interface CreateFeedbackPayload {
  title: string;
  description: string;
  request_type: FeedbackType;
  category: string;
  priority: FeedbackPriority;
  linked_order_id?: number | null;
  linked_ticket_id?: number | null;
}

export interface TriageUpdatePayload {
  status?: FeedbackStatus;
  staff_owner?: number | null;
  internal_notes?: string;
  public_response?: string;
  note?: string;
}

export interface FeedbackSummary {
  total: number;
  by_status: Record<string, number>;
  by_category: Record<string, number>;
  by_surface: Record<string, number>;
  top_voted: { id: number; title: string; upvote_count: number; status: string }[];
}

type ListResponse<T> = T[] | { count: number; next: string | null; previous: string | null; results: T[] };

export const feedbackApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<ListResponse<FeedbackItem>>(apiPath("/feedback/"), { params }),

  create: (payload: CreateFeedbackPayload) =>
    api.post<FeedbackItem>(apiPath("/feedback/"), payload),

  retrieve: (id: number) =>
    api.get<FeedbackItem>(apiPath(`/feedback/${id}/`)),

  update: (id: number, payload: Partial<CreateFeedbackPayload> | TriageUpdatePayload) =>
    api.patch<FeedbackItem>(apiPath(`/feedback/${id}/`), payload),

  vote: (id: number) =>
    api.post<{ voted: boolean; upvote_count: number }>(apiPath(`/feedback/${id}/vote/`), {}),

  respond: (id: number, response: string) =>
    api.post<FeedbackItem>(apiPath(`/feedback/${id}/respond/`), { response }),

  markDuplicate: (id: number, duplicateOf: number) =>
    api.post<FeedbackItem>(apiPath(`/feedback/${id}/mark-duplicate/`), { duplicate_of: duplicateOf }),

  triage: (params?: Record<string, unknown>) =>
    api.get<ListResponse<FeedbackItem>>(apiPath("/feedback/triage/"), { params }),

  categories: () =>
    api.get<{ surface: string; categories: FeedbackCategory[] }>(apiPath("/feedback/categories/")),

  summary: () =>
    api.get<FeedbackSummary>(apiPath("/feedback/summary/")),
};
