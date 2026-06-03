import { api, apiPath } from "./client";

export interface WriterApplicationSummary {
  id: number;
  full_name: string;
  email: string;
  country: string;
  education_level: string;
  years_of_experience: number;
  status: "pending" | "under_review" | "approved" | "rejected" | "withdrawn";
  submitted_at: string;
  reviewed_at: string | null;
}

export interface WriterApplicationDetail extends WriterApplicationSummary {
  phone_number: string;
  subjects: string[];
  application_text: string;
  resume: string | null;
  sample_work: string | null;
  reviewed_by: number | null;
  reviewed_by_name: string | null;
  rejection_reason: string;
  admin_notes: string;
  updated_at: string;
}

export interface ApprovePayload {
  initial_level_id?: number;
  require_review?: boolean;
}

export interface RejectPayload {
  rejection_reason: string;
  admin_notes?: string;
}

export interface ApproveResponse {
  detail: string;
  registration_id: string;
  public_uuid: string;
}

type ListResponse<T> = T[] | { results: T[] };

export const writerApplicationsApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<ListResponse<WriterApplicationSummary>>(
      apiPath("/writer-management/applications/"),
      { params },
    ),

  detail: (id: number) =>
    api.get<WriterApplicationDetail>(
      apiPath(`/writer-management/applications/${id}/`),
    ),

  review: (id: number) =>
    api.post<{ detail: string }>(
      apiPath(`/writer-management/applications/${id}/review/`),
    ),

  approve: (id: number, payload: ApprovePayload = {}) =>
    api.post<ApproveResponse>(
      apiPath(`/writer-management/applications/${id}/approve/`),
      { require_review: true, ...payload },
    ),

  reject: (id: number, payload: RejectPayload) =>
    api.post<{ detail: string }>(
      apiPath(`/writer-management/applications/${id}/reject/`),
      payload,
    ),

  withdraw: (id: number) =>
    api.post<{ detail: string }>(
      apiPath(`/writer-management/applications/${id}/withdraw/`),
    ),
};
