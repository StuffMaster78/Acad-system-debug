export type AdjustmentKind = "scope_increment" | "extra_service";

export type AdjustmentType =
  | "page_increase"
  | "slide_increase"
  | "diagram_increase"
  | "design_concept_increase"
  | "scope_expansion"
  | "extra_service"
  | "paid_revision"
  | "deadline_decrease"
  | "other";

export type AdjustmentStatus =
  | "pending_client_response"
  | "client_countered"
  | "accepted"
  | "declined"
  | "funding_pending"
  | "funded"
  | "counter_funded_final"
  | "approved_by_staff"
  | "rejected_by_client"
  | "rejected_by_staff"
  | "cancelled"
  | "expired"
  | "reversed";

export type ScopeUnitType =
  | "page"
  | "slide"
  | "diagram"
  | "design_concept"
  | "section"
  | "deadline"
  | "other";

export interface AdjustmentProposal {
  id: number;
  proposal_role: "system" | "client" | "writer" | "staff";
  proposal_type: "system_quote" | "client_counter" | "staff_override" | "final_agreement";
  unit_type: ScopeUnitType | null;
  currency: string | null;
  amount: string | null;
  scope_payload: Record<string, unknown>;
  is_active: boolean;
  created_at: string;
}

export interface AdjustmentRequest {
  id: number;
  order_id: number;
  status: AdjustmentStatus;
  adjustment_kind: AdjustmentKind;
  adjustment_type: AdjustmentType | null;
  title: string;
  description: string | null;
  unit_type: ScopeUnitType | null;
  extra_service_code: string | null;

  current_quantity: number | null;
  requested_quantity: number | null;
  countered_quantity: number | null;
  quantity_delta: number | null;

  request_total_amount: string | null;
  counter_total_amount: string | null;
  request_writer_compensation_amount: string | null;
  counter_writer_compensation_amount: string | null;

  requested_by_id: number | null;
  reviewed_by_id: number | null;

  proposals: AdjustmentProposal[];

  is_counter_final: boolean;
  escalated_after_counter: boolean;

  expires_at: string | null;
  accepted_at: string | null;
  declined_at: string | null;
  funded_at: string | null;
  applied_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface StaffAdjustmentInboxItem extends AdjustmentRequest {
  order_reference: string;
  order_topic: string;
  order_status: string;
  website_id: number | null;
  website_name: string | null;
  client_id: number | null;
  client_name: string;
  writer_id: number | null;
  writer_name: string;
  requires_staff_attention: boolean;
}

export interface StaffAdjustmentInboxResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: StaffAdjustmentInboxItem[];
}

export interface CreateScopeIncrementPayload {
  adjustment_type: AdjustmentType;
  unit_type: ScopeUnitType;
  requested_quantity: number;
  title: string;
  description?: string;
  writer_justification?: string;
  client_visible_note?: string;
}

export interface CreateExtraServicePayload {
  extra_service_code: string;
  title: string;
  description?: string;
  writer_justification?: string;
  client_visible_note?: string;
}
