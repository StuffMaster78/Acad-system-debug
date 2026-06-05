export type SpecialOrderStatus =
  | "inquiry"
  | "quote_pending"
  | "quote_sent"
  | "quote_accepted"
  | "awaiting_payment"
  | "partially_funded"
  | "ready_for_staffing"
  | "assigned"
  | "on_hold"
  | "submitted"
  | "in_progress"
  | "ready_for_delivery"
  | "completed"
  | "cancelled"
  | "approved"
  | "revision_requested"
  | "on_revision"
  | "refunded";

export type MilestoneStatus =
  | "pending"
  | "partially_paid"
  | "paid"
  | "overdue"
  | "cancelled"
  | "refunded";

export type DeliverableStatus = "pending" | "uploaded" | "under_review" | "approved" | "rejected" | "delivered";

export type QuoteStatus = "draft" | "sent" | "accepted" | "rejected" | "superseded";

export interface SpecialOrder {
  id: number;
  reference: string;
  title: string;
  description?: string;
  inquiry_details?: string;
  status: SpecialOrderStatus;
  client_id?: number;
  client?: number;
  client_username?: string;
  assigned_writer_id?: number | null;
  writer?: number | null;
  writer_username?: string | null;
  total_milestones: number;
  completed_milestones: number;
  quoted_price?: string | null;
  currency: string;
  duration_days?: number | null;
  writer_compensation?: { type: "fixed_amount"; amount: string; currency: string } | { type: "percentage"; percentage: string } | null;
  available_actions?: string[];
  blocked_actions?: { action: string; reason: string }[];
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
  price: string | null;
  amount_due?: string | null;
  funded_amount?: string | null;
  balance_amount?: string | null;
  currency: string;
  due_date: string | null;
  due_at?: string | null;
  status: MilestoneStatus;
  funding_status?: MilestoneStatus;
  deliverable_id?: number | null;
  deliverable_status?: DeliverableStatus | null;
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
}

// ── Quoted (estimated) order ──────────────────────────────────────────────────

export interface CreateQuotedSpecialOrderPayload {
  title: string;
  inquiry_details: string;
  budget?: string;
  duration_days?: number;
  currency?: string;
}

// ── Fixed (express) order ─────────────────────────────────────────────────────

export interface CreateFixedSpecialOrderPayload {
  predefined_config_id: number;
  predefined_duration_id: number;
  title?: string;
  inquiry_details?: string;
  currency?: string;
  platform?: string;
  writer_level?: string;
  coupon_code?: string;
}

export interface PredefinedConfigDuration {
  id: number;
  duration_days: number;
  price: string;
  is_active: boolean;
}

export interface PredefinedConfigDurationPayload {
  id?: number;
  duration_days: number;
  price: string;
  is_active: boolean;
}

export interface PredefinedConfig {
  id: number;
  website?: number;
  website_name?: string | null;
  website_domain?: string | null;
  name: string;
  slug: string;
  description: string;
  is_active: boolean;
  requires_full_payment: boolean;
  allow_wallet_payment: boolean;
  allow_external_payment: boolean;
  allow_discounts: boolean;
  durations: PredefinedConfigDuration[];
  created_by_name?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface PredefinedConfigPayload {
  website_id?: number;
  name?: string;
  slug?: string;
  description?: string;
  is_active?: boolean;
  requires_full_payment?: boolean;
  allow_wallet_payment?: boolean;
  allow_external_payment?: boolean;
  allow_discounts?: boolean;
  durations?: PredefinedConfigDurationPayload[];
}

export interface SpecialOrderQuoteSettings {
  id: number;
  default_deposit_percentage: string;
  minimum_deposit_amount: string;
  allow_installments: boolean;
  require_deposit_before_staffing: boolean;
  require_full_payment_before_delivery: boolean;
  quote_expiry_hours: number;
  allow_wallet_payment: boolean;
  allow_external_payment: boolean;
  allow_discounts: boolean;
}

export interface SpecialOrderMilestoneTemplateItem {
  id: number;
  sequence: number;
  label: string;
  percentage: string;
  required_before_staffing: boolean;
  required_before_delivery: boolean;
}

export interface SpecialOrderMilestoneTemplate {
  id: number;
  name: string;
  description: string;
  is_active: boolean;
  items: SpecialOrderMilestoneTemplateItem[];
}

export interface SpecialOrderQuoteConfig {
  settings: SpecialOrderQuoteSettings;
  milestone_templates: SpecialOrderMilestoneTemplate[];
}

export interface FixedPricePreview {
  currency: string;
  base_price: string;
  gross_amount: string;
  discount_amount: string;
  final_amount: string;
  line_items: { label: string; amount: string }[];
  discount: { reference: string | null; metadata: Record<string, unknown> };
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
