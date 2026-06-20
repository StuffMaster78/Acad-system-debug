import { api, apiPath, ordersApiPath } from "./client";
import type { Bid, BidSummary, SubmitBidPayload } from "@/types/bids";

export const bidsApi = {
  // POST /api/v1/orders/orders/<id>/bids/ — writer places a bid on a pool order
  submit: (orderId: number | string, payload: SubmitBidPayload) =>
    api.post<Bid>(ordersApiPath(`/orders/${orderId}/bids/`), payload),

  // GET /api/v1/orders/orders/<id>/bids/ — bids on a specific order (staff)
  listForOrder: (orderId: number | string) =>
    api.get<BidSummary>(ordersApiPath(`/orders/${orderId}/bids/`)),

  // GET /api/v1/bids/my/ — writer sees their own bids
  listMine: (params?: Record<string, unknown>) =>
    api.get<Bid[] | { results: Bid[] }>(apiPath("/bids/my/"), { params }),

  // POST /api/v1/orders/staffing/interests/<id>/assign/ — admin assigns from interest
  accept: (_orderId: number | string, bidId: number | string) =>
    api.post(ordersApiPath(`/staffing/interests/${bidId}/assign/`), {}),

  // Reject a bid — marks interest as declined (no dedicated endpoint: withdraw covers writer side)
  reject: (_orderId: number | string, bidId: number | string, reason?: string) =>
    api.post<Bid>(ordersApiPath(`/staffing/interests/${bidId}/decline/`), { reason }),

  // POST /api/v1/bids/<id>/withdraw/ — writer withdraws their own bid
  withdraw: (bidId: number | string) =>
    api.post<Bid>(apiPath(`/bids/${bidId}/withdraw/`), {}),

  // GET /api/v1/bids/ — admin list of all bids
  listAll: (params?: Record<string, unknown>) =>
    api.get<Bid[] | { results: Bid[]; count: number }>(apiPath("/bids/"), { params }),
};
