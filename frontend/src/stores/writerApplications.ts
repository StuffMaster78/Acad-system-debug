import { ref, computed } from "vue";
import { defineStore } from "pinia";
import {
  writerApplicationsApi,
  type WriterApplicationSummary,
  type WriterApplicationDetail,
  type ApprovePayload,
  type RejectPayload,
} from "@/api/writerApplications";

function normalizeList<T>(data: T[] | { results: T[] }): T[] {
  return Array.isArray(data) ? data : data.results;
}

export const useWriterApplicationsStore = defineStore("writerApplications", () => {
  const applications = ref<WriterApplicationSummary[]>([]);
  const selectedApplication = ref<WriterApplicationDetail | null>(null);
  const loading = ref(false);
  const actionLoading = ref(false);
  const notice = ref<{ type: "success" | "error"; message: string } | null>(null);

  // Filters
  const statusFilter = ref<string>("all");
  const search = ref("");

  const filtered = computed(() => {
    let items = applications.value;
    if (statusFilter.value !== "all") {
      items = items.filter((a) => a.status === statusFilter.value);
    }
    if (search.value.trim()) {
      const q = search.value.trim().toLowerCase();
      items = items.filter(
        (a) =>
          a.full_name.toLowerCase().includes(q) ||
          a.email.toLowerCase().includes(q) ||
          a.country.toLowerCase().includes(q),
      );
    }
    return items;
  });

  const counts = computed(() => ({
    all: applications.value.length,
    pending: applications.value.filter((a) => a.status === "pending").length,
    under_review: applications.value.filter((a) => a.status === "under_review").length,
    approved: applications.value.filter((a) => a.status === "approved").length,
    rejected: applications.value.filter((a) => a.status === "rejected").length,
    withdrawn: applications.value.filter((a) => a.status === "withdrawn").length,
  }));

  function showNotice(type: "success" | "error", message: string) {
    notice.value = { type, message };
    setTimeout(() => { notice.value = null; }, 4000);
  }

  async function load(params?: Record<string, unknown>) {
    loading.value = true;
    try {
      const { data } = await writerApplicationsApi.list(params);
      applications.value = normalizeList(data);
    } catch {
      showNotice("error", "Failed to load applications.");
    } finally {
      loading.value = false;
    }
  }

  async function select(id: number) {
    if (selectedApplication.value?.id === id) return;
    selectedApplication.value = null;
    try {
      const { data } = await writerApplicationsApi.detail(id);
      selectedApplication.value = data;
    } catch {
      showNotice("error", "Failed to load application details.");
    }
  }

  function clearSelection() {
    selectedApplication.value = null;
  }

  async function markUnderReview(id: number) {
    actionLoading.value = true;
    try {
      await writerApplicationsApi.review(id);
      await _refreshItem(id);
      showNotice("success", "Marked as under review.");
    } catch (err: unknown) {
      showNotice("error", _errMsg(err, "Failed to update status."));
    } finally {
      actionLoading.value = false;
    }
  }

  async function approve(id: number, payload: ApprovePayload = {}) {
    actionLoading.value = true;
    try {
      const { data } = await writerApplicationsApi.approve(id, payload);
      await _refreshItem(id);
      showNotice("success", `Approved. Writer ID: ${data.registration_id}`);
      return data;
    } catch (err: unknown) {
      showNotice("error", _errMsg(err, "Approval failed."));
    } finally {
      actionLoading.value = false;
    }
  }

  async function reject(id: number, payload: RejectPayload) {
    actionLoading.value = true;
    try {
      await writerApplicationsApi.reject(id, payload);
      await _refreshItem(id);
      showNotice("success", "Application rejected.");
    } catch (err: unknown) {
      showNotice("error", _errMsg(err, "Rejection failed."));
    } finally {
      actionLoading.value = false;
    }
  }

  async function _refreshItem(id: number) {
    const { data } = await writerApplicationsApi.detail(id);
    selectedApplication.value = data;
    const idx = applications.value.findIndex((a) => a.id === id);
    if (idx !== -1) {
      applications.value = applications.value.map((a) =>
        a.id === id ? { ...a, status: data.status, reviewed_at: data.reviewed_at } : a,
      );
    }
  }

  function _errMsg(err: unknown, fallback: string): string {
    if (err && typeof err === "object" && "response" in err) {
      const r = (err as { response?: { data?: { detail?: string } } }).response;
      return r?.data?.detail ?? fallback;
    }
    return fallback;
  }

  return {
    applications,
    filtered,
    counts,
    selectedApplication,
    loading,
    actionLoading,
    notice,
    statusFilter,
    search,
    load,
    select,
    clearSelection,
    markUnderReview,
    approve,
    reject,
  };
});
