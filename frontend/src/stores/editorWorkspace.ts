import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { editorApi } from "@/api/editor";
import { useUiStore } from "@/stores/ui";
import { useAuthStore } from "@/stores/auth";
import type { MetricDefinition } from "@/config/dashboard";
import type {
  EditorActivityBundle,
  EditorAnalytics,
  EditorDashboardStats,
  EditorPerformance,
  EditorProfile,
  EditorTask,
  EditorWorkload,
  SubmitEditorReviewPayload,
} from "@/types/editor";

function numberValue(value: unknown): number {
  const parsed = Number(value ?? 0);
  return Number.isFinite(parsed) ? parsed : 0;
}

function previewTasks(): EditorTask[] {
  return [
    {
      id: 311,
      order_id: 10001,
      order_topic: "Nursing leadership reflection",
      order_deadline: new Date(Date.now() + 1000 * 60 * 60 * 9).toISOString(),
      order_status: "under_editing",
      review_status: "in_review",
      assignment_type: "manual",
      assigned_at: new Date(Date.now() - 1000 * 60 * 70).toISOString(),
      notes: "Check APA references and final client-facing tone.",
    },
    {
      id: 312,
      order_id: 10008,
      order_topic: "International trade policy brief",
      order_deadline: new Date(Date.now() + 1000 * 60 * 60 * 30).toISOString(),
      order_status: "under_editing",
      review_status: "pending",
      assignment_type: "auto",
      assigned_at: new Date(Date.now() - 1000 * 60 * 35).toISOString(),
    },
    {
      id: 313,
      order_id: 10012,
      order_topic: "Marketing analytics case study",
      order_deadline: new Date(Date.now() - 1000 * 60 * 90).toISOString(),
      order_status: "under_editing",
      review_status: "pending",
      assignment_type: "claimed",
      assigned_at: new Date(Date.now() - 1000 * 60 * 190).toISOString(),
    },
  ];
}

function previewAvailable(): EditorTask[] {
  return [
    {
      id: 421,
      order_id: 10021,
      order_topic: "Education policy annotated bibliography",
      order_deadline: new Date(Date.now() + 1000 * 60 * 60 * 18).toISOString(),
      order_status: "under_editing",
      review_status: "unclaimed",
      assignment_type: "auto",
      assigned_at: new Date().toISOString(),
    },
    {
      id: 422,
      order_id: 10023,
      order_topic: "Python data analysis report",
      order_deadline: new Date(Date.now() + 1000 * 60 * 60 * 52).toISOString(),
      order_status: "under_editing",
      review_status: "unclaimed",
      assignment_type: "auto",
      assigned_at: new Date().toISOString(),
    },
  ];
}

