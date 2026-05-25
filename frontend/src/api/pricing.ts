import { api, apiPath } from "./client";
import type {
  PaperQuotePayload,
  PaperQuoteStartResponse,
  PaperQuoteUpdateResponse,
  PricingSnapshotResponse,
} from "@/types/orders";

export const pricingApi = {
  startPaperQuote: (payload: PaperQuotePayload) =>
    api.post<PaperQuoteStartResponse>(
      apiPath("/pricing/quotes/paper/start/"),
      payload,
    ),
  updatePaperQuote: (sessionId: string, payload: PaperQuotePayload) =>
    api.post<PaperQuoteUpdateResponse>(
      apiPath(`/pricing/quotes/paper/${sessionId}/update/`),
      payload,
    ),
  createSnapshot: (sessionId: string) =>
    api.post<PricingSnapshotResponse>(
      apiPath(`/pricing/quotes/${sessionId}/snapshot/`),
      {},
    ),
};
