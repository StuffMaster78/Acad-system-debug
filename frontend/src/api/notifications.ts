import { api, apiPath } from "./client";

export interface NotificationChannelPref {
  in_app: boolean;
  email: boolean;
}

export interface DndConfig {
  enabled: boolean;
  quiet_hours_enabled: boolean;
  quiet_hours_start: string;
  quiet_hours_end: string;
}

export type NotificationPreferences = Record<string, NotificationChannelPref | DndConfig>;

export const notificationsApi = {
  list: (params?: Record<string, unknown>) =>
    api.get(apiPath("/notifications/"), { params }),
  markRead: (id: number | string) =>
    api.post(apiPath(`/notifications/${id}/mark-read/`)),
  getPreferences: () =>
    api.get<NotificationPreferences>(apiPath("/notifications/preferences/")),
  updatePreferences: (payload: NotificationPreferences) =>
    api.patch<NotificationPreferences>(apiPath("/notifications/preferences/"), payload),
};
