import { api, apiPath } from "./client";

export const notificationsApi = {
  list: (params?: Record<string, unknown>) =>
    api.get(apiPath("/notifications/"), { params }),
  markRead: (id: number | string) =>
    api.post(apiPath(`/notifications/${id}/mark-read/`)),
};
