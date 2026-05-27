import { api, apiPath } from "./client";

export interface FineRecord {
  id: number;
  order_id: number | null;
  order_topic: string | null;
  fine_type_name: string | null;
  amount: string;
  reason: string | null;
  status: string;
  imposed_at: string | null;
  has_appeal: boolean;
  can_dispute: boolean;
  appeal: FineAppealRecord | null;
}

export interface FineAppealRecord {
  id: number;
  fine_id: number;
  fine_amount: string;
  fine_status: string;
  order_topic: string | null;
  reason: string;
  created_at: string;
  reviewed_at: string | null;
  accepted: boolean | null;
  escalated: boolean;
  resolution_notes: string | null;
  events: FineAppealEvent[];
}

export interface FineAppealEvent {
  id: number;
  event_type: string;
  actor_role: string;
  message: string;
  created_at: string;
}

export const finesApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<FineRecord[]>(apiPath("/fines/fines/"), { params }),

  dispute: (fineId: number, reason: string) =>
    api.post<FineRecord>(apiPath(`/fines/fines/${fineId}/dispute/`), { reason }),
};
