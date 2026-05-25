import { computed, ref } from "vue";
import { defineStore } from "pinia";
import {
  analyticsApi,
  type ClassAnalytics,
  type ClientAnalytics,
  type WriterAnalytics,
} from "@/api/analytics";
import { useAuthStore } from "@/stores/auth";

function normalizeList<T>(data: T[] | { results: T[] }): T[] {
  return Array.isArray(data) ? data : data.results;
}

function numberValue(value: string | number | undefined | null): number {
  const parsed = Number(value ?? 0);
  return Number.isFinite(parsed) ? parsed : 0;
}

export const useAdminAnalyticsStore = defineStore("adminAnalytics", () => {
  const clients = ref<ClientAnalytics[]>([]);
  const writers = ref<WriterAnalytics[]>([]);
  const classes = ref<ClassAnalytics[]>([]);
  const isLoading = ref(false);
  const error = ref("");
  const notice = ref("");

  const totalRevenue = computed(() =>
    clients.value.reduce((sum, item) => sum + numberValue(item.total_spend), 0),
  );
  const totalOrders = computed(() =>
    clients.value.reduce((sum, item) => sum + numberValue(item.total_orders), 0),
  );
  const averageOnTimeRate = computed(() => {
    if (!clients.value.length) return 0;
    return clients.value.reduce((sum, item) => sum + numberValue(item.on_time_delivery_rate), 0) / clients.value.length;
  });
  const averageWriterQuality = computed(() => {
    if (!writers.value.length) return 0;
    return writers.value.reduce((sum, item) => sum + numberValue(item.quality_score), 0) / writers.value.length;
  });
  const riskWriters = computed(() =>
    writers.value.filter((writer) => numberValue(writer.revision_rate) >= 18 || numberValue(writer.rejection_rate) >= 8),
  );

  async function hydrate() {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        clients.value = [
          {
            id: 1,
            client_email: "nora@preview.local",
            client_name: "Nora Client",
            period_start: "2026-04-25",
            period_end: "2026-05-25",
            total_spend: "2840.00",
            average_order_value: "236.67",
            total_orders: 12,
            on_time_delivery_count: 11,
            late_delivery_count: 1,
            on_time_delivery_rate: "91.7",
            total_revisions: 2,
            revision_rate: "16.7",
            average_writer_rating: "4.8",
          },
          {
            id: 2,
            client_email: "research@preview.local",
            client_name: "Research Team",
            period_start: "2026-04-25",
            period_end: "2026-05-25",
            total_spend: "5175.00",
            average_order_value: "345.00",
            total_orders: 15,
            on_time_delivery_count: 13,
            late_delivery_count: 2,
            on_time_delivery_rate: "86.7",
            total_revisions: 4,
            revision_rate: "26.7",
            average_writer_rating: "4.5",
          },
        ];
        writers.value = [
          {
            id: 1,
            writer_email: "writer.one@preview.local",
            writer_name: "Amina Writer",
            period_start: "2026-04-25",
            period_end: "2026-05-25",
            total_earnings: "1460.00",
            effective_hourly_rate: "31.80",
            total_orders_completed: 18,
            total_orders_in_progress: 3,
            average_completion_time_hours: "34.5",
            revision_rate: "11.1",
            approval_rate: "94.0",
            rejection_rate: "1.0",
            average_rating: "4.9",
            quality_score: "96",
          },
          {
            id: 2,
            writer_email: "writer.two@preview.local",
            writer_name: "Jon Writer",
            period_start: "2026-04-25",
            period_end: "2026-05-25",
            total_earnings: "970.00",
            effective_hourly_rate: "24.10",
            total_orders_completed: 11,
            total_orders_in_progress: 5,
            average_completion_time_hours: "46.0",
            revision_rate: "21.0",
            approval_rate: "82.0",
            rejection_rate: "9.0",
            average_rating: "4.1",
            quality_score: "78",
          },
        ];
        classes.value = [
          {
            id: 1,
            class_name: "Nursing Leadership Cohort",
            class_id: "NUR-501",
            period_start: "2026-04-25",
            period_end: "2026-05-25",
            total_students: 42,
            active_students: 31,
            attendance_rate: "73.8",
            total_orders: 38,
            completed_orders: 29,
            completion_rate: "76.3",
            average_grade: "84.2",
            on_time_submission_rate: "89.0",
            reports_count: 2,
          },
        ];
        return;
      }

      const [clientRes, writerRes, classRes] = await Promise.allSettled([
        analyticsApi.clients(),
        analyticsApi.writers(),
        analyticsApi.classes(),
      ]);
      if (clientRes.status === "fulfilled") clients.value = normalizeList(clientRes.value.data);
      if (writerRes.status === "fulfilled") writers.value = normalizeList(writerRes.value.data);
      if (classRes.status === "fulfilled") classes.value = normalizeList(classRes.value.data);
      if ([clientRes, writerRes, classRes].some((result) => result.status === "rejected")) {
        error.value = "Some analytics data is unavailable.";
      }
    } finally {
      isLoading.value = false;
    }
  }

  function markReviewed() {
    notice.value = "Analytics review marked in preview.";
  }

  return {
    clients,
    writers,
    classes,
    isLoading,
    error,
    notice,
    totalRevenue,
    totalOrders,
    averageOnTimeRate,
    averageWriterQuality,
    riskWriters,
    hydrate,
    markReviewed,
  };
});
