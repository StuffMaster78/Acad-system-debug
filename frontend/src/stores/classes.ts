import { ref, computed } from "vue";
import { defineStore } from "pinia";
import { classesApi } from "@/api/classes";
import { useAuthStore } from "@/stores/auth";
import type {
  ClassOrder,
  ClassOrderDetail,
  ClassTask,
  ClassInstallment,
  SubmitTaskPayload,
  GradeTaskPayload,
} from "@/types/classes";

function normalizeList<T>(data: T[] | { results: T[] }): T[] {
  return Array.isArray(data) ? data : data.results;
}

const PREVIEW_ORDERS: ClassOrder[] = [
  {
    id: 1,
    reference: "CLS-001",
    title: "Intro to Statistics — Full Semester",
    subject: "Statistics",
    academic_level: "Undergraduate",
    status: "active",
    client_id: 10,
    client_username: "john.doe",
    assigned_writer_id: 5,
    writer_username: "writer.pro",
    total_tasks: 8,
    completed_tasks: 3,
    total_price: "480.00",
    currency: "USD",
    payment_status: "partial",
    portal_access_enabled: true,
    start_date: "2026-01-15",
    end_date: "2026-05-15",
    created_at: "2026-01-10T09:00:00Z",
    updated_at: "2026-04-20T14:00:00Z",
  },
  {
    id: 2,
    reference: "CLS-002",
    title: "Business Ethics — 8-Week Course",
    subject: "Ethics",
    academic_level: "Graduate",
    status: "active",
    client_id: 11,
    client_username: "jane.smith",
    assigned_writer_id: null,
    writer_username: null,
    total_tasks: 5,
    completed_tasks: 0,
    total_price: "320.00",
    currency: "USD",
    payment_status: "pending",
    portal_access_enabled: false,
    start_date: "2026-04-01",
    end_date: "2026-05-30",
    created_at: "2026-03-25T11:00:00Z",
    updated_at: "2026-03-25T11:00:00Z",
  },
];

const PREVIEW_DETAIL: ClassOrderDetail = {
  ...PREVIEW_ORDERS[0],
  tasks: [
    {
      id: 1,
      class_order_id: 1,
      sequence: 1,
      title: "Week 1 Discussion Post",
      description: "Respond to the course introduction prompt.",
      due_date: "2026-01-22",
      status: "approved",
      writer_id: 5,
      writer_username: "writer.pro",
      submission_file_url: null,
      submission_notes: "Submitted on time.",
      grade: "A",
      grade_feedback: "Well written.",
      submitted_at: "2026-01-21T18:00:00Z",
      approved_at: "2026-01-22T09:00:00Z",
      created_at: "2026-01-15T00:00:00Z",
    },
    {
      id: 2,
      class_order_id: 1,
      sequence: 2,
      title: "Week 2 Quiz Preparation",
      description: "Complete practice problems for Chapter 2.",
      due_date: "2026-01-29",
      status: "submitted",
      writer_id: 5,
      writer_username: "writer.pro",
      submission_file_url: null,
      submission_notes: "Answers attached.",
      grade: null,
      grade_feedback: null,
      submitted_at: "2026-01-28T20:00:00Z",
      approved_at: null,
      created_at: "2026-01-15T00:00:00Z",
    },
    {
      id: 3,
      class_order_id: 1,
      sequence: 3,
      title: "Week 3 Assignment",
      description: "Descriptive statistics analysis — 4 pages.",
      due_date: "2026-02-05",
      status: "in_progress",
      writer_id: 5,
      writer_username: "writer.pro",
      submission_file_url: null,
      submission_notes: null,
      grade: null,
      grade_feedback: null,
      submitted_at: null,
      approved_at: null,
      created_at: "2026-01-15T00:00:00Z",
    },
  ],
  installments: [
    {
      id: 1,
      class_order_id: 1,
      label: "Initial deposit",
      amount: "160.00",
      currency: "USD",
      due_date: "2026-01-15",
      status: "paid",
      paid_at: "2026-01-14T10:00:00Z",
      payment_reference: "TXN-001",
    },
    {
      id: 2,
      class_order_id: 1,
      label: "Mid-semester payment",
      amount: "160.00",
      currency: "USD",
      due_date: "2026-03-01",
      status: "paid",
      paid_at: "2026-03-01T08:00:00Z",
      payment_reference: "TXN-002",
    },
    {
      id: 3,
      class_order_id: 1,
      label: "Final payment",
      amount: "160.00",
      currency: "USD",
      due_date: "2026-05-01",
      status: "pending",
      paid_at: null,
      payment_reference: null,
    },
  ],
  portal_access: {
    enabled: true,
    portal_url: "https://lms.example.edu",
    username: "jdoe@example.edu",
    password_hint: "Check secure notes",
    notes: "Course code: STAT101-S26",
    last_accessed_at: "2026-04-19T14:00:00Z",
  },
};