export const useEditorWorkspaceStore = defineStore("editorWorkspace", () => {
  const profile = ref<EditorProfile | null>(null);
  const stats = ref<EditorDashboardStats>({});
  const tasks = ref<EditorTask[]>([]);
  const availableTasks = ref<EditorTask[]>([]);
  const performance = ref<EditorPerformance>({});
  const analytics = ref<EditorAnalytics>({});
  const activity = ref<EditorActivityBundle>({});
  const workload = ref<EditorWorkload>({});
  const isLoading = ref(false);
  const isMutating = ref(false);
  const error = ref("");
  const notice = ref("");

  const activeTasks = computed(() =>
    tasks.value.filter((task) => ["pending", "in_review"].includes(String(task.review_status))),
  );

  const overdueTasks = computed(() =>
    activeTasks.value.filter((task) => task.order_deadline && new Date(task.order_deadline) < new Date()),
  );

  const capacity = computed(() => workload.value.current_workload?.capacity_percentage ?? 0);

  const metrics = computed<MetricDefinition[]>(() => [
    {
      label: "Active reviews",
      value: String(stats.value.active_tasks ?? activeTasks.value.length),
      detail: `${stats.value.pending_tasks ?? activeTasks.value.filter((task) => task.review_status === "pending").length} pending in queue`,
      tone: overdueTasks.value.length ? "warn" : "neutral",
    },
    {
      label: "Overdue",
      value: String(analytics.value.overdue_tasks_count ?? workload.value.deadline_analysis?.overdue_tasks ?? overdueTasks.value.length),
      detail: `${analytics.value.urgent_tasks_count ?? workload.value.deadline_analysis?.urgent_tasks ?? 0} urgent within 24 hours`,
      tone: overdueTasks.value.length ? "risk" : "good",
    },
    {
      label: "Quality score",
      value: numberValue(performance.value.average_quality_score ?? performance.value.quality_score).toFixed(1),
      detail: `${performance.value.total_reviews ?? stats.value.completed_tasks ?? 0} reviews tracked`,
      tone: "good",
    },
    {
      label: "Capacity",
      value: `${Math.round(numberValue(capacity.value))}%`,
      detail: `${workload.value.current_workload?.available_slots ?? 0} slots open`,
      tone: numberValue(capacity.value) >= 90 ? "warn" : "neutral",
    },
  ]);

  async function hydrate() {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        const seededTasks = previewTasks();
        profile.value = {
          id: 7,
          name: "Editor Preview",
          registration_id: "Editor #70001",
          email: "editor@preview.local",
          is_active: true,
          orders_reviewed: 146,
          active_tasks_count: 3,
          max_concurrent_tasks: 5,
          can_self_assign: true,
          can_take_more_tasks: true,
        };
        tasks.value = seededTasks;
        availableTasks.value = previewAvailable();
        stats.value = {
          active_tasks: 3,
          pending_tasks: 2,
          in_review_tasks: 1,
          completed_tasks: 32,
          available_tasks: 2,
          average_quality_score: 9.1,
          average_review_time_hours: 3.4,
        };
        performance.value = {
          average_quality_score: 9.1,
          total_reviews: 146,
          average_review_time_hours: 3.4,
          on_time_completion_rate: 96,
          revision_rate: 7,
        };
        analytics.value = {
          status_breakdown: { pending: 2, in_review: 1, completed: 32 },
          assignment_breakdown: { manual: 1, auto: 1, claimed: 1 },
          urgent_tasks_count: 1,
          overdue_tasks_count: 1,
          total_tasks: 35,
          weekly_tasks: [
            { week: "2026-05-04", count: 7 },
            { week: "2026-05-11", count: 9 },
            { week: "2026-05-18", count: 11 },
          ],
        };
        workload.value = {
          current_workload: {
            active_tasks_count: 3,
            max_concurrent_tasks: 5,
            capacity_percentage: 60,
            available_slots: 2,
            is_at_capacity: false,
            can_take_more: true,
          },
          deadline_analysis: { urgent_tasks: 1, overdue_tasks: 1, total_with_deadlines: 3 },
          time_estimates: { average_hours_per_task: 14.3, estimated_hours_until_all_deadlines: 43 },
          recommendations: { recommended_max_orders: 2, should_claim_more: false, should_focus_on_urgent: true },
        };
        activity.value = {
          activity_logs: [
            {
              id: 1,
              action_type: "started_review",
              action: "Started reviewing Nursing leadership reflection",
              order_id: 10001,
              order_topic: "Nursing leadership reflection",
              timestamp: new Date(Date.now() - 1000 * 60 * 18).toISOString(),
            },
            {
              id: 2,
              action_type: "submitted_review",
              action: "Submitted QA review for Economics outline",
              order_id: 9981,
              order_topic: "Economics outline",
              timestamp: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
            },
          ],
          recent_reviews: [
            {
              id: 91,
              order_id: 9981,
              order_topic: "Economics outline",
              quality_score: 9.4,
              is_approved: true,
              requires_revision: false,
              submitted_at: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
            },
          ],
          recent_assignments: seededTasks,
        };
        return;
      }

      const [profileRes, statsRes, tasksRes, availableRes, performanceRes, analyticsRes, activityRes, workloadRes] =
        await Promise.allSettled([
          editorApi.profile(),
          editorApi.stats(),
          editorApi.tasks({ limit: 20 }),
          editorApi.availableTasks({ limit: 12 }),
          editorApi.performance(),
          editorApi.analytics(),
          editorApi.activity(),
          editorApi.workload(),
        ]);

      if (profileRes.status === "fulfilled") profile.value = profileRes.value.data;
      if (statsRes.status === "fulfilled") stats.value = statsRes.value.data;
      if (tasksRes.status === "fulfilled") tasks.value = tasksRes.value.data.tasks ?? [];
      if (availableRes.status === "fulfilled") availableTasks.value = availableRes.value.data.tasks ?? [];
      if (performanceRes.status === "fulfilled") performance.value = performanceRes.value.data;
      if (analyticsRes.status === "fulfilled") analytics.value = analyticsRes.value.data;
      if (activityRes.status === "fulfilled") activity.value = activityRes.value.data;
      if (workloadRes.status === "fulfilled") workload.value = workloadRes.value.data;

      const failed = [profileRes, statsRes, tasksRes, availableRes, performanceRes, analyticsRes, activityRes, workloadRes]
        .some((result) => result.status === "rejected");
      if (failed) error.value = "Some editor workspace data is unavailable from the backend.";
    } finally {
      isLoading.value = false;
    }
  }

  async function refreshTasks() {
    const [tasksRes, availableRes] = await Promise.allSettled([
      editorApi.tasks({ limit: 20 }),
      editorApi.availableTasks({ limit: 12 }),
    ]);
    if (tasksRes.status === "fulfilled") tasks.value = tasksRes.value.data.tasks ?? [];
    if (availableRes.status === "fulfilled") availableTasks.value = availableRes.value.data.tasks ?? [];
  }

  async function mutateTask(action: "start" | "complete" | "reject" | "unclaim", taskId: number | string, payload = "") {
    const auth = useAuthStore();
    const ui = useUiStore();
    isMutating.value = true;
    error.value = "";
    notice.value = "";
    try {
      if (auth.isPreviewSession) {
        tasks.value = tasks.value.map((task) => {
          if (task.id !== taskId) return task;
          if (action === "start") return { ...task, review_status: "in_review", started_at: new Date().toISOString() };
          if (action === "complete") return { ...task, review_status: "completed", reviewed_at: new Date().toISOString(), notes: payload || task.notes };
          if (action === "reject") return { ...task, review_status: "rejected", notes: payload };
          return { ...task, review_status: "unclaimed" };
        });
        notice.value = "Preview task updated.";
        ui.toast("Task updated.", "success");
        return;
      }

      if (action === "start") await editorApi.startReview(taskId);
      if (action === "complete") await editorApi.completeTask(taskId, payload);
      if (action === "reject") await editorApi.rejectTask(taskId, payload);
      if (action === "unclaim") await editorApi.unclaim(taskId);
      await refreshTasks();
      notice.value = "Task updated.";
      ui.toast("Task updated.", "success");
    } catch (caught) {
      error.value = "Unable to update that editor task.";
      ui.toast("Unable to update that editor task.", "error");
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function submitReview(payload: SubmitEditorReviewPayload) {
    const auth = useAuthStore();
    const ui = useUiStore();
    isMutating.value = true;
    error.value = "";
    notice.value = "";
    try {
      if (!auth.isPreviewSession) {
        await editorApi.submitReview(payload);
        await refreshTasks();
      }
      const msg = payload.requires_revision ? "Review submitted with revision request." : "Review submitted for delivery.";
      notice.value = msg;
      ui.toast(msg, "success");
    } catch (caught) {
      error.value = "Unable to submit the review.";
      ui.toast("Unable to submit the review.", "error");
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function claim(orderId: number | string) {
    const auth = useAuthStore();
    const ui = useUiStore();
    isMutating.value = true;
    error.value = "";
    notice.value = "";
    try {
      if (auth.isPreviewSession) {
        const task = availableTasks.value.find((row) => String(row.order_id ?? row.order) === String(orderId));
        if (task) {
          availableTasks.value = availableTasks.value.filter((row) => row.id !== task.id);
          tasks.value = [{ ...task, review_status: "pending", assignment_type: "claimed" }, ...tasks.value];
        }
      } else {
        await editorApi.claim(orderId);
        await refreshTasks();
      }
      notice.value = `Order ${orderId} claimed for QA.`;
      ui.toast(`Order ${orderId} claimed for QA.`, "success");
    } catch (caught) {
      error.value = "Unable to claim that order.";
      ui.toast("Unable to claim that order.", "error");
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  return {
    profile,
    stats,
    tasks,
    availableTasks,
    performance,
    analytics,
    activity,
    workload,
    isLoading,
    isMutating,
    error,
    notice,
    activeTasks,
    overdueTasks,
    capacity,
    metrics,
    hydrate,
    refreshTasks,
    mutateTask,
    submitReview,
    claim,
  };
});
