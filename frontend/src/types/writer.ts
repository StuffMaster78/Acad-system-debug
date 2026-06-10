export type WriterOnboardingStatus =
  | "not_started"
  | "in_progress"
  | "documents_pending"
  | "review_pending"
  | "rejected"
  | "completed";

export interface WriterProfile {
  id?: number | string;
  registration_id?: string;
  display_name?: string;
  email?: string;
  phone_number?: string | null;
  writer_level?: string | { name?: string; label?: string };
  rating?: number | string;
  status?: string;
  is_accepting_orders?: boolean;
  onboarding_status?: WriterOnboardingStatus;
  rejection_reason?: string | null;
  [key: string]: unknown;
}

export interface AvailabilityWindow {
  id: number;
  start_at: string;
  end_at?: string | null;
  reason?: string;
  note?: string;
  [key: string]: unknown;
}

export interface WriterAvailability {
  active_window: AvailabilityWindow | null;
  upcoming_windows: AvailabilityWindow[];
}

export interface WriterCurrentWindow {
  window: Record<string, unknown> | null;
  net: string;
  count: number;
  is_processing: boolean;
  [key: string]: unknown;
}

export interface WriterBalance {
  pending: string | number;
  lifetime: string | number;
}

export interface WriterCompensationSummary {
  total_earned?: string | number;
  total_paid?: string | number;
  total_pending?: string | number;
  completed_orders?: number;
  [key: string]: unknown;
}

export interface WriterEvent {
  id?: number | string;
  event_type?: string;
  status?: string;
  amount?: string | number;
  net_amount?: string | number;
  created_at?: string;
  description?: string;
  [key: string]: unknown;
}

export interface StaffingActionResponse {
  message: string;
  order_id?: number;
  interest_id?: number;
  assignment_id?: number;
  status?: string;
  source?: string;
}
