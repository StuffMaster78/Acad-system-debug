export type EditorTaskStatus = "pending" | "in_review" | "completed" | "rejected" | "unclaimed" | string;
export type EditorAssignmentType = "auto" | "manual" | "claimed" | string;

export interface EditorProfile {
  id?: number | string;
  name?: string;
  registration_id?: string;
  email?: string;
  is_active?: boolean;
  orders_reviewed?: number;
  active_tasks_count?: number;
  max_concurrent_tasks?: number;
  can_self_assign?: boolean;
  can_take_more_tasks?: boolean;
  [key: string]: unknown;
}

export interface EditorTask {
  id: number | string;
  order?: number | string;
  order_id?: number | string;
  order_topic?: string;
  order_deadline?: string | null;
  order_status?: string;
  review_status?: EditorTaskStatus;
  assignment_type?: EditorAssignmentType;
  assigned_at?: string;
  started_at?: string | null;
  reviewed_at?: string | null;
  notes?: string | null;
  editor_rating?: number | null;
  [key: string]: unknown;
}

export interface EditorDashboardStats {
  active_tasks?: number;
  pending_tasks?: number;
  in_review_tasks?: number;
  completed_tasks?: number;
  rejected_tasks?: number;
  orders_reviewed?: number;
  available_tasks?: number;
  average_quality_score?: number | string;
  average_review_time_hours?: number | string;
  [key: string]: unknown;
}

export interface EditorPerformance {
  quality_score?: number | string;
  average_quality_score?: number | string;
  total_reviews?: number;
  reviews_completed?: number;
  average_review_time_hours?: number | string;
  on_time_completion_rate?: number | string;
  revision_rate?: number | string;
  last_calculated_at?: string;
  [key: string]: unknown;
}

export interface EditorAnalytics {
  status_breakdown?: Record<string, number>;
  assignment_breakdown?: Record<string, number>;
  weekly_tasks?: Array<{ week?: string | null; count: number }>;
  urgent_tasks_count?: number;
  overdue_tasks_count?: number;
  total_tasks?: number;
}

export interface EditorWorkload {
  current_workload?: {
    active_tasks_count?: number;
    max_concurrent_tasks?: number;
    capacity_percentage?: number;
    available_slots?: number;
    is_at_capacity?: boolean;
    can_take_more?: boolean;
  };
  deadline_analysis?: {
    urgent_tasks?: number;
    overdue_tasks?: number;
    total_with_deadlines?: number;
  };
  time_estimates?: {
    estimated_hours_until_all_deadlines?: number;
    average_hours_per_task?: number;
  };
  recommendations?: {
    recommended_max_orders?: number;
    should_claim_more?: boolean;
    should_focus_on_urgent?: boolean;
  };
}

export interface EditorActivityLog {
  id: number | string;
  action_type?: string;
  action?: string;
  order_id?: number | string | null;
  order_topic?: string | null;
  timestamp?: string | null;
}

export interface EditorReviewSummary {
  id: number | string;
  order_id?: number | string | null;
  order_topic?: string | null;
  quality_score?: number | string | null;
  is_approved?: boolean;
  requires_revision?: boolean;
  submitted_at?: string | null;
}

export interface EditorActivityBundle {
  activity_logs?: EditorActivityLog[];
  recent_reviews?: EditorReviewSummary[];
  recent_assignments?: EditorTask[];
}

export interface AvailableEditorTasksResponse {
  tasks: EditorTask[];
  count: number;
  total_available: number;
  filters_applied?: Record<string, unknown>;
}

export interface SubmitEditorReviewPayload {
  task_id: number | string;
  quality_score?: number | string | null;
  issues_found?: string;
  corrections_made?: string;
  recommendations?: string;
  is_approved?: boolean;
  requires_revision?: boolean;
  revision_notes?: string;
  edited_files?: number[];
}
