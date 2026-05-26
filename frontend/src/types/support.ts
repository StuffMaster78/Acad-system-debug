import type {
  CommunicationEscalationRecord,
  SavedReplyRecord,
  SupportQueueResponse,
  SupportTicketRecord,
  SupportWorkloadResponse,
} from "@/api/adminSupport";

export type {
  CommunicationEscalationRecord,
  SavedReplyRecord,
  SupportQueueResponse,
  SupportTicketRecord,
  SupportWorkloadResponse,
};

export type SupportDeskFilter = "all" | "mine" | "unassigned" | "high_priority" | "overdue" | "escalated";

export interface SupportMetric {
  label: string;
  value: string;
  detail: string;
  tone: "neutral" | "good" | "warn" | "risk";
}

export interface SupportOrderBucket {
  count?: number;
  orders?: Array<Record<string, unknown>>;
  refunds?: Array<Record<string, unknown>>;
}

export interface SupportOrdersDashboard {
  disputed_orders?: SupportOrderBucket;
  payment_issue_orders?: SupportOrderBucket;
  pending_refunds?: SupportOrderBucket;
  orders_with_tickets?: SupportOrderBucket;
  summary?: {
    total_requiring_attention?: number;
  };
}

export interface SupportSlaDashboard {
  metrics?: Record<string, unknown>;
  active_status?: {
    on_track?: number;
    warning?: number;
    breached?: number;
    total_active?: number;
  };
  upcoming_deadlines?: Array<Record<string, unknown>>;
  recent_breaches?: Array<Record<string, unknown>>;
}

export interface SupportAnalytics {
  performance?: Record<string, unknown>;
  trends?: Array<Record<string, unknown>>;
  sla?: Record<string, unknown>;
}
