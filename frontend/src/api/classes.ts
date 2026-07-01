import { api, apiPath } from "./client";
import type {
  ClassOrder,
  ClassOrderDetail,
  ClassTask,
  ClassInstallment,
  ClassServiceConfig,
  PortalAccess,
  CreateClassOrderPayload,
  SubmitTaskPayload,
  GradeTaskPayload,
} from "@/types/classes";

const base = (path: string) => apiPath(`/class-management${path}`);

type ApiPage<T> = { count: number; next: string | null; previous: string | null; results: T[] };
type ApiRecord = Record<string, unknown>;

function asRecord(value: unknown): ApiRecord {
  return value && typeof value === "object" ? value as ApiRecord : {};
}

function asString(value: unknown, fallback = ""): string {
  if (value === null || value === undefined) return fallback;
  return String(value);
}

function asNumber(value: unknown, fallback = 0): number {
  const next = Number(value);
  return Number.isFinite(next) ? next : fallback;
}

function normalizeClassOrder(raw: unknown): ClassOrder {
  const row = asRecord(raw);
  const id = asNumber(row.id);
  const assignedWriter = row.assigned_writer ?? row.assigned_writer_id;
  const client = row.client ?? row.client_id;
  const finalAmount = row.final_amount ?? row.total_price ?? row.accepted_amount ?? row.quoted_amount ?? "0.00";
  const completedTasks = asNumber(row.completed_tasks);
  const totalTasks = asNumber(row.total_tasks);

  return {
    id,
    reference: asString(row.reference, id ? `CLS-${id}` : "CLS"),
    title: asString(row.title, "Untitled class"),
    subject: asString(row.subject ?? row.class_subject),
    academic_level: asString(row.academic_level),
    status: asString(row.status, "pending") as ClassOrder["status"],
    client_id: asNumber(client),
    client_username: asString(row.client_username ?? row.client_name ?? client, client ? `Client #${client}` : ""),
    assigned_writer_id: assignedWriter === null || assignedWriter === undefined ? null : asNumber(assignedWriter),
    writer_username: assignedWriter === null || assignedWriter === undefined
      ? null
      : asString(row.writer_username ?? row.assigned_writer_name ?? assignedWriter),
    total_tasks: totalTasks,
    completed_tasks: completedTasks,
    total_price: asString(finalAmount, "0.00"),
    currency: asString(row.currency, "USD"),
    payment_status: asString(row.payment_status, "unpaid"),
    portal_access_enabled: Boolean(row.portal_access_enabled ?? row.class_portal_url ?? row.has_access_detail),
    start_date: asString(row.start_date ?? row.starts_on),
    end_date: asString(row.end_date ?? row.ends_on),
    created_at: asString(row.created_at),
    updated_at: asString(row.updated_at),
    notes: asString(row.notes ?? row.initial_client_notes ?? row.writer_visible_notes),
    available_actions: Array.isArray(row.available_actions) ? row.available_actions.map(String) : undefined,
    blocked_actions: Array.isArray(row.blocked_actions)
      ? row.blocked_actions.map((item) => {
          const action = asRecord(item);
          return {
            action: asString(action.action),
            reason: asString(action.reason),
          };
        })
      : undefined,
  };
}

