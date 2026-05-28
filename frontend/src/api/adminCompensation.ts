import { api, apiPath } from "./client";

type PageResponse<T> = { count: number; next: string | null; previous: string | null; results: T[] } | T[];

const base = (path: string) => apiPath(`/writer-compensation/api${path}`);

// ── Interfaces ──────────────────────────────────────────────────────────────

export interface PaymentWindow {
  id: number;
  cycle_type: string;
  start_date: string;
  end_date: string;
  status: string;
  is_locked: boolean;
  is_editable: boolean;
  closed_at: string | null;
  processing_at: string | null;
  done_at: string | null;
  created_at: string;
}

export interface PayoutRecord {
  id: number;
  writer_name: string;
  writer_email: string;
  total_amount: string;
  status: string;
  hold_reason: string | null;
  confirmed_at: string | null;
  confirmed_by_name: string | null;
  paid_at: string | null;
  paid_by_name: string | null;
  notes: string | null;
}

export interface PayoutBatch {
  id: number;
  payment_window: PaymentWindow;
  total_amount: string;
  total_writers: number;
  status: string;
  paid_at: string | null;
  paid_count: number;
  held_count: number;
  pending_count: number;
  notes: string | null;
  records: PayoutRecord[];
  created_at: string;
}

export interface CycleChangeRequest {
  id: number;
  writer_name: string;
  from_cycle: string;
  requested_cycle: string;
  reason: string | null;
  status: string;
  rejection_reason: string | null;
  reviewed_at: string | null;
  created_at: string;
}

export interface SettlementItem {
  id: number;
  financial_event: number;
  amount: string;
  created_at: string;
}

export interface Settlement {
  id: number;
  website: number | null;
  writer: number;
  payment_window: number;
  status: string;
  gross_earnings: string;
  total_tips: string;
  total_bonuses: string;
  total_adjustments: string;
  total_fines: string;
  total_deductions: string;
  total_advances: string;
  total_reversals: string;
  net_payable: string;
  total_financial_events: number;
  total_settlement_items: number;
  is_locked: boolean;
  locked_at: string | null;
  finalized_at: string | null;
  created_at: string;
  updated_at: string;
  items: SettlementItem[];
}

export interface AdvanceRecovery {
  id: number;
  amount: string;
  settlement_period: number | null;
  notes: string | null;
  recovered_at: string;
}

export interface AdvanceRequest {
  id: number;
  writer_name: string;
  payment_window: number | null;
  status: string;
  requested_amount: string;
  approved_amount: string | null;
  recovered_amount: string;
  outstanding_balance: string;
  reason: string;
  admin_notes: string | null;
  reviewed_at: string | null;
  created_at: string;
  recoveries: AdvanceRecovery[];
}

export interface WindowSummary {
  total_gross: string;
  total_net: string;
  total_writers: number;
  total_batches: number;
  [key: string]: unknown;
}

export interface WriterWindowDetail {
  events: Record<string, unknown>[];
  gross: string;
  deductions: string;
  net: string;
  count: number;
  breakdown: Record<string, unknown>[];
}

// ── API ─────────────────────────────────────────────────────────────────────

