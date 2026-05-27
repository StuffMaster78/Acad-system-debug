import { api, apiPath } from "./client";

export interface TipRecord {
  id: number;
  sender_id: number;
  receiver_id: number;
  gross_amount_cents: number;
  writer_share_cents: number;
  platform_fee_cents: number;
  status: string;
  message: string | null;
  currency: string;
  payment_intent_id?: string | null;
  created_at: string;
}

export interface CreateTipPayload {
  receiver_id: number;
  gross_amount_cents: number;
  currency?: string;
  context_type: string;
  message?: string;
  idempotency_key: string;
}

export interface TipPolicy {
  id: number;
  writer_percentage: number;
  is_active: boolean;
  [key: string]: unknown;
}

type ListResponse<T> = T[] | { results: T[] };

export const tipsApi = {
  create: (payload: CreateTipPayload) =>
    api.post<TipRecord>(apiPath("/tips/create/"), payload),

  sent: (params?: Record<string, unknown>) =>
    api.get<ListResponse<TipRecord>>(apiPath("/tips/sent/"), { params }),

  received: (params?: Record<string, unknown>) =>
    api.get<ListResponse<TipRecord>>(apiPath("/tips/received/"), { params }),

  policy: () =>
    api.get<TipPolicy>(apiPath("/tips/policy/")),
};