function normalizeTask(raw: unknown): ClassTask {
  const row = asRecord(raw);
  const id = asNumber(row.id);
  const writer = row.assigned_writer ?? row.writer_id;
  const due = row.due_date ?? row.due_at;
  const portalSubmittedAt = row.portal_submitted_at;

  return {
    id,
    class_order_id: asNumber(row.class_order ?? row.class_order_id),
    sequence: asNumber(row.sequence, id),
    title: asString(row.title, "Untitled task"),
    description: asString(row.description ?? row.client_visible_notes ?? row.writer_notes),
    due_date: asString(due),
    status: asString(row.status, "pending") as ClassTask["status"],
    writer_id: writer === null || writer === undefined ? null : asNumber(writer),
    writer_username: writer === null || writer === undefined ? null : asString(row.writer_username ?? row.assigned_writer_name ?? writer),
    submission_file_url: row.submission_file_url === null || row.submission_file_url === undefined ? null : asString(row.submission_file_url),
    submission_notes: asString(row.submission_notes ?? row.portal_submission_notes ?? row.writer_notes) || null,
    grade: row.grade === null || row.grade === undefined ? null : asString(row.grade),
    grade_feedback: row.grade_feedback === null || row.grade_feedback === undefined ? null : asString(row.grade_feedback),
    submitted_at: row.submitted_at === null || row.submitted_at === undefined ? null : asString(row.submitted_at),
    approved_at: row.approved_at === null || row.approved_at === undefined ? null : asString(row.approved_at ?? row.completed_at ?? portalSubmittedAt),
    created_at: asString(row.created_at),
  };
}

function normalizeInstallment(raw: unknown): ClassInstallment {
  const row = asRecord(raw);
  const metadata = asRecord(row.metadata);
  return {
    id: asNumber(row.id),
    class_order_id: asNumber(row.class_order ?? row.class_order_id ?? row.plan),
    label: asString(row.label, "Payment"),
    amount: asString(row.amount, "0.00"),
    currency: asString(row.currency, "USD"),
    due_date: asString(row.due_date ?? row.due_at),
    status: asString(row.status, "pending") as ClassInstallment["status"],
    paid_at: row.paid_at === null || row.paid_at === undefined ? null : asString(row.paid_at),
    payment_reference: row.payment_reference === null || row.payment_reference === undefined
      ? asString(row.payment_intent_id ?? row.invoice_id ?? metadata.payment_reference) || null
      : asString(row.payment_reference),
  };
}

function normalizePortalAccess(raw: unknown): PortalAccess {
  const row = asRecord(raw);
  return {
    enabled: Boolean(row.enabled ?? row.class_portal_url ?? row.login_username),
    portal_url: row.portal_url === null || row.portal_url === undefined ? asString(row.class_portal_url) || null : asString(row.portal_url),
    username: row.username === null || row.username === undefined ? asString(row.login_username) || null : asString(row.username),
    password_hint: row.password_hint === null || row.password_hint === undefined ? asString(row.login_password) || null : asString(row.password_hint),
    notes: row.notes === null || row.notes === undefined ? asString(row.extra_login_notes) || null : asString(row.notes),
    last_accessed_at: row.last_accessed_at === null || row.last_accessed_at === undefined ? null : asString(row.last_accessed_at),
  };
}

function classCreatePayload(payload: CreateClassOrderPayload): ApiRecord {
  return {
    class_config_id: payload.class_config_id ?? null,
    duration_key: payload.duration_key ?? "",
    workload_key: payload.workload_key ?? "",
    selected_task_keys: payload.selected_task_keys ?? [],
    portal_access_enabled: Boolean(payload.portal_access_enabled),
    title: payload.title,
    class_subject: payload.subject,
    academic_level: payload.academic_level,
    starts_on: payload.start_date || null,
    ends_on: payload.end_date || null,
    initial_client_notes: payload.notes ?? "",
  };
}

function classUpdatePayload(payload: Partial<CreateClassOrderPayload>): ApiRecord {
  const data: ApiRecord = {};
  if (payload.title !== undefined) data.title = payload.title;
  if (payload.subject !== undefined) data.class_subject = payload.subject;
  if (payload.academic_level !== undefined) data.academic_level = payload.academic_level;
  if (payload.start_date !== undefined) data.starts_on = payload.start_date || null;
  if (payload.end_date !== undefined) data.ends_on = payload.end_date || null;
  if (payload.notes !== undefined) data.initial_client_notes = payload.notes;
  return data;
}

