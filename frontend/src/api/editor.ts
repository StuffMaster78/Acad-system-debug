import { api, apiPath } from "./client";
import type {
  AvailableEditorTasksResponse,
  EditorActivityBundle,
  EditorAnalytics,
  EditorDashboardStats,
  EditorPerformance,
  EditorProfile,
  EditorTask,
  EditorWorkload,
  SubmitEditorReviewPayload,
} from "@/types/editor";

type ListResponse<T> = T[] | { results: T[] };

export const editorApi = {
  profile: () =>
    api.get<EditorProfile>(apiPath("/editor-management/profiles/my_profile/")),
  stats: (days = 30) =>
    api.get<EditorDashboardStats>(
      apiPath("/editor-management/profiles/dashboard_stats/"),
      { params: { days } },
    ),
  tasks: (params?: Record<string, unknown>) =>
    api.get<ListResponse<EditorTask>>(
      apiPath("/editor-management/profiles/dashboard/tasks/"),
      { params },
    ),
  performance: (days = 30) =>
    api.get<EditorPerformance>(
      apiPath("/editor-management/profiles/dashboard/performance/"),
      { params: { days } },
    ),
  analytics: (days = 30) =>
    api.get<EditorAnalytics>(
      apiPath("/editor-management/profiles/dashboard/analytics/"),
      { params: { days } },
    ),
  activity: (days = 7, limit = 12) =>
    api.get<EditorActivityBundle>(
      apiPath("/editor-management/profiles/dashboard/activity/"),
      { params: { days, limit } },
    ),
  workload: () =>
    api.get<EditorWorkload>(
      apiPath("/editor-management/profiles/dashboard/workload/"),
    ),
  availableTasks: (params?: Record<string, unknown>) =>
    api.get<AvailableEditorTasksResponse>(
      apiPath("/editor-management/tasks/available_tasks/"),
      { params },
    ),
  claim: (orderId: number | string) =>
    api.post<EditorTask>(apiPath("/editor-management/tasks/claim/"), {
      order_id: orderId,
    }),
  startReview: (taskId: number | string) =>
    api.post<EditorTask>(
      apiPath(`/editor-management/tasks/${taskId}/start_review/`),
      {},
    ),
  submitReview: (payload: SubmitEditorReviewPayload) =>
    api.post(apiPath("/editor-management/tasks/submit_review/"), payload),
  completeTask: (taskId: number | string, finalNotes = "") =>
    api.post<EditorTask>(apiPath("/editor-management/tasks/complete_task/"), {
      task_id: taskId,
      final_notes: finalNotes,
    }),
  rejectTask: (taskId: number | string, reason: string) =>
    api.post<EditorTask>(apiPath("/editor-management/tasks/reject_task/"), {
      task_id: taskId,
      reason,
    }),
  unclaim: (taskId: number | string) =>
    api.post<EditorTask>(apiPath("/editor-management/tasks/unclaim/"), {
      task_id: taskId,
    }),
};
