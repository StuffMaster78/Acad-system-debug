import { api, apiPath } from "./client";
import type {
  DesignQuotePayload,
  DiagramQuotePayload,
  PaperQuotePayload,
  PaperQuoteStartResponse,
  PaperQuoteUpdateResponse,
  PricingSnapshotResponse,
  ServiceAddon,
} from "@/types/orders";

type QuoteType = "paper" | "design" | "diagram";

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
  startDesignQuote: (payload: DesignQuotePayload) =>
    api.post<PaperQuoteStartResponse>(
      apiPath("/pricing/quotes/design/start/"),
      payload,
    ),
  updateDesignQuote: (sessionId: string, payload: DesignQuotePayload) =>
    api.post<PaperQuoteUpdateResponse>(
      apiPath(`/pricing/quotes/design/${sessionId}/update/`),
      payload,
    ),
  startDiagramQuote: (payload: DiagramQuotePayload) =>
    api.post<PaperQuoteStartResponse>(
      apiPath("/pricing/quotes/diagram/start/"),
      payload,
    ),
  updateDiagramQuote: (sessionId: string, payload: DiagramQuotePayload) =>
    api.post<PaperQuoteUpdateResponse>(
      apiPath(`/pricing/quotes/diagram/${sessionId}/update/`),
      payload,
    ),
  // Generic dispatcher — used by the shared composable
  startQuote: (type: QuoteType, payload: Record<string, unknown>) =>
    api.post<PaperQuoteStartResponse>(
      apiPath(`/pricing/quotes/${type}/start/`),
      payload,
    ),
  updateQuote: (type: QuoteType, sessionId: string, payload: Record<string, unknown>) =>
    api.post<PaperQuoteUpdateResponse>(
      apiPath(`/pricing/quotes/${type}/${sessionId}/update/`),
      payload,
    ),
  addons: (serviceCode: string) =>
    api.get<ServiceAddon[]>(
      apiPath(`/pricing/public/addons/?service_code=${serviceCode}`),
    ),
  createSnapshot: (sessionId: string) =>
    api.post<PricingSnapshotResponse>(
      apiPath(`/pricing/quotes/${sessionId}/snapshot/`),
      {},
    ),
  createCompositeQuote: (componentSessionIds: string[]) =>
    api.post<{ session_id: string; total: string; subtotal: string; currency: string; items: unknown[] }>(
      apiPath("/pricing/quotes/composite/create/"),
      { component_session_ids: componentSessionIds },
    ),
  finalizeCompositeQuote: (sessionId: string) =>
    api.post<{ session_id: string; total: string; component_snapshot_ids: number[] }>(
      apiPath(`/pricing/quotes/composite/${sessionId}/finalize/`),
      {},
    ),
};