function portalAccessPayload(payload: Partial<PortalAccess>): ApiRecord {
  return {
    class_portal_url: payload.portal_url ?? "",
    login_username: payload.username ?? "",
    login_password: payload.password_hint ?? "",
    extra_login_notes: payload.notes ?? "",
  };
}

function normalizeListResponse<T>(data: unknown[] | ApiPage<unknown>, mapper: (item: unknown) => T): T[] | ApiPage<T> {
  if (Array.isArray(data)) return data.map(mapper);
  return { ...data, results: data.results.map(mapper) };
}

export const classesApi = {
  configs: (params?: Record<string, unknown>) =>
    api.get<ClassServiceConfig[]>(base("/configs/"), { params }),

  createConfig: (payload: Partial<ClassServiceConfig>, params?: Record<string, unknown>) =>
    api.post<ClassServiceConfig>(base("/configs/"), payload, { params }),

  updateConfig: (id: number | string, payload: Partial<ClassServiceConfig>, params?: Record<string, unknown>) =>
    api.patch<ClassServiceConfig>(base(`/configs/${id}/`), payload, { params }),

  seedConfigDefaults: (params?: Record<string, unknown>) =>
    api.post<{ created: number; updated: number }>(base("/configs/seed-defaults/"), {}, { params }),

  list: (params?: Record<string, unknown>) =>
    api.get<unknown[] | ApiPage<unknown>>(
      base("/classes/"),
      { params },
    ).then((res) => ({ ...res, data: normalizeListResponse(res.data, normalizeClassOrder) })),

  get: (id: number | string) =>
    api.get<unknown>(base(`/classes/${id}/`))
      .then((res) => ({
        ...res,
        data: {
          ...normalizeClassOrder(res.data),
          tasks: [],
          installments: [],
          portal_access: null,
          pricing_snapshot: asRecord(asRecord(res.data).pricing_snapshot),
        } satisfies ClassOrderDetail,
      })),

  create: (payload: CreateClassOrderPayload) =>
    api.post<unknown>(base("/classes/"), classCreatePayload(payload))
      .then((res) => ({ ...res, data: normalizeClassOrder(res.data) })),

  update: (id: number | string, payload: Partial<CreateClassOrderPayload>) =>
    api.patch<unknown>(base(`/classes/${id}/`), classUpdatePayload(payload))
      .then((res) => ({ ...res, data: normalizeClassOrder(res.data) })),

  assignWriter: (id: number | string, writerId: number) =>
    api.post(base(`/classes/${id}/assignments/`), { writer_id: writerId }),

  manualVerifyPayment: (id: number | string, payload: {
    amount: string;
    transaction_reference: string;
    verification_note: string;
    payment_method?: string;
  }) =>
    api.post(base(`/classes/${id}/payments/manual-verify/`), payload),

  cancel: (id: number | string, reason?: string) =>
    api.post<unknown>(base(`/classes/${id}/cancel/`), { reason })
      .then((res) => ({ ...res, data: normalizeClassOrder(res.data) })),

  startWork: (id: number | string) =>
    api.post<unknown>(base(`/classes/${id}/start-work/`), {})
      .then((res) => ({ ...res, data: normalizeClassOrder(res.data) })),

  complete: (id: number | string) =>
    api.post<unknown>(base(`/classes/${id}/complete/`), {})
      .then((res) => ({ ...res, data: normalizeClassOrder(res.data) })),

  availableActions: (id: number | string) =>
    api.get<{ available_actions: string[]; blocked_actions: { action: string; reason: string }[] }>(
      base(`/classes/${id}/available-actions/`),
    ),

  tasks: {
    list: (classId: number | string) =>
      api.get<unknown[]>(base(`/classes/${classId}/tasks/`))
        .then((res) => ({ ...res, data: res.data.map(normalizeTask) })),

    create: (classId: number | string, payload: { title: string; description: string; due_date: string; sequence?: number }) =>
      api.post<unknown>(base(`/classes/${classId}/tasks/`), {
        title: payload.title,
        description: payload.description,
        due_at: payload.due_date || null,
      }).then((res) => ({ ...res, data: normalizeTask(res.data) })),

    submit: (classId: number | string, taskId: number | string, payload: SubmitTaskPayload) =>
      api.post<unknown>(base(`/classes/${classId}/tasks/${taskId}/submit/`), {
        notes: payload.submission_notes ?? "",
        portal_submitted: Boolean(payload.submission_file_url),
      }).then((res) => ({ ...res, data: normalizeTask(res.data) })),

    grade: (classId: number | string, taskId: number | string, payload: GradeTaskPayload) =>
      api.post<unknown>(base(`/classes/${classId}/tasks/${taskId}/complete/`), {
        notes: [payload.grade, payload.grade_feedback].filter(Boolean).join(" - "),
      }).then((res) => ({ ...res, data: normalizeTask(res.data) })),

    cancel: (classId: number | string, taskId: number | string, notes: string) =>
      api.post<unknown>(base(`/classes/${classId}/tasks/${taskId}/cancel/`), { notes })
        .then((res) => ({ ...res, data: normalizeTask(res.data) })),
  },

  installments: {
    list: (classId: number | string) =>
      api.get<unknown[]>(base(`/classes/${classId}/payments/installments/`))
        .then((res) => ({ ...res, data: res.data.map(normalizeInstallment) })),

    createPlan: (classId: number | string, payload: {
      milestone_count: number;
      due_dates: string[];
      deposit_amount?: string;
      allow_work_before_full_payment?: boolean;
      pause_work_when_overdue?: boolean;
      notes?: string;
    }) =>
      api.post<unknown>(base(`/classes/${classId}/payments/create-equal-installments/`), payload),

    preparePayment: (
      classId: number | string,
      payload: { amount: string | number; use_wallet?: boolean; installment_id?: number | string },
    ) =>
      api.post(base(`/classes/${classId}/payments/prepare/`), payload),

    waive: (classId: number | string, installmentId: number | string, reason = "") =>
      api.post<unknown>(base(`/classes/${classId}/payments/installments/${installmentId}/waive/`), { reason })
        .then((res) => ({ ...res, data: normalizeInstallment(res.data) })),

    edit: (classId: number | string, installmentId: number | string, payload: {
      label?: string;
      amount?: string;
      due_at?: string;
    }) =>
      api.patch<unknown>(base(`/classes/${classId}/payments/installments/${installmentId}/edit/`), payload)
        .then((res) => ({ ...res, data: normalizeInstallment(res.data) })),

    markPaid: (classId: number | string, installmentId: number | string, payload: {
      transaction_reference?: string;
      note?: string;
    }) =>
      api.post<unknown>(base(`/classes/${classId}/payments/installments/${installmentId}/mark-paid/`), payload)
        .then((res) => ({ ...res, data: normalizeInstallment(res.data) })),

    resetPlan: (classId: number | string, reason = "") =>
      api.delete(base(`/classes/${classId}/payments/plan/reset/`), { data: { reason } }),

    resumeWork: (classId: number | string, reason = "") =>
      api.post(base(`/classes/${classId}/payments/resume-work/`), { reason }),
  },

  portalAccess: {
    get: (classId: number | string) =>
      api.post<unknown>(base(`/classes/${classId}/access/view-details/`), {
        reason: "Class portal access view",
      }).then((res) => ({ ...res, data: normalizePortalAccess(res.data) })),

    update: (classId: number | string, payload: Partial<PortalAccess>) =>
      api.patch<unknown>(base(`/classes/${classId}/access/details/`), portalAccessPayload(payload))
        .then((res) => ({ ...res, data: normalizePortalAccess(res.data) })),
  },

  timeline: (classId: number | string) =>
    api.get<Array<Record<string, unknown>>>(base(`/classes/${classId}/timeline/`)),
};
