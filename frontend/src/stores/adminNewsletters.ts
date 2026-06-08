import { ref, computed } from "vue";
import { defineStore } from "pinia";
import {
  adminNewslettersApi,
  type Subscriber,
  type NewsletterSummary,
  type NewsletterDetail,
  type SubscriberStats,
  type SubscriberCategory,
} from "@/api/adminNewsletters";

export const useAdminNewslettersStore = defineStore("adminNewsletters", () => {
  const stats = ref<SubscriberStats | null>(null);
  const subscribers = ref<Subscriber[]>([]);
  const subscriberTotal = ref(0);
  const newsletters = ref<NewsletterSummary[]>([]);
  const newsletterTotal = ref(0);
  const selectedNewsletter = ref<NewsletterDetail | null>(null);
  const categories = ref<SubscriberCategory[]>([]);

  const loading = ref(false);
  const actionLoading = ref(false);
  const notice = ref<{ type: "success" | "error"; message: string } | null>(null);

  // Subscriber filters
  const subscriberSearch = ref("");
  const subscriberStatusFilter = ref<"all" | "active" | "inactive">("all");
  const subscriberSourceFilter = ref("all");

  // Newsletter filters
  const newsletterSearch = ref("");
  const newsletterStatusFilter = ref("all");

  const activeSubscribers = computed(() =>
    subscribers.value.filter((s) => s.is_active).length,
  );
  const inactiveSubscribers = computed(() =>
    subscribers.value.filter((s) => !s.is_active).length,
  );

  function showNotice(type: "success" | "error", message: string) {
    notice.value = { type, message };
    setTimeout(() => { notice.value = null; }, 4000);
  }

  async function loadStats() {
    try {
      const { data } = await adminNewslettersApi.stats();
      stats.value = data;
    } catch { /* non-fatal */ }
  }

  async function loadSubscribers(page = 1) {
    loading.value = true;
    try {
      const params: Record<string, unknown> = { page, page_size: 50 };
      if (subscriberStatusFilter.value !== "all") {
        params.is_active = subscriberStatusFilter.value === "active";
      }
      if (subscriberSourceFilter.value !== "all") {
        params.source = subscriberSourceFilter.value;
      }
      if (subscriberSearch.value.trim()) {
        params.search = subscriberSearch.value.trim();
      }
      const { data } = await adminNewslettersApi.subscribers(params);
      subscribers.value = data.results ?? [];
      subscriberTotal.value = data.count;
    } catch {
      showNotice("error", "Failed to load subscribers.");
    } finally {
      loading.value = false;
    }
  }

  async function deactivateSubscriber(id: number) {
    actionLoading.value = true;
    try {
      await adminNewslettersApi.deactivateSubscriber(id);
      subscribers.value = subscribers.value.map((s) =>
        s.id === id ? { ...s, is_active: false } : s,
      );
      showNotice("success", "Subscriber deactivated.");
    } catch {
      showNotice("error", "Failed to deactivate subscriber.");
    } finally {
      actionLoading.value = false;
    }
  }

  async function reactivateSubscriber(id: number) {
    actionLoading.value = true;
    try {
      await adminNewslettersApi.reactivateSubscriber(id);
      subscribers.value = subscribers.value.map((s) =>
        s.id === id ? { ...s, is_active: true } : s,
      );
      showNotice("success", "Subscriber reactivated.");
    } catch {
      showNotice("error", "Failed to reactivate subscriber.");
    } finally {
      actionLoading.value = false;
    }
  }

  async function loadNewsletters(page = 1) {
    loading.value = true;
    try {
      const params: Record<string, unknown> = { page, page_size: 30 };
      if (newsletterStatusFilter.value !== "all") {
        params.status = newsletterStatusFilter.value;
      }
      if (newsletterSearch.value.trim()) {
        params.search = newsletterSearch.value.trim();
      }
      const { data } = await adminNewslettersApi.newsletters(params);
      newsletters.value = data.results ?? [];
      newsletterTotal.value = data.count;
    } catch {
      showNotice("error", "Failed to load newsletters.");
    } finally {
      loading.value = false;
    }
  }

  async function selectNewsletter(id: number) {
    selectedNewsletter.value = null;
    try {
      const { data } = await adminNewslettersApi.newsletterDetail(id);
      selectedNewsletter.value = data;
    } catch {
      showNotice("error", "Failed to load newsletter details.");
    }
  }

  async function loadCategories() {
    try {
      const { data } = await adminNewslettersApi.categories();
      categories.value = Array.isArray(data) ? data : [];
    } catch { /* non-fatal */ }
  }

  async function createCategory(name: string) {
    try {
      const { data } = await adminNewslettersApi.createCategory(name);
      categories.value = [...categories.value, data];
      showNotice("success", `Category "${data.name}" created.`);
    } catch {
      showNotice("error", "Failed to create category.");
    }
  }

  return {
    stats,
    subscribers,
    subscriberTotal,
    newsletters,
    newsletterTotal,
    selectedNewsletter,
    categories,
    loading,
    actionLoading,
    notice,
    subscriberSearch,
    subscriberStatusFilter,
    subscriberSourceFilter,
    newsletterSearch,
    newsletterStatusFilter,
    activeSubscribers,
    inactiveSubscribers,
    loadStats,
    loadSubscribers,
    deactivateSubscriber,
    reactivateSubscriber,
    loadNewsletters,
    selectNewsletter,
    loadCategories,
    createCategory,
  };
});
