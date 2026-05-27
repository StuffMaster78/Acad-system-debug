export type SpecialOrderStatus =
  | "draft"
  | "pending_quote"
  | "quote_sent"
  | "quote_accepted"
  | "quote_rejected"
  | "in_progress"
  | "completed"
  | "cancelled";

export type MilestoneStatus =
  | "pending"
  | "in_progress"
  | "submitted"
  | "revision_requested"
  | "approved"
  | "cancelled";

export type QuoteStatus = "draft" | "sent" | "accepted" | "rejected" | "superseded";

export interface SpecialOrder {
  id: number;
  reference: string;
  title: string;
  description: string;
  status: SpecialOrderStatus;
  client_id: number;
  client_username: string;
  assigned_writer_id: number | null;
  writer_username: string | null;
  total_milestones: number;
  completed_milestones: number;
  quoted_price: string | null;
  final_price: string | null;
  currency: string;
  payment_status: string;
  deadline: string | null;
  created_at: string;
  updated_at: string;
  attachments_count: number;
}

export interface Quote {
  id: number;
  special_order_id: number;
  status: QuoteStatus;
  price: string;
  currency: string;
  valid_until: string | null;
  notes: string;
  milestones_preview: { label: string; due_date: string; price: string }[];
  created_by: string;
  created_at: string;
  responded_at: string | null;
  rejection_reason: string | null;
}

export interface SpecialOrderMilestone {
  id: number;
  special_order_id: number;
  sequence: number;
  label: string;
  description: string;
  price: string;
  currency: string;
  due_date: string;
  status: MilestoneStatus;
  writer_id: number | null;
  writer_username: string | null;
  delivery_file_url: string | null;
  delivery_notes: string | null;
  revision_notes: string | null;
  delivered_at: string | null;
  approved_at: string | null;
}

export interface SensitiveAccess {
  portal_url: string | null;
  credentials_hint: string | null;
  notes: string | null;
}

export interface SpecialOrderDetail extends SpecialOrder {
  milestones: SpecialOrderMilestone[];
  quotes: Quote[];
  sensitive_access: SensitiveAccess | null;
  latest_quote: Quote | null;
}

export interface CreateSpecialOrderPayload {
  title: string;
  description: string;
  deadline?: string;
}

export interface SubmitQuotePayload {
  price: string;
  valid_until?: string;
  notes?: string;
  milestones: { label: string; due_date: string; price: string }[];
}

export interface DeliverMilestonePayload {
  delivery_notes?: string;
  delivery_file_url?: string;
}
