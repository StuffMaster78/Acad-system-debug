import { api, apiPath } from "./client";

export interface AdminWriterSummary {
  id: number;
  public_uuid?: string;
  registration_id: string;
  pen_name?: string;
  full_name?: string;
  level_name?: string | null;
  onboarding_status: string;
  verification_status: string;
  is_verified: boolean;
  is_deleted: boolean;
  joined_at: string;
}

export interface AdminWriterDetail extends AdminWriterSummary {
  email?: string;
  phone_number?: string | null;
  bio?: string;
  years_of_experience?: number | null;
  timezone?: string;
  can_take_orders?: boolean;
  is_accepting_orders?: boolean;
  active_orders_count?: number;
  is_suspended?: boolean;
  is_blacklisted?: boolean;
  is_on_probation?: boolean;
  active_warning_count?: number;
  active_strike_count?: number;
}

export interface WriterDisciplineState {
  is_suspended: boolean;
  is_blacklisted: boolean;
  is_on_probation: boolean;
  is_restricted: boolean;
  active_strike_count: number;
  lifetime_strike_count: number;
  active_warning_count: number;
  lifetime_warning_count: number;
  suspension_ends_at?: string | null;
  probation_ends_at?: string | null;
  last_discipline_event_at?: string | null;
}

export interface WriterActionResponse {
  detail?: string;
  id?: number;
  status?: string;
}

export type WriterResourceType = "document" | "link" | "video" | "article" | "tool";

export interface WriterResourceCategory {
  id: number;
  name: string;
  description?: string;
  display_order: number;
  is_active: boolean;
}

export interface AdminWriterResource {
  id: number;
  title: string;
  description?: string;
  resource_type: WriterResourceType;
  resource_type_display?: string;
  category?: number | null;
  category_name?: string | null;
  file_url?: string | null;
  files_app_file_id?: number | null;
  external_url?: string | null;
  video_url?: string | null;
  content?: string;
  is_featured: boolean;
  is_active: boolean;
  display_order: number;
  view_count: number;
  download_count: number;
  created_by_name?: string | null;
  updated_by_name?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface WriterResourcePayload {
  title: string;
  description?: string;
  resource_type: WriterResourceType;
  category?: number | null;
  file_url?: string | null;
  files_app_file_id?: number | null;
  external_url?: string;
  video_url?: string;
  content?: string;
  is_featured?: boolean;
  is_active?: boolean;
  display_order?: number;
}

type ListResponse<T> = T[] | { results: T[] };

export const adminWritersApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<ListResponse<AdminWriterSummary>>(
      apiPath("/writer-management/writers/"),
      { params },
    ),
  detail: (registrationId: string) =>
    api.get<AdminWriterDetail>(
      apiPath(`/writer-management/writers/${registrationId}/`),
    ),
  discipline: (registrationId: string) =>
    api.get<WriterDisciplineState>(
      apiPath(`/writer-management/writers/${registrationId}/discipline/`),
    ),
  issueWarning: (registrationId: string, reason: string, category = "quality") =>
    api.post<WriterActionResponse>(
      apiPath(`/writer-management/writers/${registrationId}/warnings/issue/`),
      { reason, category },
    ),
  issueStrike: (registrationId: string, reason: string, category = "quality") =>
    api.post<WriterActionResponse>(
      apiPath(`/writer-management/writers/${registrationId}/strikes/issue/`),
      { reason, category },
    ),
  suspend: (registrationId: string, reason: string, duration_days = 7) =>
    api.post<WriterActionResponse>(
      apiPath(`/writer-management/writers/${registrationId}/suspend/`),
      { reason, duration_days },
    ),
  liftSuspension: (registrationId: string, reason: string) =>
    api.post<WriterActionResponse>(
      apiPath(`/writer-management/writers/${registrationId}/lift-suspension/`),
      { reason },
    ),
  softDelete: (registrationId: string, reason: string) =>
    api.post<WriterActionResponse>(
      apiPath(`/writer-management/writers/${registrationId}/delete/`),
      { reason },
    ),
  restore: (registrationId: string, reason: string) =>
    api.post<WriterActionResponse>(
      apiPath(`/writer-management/writers/${registrationId}/restore/`),
      { reason },
    ),
  blacklist: (registrationId: string, reason: string) =>
    api.post<WriterActionResponse>(
      apiPath(`/writer-management/writers/${registrationId}/blacklist/`),
      { reason },
    ),
  liftBlacklist: (registrationId: string, reason: string) =>
    api.post<WriterActionResponse>(
      apiPath(`/writer-management/writers/${registrationId}/lift-blacklist/`),
      { reason },
    ),
  placeProbation: (registrationId: string, reason: string, duration_days = 14) =>
    api.post<WriterActionResponse>(
      apiPath(`/writer-management/writers/${registrationId}/probation/`),
      { reason, duration_days },
    ),
  applyPenalty: (registrationId: string, reason: string, amount: string | number) =>
    api.post<WriterActionResponse>(
      apiPath(`/writer-management/writers/${registrationId}/penalties/`),
      { reason, amount },
    ),
  createNote: (registrationId: string, body: string, is_pinned = false) =>
    api.post<WriterActionResponse>(
      apiPath(`/writer-management/writers/${registrationId}/notes/create/`),
      { body, is_pinned },
    ),
  resourceCategories: (params?: Record<string, unknown>) =>
    api.get<WriterResourceCategory[]>(
      apiPath("/writer-management/admin/resource-categories/"),
      { params },
    ),
  createResourceCategory: (payload: {
    name: string;
    description?: string;
    display_order?: number;
    is_active?: boolean;
  }) =>
    api.post<WriterResourceCategory>(
      apiPath("/writer-management/admin/resource-categories/"),
      payload,
    ),
  resources: (params?: Record<string, unknown>) =>
    api.get<AdminWriterResource[]>(
      apiPath("/writer-management/admin/resources/"),
      { params },
    ),
  createResource: (payload: WriterResourcePayload) =>
    api.post<AdminWriterResource>(
      apiPath("/writer-management/admin/resources/"),
      payload,
    ),
  updateResource: (id: number | string, payload: Partial<WriterResourcePayload>) =>
    api.patch<AdminWriterResource>(
      apiPath(`/writer-management/admin/resources/${id}/`),
      payload,
    ),
  deleteResource: (id: number | string) =>
    api.delete(apiPath(`/writer-management/admin/resources/${id}/`)),
};
