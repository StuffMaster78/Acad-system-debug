export interface CancellationRequest {
  id: number;
  order_id: number;
  status: "pending" | "approved" | "rejected";
  reason: string;
  pre_request_status: string;
  forfeiture_pct: string;
  forfeiture_amount: string;
  refund_amount: string;
  reviewed_by: number | null;
  reviewed_at: string | null;
  reviewer_notes: string;
  requested_at: string;
}
