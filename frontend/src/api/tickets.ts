import { api, apiPath } from "./client";

export const ticketsApi = {
  list: (params?: Record<string, unknown>) =>
    api.get(apiPath("/tickets/tickets/"), { params }),
  get: (id: number | string) => api.get(apiPath(`/tickets/tickets/${id}/`)),
  create: (payload: Record<string, unknown>) =>
    api.post(apiPath("/tickets/tickets/"), payload),
  messages: (params?: Record<string, unknown>) =>
    api.get(apiPath("/tickets/messages/"), { params }),
  statistics: () => api.get(apiPath("/tickets/statistics/")),
};