export const useClassesStore = defineStore("classes", () => {
  const orders = ref<ClassOrder[]>([]);
  const detail = ref<ClassOrderDetail | null>(null);
  const isLoading = ref(false);
  const isLoadingDetail = ref(false);
  const isSaving = ref(false);
  const error = ref<string | null>(null);
  const activeTab = ref<"tasks" | "installments" | "portal">("tasks");

  const pendingTasks = computed(() =>
    (detail.value?.tasks ?? []).filter((t) => ["pending", "assigned", "in_progress"].includes(t.status)),
  );
  const completedTasks = computed(() =>
    (detail.value?.tasks ?? []).filter((t) => ["approved", "cancelled"].includes(t.status)),
  );
  const pendingInstallments = computed(() =>
    (detail.value?.installments ?? []).filter((i) => i.status === "pending" || i.status === "overdue"),
  );

  async function loadOrders(params?: Record<string, unknown>) {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = null;
    try {
      if (auth.isPreviewSession) {
        orders.value = PREVIEW_ORDERS;
        return;
      }
      const res = await classesApi.list(params);
      orders.value = normalizeList(res.data);
    } catch {
      error.value = "Failed to load classes.";
    } finally {
      isLoading.value = false;
    }
  }

  async function loadDetail(id: number | string) {
    const auth = useAuthStore();
    isLoadingDetail.value = true;
    detail.value = null;
    error.value = null;
    try {
      if (auth.isPreviewSession) {
        detail.value = PREVIEW_DETAIL;
        return;
      }
      const [classRes, tasksRes, installmentsRes] = await Promise.all([
        classesApi.get(id),
        classesApi.tasks.list(id).catch(() => ({ data: [] as ClassTask[] })),
        classesApi.installments.list(id).catch(() => ({ data: [] as ClassInstallment[] })),
      ]);
      detail.value = {
        ...classRes.data,
        tasks: tasksRes.data,
        installments: installmentsRes.data,
        portal_access: null,
        portal_access_enabled: classRes.data.portal_access_enabled,
      };
    } catch {
      error.value = "Failed to load class detail.";
    } finally {
      isLoadingDetail.value = false;
    }
  }

  async function loadPortalAccess(classId: number | string) {
    const auth = useAuthStore();
    if (!detail.value) return;
    isSaving.value = true;
    try {
      if (auth.isPreviewSession) return;
      const res = await classesApi.portalAccess.get(classId);
      detail.value.portal_access = res.data;
      detail.value.portal_access_enabled = res.data.enabled;
    } finally {
      isSaving.value = false;
    }
  }

  async function submitTask(classId: number | string, taskId: number | string, payload: SubmitTaskPayload) {
    const auth = useAuthStore();
    isSaving.value = true;
    try {
      if (auth.isPreviewSession) {
        if (detail.value) {
          const t = detail.value.tasks.find((t) => t.id === Number(taskId));
          if (t) { t.status = "submitted"; t.submitted_at = new Date().toISOString(); }
        }
        return;
      }
      const res = await classesApi.tasks.submit(classId, taskId, payload);
      if (detail.value) {
        const idx = detail.value.tasks.findIndex((t) => t.id === Number(taskId));
        if (idx !== -1) detail.value.tasks[idx] = res.data;
      }
    } finally {
      isSaving.value = false;
    }
  }

  async function gradeTask(classId: number | string, taskId: number | string, payload: GradeTaskPayload) {
    const auth = useAuthStore();
    isSaving.value = true;
    try {
      if (auth.isPreviewSession) {
        if (detail.value) {
          const t = detail.value.tasks.find((t) => t.id === Number(taskId));
          if (t) { t.grade = payload.grade; t.grade_feedback = payload.grade_feedback ?? null; t.status = "approved"; }
        }
        return;
      }
      const res = await classesApi.tasks.grade(classId, taskId, payload);
      if (detail.value) {
        const idx = detail.value.tasks.findIndex((t) => t.id === Number(taskId));
        if (idx !== -1) detail.value.tasks[idx] = res.data;
      }
    } finally {
      isSaving.value = false;
    }
  }

  async function assignWriter(classId: number | string, writerId: number) {
    const auth = useAuthStore();
    isSaving.value = true;
    try {
      if (auth.isPreviewSession) {
        const o = orders.value.find((o) => o.id === Number(classId));
        if (o) o.assigned_writer_id = writerId;
        return;
      }
      await classesApi.assignWriter(classId, writerId);
      await loadDetail(classId);
    } finally {
      isSaving.value = false;
    }
  }

  async function cancelClass(classId: number | string, reason = "Cancelled from staff portal") {
    const auth = useAuthStore();
    isSaving.value = true;
    try {
      if (auth.isPreviewSession) {
        const o = orders.value.find((o) => o.id === Number(classId));
        if (o) o.status = "cancelled";
        if (detail.value?.id === Number(classId)) detail.value.status = "cancelled";
        return;
      }
      const res = await classesApi.cancel(classId, reason);
      if (detail.value?.id === Number(classId)) {
        detail.value = {
          ...detail.value,
          ...res.data,
        };
      }
      const idx = orders.value.findIndex((o) => o.id === Number(classId));
      if (idx !== -1) orders.value[idx] = res.data;
    } finally {
      isSaving.value = false;
    }
  }

  function reset() {
    orders.value = [];
    detail.value = null;
    error.value = null;
    activeTab.value = "tasks";
  }

  return {
    orders,
    detail,
    isLoading,
    isLoadingDetail,
    isSaving,
    error,
    activeTab,
    pendingTasks,
    completedTasks,
    pendingInstallments,
    loadOrders,
    loadDetail,
    submitTask,
    gradeTask,
    assignWriter,
    cancelClass,
    loadPortalAccess,
    reset,
  };
});
