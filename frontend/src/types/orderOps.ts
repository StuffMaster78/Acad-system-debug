export type OrderOpsQueueKey =
  | "late"
  | "critical"
  | "awaiting_approval"
  | "awaiting_acknowledgement"
  | "pending_staffing"
  | "preferred_writer_pending"
  | "eligible_for_archive";

export interface OrderOpsCounts {
  late_orders: number;
  critical_orders: number;
  awaiting_approval: number;
  awaiting_acknowledgement: number;
  pending_staffing: number;
  preferred_writer_pending: number;
  eligible_for_archive: number;
}

export interface OrderOpsRow {
  id: number;
  topic: string;
  status: string;
  payment_status: string;
  total_price: string;
  amount_paid: string;
  client_deadline: string | null;
  writer_deadline: string | null;
  preferred_writer_status: string;
  client_id: number | null;
  preferred_writer_id: number | null;
  available_actions?: string[];
}

export interface OrderOpsQueueResponse {
  queue_key: OrderOpsQueueKey;
  count: number;
  results: OrderOpsRow[];
}

export interface OrderOpsQueueDefinition {
  key: OrderOpsQueueKey;
  countKey: keyof OrderOpsCounts;
  label: string;
  description: string;
  tone: "neutral" | "good" | "warn" | "risk";
}
