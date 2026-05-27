import { api, apiPath } from "./client";
import type { Bid, BidSummary, SubmitBidPayload } from "@/types/bids";

export const bidsApi = {
  submit: (orderId: number | string, payload: SubmitBidPayload) =>
    api.post<Bid>(apiPath(`/orders/${orderId}/bids/`), payload),

  listForOrder: (orderId: number | string) =>
    api.get<BidSummary>(apiPath(`/orders/${orderId}/bids/`)),

  listMine: (params?: Record<string, unknown>) =>
    api.get<Bid[] | { results: Bid[] }>(apiPath("/bids/my/"), { params }),

  accept: (orderId: number | string, bidId: number | string) =>
    api.post<Bid>(apiPath(`/orders/${orderId}/bids/${bidId}/accept/`), {}),

  reject: (orderId: number | string, bidId: number | string, reason?: string) =>
    api.post<Bid>(apiPath(`/orders/${orderId}/bids/${bidId}/reject/`), { reason }),

  withdraw: (bidId: number | string) =>
    api.post<Bid>(apiPath(`/bids/${bidId}/withdraw/`), {}),

  listAll: (params?: Record<string, unknown>) =>
    api.get<Bid[] | { results: Bid[]; count: number }>(apiPath("/bids/"), { params }),
};
