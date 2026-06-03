import { api, apiPath } from "./client";
import type {
  PaperQuotePayload,
  PaperQuoteStartResponse,
  PaperQuoteUpdateResponse,
  PricingSnapshotResponse,
} from "@/types/orders";

export interface ConfigOption {
  id: number;
  name: string;
  code: string;
  is_active?: boolean;
  display_order?: number;
}

export interface DeadlineConfig extends ConfigOption {
  hours?: number;
  is_urgent?: boolean;
}

export const pricingApi = {
  // ── Config dropdowns (public, no auth required) ──────────────────────────
  academicLevels: () =>
    api.get<ConfigOption[]>(apiPath("/order-configs/academic-levels/")),

  paperTypes: () =>
    api.get<ConfigOption[]>(apiPath("/order-configs/paper-types/")),

  deadlineConfigs: () =>
    api.get<DeadlineConfig[]>(apiPath("/order-configs/writer-deadline-configs/")),

  subjects: () =>
    api.get<ConfigOption[]>(apiPath("/order-configs/subjects/")),

  typesOfWork: () =>
    api.get<ConfigOption[]>(apiPath("/order-configs/types-of-work/")),

  // ── Quote sessions (anonymous) ───────────────────────────────────────────
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
