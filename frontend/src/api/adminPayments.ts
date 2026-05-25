import { api, apiPath } from "./client";

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

type ListResponse<T> = T[] | { results: T[] };

export const adminPaymentsApi = {
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
};
