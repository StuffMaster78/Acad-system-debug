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

// ── Config management types ───────────────────────────────────────────────────
export interface MilestoneTemplateItem {
  id?: number;
  sequence: number;
  label: string;
  percentage: string;
  required_before_staffing: boolean;
  required_before_delivery: boolean;
}

export interface MilestoneTemplate {
  id: number;
  name: string;
  description: string;
  is_active: boolean;
  items: MilestoneTemplateItem[];
}

export interface RushRule      { id?: number; max_duration_days: number; surcharge_percentage: string; is_active: boolean }
export interface WriterLevelRule { id?: number; writer_level: string; surcharge_percentage: string; is_active: boolean }
export interface ClientTierRule  { id?: number; client_tier: string; discount_percentage: string; is_active: boolean }
export interface DifficultyRule  { id?: number; platform: string; difficulty_level: string; multiplier: string; is_active: boolean }

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

  seedPredefinedConfigDefaults: (params?: Record<string, unknown>) =>
    api.post<{
      configs_created: number;
      configs_updated: number;
      durations_created: number;
      durations_updated: number;
    }>(apiPath("/special-orders/predefined-configs/seed-defaults/"), {}, { params }),

  updateQuoteConfig: (payload: Partial<SpecialOrderQuoteConfig["settings"]>, params?: Record<string, unknown>) =>
    api.patch<SpecialOrderQuoteConfig>(apiPath("/special-orders/quote-config/"), payload, { params }),

  update: (id: number | string, payload: Partial<CreateSpecialOrderPayload>) =>
    api.patch<SpecialOrder>(apiPath(`/special-orders/${id}/`), payload),

  availableActions: (id: number | string) =>
    api.get<{ available_actions: string[]; blocked_actions: { action: string; reason: string }[] }>(
      apiPath(`/special-orders/${id}/available-actions/`),
    ),

  cancel: (id: number | string, reason?: string) =>
    api.post(apiPath(`/special-orders/${id}/cancel/`), { reason }),

  complete: (id: number | string) =>
    api.post(apiPath(`/special-orders/${id}/complete/`), {}),

  assignWriter: (id: number | string, writerId: number) =>
    api.post(apiPath(`/special-orders/${id}/assign-writer/`), { writer_id: writerId }),

  manualVerifyPayment: (id: number | string, payload: {
    amount: string;
    transaction_reference: string;
    verification_note: string;
    payment_method?: string;
  }) =>
    api.post(apiPath(`/special-orders/${id}/payments/manual-verify/`), payload),

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

  // ── Milestone templates ─────────────────────────────────────────────────
  milestoneTemplates: (params?: Record<string, unknown>) =>
    api.get<MilestoneTemplate[]>(apiPath("/special-orders/milestone-templates/"), { params }),

  createMilestoneTemplate: (payload: Partial<MilestoneTemplate>) =>
    api.post<MilestoneTemplate>(apiPath("/special-orders/milestone-templates/"), payload),

  updateMilestoneTemplate: (id: number, payload: Partial<MilestoneTemplate>) =>
    api.patch<MilestoneTemplate>(apiPath(`/special-orders/milestone-templates/${id}/`), payload),

  deleteMilestoneTemplate: (id: number) =>
    api.delete(apiPath(`/special-orders/milestone-templates/${id}/`)),

  addMilestoneTemplateItem: (templateId: number, item: Partial<MilestoneTemplateItem>) =>
    api.post<MilestoneTemplate>(apiPath(`/special-orders/milestone-templates/${templateId}/items/`), item),

  updateMilestoneTemplateItem: (itemId: number, payload: Partial<MilestoneTemplateItem>) =>
    api.patch<MilestoneTemplateItem>(apiPath(`/special-orders/milestone-template-items/${itemId}/`), payload),

  deleteMilestoneTemplateItem: (itemId: number) =>
    api.delete(apiPath(`/special-orders/milestone-template-items/${itemId}/`)),

  // ── Pricing rules ───────────────────────────────────────────────────────
  rushRules:        (configId: number) => api.get<RushRule[]>(apiPath(`/special-orders/predefined-configs/${configId}/rules/rush/`)),
  writerLevelRules: (configId: number) => api.get<WriterLevelRule[]>(apiPath(`/special-orders/predefined-configs/${configId}/rules/writer-level/`)),
  clientTierRules:  (configId: number) => api.get<ClientTierRule[]>(apiPath(`/special-orders/predefined-configs/${configId}/rules/client-tier/`)),
  difficultyRules:  (configId: number) => api.get<DifficultyRule[]>(apiPath(`/special-orders/predefined-configs/${configId}/rules/difficulty/`)),

  createRushRule:        (configId: number, r: Omit<RushRule, "id">) => api.post<RushRule>(apiPath(`/special-orders/predefined-configs/${configId}/rules/rush/`), r),
  createWriterLevelRule: (configId: number, r: Omit<WriterLevelRule, "id">) => api.post<WriterLevelRule>(apiPath(`/special-orders/predefined-configs/${configId}/rules/writer-level/`), r),
  createClientTierRule:  (configId: number, r: Omit<ClientTierRule, "id">) => api.post<ClientTierRule>(apiPath(`/special-orders/predefined-configs/${configId}/rules/client-tier/`), r),
  createDifficultyRule:  (configId: number, r: Omit<DifficultyRule, "id">) => api.post<DifficultyRule>(apiPath(`/special-orders/predefined-configs/${configId}/rules/difficulty/`), r),

  deleteRushRule:        (id: number) => api.delete(apiPath(`/special-orders/rules/rush/${id}/`)),
  deleteWriterLevelRule: (id: number) => api.delete(apiPath(`/special-orders/rules/writer-level/${id}/`)),
  deleteClientTierRule:  (id: number) => api.delete(apiPath(`/special-orders/rules/client-tier/${id}/`)),
  deleteDifficultyRule:  (id: number) => api.delete(apiPath(`/special-orders/rules/difficulty/${id}/`)),
};
