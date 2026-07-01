import { api, apiPath } from "./client";
import type { Dispute, ResolveDisputePayload } from "@/types/disputes";

type ListResponse<T> = T[] | { results: T[]; count?: number };

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function normalize(raw: any): Dispute {
  return {
    id: raw.id,
    order_id: raw.order,
    order_topic: raw.order_title ?? raw.title ?? `Order #${raw.order}`,
    raised_by: raw.raised_by,
    raised_by_username: raw.raised_by_name ?? raw.raised_by_username ?? "",
    assigned_admin: raw.assigned_to ?? null,
    assigned_admin_username: raw.assigned_to_name ?? null,
    status: raw.status,
    reason: raw.description ?? "",
    verdict: raw.resolution_outcome ?? null,
    resolution: raw.resolution_notes ?? null,
    admin_notes: raw.escalation_reason ?? null,
    created_at: raw.created_at,
    updated_at: raw.updated_at,
    resolved_at: raw.resolved_at ?? null,
  };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function normalizeList(data: any): Dispute[] {
  const items = Array.isArray(data) ? data : (data.results ?? []);
  return items.map(normalize);
}

const BASE = "/support-management/disputes/";

export const disputesApi = {
  mine: (params?: Record<string, unknown>) =>
    api.get<ListResponse<unknown>>(apiPath(BASE), { params }).then((r) => ({
      ...r,
      data: normalizeList(r.data),
    })),

  list: (params?: Record<string, unknown>) =>
    api.get<ListResponse<unknown>>(apiPath(BASE), { params }).then((r) => ({
      ...r,
      data: normalizeList(r.data),
    })),

  get: (id: number | string) =>
    api.get<unknown>(apiPath(`${BASE}${id}/`)).then((r) => ({
      ...r,
      data: normalize(r.data),
    })),

  raise: (orderId: number | string, reason: string) =>
    api
      .post<unknown>(apiPath(BASE), {
        order: orderId,
        title: "Dispute",
        description: reason,
      })
      .then((r) => ({ ...r, data: normalize(r.data) })),

  resolve: (id: number | string, payload: ResolveDisputePayload) =>
    api
      .post<unknown>(apiPath(`${BASE}${id}/resolve/`), {
        resolution_notes: payload.resolution,
        resolution_outcome: payload.verdict,
      })
      .then((r) => ({ ...r, data: normalize(r.data) })),

  close: (id: number | string, notes?: string) =>
    api
      .post<unknown>(apiPath(`${BASE}${id}/close/`), { notes: notes ?? "" })
      .then((r) => ({ ...r, data: normalize(r.data) })),
};
