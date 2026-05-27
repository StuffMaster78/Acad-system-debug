import { api, apiPath } from "./client";
import type { Dispute } from "@/types/disputes";

type ListResponse<T> = T[] | { results: T[]; count?: number };

export const disputesApi = {
  mine: (params?: Record<string, unknown>) =>
    api.get<ListResponse<Dispute>>(apiPath("/disputes/my/"), { params }),
  list: (params?: Record<string, unknown>) =>
    api.get<ListResponse<Dispute>>(apiPath("/disputes/"), { params }),
  get: (id: number | string) =>
    api.get<Dispute>(apiPath(`/disputes/${id}/`)),
  raise: (orderId: number | string, reason: string) =>
    api.post<Dispute>(apiPath(`/orders/${orderId}/dispute/`), { reason }),
  resolve: (id: number | string, resolution: string) =>
    api.post<Dispute>(apiPath(`/disputes/${id}/resolve/`), { resolution }),
  close: (id: number | string, notes?: string) =>
    api.post<Dispute>(apiPath(`/disputes/${id}/close/`), { notes: notes ?? "" }),
  withdraw: (id: number | string) =>
    api.post<Dispute>(apiPath(`/disputes/${id}/withdraw/`), {}),
};
