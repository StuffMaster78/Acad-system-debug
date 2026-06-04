import { ref, computed } from "vue";
import { defineStore } from "pinia";
import {
  feedbackApi,
  type CreateFeedbackPayload,
  type FeedbackCategory,
  type FeedbackItem,
  type FeedbackSummary,
  type TriageUpdatePayload,
} from "@/api/feedback";

function normalize<T>(data: T[] | { results: T[] }): T[] {
  return Array.isArray(data) ? data : data.results;
}

export const useFeedbackStore = defineStore("feedback", () => {
  const items = ref<FeedbackItem[]>([]);
  const categories = ref<FeedbackCategory[]>([]);
  const summary = ref<FeedbackSummary | null>(null);
  const detail = ref<FeedbackItem | null>(null);
  const isLoading = ref(false);
  const isMutating = ref(false);
  const error = ref("");
  const notice = ref("");

  // Pagination state
  const page = ref(1);
  const totalCount = ref(0);
  const hasMore = ref(false);

  // Triage filters (staff)
  const filters = ref({
    status: "",
    category: "",
    surface: "",
    priority: "",
    request_type: "",
    owner: "",
    search: "",
  });

  const activeFilterCount = computed(
    () => Object.values(filters.value).filter(Boolean).length
  );

  function _params() {
    const p: Record<string, unknown> = { page: page.value };
    const f = filters.value;
    if (f.status) p.status = f.status;
    if (f.category) p.category = f.category;
    if (f.surface) p.surface = f.surface;
    if (f.priority) p.priority = f.priority;
    if (f.request_type) p.request_type = f.request_type;
    if (f.owner) p.owner = f.owner;
    if (f.search) p.search = f.search;
    return p;
  }

  async function load(reset = false) {
    if (reset) page.value = 1;
    isLoading.value = true;
    error.value = "";
    try {
      const { data } = await feedbackApi.list(_params());
      const results = normalize(data);
      items.value = reset ? results : [...items.value, ...results];
      if (!Array.isArray(data)) {
        totalCount.value = data.count;
        hasMore.value = !!data.next;
      }
    } catch {
      error.value = "Failed to load feedback requests.";
    } finally {
      isLoading.value = false;
    }
  }

  async function loadCategories() {
    try {
      const { data } = await feedbackApi.categories();
      categories.value = data.categories;
    } catch {
      categories.value = [];
    }
  }

  async function loadSummary() {
    try {
      const { data } = await feedbackApi.summary();
      summary.value = data;
    } catch {
      summary.value = null;
    }
  }

  async function loadDetail(id: number) {
    isLoading.value = true;
    try {
      const { data } = await feedbackApi.retrieve(id);
      detail.value = data;
    } catch {
      detail.value = null;
    } finally {
      isLoading.value = false;
    }
  }

  async function submit(payload: CreateFeedbackPayload): Promise<FeedbackItem | null> {
    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      const { data } = await feedbackApi.create(payload);
      items.value = [data, ...items.value];
      totalCount.value += 1;
      notice.value = "Your request has been submitted. Thank you!";
      return data;
    } catch (e: unknown) {
      error.value = "Failed to submit feedback.";
      return null;
    } finally {
      isMutating.value = false;
    }
  }

  async function vote(id: number) {
    isMutating.value = true;
    try {
      const { data } = await feedbackApi.vote(id);
      const item = items.value.find((i) => i.id === id);
      if (item) {
        item.has_voted = data.voted;
        item.upvote_count = data.upvote_count;
      }
      if (detail.value?.id === id) {
        detail.value.has_voted = data.voted;
        detail.value.upvote_count = data.upvote_count;
      }
    } finally {
      isMutating.value = false;
    }
  }

  async function triageUpdate(id: number, payload: TriageUpdatePayload) {
    isMutating.value = true;
    notice.value = "";
    try {
      const { data } = await feedbackApi.update(id, payload);
      _replaceInList(data);
      if (detail.value?.id === id) detail.value = data;
      notice.value = "Updated.";
    } catch {
      error.value = "Update failed.";
    } finally {
      isMutating.value = false;
    }
  }

  async function respond(id: number, response: string) {
    isMutating.value = true;
    notice.value = "";
    try {
      const { data } = await feedbackApi.respond(id, response);
      _replaceInList(data);
      if (detail.value?.id === id) detail.value = data;
      notice.value = "Response posted.";
    } catch {
      error.value = "Failed to post response.";
    } finally {
      isMutating.value = false;
    }
  }

  async function markDuplicate(id: number, parentId: number) {
    isMutating.value = true;
    try {
      const { data } = await feedbackApi.markDuplicate(id, parentId);
      _replaceInList(data);
      if (detail.value?.id === id) detail.value = data;
      notice.value = "Marked as duplicate.";
    } catch {
      error.value = "Failed to mark duplicate.";
    } finally {
      isMutating.value = false;
    }
  }

  function _replaceInList(updated: FeedbackItem) {
    const idx = items.value.findIndex((i) => i.id === updated.id);
    if (idx !== -1) items.value[idx] = updated;
  }

  function resetFilters() {
    filters.value = {
      status: "", category: "", surface: "", priority: "",
      request_type: "", owner: "", search: "",
    };
  }

  return {
    items, categories, summary, detail,
    isLoading, isMutating, error, notice,
    page, totalCount, hasMore, filters, activeFilterCount,
    load, loadCategories, loadSummary, loadDetail,
    submit, vote, triageUpdate, respond, markDuplicate, resetFilters,
  };
});
