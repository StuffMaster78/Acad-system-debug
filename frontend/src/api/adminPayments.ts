import { api, apiPath, ordersApiPath } from "./client";

export interface WriterPayoutRequestRecord {
  id: number;
  website_id?: number | null;
  wallet_id?: number;
  writer_id?: number;
  writer_email?: string;
  amount: string | number;
  status: string;
  workflow_status?: string | null;
  reason?: string;
  reference?: string;
  reference_type?: string;
  metadata?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
  released_at?: string | null;
  captured_at?: string | null;
}

export interface AdminWalletRecord {
  id: number;
  website_id?: number | null;
  owner_user_id?: number | null;
  wallet_type: "client" | "writer" | "system" | string;
  currency?: string;
  status?: string;
  is_active?: boolean;
  available_balance?: string | number;
  pending_balance?: string | number;
  total_credited?: string | number;
  total_debited?: string | number;
  last_activity_at?: string | null;
  metadata?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
}

export interface WalletEntryRecord {
  id: number;
  website_id?: number | null;
  wallet_id?: number;
  entry_type?: string;
  direction?: "credit" | "debit" | string;
  status?: string;
  amount: string | number;
  balance_before?: string | number;
  balance_after?: string | number;
  reference?: string;
  reference_type?: string;
  reference_id?: string;
  description?: string;
  metadata?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
}

export interface RefundRecord {
  id: number;
  order?: number | string | null;
  client?: number | string | null;
  website?: number | string | null;
  amount?: string | number;
  wallet_amount?: string | number;
  external_amount?: string | number;
  status: string;
  refund_method?: string;
  reason?: string;
  created_at?: string;
  processed_at?: string | null;
  [key: string]: unknown;
}

export interface FinancialOverviewResponse {
  summary?: {
    total_revenue?: number;
    revenue_breakdown?: {
      orders?: number;
      special_orders?: number;
      classes?: number;
    };
    total_expenses?: number;
    expenses_breakdown?: {
      writer_payments?: number;
      tips?: number;
    };
    net_revenue?: number;
    profit_margin?: number;
  };
  period_breakdown?: Array<{
    period?: string;
    month?: string;
    revenue?: {
      orders?: number;
      special_orders?: number;
      classes?: number;
      total?: number;
    };
    expenses?: {
      writer_payments?: number;
      total?: number;
    };
    net_revenue?: number;
  }>;
  filters?: Record<string, unknown>;
}

export interface WriterPaymentRecord {
  id?: number;
  writer_id?: number;
  writer_username?: string;
  writer_email?: string;
  website?: string;
  website_id?: number;
  amount?: string | number;
  total_amount?: string | number;
  status?: string;
  paid_at?: string | null;
  batch_id?: number | null;
  client_total?: string | number;
  platform_margin?: string | number;
  order_count?: number;
  tips_total?: string | number;
  fines_total?: string | number;
  [key: string]: unknown;
}

export interface FinanceDashboardResponse {
  summary?: Record<string, number | string | null | undefined>;
  recent_refunds?: Array<Record<string, unknown>>;
  recent_disputes?: Array<Record<string, unknown>>;
  payment_status?: Record<string, number>;
  [key: string]: unknown;
}

export interface QueueResponse {
  refunds?: Array<Record<string, unknown>>;
  disputes?: Array<Record<string, unknown>>;
  payment_milestones?: Array<Record<string, unknown>>;
  class_orders?: Array<Record<string, unknown>>;
  results?: Array<Record<string, unknown>>;
  count?: number;
  statistics?: Record<string, unknown>;
  summary?: Record<string, unknown>;
  [key: string]: unknown;
}

type ListResponse<T> = T[] | { results: T[] };

export const adminPaymentsApi = {
  financialOverview: (params?: Record<string, unknown>) =>
    api.get<FinancialOverviewResponse>(
      apiPath("/admin-management/financial-overview/overview/"),
      { params },
    ),
  allWriterPayments: (params?: Record<string, unknown>) =>
    api.get<{ payments?: WriterPaymentRecord[]; results?: WriterPaymentRecord[] } | WriterPaymentRecord[]>(
      apiPath("/admin-management/financial-overview/all-payments/"),
      { params },
    ),
  wallets: (params?: Record<string, unknown>) =>
    api.get<ListResponse<AdminWalletRecord>>(
      apiPath("/wallets/admin/wallets/"),
      { params },
    ),
  walletEntries: (walletId: number, params?: Record<string, unknown>) =>
    api.get<ListResponse<WalletEntryRecord>>(
      apiPath(`/wallets/admin/wallets/${walletId}/entries/`),
      { params },
    ),
  payoutRequests: () =>
    api.get<ListResponse<WriterPayoutRequestRecord>>(
      apiPath("/wallets/admin/payout-requests/"),
    ),
  approvePayout: (holdId: number, review_notes = "") =>
    api.post(apiPath(`/wallets/admin/payout-requests/${holdId}/approve/`), {
      review_notes,
    }),
  rejectPayout: (holdId: number, review_notes = "") =>
    api.post(apiPath(`/wallets/admin/payout-requests/${holdId}/reject/`), {
      review_notes,
    }),
  processPayout: (holdId: number, external_reference = "") =>
    api.post(apiPath(`/wallets/admin/payout-requests/${holdId}/process/`), {
      external_reference,
    }),
  refunds: () =>
    api.get<ListResponse<RefundRecord>>(
      apiPath("/refunds/refunds/"),
    ),
  processRefund: (refundId: number | string, notes = "") =>
    api.post(apiPath(`/refunds/refunds/${refundId}/process/`), { notes }),
  cancelRefund: (refundId: number | string, reason: string) =>
    api.post(apiPath(`/refunds/refunds/${refundId}/cancel/`), { reason }),
  refundDashboard: () =>
    api.get<FinanceDashboardResponse>(
      apiPath("/admin-management/refunds/dashboard/dashboard/"),
    ),
  pendingRefunds: () =>
    api.get<QueueResponse>(
      apiPath("/admin-management/refunds/dashboard/pending/"),
    ),
  disputeDashboard: () =>
    api.get<FinanceDashboardResponse>(
      apiPath("/admin-management/disputes/dashboard/"),
    ),
  pendingDisputes: () =>
    api.get<QueueResponse>(
      apiPath("/admin-management/disputes/pending/"),
    ),
  resolveDispute: (disputeId: number | string, resolution: string) =>
    api.post(ordersApiPath(`/disputes/${disputeId}/resolve/`), { resolution }),
  closeDispute: (disputeId: number | string, notes = "") =>
    api.post(ordersApiPath(`/disputes/${disputeId}/close/`), { notes }),
  classPaymentMilestones: () =>
    api.get<QueueResponse>(
      apiPath("/admin-management/class-bundles/payment-milestones/"),
      { params: { limit: 20, status: "unpaid" } },
    ),
  pendingClassDeposits: () =>
    api.get<QueueResponse>(
      apiPath("/admin-management/class-bundles/deposit-pending/"),
      { params: { limit: 20 } },
    ),
  tipDashboard: () =>
    api.get<FinanceDashboardResponse>(
      apiPath("/admin-management/tips/dashboard/"),
    ),
  tipList: () =>
    api.get<QueueResponse>(
      apiPath("/admin-management/tips/list_tips/"),
      { params: { limit: 20 } },
    ),
};
