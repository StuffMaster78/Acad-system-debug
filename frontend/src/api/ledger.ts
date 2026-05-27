import { api, apiPath } from "./client";

export interface LedgerAccount {
  id: string;
  website: number;
  code: string;
  name: string;
  account_type: string;
  currency: string;
  status: string;
  is_system_account: boolean;
  allows_negative: boolean;
  description: string | null;
  metadata: Record<string, unknown> | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface JournalLine {
  id: string;
  journal_entry: string;
  journal_entry_number: string;
  ledger_account: string;
  ledger_account_code: string;
  ledger_account_name: string;
  entry_side: "debit" | "credit";
  amount: string;
  currency: string;
  description: string | null;
  user: number | null;
  wallet_reference: string | null;
  payment_intent_reference: string | null;
  related_object_type: string | null;
  related_object_id: string | null;
  is_debit: boolean;
  is_credit: boolean;
  created_at: string;
}

export interface JournalEntry {
  id: string;
  website: number;
  entry_number: string;
  entry_type: string;
  status: string;
  currency: string;
  description: string | null;
  reference: string | null;
  source_app: string | null;
  source_model: string | null;
  source_object_id: string | null;
  external_reference: string | null;
  payment_intent_reference: string | null;
  triggered_by: number | null;
  approved_by: number | null;
  reversal_of: string | null;
  effective_at: string | null;
  posted_at: string | null;
  failure_reason: string | null;
  is_draft: boolean;
  is_pending: boolean;
  is_posted: boolean;
  is_reversed: boolean;
  is_failed: boolean;
  is_final: boolean;
  lines: JournalLine[];
  created_at: string;
  updated_at: string;
}

export interface ReconciliationRecord {
  id: string;
  journal_entry: string;
  journal_entry_number: string;
  user: number | null;
  status: string;
  currency: string;
  expected_amount: string;
  actual_amount: string;
  matched_amount: string;
  variance_amount: string;
  reference: string | null;
  external_reference: string | null;
  payment_intent_reference: string | null;
  source_app: string | null;
  mismatch_reason: string | null;
  resolved_by: number | null;
  resolved_at: string | null;
  is_unreconciled: boolean;
  is_matched: boolean;
  is_partially_matched: boolean;
  is_mismatched: boolean;
  is_resolved: boolean;
  is_final: boolean;
  created_at: string;
}

type PageResponse<T> = { count: number; next: string | null; previous: string | null; results: T[] } | T[];

export const ledgerApi = {
  accounts: (params?: Record<string, unknown>) =>
    api.get<PageResponse<LedgerAccount>>(apiPath("/ledger/accounts/"), { params }),
  account: (id: string) =>
    api.get<LedgerAccount>(apiPath(`/ledger/accounts/${id}/`)),
  journalEntries: (params?: Record<string, unknown>) =>
    api.get<PageResponse<JournalEntry>>(apiPath("/ledger/journal-entries/"), { params }),
  journalEntry: (id: string) =>
    api.get<JournalEntry>(apiPath(`/ledger/journal-entries/${id}/`)),
  reconciliations: (params?: Record<string, unknown>) =>
    api.get<PageResponse<ReconciliationRecord>>(apiPath("/ledger/reconciliations/"), { params }),
};
