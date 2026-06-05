export type ClassStatus =
  | "draft"
  | "submitted"
  | "needs_client_info"
  | "under_review"
  | "price_proposed"
  | "negotiating"
  | "accepted"
  | "pending_payment"
  | "partially_paid"
  | "paid"
  | "assigned"
  | "in_progress"
  | "pending"
  | "active"
  | "paused"
  | "quality_review"
  | "completed"
  | "cancelled"
  | "archived";

export type ClassTaskStatus =
  | "pending"
  | "assigned"
  | "in_progress"
  | "submitted"
  | "revision_requested"
  | "approved"
  | "completed"
  | "cancelled";

export type InstallmentStatus = "pending" | "due" | "paid" | "overdue" | "waived" | "cancelled";

export interface ClassOrder {
  id: number;
  reference: string;
  title: string;
  subject: string;
  academic_level: string;
  status: ClassStatus;
  client_id: number;
  client_username: string;
  assigned_writer_id: number | null;
  writer_username: string | null;
  total_tasks: number;
  completed_tasks: number;
  total_price: string;
  currency: string;
  payment_status: string;
  portal_access_enabled: boolean;
  start_date: string;
  end_date: string;
  created_at: string;
  updated_at: string;
  notes?: string;
  available_actions?: string[];
  blocked_actions?: { action: string; reason: string }[];
}

export interface ClassTask {
  id: number;
  class_order_id: number;
  sequence: number;
  title: string;
  description: string;
  due_date: string;
  status: ClassTaskStatus;
  writer_id: number | null;
  writer_username: string | null;
  submission_file_url: string | null;
  submission_notes: string | null;
  grade: string | null;
  grade_feedback: string | null;
  submitted_at: string | null;
  approved_at: string | null;
  created_at: string;
}

export interface ClassInstallment {
  id: number;
  class_order_id: number;
  label: string;
  amount: string;
  currency: string;
  due_date: string;
  status: InstallmentStatus;
  paid_at: string | null;
  payment_reference: string | null;
}

export interface PortalAccess {
  enabled: boolean;
  portal_url: string | null;
  username: string | null;
  password_hint: string | null;
  notes: string | null;
  last_accessed_at: string | null;
}

export interface ClassConfigOption {
  key: string;
  label: string;
  description?: string;
  weeks?: number;
  complexity?: string;
  price_hint?: string;
  required?: boolean;
}

export interface ClassServiceConfig {
  id: number;
  website?: number;
  website_name?: string | null;
  website_domain?: string | null;
  name: string;
  slug: string;
  description: string;
  service_type: string;
  pricing_mode: "quote" | "package";
  base_price: string;
  currency: string;
  duration_options: ClassConfigOption[];
  workload_options: ClassConfigOption[];
  task_options: ClassConfigOption[];
  required_fields: string[];
  requires_portal_access: boolean;
  allow_installments: boolean;
  require_deposit_before_start: boolean;
  deposit_percentage: string;
  quote_expiry_hours: number;
  is_active: boolean;
  display_order: number;
  created_by_name?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface ClassPricingSnapshot {
  source?: string;
  config_id?: number;
  config_name?: string;
  config_slug?: string;
  service_type?: string;
  pricing_mode?: "quote" | "package" | string;
  base_price?: string;
  currency?: string;
  payment_policy?: {
    allow_installments?: boolean;
    require_deposit_before_start?: boolean;
    deposit_percentage?: string;
    quote_expiry_hours?: number;
  };
  selected_duration?: ClassConfigOption | null;
  selected_workload?: ClassConfigOption | null;
  selected_tasks?: ClassConfigOption[];
  portal_access_enabled?: boolean;
}

export interface ClassOrderDetail extends ClassOrder {
  tasks: ClassTask[];
  installments: ClassInstallment[];
  portal_access: PortalAccess | null;
  pricing_snapshot?: ClassPricingSnapshot;
}

export interface CreateClassOrderPayload {
  title: string;
  subject: string;
  academic_level: string;
  start_date: string;
  end_date: string;
  notes?: string;
  portal_access_enabled?: boolean;
  class_config_id?: number;
  duration_key?: string;
  workload_key?: string;
  selected_task_keys?: string[];
}

export interface SubmitTaskPayload {
  submission_notes?: string;
  submission_file_url?: string;
}

export interface GradeTaskPayload {
  grade: string;
  grade_feedback?: string;
}