export const adminCompensationApi = {
  // ── Payout Windows ─────────────────────────────────────────────────────────
  windows: (params?: Record<string, unknown>) =>
    api.get<PageResponse<PaymentWindow>>(base("/admin/windows/"), { params }),
  createWindow: (payload: { cycle_type: string; start_date: string; end_date: string }) =>
    api.post<PaymentWindow>(base("/admin/windows/"), payload),
  windowDetail: (windowId: number) =>
    api.get<PaymentWindow>(base(`/admin/windows/${windowId}/`)),
  windowSummary: (windowId: number) =>
    api.get<WindowSummary>(base(`/admin/windows/${windowId}/summary/`)),
  closeWindow: (windowId: number) =>
    api.post<{ detail: string }>(base(`/admin/windows/${windowId}/close/`), {}),
  startProcessing: (windowId: number) =>
    api.post<{ detail: string }>(base(`/admin/windows/${windowId}/start-processing/`), {}),
  markDone: (windowId: number) =>
    api.post<{ detail: string }>(base(`/admin/windows/${windowId}/mark-done/`), {}),
  adjustWindow: (windowId: number, payload: Record<string, unknown>) =>
    api.post<{ detail: string }>(base(`/admin/windows/${windowId}/adjust/`), payload),
  writerWindowEvents: (windowId: number, writerId: number) =>
    api.get<WriterWindowDetail>(base(`/admin/windows/${windowId}/writers/${writerId}/events/`)),

  // ── Batches ────────────────────────────────────────────────────────────────
  batchDetail: (batchId: number) =>
    api.get<PayoutBatch>(base(`/admin/batches/${batchId}/`)),
  bulkConfirm: (batchId: number) =>
    api.post<{ detail: string }>(base(`/admin/batches/${batchId}/bulk-confirm/`), {}),
  bulkMarkPaid: (batchId: number) =>
    api.post<{ detail: string }>(base(`/admin/batches/${batchId}/bulk-mark-paid/`), {}),

  // ── Payout items ───────────────────────────────────────────────────────────
  confirmPayout: (itemId: number) =>
    api.post<PayoutRecord>(base(`/admin/payout-items/${itemId}/confirm/`), {}),
  markPaid: (itemId: number, notes?: string) =>
    api.post<PayoutRecord>(base(`/admin/payout-items/${itemId}/mark-paid/`), { notes: notes ?? "" }),
  holdPayout: (itemId: number, reason: string) =>
    api.post<PayoutRecord>(base(`/admin/payout-items/${itemId}/hold/`), { reason }),
  releasePayout: (itemId: number) =>
    api.post<PayoutRecord>(base(`/admin/payout-items/${itemId}/release/`), {}),

  // ── Cycle changes ──────────────────────────────────────────────────────────
  cycleChanges: (params?: Record<string, unknown>) =>
    api.get<PageResponse<CycleChangeRequest>>(base("/admin/cycle-changes/"), { params }),
  approveCycleChange: (requestId: number) =>
    api.post<{ detail: string }>(base(`/admin/cycle-changes/${requestId}/approve/`), {}),
  rejectCycleChange: (requestId: number, rejection_reason?: string) =>
    api.post<{ detail: string }>(base(`/admin/cycle-changes/${requestId}/reject/`), { rejection_reason: rejection_reason ?? "" }),

  // ── Earnings & bonuses ─────────────────────────────────────────────────────
  windowEarnings: (windowId: number) =>
    api.get<Record<string, unknown>>(base(`/admin/windows/${windowId}/earnings/`)),
  writerEarnings: (writerId: number, params: { from_date: string; to_date: string }) =>
    api.get<Record<string, unknown>>(base(`/admin/writers/${writerId}/earnings/`), { params }),
  writerBonuses: (writerId: number) =>
    api.get<Record<string, unknown>[]>(base(`/admin/writers/${writerId}/bonuses/`)),
  applyMilestoneBonus: (writerId: number, payload: Record<string, unknown>) =>
    api.post<{ detail: string }>(base(`/admin/writers/${writerId}/bonuses/milestone/`), payload),
  applyPerformanceBonus: (writerId: number, payload: Record<string, unknown>) =>
    api.post<{ detail: string }>(base(`/admin/writers/${writerId}/bonuses/performance/`), payload),
  applyRetentionBonus: (writerId: number, payload: Record<string, unknown>) =>
    api.post<{ detail: string }>(base(`/admin/writers/${writerId}/bonuses/retention/`), payload),

  // ── Settlements ────────────────────────────────────────────────────────────
  settlements: (params?: Record<string, unknown>) =>
    api.get<PageResponse<Settlement>>(base("/settlements/"), { params }),
  settlementDetail: (id: number) =>
    api.get<Settlement>(base(`/settlements/${id}/`)),
  runSettlement: (payload: Record<string, unknown>) =>
    api.post<{ detail: string }>(base("/settlements/run/"), payload),

  // ── Advances (admin) ───────────────────────────────────────────────────────
  advances: (params?: Record<string, unknown>) =>
    api.get<PageResponse<AdvanceRequest>>(base("/advances/admin/"), { params }),
  approveAdvance: (id: number, approved_amount: string, admin_notes?: string) =>
    api.post<AdvanceRequest>(base(`/advances/admin/${id}/approve/`), { approved_amount, admin_notes: admin_notes ?? "" }),
  rejectAdvance: (id: number) =>
    api.post<AdvanceRequest>(base(`/advances/admin/${id}/reject/`), {}),
  recoverAdvance: (id: number, amount: string, notes?: string) =>
    api.post<AdvanceRequest>(base(`/advances/admin/${id}/recover/`), { amount, notes: notes ?? "" }),
};
