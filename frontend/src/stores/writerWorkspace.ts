import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { writerApi } from "@/api/writer";
import type {
  WriterAvailability,
  WriterBalance,
  WriterCompensationSummary,
  WriterCurrentWindow,
  WriterEvent,
  WriterProfile,
} from "@/types/writer";
import type { OrderSummary } from "@/types/orders";

export const useWriterWorkspaceStore = defineStore("writerWorkspace", () => {
  const profile = ref<WriterProfile | null>(null);
  const availability = ref<WriterAvailability | null>(null);
  const currentWindow = ref<WriterCurrentWindow | null>(null);
  const balance = ref<WriterBalance | null>(null);
  const summary = ref<WriterCompensationSummary | null>(null);
  const events = ref<WriterEvent[]>([]);
  const poolOrders = ref<OrderSummary[]>([]);
  const poolPagination = ref({ page: 1, pageSize: 20, count: 0 });
  const isLoading = ref(false);
  const isPoolLoading = ref(false);
  const isMutating = ref(false);
  const error = ref("");
  const poolError = ref("");
  const notice = ref("");

  const isUnavailable = computed(() => Boolean(availability.value?.active_window));
  const isAcceptingOrders = computed(() => {
    const raw = profile.value?.is_accepting_orders;
    if (typeof raw === "boolean") return raw;
    return !isUnavailable.value;
  });

  async function hydrate() {
    isLoading.value = true;
    error.value = "";
    try {
      const [profileRes, availabilityRes, windowRes, balanceRes, summaryRes, eventsRes] =
        await Promise.allSettled([
          writerApi.profile(),
          writerApi.availability(),
          writerApi.currentWindow(),
          writerApi.balance(),
          writerApi.compensationSummary(),
          writerApi.events({ limit: 5 }),
        ]);

      if (profileRes.status === "fulfilled") profile.value = profileRes.value.data;
      if (availabilityRes.status === "fulfilled") availability.value = availabilityRes.value.data;
      if (windowRes.status === "fulfilled") currentWindow.value = windowRes.value.data;
      if (balanceRes.status === "fulfilled") balance.value = balanceRes.value.data;
      if (summaryRes.status === "fulfilled") summary.value = summaryRes.value.data;
      if (eventsRes.status === "fulfilled") events.value = eventsRes.value.data;

      const failed = [
        profileRes,
        availabilityRes,
        windowRes,
        balanceRes,
        summaryRes,
        eventsRes,
      ].some((result) => result.status === "rejected");

      if (failed) {
        error.value = "Some writer workspace data is unavailable from the backend.";
      }
    } finally {
      isLoading.value = false;
    }
  }

  async function toggleAcceptingOrders() {
    isMutating.value = true;
    error.value = "";
    notice.value = "";
    try {
      const next = !isAcceptingOrders.value;
      const { data } = await writerApi.toggleAcceptingOrders(next);
      profile.value = {
        ...(profile.value ?? {}),
        is_accepting_orders: data.is_accepting_orders,
      };
      notice.value = data.is_accepting_orders
        ? "You are accepting new orders."
        : "You are paused for new orders.";
    } catch (caught) {
      error.value = "Unable to update availability.";
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function expressInterest(orderId: number | string, message: string) {
    isMutating.value = true;
    error.value = "";
    notice.value = "";
    try {
      const { data } = await writerApi.expressInterest(orderId, message);
      notice.value = data.message;
      return data;
    } catch (caught) {
      error.value = "Unable to express interest in that order.";
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function takeOrder(orderId: number | string) {
    isMutating.value = true;
    error.value = "";
    notice.value = "";
    try {
      const { data } = await writerApi.takeOrder(orderId);
      notice.value = data.message;
      return data;
    } catch (caught) {
      error.value = "Unable to take that order.";
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function fetchPoolOrders(page = 1, params?: Record<string, unknown>) {
    isPoolLoading.value = true;
    poolError.value = "";
    try {
      const { data } = await writerApi.poolOrders({
        page,
        page_size: poolPagination.value.pageSize,
        ...params,
      });
      if (Array.isArray(data)) {
        poolOrders.value = data;
      } else {
        poolOrders.value = data.results;
        poolPagination.value = { ...poolPagination.value, page, count: data.count };
      }
    } catch {
      poolError.value = "Could not load available orders from the backend.";
    } finally {
      isPoolLoading.value = false;
    }
  }

  function removePoolOrder(orderId: number | string) {
    poolOrders.value = poolOrders.value.filter((o) => String(o.id) !== String(orderId));
  }

  async function withdrawInterest(interestId: number | string) {
    isMutating.value = true;
    error.value = "";
    notice.value = "";
    try {
      const { data } = await writerApi.withdrawInterest(interestId);
      notice.value = data.message;
      return data;
    } catch (caught) {
      error.value = "Unable to withdraw that interest.";
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  return {
    profile,
    availability,
    currentWindow,
    balance,
    summary,
    events,
    poolOrders,
    poolPagination,
    isLoading,
    isPoolLoading,
    isMutating,
    error,
    poolError,
    notice,
    isUnavailable,
    isAcceptingOrders,
    hydrate,
    fetchPoolOrders,
    removePoolOrder,
    toggleAcceptingOrders,
    expressInterest,
    takeOrder,
    withdrawInterest,
  };
});
