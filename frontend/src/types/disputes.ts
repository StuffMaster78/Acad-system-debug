export type DisputeStatus = "open" | "under_review" | "resolved" | "closed" | "withdrawn";

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
  resolution: string;
}
