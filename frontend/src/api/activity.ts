import { api, apiPath } from "./client";
import type { ActivityEvent } from "@/types/activity";

type ListResponse<T> = T[] | { results: T[] };

export const activityApi = {
  feed: (params?: Record<string, unknown>) =>
    api.get<ListResponse<ActivityEvent>>(
      apiPath("/activity/"),
      { params },
    ),
  markRead: (eventId: string) =>
    api.post(apiPath(`/activity/feed/${eventId}/mark-read/`), {}),
  markUnread: (eventId: string) =>
    api.post(apiPath(`/activity/feed/${eventId}/mark-unread/`), {}),
  dismiss: (eventId: string) =>
    api.post(apiPath(`/activity/feed/${eventId}/dismiss/`), {}),
  pin: (eventId: string) =>
    api.post(apiPath(`/activity/feed/${eventId}/pin/`), {}),
};
