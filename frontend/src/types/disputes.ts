export type DisputeStatus = "open" | "under_review" | "resolved" | "escalated" | "closed";
export type DisputeVerdict =
  | "writer_wins"
  | "client_wins"
  | "partial_refund"
  | "extend_deadline"
  | "reassign";
export type DisputeRemedy = DisputeVerdict;

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
  resolution: string;
}
