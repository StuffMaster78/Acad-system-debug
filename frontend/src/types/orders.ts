export interface OrderSummary {
  id: number;
  topic: string;
  status: string;
  website?: number | null;
  client?: number | null;
  client_username?: string;
  client_email?: string;
  client_registration_id?: string;
  assigned_writer?: number | null;
  writer_username?: string;
  preferred_writer?: number | null;
  payment_status?: string;
  total_price?: string;
  amount_paid?: string;
  remaining_balance?: string;
  writer_compensation?: string | number | null;
  currency?: string;
  service_family?: string;
  service_code?: string;
  paper_type?: number | string | null;
  academic_level?: number | string | null;
  formatting_style?: number | string | null;
  type_of_work?: number | string | null;
  english_type?: number | string | null;
  number_of_pages?: number | string | null;
  number_of_slides?: number | string | null;
  number_of_refereces?: number | string | null;
  spacing?: string;
  subject?: number | string | null;
  subject_is_technical?: boolean;
  discount_code_used?: string;
  is_composite?: boolean;
  is_paid?: boolean;
  is_urgent?: boolean;
  flags?: string[];
  client_deadline?: string;
  writer_deadline?: string | null;
  pricing_snapshot_id?: number | null;
  order_instructions?: string;
  instructions?: string;
  qa_review_note?: string;
  qa_approved_at?: string | null;
  qa_returned_at?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface OrderLifecycle {
  order_id: number;
  order_status: string;
  website_id: number | null;
  client_id: number | null;
  current_assignment_id: number | null;
  current_writer_id: number | null;
  has_current_assignment: boolean;
  active_hold_id: number | null;
  has_active_hold: boolean;
  pending_reassignment_request_id: number | null;
  has_pending_reassignment_request: boolean;
  active_dispute_id: number | null;
  has_active_dispute: boolean;
  latest_adjustment_request_id: number | null;
  latest_adjustment_status: string | null;
  latest_revision_request_id: number | null;
  latest_revision_status: string | null;
  is_revision_window_open: boolean;
  revision_window_days: number;
}

export interface OrderActionResponse {
  message?: string;
  detail?: string;
  order_id?: number;
  status?: string;
  [key: string]: unknown;
}

export interface RevisionRequestPayload {
  reason: string;
  scope_summary: string;
  is_within_original_scope: boolean;
}

export interface CancelOrderPayload {
  reason: string;
  refund_destination: "wallet" | "external";
  notes?: string;
}

export interface CreateOrderPayload {
  topic: string;
  paper_type_id: number;
  academic_level_id?: number | null;
  formatting_style_id?: number | null;
  subject_id?: number | null;
  type_of_work_id?: number | null;
  english_type_id?: number | null;
  writer_level_id?: number | null;
  discount_id?: number | null;
  discount_code_used?: string;
  is_follow_up?: boolean;
  previous_order_id?: number | null;
  preferred_writer_id?: number | null;
  flags?: string[];
  client_id?: number | null;
  client_deadline: string;
  writer_deadline?: string | null;
  is_urgent?: boolean;
  requires_editing?: boolean | null;
  editing_skip_reason?: string;
  order_instructions: string;
  external_contact_name?: string;
  external_contact_email?: string;
  external_contact_phone?: string;
  allow_unpaid_access?: boolean;
  pricing_snapshot_id: number;
  payment_provider?: string;
  payment_method_code?: string;
}

export interface CreateOrderResponse {
  message: string;
  order: OrderSummary;
  checkout_started: boolean;
  payment_intent: Record<string, unknown> | null;
}

export interface PaperQuotePayload {
  service_code: string;
  pages: number;
  deadline_hours: number;
  spacing: "single" | "double";
  paper_type_code: string;
  work_type_code: string;
  subject_code: string;
  academic_level_code: string;
  analysis_level?: string;
  writer_level_code?: string;
  preferred_writer_id?: string;
  selected_addon_codes?: string[];
  topic?: string;
  instructions?: string;
}

export interface OrderNote {
  id: number;
  author_id: number | null;
  author_username: string | null;
  body: string;
  is_pinned: boolean;
  created_at: string | null;
  updated_at: string | null;
}

export interface OrderInterestRecord {
  id: number;
  writer_id: number;
  writer_username: string | null;
  interest_type: string;
  status: string;
  message: string;
  created_at: string | null;
  reviewed_at: string | null;
}

export interface RevisionRequest {
  id: number;
  status: string;
  reason: string;
  scope_summary: string;
  writer_notes: string;
  is_within_free_window: boolean;
  approved_at: string | null;
  submitted_at: string | null;
  accepted_at: string | null;
  rejected_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface RevisionRouteResponse {
  routing: "free_revision" | "paid_adjustment";
  message: string;
  adjustment_request_id?: number;
  status?: string;
}

export interface PaperQuoteStartResponse {
  session_id: string;
  status: string;
  current_step: number;
  estimated_min_price: string | number | null;
  estimated_max_price: string | number | null;
  currency: string;
}

export interface PriceLine {
  line_type: string;
  code: string;
  label: string;
  amount: string | number;
  metadata: Record<string, unknown>;
}

export interface PaperQuoteUpdateResponse {
  session_id: string;
  status: string;
  current_step: number;
  calculated_price: string | number | null;
  currency: string;
  lines: PriceLine[];
}

export interface PricingSnapshotResponse {
  snapshot_id: number;
  final_price: string | number;
  currency: string;
}

export interface PaymentRecord {
  id: number | string;
  amount: string;
  status: string;
  payment_method: string | null;
  payment_type: string | null;
  reference_id: string | null;
  transaction_id: string | null;
  created_at: string | null;
  confirmed_at: string | null;
}

export interface OrderPaymentSummary {
  order_id: number | string;
  currency: string;
  order_total: string;
  amount_paid: string;
  pending_amount: string;
  refunded_amount: string;
  balance_due: string;
  is_fully_paid: boolean;
  last_payment_at: string | null;
  payments: PaymentRecord[];
}
