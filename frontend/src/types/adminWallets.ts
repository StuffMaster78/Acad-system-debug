export type WalletTone = "neutral" | "good" | "warn" | "risk";

export interface AdminWalletMetric {
  label: string;
  value: string | number;
  detail: string;
  tone: WalletTone;
}

export interface AdminWalletRecord {
  id: number;
  website_id?: number | null;
  website_name?: string | null;
  owner_user_id?: number | null;
  owner_user_email?: string | null;
  owner_user_name?: string | null;
  owner_user_role?: string | null;
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

export interface AdminWalletEntryRecord {
  id: number;
  website_id?: number | null;
  wallet_id?: number;
  entry_type?: string;
  ledger_transaction_id?: string | number | null;
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
  created_by_id?: number | null;
  created_at?: string;
  updated_at?: string;
}

export interface AdminWalletHoldRecord {
  id: number;
  website_id?: number | null;
  wallet_id?: number;
  amount: string | number;
  status?: string;
  reason?: string;
  reference?: string;
  reference_type?: string;
  reference_id?: string;
  expires_at?: string | null;
  released_at?: string | null;
  captured_at?: string | null;
  metadata?: Record<string, unknown>;
  created_by_id?: number | null;
  created_at?: string;
  updated_at?: string;
}

export interface AdminWalletAdjustmentPayload {
  amount: number;
  description?: string;
  reference?: string;
  reference_type?: string;
  reference_id?: string;
  metadata?: Record<string, unknown>;
}

export interface AdminEnsureWalletPayload {
  user_id?: number | null;
  user_lookup?: string;
  wallet_type: "client" | "writer";
  currency?: string;
  website_id?: number | null;
}

export interface AdminWalletHoldPayload {
  amount: number;
  reason: string;
  reference?: string;
  reference_type?: string;
  reference_id?: string;
  expires_at?: string | null;
  metadata?: Record<string, unknown>;
}
