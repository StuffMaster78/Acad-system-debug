export type DisputeStatus = "open" | "under_review" | "resolved" | "closed" | "withdrawn";
export type DisputeVerdict = "writer_wins" | "client_wins";
export type DisputeRemedy =
  | "partial_refund"
  | "full_refund"
  | "reassign"
  | "revision"
  | "cancel_refund";

export interface Dispute {
  id: number;
  order_id: number;
  order_topic: string;
  raised_by: number;
  raised_by_username: string;
  assigned_admin?: number | null;
  assigned_admin_username?: string | null;
  status: DisputeStatus;
  reason: string;
  verdict?: DisputeVerdict | null;
  remedy?: DisputeRemedy | null;
  refund_amount?: string | null;
  resolution?: string | null;
  admin_notes?: string | null;
  created_at: string;
  updated_at: string;
  resolved_at?: string | null;
}

export interface RaiseDisputePayload {
  order_id: number | string;
  reason: string;
}

export interface ResolveDisputePayload {
  verdict: DisputeVerdict;
  remedy?: DisputeRemedy;
  refund_amount?: string;
  resolution: string;
}
