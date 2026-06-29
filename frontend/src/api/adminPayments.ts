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
  processor_display_name?: string;
  statement_descriptor_snapshot?: string;
  client_disclosure_text?: string;
  disclosure_shown_at?: string | null;
  disclosure_accepted_at?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface ReceiptRecord {
  id: number;
  reference: string;
  client?: number | null;
  recipient_email?: string;
  recipient_name?: string;
  invoice?: number | null;
  payment_request?: number | null;
  title_snapshot?: string;
  description_snapshot?: string;
  company_name_snapshot?: string;
  website_name_snapshot?: string;
  website_domain_snapshot?: string;
  support_email_snapshot?: string;
  amount: string | number;
  currency?: string;
  status: string;
  payment_intent_reference?: string;
  external_reference?: string;
  payment_provider?: string;
  processor_display_name?: string;
  statement_descriptor_snapshot?: string;
  client_disclosure_text?: string;
  disclosure_shown_at?: string | null;
  disclosure_accepted_at?: string | null;
  issued_at?: string | null;
  voided_at?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface RefundRecord {
  id: number;
  order_payment: number | null;
  payment_refund: number | null;
  order: number | null;
  client: number | null;
  website: number | null;
  type: string | null;
  wallet_amount: string;
  external_amount: string;
  refund_method: string | null;
  reason: string | null;
  processed_by: number | null;
  processed_at: string | null;
  status: string;
  metadata: Record<string, unknown> | null;
  error_message: string | null;
  total_amount: string;
  refundable_amount: string;
  created_at: string;
  updated_at: string;
}

export interface RefundLogRecord {
  id: number;
  order: number | null;
  amount: string;
  website: number | null;
  source: string | null;
  status: string;
  metadata: Record<string, unknown> | null;
  created_at: string;
  refund: number | null;
  client: number | null;
  processed_by: number | null;
  action: string | null;
}

export interface RefundReceiptRecord {
  id: number;
  website: number | null;
  refund: number | null;
  generated_at: string;
  reference_code: string;
  amount: string;
  order_payment: number | null;
  client: number | null;
  processed_by: number | null;
  reason: string | null;
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
  payment_id?: string;
  writer_id?: number;
  writer_username?: string;
  writer_email?: string;
  writer?: { id?: number; name?: string; email?: string; registration_id?: string };
  website?: string;
  website_id?: number;
  amount?: string | number;
  total_amount?: string | number;
  total_earnings?: string | number;
  status?: string;
  type?: string;
  paid_at?: string | null;
  date?: string | null;
  batch_id?: number | null;
  batch_reference?: string | null;
  reference?: string;
  client_total?: string | number;
  platform_margin?: string | number;
  order_count?: number;
  number_of_orders?: number;
  tips?: string | number;
  tips_total?: string | number;
  fines?: string | number;
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
  payoutRequests: (params?: Record<string, unknown>) =>
    api.get<ListResponse<WriterPayoutRequestRecord>>(
      apiPath("/wallets/admin/payout-requests/"),
      { params },
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
  refunds: (params?: Record<string, unknown>) =>
    api.get<ListResponse<RefundRecord>>(
      apiPath("/refunds/refunds/"),
      { params },
    ),
  refund: (refundId: number | string) =>
    api.get<RefundRecord>(apiPath(`/refunds/refunds/${refundId}/`)),
  processRefund: (refundId: number | string, reason = "") =>
    api.post<RefundRecord>(apiPath(`/refunds/refunds/${refundId}/process/`), { reason }),
  cancelRefund: (refundId: number | string, reason: string) =>
    api.post<{ success: string }>(apiPath(`/refunds/refunds/${refundId}/cancel/`), { reason }),
  retryRefund: (refundId: number | string) =>
    api.post<RefundRecord>(apiPath(`/refunds/refunds/${refundId}/retry/`), {}),
  refundLogs: (params?: Record<string, unknown>) =>
    api.get<ListResponse<RefundLogRecord>>(apiPath("/refunds/refund-logs/"), { params }),
  refundReceipts: (params?: Record<string, unknown>) =>
    api.get<ListResponse<RefundReceiptRecord>>(apiPath("/refunds/refund-receipts/"), { params }),
  receipts: (params?: Record<string, unknown>) =>
    api.get<ListResponse<ReceiptRecord>>(apiPath("/billing/receipts/"), { params }),
  voidReceipt: (receiptId: number) =>
    api.post<ReceiptRecord>(apiPath(`/billing/receipts/${receiptId}/void/`), {}),
  refundDashboard: (params?: Record<string, unknown>) =>
    api.get<FinanceDashboardResponse>(
      apiPath("/admin-management/refunds/dashboard/dashboard/"),
      { params },
    ),
  pendingRefunds: (params?: Record<string, unknown>) =>
    api.get<QueueResponse>(
      apiPath("/admin-management/refunds/dashboard/pending/"),
      { params },
    ),
  disputeDashboard: (params?: Record<string, unknown>) =>
    api.get<FinanceDashboardResponse>(
      apiPath("/admin-management/disputes/dashboard/"),
      { params },
    ),
  pendingDisputes: (params?: Record<string, unknown>) =>
    api.get<QueueResponse>(
      apiPath("/admin-management/disputes/pending/"),
      { params },
    ),
  resolveDispute: (disputeId: number | string, resolution: string) =>
    api.post(ordersApiPath(`/disputes/${disputeId}/resolve/`), { resolution }),
  closeDispute: (disputeId: number | string, notes = "") =>
    api.post(ordersApiPath(`/disputes/${disputeId}/close/`), { notes }),
  classPaymentMilestones: (params?: Record<string, unknown>) =>
    api.get<QueueResponse>(
      apiPath("/admin-management/class-bundles/payment-milestones/"),
      { params: { limit: 20, status: "unpaid", ...params } },
    ),
  pendingClassDeposits: (params?: Record<string, unknown>) =>
    api.get<QueueResponse>(
      apiPath("/admin-management/class-bundles/deposit-pending/"),
      { params: { limit: 20, ...params } },
    ),
  tipDashboard: (params?: Record<string, unknown>) =>
    api.get<FinanceDashboardResponse>(
      apiPath("/admin-management/tips/dashboard/"),
      { params },
    ),
  tipList: (params?: Record<string, unknown>) =>
    api.get<QueueResponse>(
      apiPath("/admin-management/tips/list_tips/"),
      { params: { limit: 25, ...params } },
    ),
  finesDashboard: (params?: Record<string, unknown>) =>
    api.get(apiPath("/admin-management/fines/dashboard/"), { params }),
  finesList: (params?: Record<string, unknown>) =>
    api.get(apiPath("/admin-management/fines/pending/"), { params }),
};
