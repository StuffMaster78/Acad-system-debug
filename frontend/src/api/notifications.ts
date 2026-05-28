import { api, apiPath } from "./client";

export interface NotificationItem {
  id: number | string;
  event_key?: string;
  category?: string;
  priority?: string;
  title?: string;
  message?: string;
  is_read: boolean;
  is_pinned?: boolean;
  is_critical?: boolean;
  created_at?: string;
  time_ago?: string;
}

export interface NotificationPollResult {
  unread_count: number;
  latest: NotificationItem | null;
}

export interface MasterPreferences {
  id?: number;
  email_enabled: boolean;
  in_app_enabled: boolean;
  dnd_enabled: boolean;
  dnd_start_hour: number;
  dnd_end_hour: number;
  mute_all?: boolean;
  mute_until?: string | null;
  digest_enabled?: boolean;
  min_priority?: string;
  updated_at?: string;
}

export const notificationsApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<{ count: number; results: NotificationItem[] }>(apiPath("/notifications/feed/"), { params }),
  markRead: (id: number | string) =>
    api.patch(apiPath(`/notifications/feed/${id}/mark-read/`)),
  markAllRead: () =>
    api.patch(apiPath("/notifications/feed/mark-all-read/")),
  poll: () =>
    api.get<NotificationPollResult>(apiPath("/notifications/poll/")),
  getPreferences: () =>
    api.get<MasterPreferences>(apiPath("/notifications/preferences/")),
  updatePreferences: (payload: Partial<MasterPreferences>) =>
    api.patch<MasterPreferences>(apiPath("/notifications/preferences/"), payload),
};
