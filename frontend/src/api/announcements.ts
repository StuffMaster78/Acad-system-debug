import { api, apiPath } from "./client";

export interface AnnouncementRecord {
  id: number;
  title: string;
  message: string;
  category: string;
  featured_image_url: string | null;
  read_more_url: string | null;
  is_pinned: boolean;
  is_active: boolean;
  target_roles: string[];
  view_count: number;
  created_at: string;
  expires_at: string | null;
  created_by_name: string | null;
  is_read: boolean;
  is_acknowledged: boolean;
  viewed_at: string | null;
}

export interface CreateAnnouncementPayload {
  title: string;
  message: string;
  category?: string;
  target_roles?: string[];
  channels?: string[];
  pinned?: boolean;
  require_acknowledgement?: boolean;
  expires_at?: string | null;
}

type ListResponse<T> = T[] | { count: number; next: string | null; previous: string | null; results: T[] };

export const announcementsApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<ListResponse<AnnouncementRecord>>(apiPath("/announcements/announcements/"), { params }),
  unreadCount: () =>
    api.get<{ unread_count: number }>(apiPath("/announcements/announcements/unread_count/")),
  trackView: (id: number, timeSpent?: number) =>
    api.post(apiPath(`/announcements/announcements/${id}/view/`), timeSpent ? { time_spent: timeSpent } : {}),
  acknowledge: (id: number) =>
    api.post(apiPath(`/announcements/announcements/${id}/acknowledge/`), {}),
  create: (payload: CreateAnnouncementPayload) =>
    api.post<AnnouncementRecord>(apiPath("/announcements/announcements/"), payload),
  pin: (id: number) =>
    api.post(apiPath(`/announcements/announcements/${id}/pin/`), {}),
  unpin: (id: number) =>
    api.post(apiPath(`/announcements/announcements/${id}/unpin/`), {}),
  delete: (id: number) =>
    api.delete(apiPath(`/announcements/announcements/${id}/`)),
};
