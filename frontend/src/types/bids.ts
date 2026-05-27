export type BidStatus = "pending" | "accepted" | "rejected" | "withdrawn" | "expired";

export interface Bid {
  id: number;
  order_id: number;
  order_topic: string;
  writer_id: number;
  writer_username: string;
  writer_rating: number | null;
  price: string;
  currency: string;
  delivery_hours: number;
  pitch: string;
  status: BidStatus;
  created_at: string;
  responded_at: string | null;
  rejection_reason: string | null;
}

export interface SubmitBidPayload {
  price: string;
  delivery_hours: number;
  pitch?: string;
}

export interface BidSummary {
  order_id: number;
  total_bids: number;
  pending_bids: number;
  bids: Bid[];
}
