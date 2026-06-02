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

export interface ClassOrderDetail extends ClassOrder {
  tasks: ClassTask[];
  installments: ClassInstallment[];
  portal_access: PortalAccess | null;
}

export interface CreateClassOrderPayload {
  title: string;
  subject: string;
  academic_level: string;
  start_date: string;
  end_date: string;
  notes?: string;
  portal_access_enabled?: boolean;
}

export interface SubmitTaskPayload {
  submission_notes?: string;
  submission_file_url?: string;
}

export interface GradeTaskPayload {
  grade: string;
  grade_feedback?: string;
}
