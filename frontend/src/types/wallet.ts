export interface WalletBalance {
  id?: number;
  wallet_type?: string;
  currency: string;
  status?: string;
  available_balance: string | number;
  pending_balance?: string | number;
  total_credited?: string | number;
  total_debited?: string | number;
  last_activity_at?: string | null;
}

export interface WalletEntry {
  id: number;
  entry_type?: string;
  direction?: string;
  status?: string;
  amount: string | number;
  balance_after?: string | number;
  reference?: string;
  reference_type?: string;
  description?: string;
  created_at?: string;
}

export interface WalletHold {
  id: number;
  amount: string | number;
  status: string;
  reason?: string;
  reference?: string;
  created_at?: string;
  expires_at?: string | null;
}

export interface PayoutRequest {
  id: number;
  amount: string | number;
  status: string;
  workflow_status?: string | null;
  reason?: string;
  reference?: string;
  created_at?: string;
}

export interface PayoutRequestPayload {
  amount: string | number;
  reason?: string;
  metadata?: Record<string, unknown>;
}

export interface TopupPayload {
  amount: string | number;
  payment_provider: "stripe" | "mpesa";
  payment_method_code?: string;
  phone?: string;
}

export interface TopupResponse {
  status: string;
  message?: string;
  checkout_url?: string;
  reference?: string;
  checkout_started?: boolean;
}
