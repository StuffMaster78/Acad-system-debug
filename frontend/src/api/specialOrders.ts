import { api, apiPath } from "./client";
import type {
  SpecialOrder,
  SpecialOrderDetail,
  SpecialOrderMilestone,
  Quote,
  CreateSpecialOrderPayload,
  CreateQuotedSpecialOrderPayload,
  CreateFixedSpecialOrderPayload,
  FixedPricePreview,
  PredefinedConfig,
  PredefinedConfigPayload,
  SpecialOrderQuoteConfig,
  SubmitQuotePayload,
  DeliverMilestonePayload,
} from "@/types/specialOrders";

export const specialOrdersApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<SpecialOrder[] | { count: number; next: string | null; previous: string | null; results: SpecialOrder[] }>(
      apiPath("/special-orders/"),
      { params },
    ),

  get: (id: number | string) =>
    api.get<SpecialOrderDetail>(apiPath(`/special-orders/${id}/`)),

  /** @deprecated Use createQuoted or createFixed instead */
  create: (payload: CreateSpecialOrderPayload) =>
    api.post<SpecialOrder>(apiPath("/special-orders/quoted/"), {
      title: payload.title,
      inquiry_details: payload.description,
    }),

  createQuoted: (payload: CreateQuotedSpecialOrderPayload) =>
    api.post<SpecialOrder>(apiPath("/special-orders/quoted/"), payload),

  createFixed: (payload: CreateFixedSpecialOrderPayload) =>
    api.post<SpecialOrder>(apiPath("/special-orders/fixed/"), payload),

  previewFixedPrice: (payload: { predefined_config_id: number; predefined_duration_id: number; currency?: string; platform?: string; writer_level?: string; coupon_code?: string }) =>
    api.post<FixedPricePreview>(apiPath("/special-orders/fixed/preview-price/"), payload),

  listPredefinedConfigs: (params?: Record<string, unknown>) =>
    api.get<PredefinedConfig[]>(apiPath("/special-orders/predefined-configs/"), { params }),

  quoteConfig: (params?: Record<string, unknown>) =>
    api.get<SpecialOrderQuoteConfig>(apiPath("/special-orders/quote-config/"), { params }),

  createPredefinedConfig: (payload: PredefinedConfigPayload, params?: Record<string, unknown>) =>
    api.post<PredefinedConfig>(apiPath("/special-orders/predefined-configs/"), payload, { params }),

  updatePredefinedConfig: (id: number | string, payload: PredefinedConfigPayload, params?: Record<string, unknown>) =>
    api.patch<PredefinedConfig>(apiPath(`/special-orders/predefined-configs/${id}/`), payload, { params }),

  updateQuoteConfig: (payload: Partial<SpecialOrderQuoteConfig["settings"]>, params?: Record<string, unknown>) =>
    api.patch<SpecialOrderQuoteConfig>(apiPath("/special-orders/quote-config/"), payload, { params }),

  update: (id: number | string, payload: Partial<CreateSpecialOrderPayload>) =>
    api.patch<SpecialOrder>(apiPath(`/special-orders/${id}/`), payload),

  cancel: (id: number | string, reason?: string) =>
    api.post(apiPath(`/special-orders/${id}/cancel/`), { reason }),

  complete: (id: number | string) =>
    api.post(apiPath(`/special-orders/${id}/complete/`), {}),

  assignWriter: (id: number | string, writerId: number) =>
    api.post(apiPath(`/special-orders/${id}/assign-writer/`), { writer_id: writerId }),

  quotes: {
    submit: (orderId: number | string, payload: SubmitQuotePayload) =>
      api.post<Quote>(apiPath(`/special-orders/${orderId}/quotes/`), payload),

    accept: (orderId: number | string, quoteId: number | string) =>
      api.post<Quote>(apiPath(`/special-orders/quotes/${quoteId}/accept/`), {}),

    reject: (orderId: number | string, quoteId: number | string, reason: string) =>
      api.post<Quote>(apiPath(`/special-orders/quotes/${quoteId}/reject/`), { reason }),
  },

  milestones: {
    list: (orderId: number | string) =>
      api.get<SpecialOrderMilestone[]>(apiPath(`/special-orders/${orderId}/milestones/`)),

    deliver: (orderId: number | string, milestoneId: number | string, payload: DeliverMilestonePayload) =>
      api.post<SpecialOrderMilestone>(
        apiPath(`/special-orders/${orderId}/milestones/${milestoneId}/deliver/`),
        payload,
      ),

    approve: (orderId: number | string, milestoneId: number | string) =>
      api.post<SpecialOrderMilestone>(
        apiPath(`/special-orders/${orderId}/milestones/${milestoneId}/approve/`),
        {},
      ),

    requestRevision: (orderId: number | string, milestoneId: number | string, notes: string) =>
      api.post<SpecialOrderMilestone>(
        apiPath(`/special-orders/${orderId}/milestones/${milestoneId}/request-revision/`),
        { notes },
      ),
  },
};
