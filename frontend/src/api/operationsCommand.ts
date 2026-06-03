import { api, apiPath } from "./client";

export type OperationsPriority = "critical" | "high" | "medium" | "low";

export interface OperationsWebsiteRef {
  id: number | null;
  name: string;
  domain: string | null;
}

export interface OperationsEntityRef {
  type: string;
  id: number;
  label: string;
}

export interface OperationsMeta {
  label: string;
  value: string;
}

export interface OperationsCommandState {
  status: "active" | "acknowledged" | "snoozed" | "resolved";
  note: string;
  snoozed_until: string | null;
  assigned_to: string | null;
  assigned_to_id: number | null;
  assigned_at: string | null;
  updated_by: string | null;
  updated_at: string | null;
  acknowledged_at: string | null;
  resolved_at: string | null;
}

export interface OperationsCommandItem {
  id: string;
  domain: string;
  priority: OperationsPriority;
  score: number;
  title: string;
  description: string;
  website: OperationsWebsiteRef | null;
  entity: OperationsEntityRef;
  action_label: string;
  action_url: string;
  created_at: string | null;
  due_at: string | null;
  meta: OperationsMeta[];
  state: OperationsCommandState;
}

export interface OperationsCommandEvent {
  id: number;
  action: string;
  note: string;
  actor: string | null;
  actor_id: number | null;
  from_status: string;
  to_status: string;
  metadata: Record<string, unknown>;
  created_at: string | null;
}

export interface OperationsCommandHistoryResponse {
  item_id: string;
  events: OperationsCommandEvent[];
}

export interface OperationsCommandSummary {
  critical: number;
  high: number;
  medium: number;
  low: number;
  total: number;
  orders_at_risk: number;
  payments_need_attention: number;
  writer_reviews: number;
  cms_alerts: number;
  support_escalations: number;
  assigned: number;
  unassigned: number;
}

export interface OperationsCommandResponse {
  generated_at: string;
  scope: {
    website_id: number | null;
    website_name: string | null;
    is_cross_tenant: boolean;
  };
  summary: OperationsCommandSummary;
  items: OperationsCommandItem[];
}

export const operationsCommandApi = {
  get(params?: { website_id?: number | null }) {
    return api.get<OperationsCommandResponse>(
      apiPath("/admin-management/operations-command-center/"),
      { params },
    );
  },
  act(payload: {
    item_id: string;
    action: "acknowledge" | "snooze" | "resolve" | "reopen" | "claim" | "release";
    domain: string;
    website_id?: number | null;
    entity: OperationsEntityRef;
    note?: string;
    snooze_hours?: number;
  }) {
    return api.post<{ state: OperationsCommandState }>(
      apiPath("/admin-management/operations-command-center/item-action/"),
      payload,
    );
  },
  history(itemId: string) {
    return api.get<OperationsCommandHistoryResponse>(
      apiPath("/admin-management/operations-command-center/item-history/"),
      { params: { item_id: itemId } },
    );
  },
};
