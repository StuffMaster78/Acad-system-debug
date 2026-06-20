import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { writerApi } from "@/api/writer";
import { walletsApi } from "@/api/wallets";
import { useUiStore } from "@/stores/ui";
import { useAuthStore } from "@/stores/auth";
import type { PayoutRequest, PayoutRequestPayload } from "@/types/wallet";
import type {
  WriterAvailability,
  WriterBalance,
  WriterCompensationSummary,
  WriterCurrentWindow,
  WriterEvent,
  WriterProfile,
} from "@/types/writer";
import type { OrderSummary } from "@/types/orders";

function previewProfile(): WriterProfile {
  return {
    id: 108,
    registration_id: "WR-0108",
    display_name: "Alex Writer",
    email: "writer@preview.local",
    writer_level: "Premium",
    rating: "4.8",
    status: "active",
    is_accepting_orders: true,
    onboarding_status: "completed",
  };
}

function previewAvailability(): WriterAvailability {
  return { active_window: null, upcoming_windows: [] };
}

function previewCurrentWindow(): WriterCurrentWindow {
  return { window: null, net: "320.00", count: 5, is_processing: false };
}

function previewBalance(): WriterBalance {
  return { pending: "85.00", lifetime: "4280.00" };
}

function previewSummary(): WriterCompensationSummary {
  return {
    total_earned: "4280.00",
    total_paid: "4195.00",
    total_pending: "85.00",
    completed_orders: 31,
  };
}

function previewEvents(): WriterEvent[] {
  return [
    {
      id: 1, event_type: "order_payment", status: "posted",
      amount: "120.00", is_positive: true, title: "Order #1042 payment",
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    },
    {
      id: 2, event_type: "order_payment", status: "posted",
      amount: "200.00", is_positive: true, title: "Order #1039 payment",
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    },
  ];
}

function previewAssignmentsList(): OrderSummary[] {
  return [
    {
      id: 1042, topic: "Healthcare policy brief",
      status: "in_progress", payment_status: "paid",
      total_price: "186.00", amount_paid: "186.00", remaining_balance: "0.00",
      currency: "USD", service_code: "paper", service_family: "academic_writing",
      client_deadline: new Date(Date.now() + 1000 * 60 * 60 * 18).toISOString(),
      writer_deadline: new Date(Date.now() + 1000 * 60 * 60 * 12).toISOString(),
    },
    {
      id: 1039, topic: "Machine learning report",
      status: "revision_requested", payment_status: "paid",
      total_price: "240.00", amount_paid: "240.00", remaining_balance: "0.00",
      currency: "USD", service_code: "paper", service_family: "academic_writing",
      client_deadline: new Date(Date.now() + 1000 * 60 * 60 * 36).toISOString(),
      writer_deadline: new Date(Date.now() + 1000 * 60 * 60 * 24).toISOString(),
    },
  ];
}

function previewPoolOrdersList(): OrderSummary[] {
  return [
    {
      id: 1055, topic: "Environmental law case study",
      status: "ready_for_staffing", payment_status: "paid",
      total_price: "160.00", amount_paid: "160.00", remaining_balance: "0.00",
      currency: "USD", service_code: "paper", service_family: "academic_writing",
      client_deadline: new Date(Date.now() + 1000 * 60 * 60 * 48).toISOString(),
      writer_deadline: new Date(Date.now() + 1000 * 60 * 60 * 40).toISOString(),
    },
    {
      id: 1056, topic: "Business finance presentation",
      status: "ready_for_staffing", payment_status: "paid",
      total_price: "98.00", amount_paid: "98.00", remaining_balance: "0.00",
      currency: "USD", service_code: "paper", service_family: "academic_writing",
      client_deadline: new Date(Date.now() + 1000 * 60 * 60 * 72).toISOString(),
      writer_deadline: new Date(Date.now() + 1000 * 60 * 60 * 60).toISOString(),
    },
  ];
}

export const useWriterWorkspaceStore = defineStore("writerWorkspace", () => {
  const profile = ref<WriterProfile | null>(null);
  const availability = ref<WriterAvailability | null>(null);
  const currentWindow = ref<WriterCurrentWindow | null>(null);
  const balance = ref<WriterBalance | null>(null);
  const summary = ref<WriterCompensationSummary | null>(null);
  const events = ref<WriterEvent[]>([]);
  const poolOrders = ref<OrderSummary[]>([]);
  const poolPagination = ref({ page: 1, pageSize: 20, count: 0 });
  const assignments = ref<OrderSummary[]>([]);
  const assignmentsPagination = ref({ page: 1, pageSize: 20, count: 0 });
  const payoutRequests = ref<PayoutRequest[]>([]);
  const eventsPagination = ref({ page: 1, pageSize: 20, count: 0 });
  const isLoading = ref(false);
  const isPoolLoading = ref(false);
  const isAssignmentsLoading = ref(false);
  const isMutating = ref(false);
  const error = ref("");
  const poolError = ref("");
  const assignmentsError = ref("");
  const notice = ref("");

  const isUnavailable = computed(() => Boolean(availability.value?.active_window));
  const isAcceptingOrders = computed(() => {
    const raw = profile.value?.is_accepting_orders;
    if (typeof raw === "boolean") return raw;
    return !isUnavailable.value;
  });

  async function hydrate() {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        profile.value = previewProfile();
        availability.value = previewAvailability();
        currentWindow.value = previewCurrentWindow();
        balance.value = previewBalance();
        summary.value = previewSummary();
        events.value = previewEvents();
        return;
      }
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
      if (eventsRes.status === "fulfilled") {
        const d = eventsRes.value.data;
        events.value = Array.isArray(d) ? d : d.results;
      }

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

  async function saveProfile(payload: Partial<Pick<WriterProfile, "display_name"> & { bio?: string }>) {
    const ui = useUiStore();
    isMutating.value = true;
    error.value = "";
    try {
      const { data } = await writerApi.updateProfile(payload);
      profile.value = { ...(profile.value ?? {}), ...data };
      ui.toast("Profile updated.", "success");
    } catch (caught) {
      error.value = "Could not update profile.";
      ui.toast("Could not update profile.", "error");
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function toggleAcceptingOrders() {
    const ui = useUiStore();
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
      const msg = data.is_accepting_orders ? "You are accepting new orders." : "You are paused for new orders.";
      notice.value = msg;
      ui.toast(msg, "info");
    } catch (caught) {
      error.value = "Unable to update availability.";
      ui.toast("Unable to update availability.", "error");
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function expressInterest(orderId: number | string, message: string) {
    const ui = useUiStore();
    isMutating.value = true;
    error.value = "";
    notice.value = "";
    try {
      const { data } = await writerApi.expressInterest(orderId, message);
      notice.value = data.message;
      ui.toast(data.message ?? "Interest expressed.", "success");
      return data;
    } catch (caught) {
      error.value = "Unable to express interest in that order.";
      ui.toast("Unable to express interest in that order.", "error");
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function takeOrder(orderId: number | string) {
    const ui = useUiStore();
    isMutating.value = true;
    error.value = "";
    notice.value = "";
    try {
      const { data } = await writerApi.takeOrder(orderId);
      notice.value = data.message;
      ui.toast(data.message ?? "Order taken.", "success");
      return data;
    } catch (caught) {
      error.value = "Unable to take that order.";
      ui.toast("Unable to take that order.", "error");
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function fetchPoolOrders(page = 1, params?: Record<string, unknown>) {
    const auth = useAuthStore();
    isPoolLoading.value = true;
    poolError.value = "";
    try {
      if (auth.isPreviewSession) {
        poolOrders.value = previewPoolOrdersList();
        poolPagination.value = { ...poolPagination.value, page: 1, count: previewPoolOrdersList().length };
        return;
      }
      const { data } = await writerApi.poolOrders({
        page,
        page_size: poolPagination.value.pageSize,
        ...params,
      });
      if (Array.isArray(data)) {
        poolOrders.value = data;
      } else {
        poolOrders.value = data.results ?? [];
        poolPagination.value = { ...poolPagination.value, page, count: data.count ?? 0 };
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

  async function fetchAssignments(page = 1, status?: string) {
    const auth = useAuthStore();
    isAssignmentsLoading.value = true;
    assignmentsError.value = "";
    try {
      if (auth.isPreviewSession) {
        assignments.value = previewAssignmentsList();
        assignmentsPagination.value = { ...assignmentsPagination.value, page: 1, count: previewAssignmentsList().length };
        return;
      }
      const params: Record<string, unknown> = {
        page,
        page_size: assignmentsPagination.value.pageSize,
      };
      if (status) params.status = status;
      const { data } = await writerApi.assignments(params);
      if (Array.isArray(data)) {
        assignments.value = data;
      } else {
        assignments.value = data.results ?? [];
        assignmentsPagination.value = { ...assignmentsPagination.value, page, count: data.count ?? 0 };
      }
    } catch {
      assignmentsError.value = "Could not load assignments from the backend.";
    } finally {
      isAssignmentsLoading.value = false;
    }
  }

  async function fetchEvents(page = 1) {
    isLoading.value = true;
    try {
      const { data } = await writerApi.events({
        page,
        page_size: eventsPagination.value.pageSize,
      });
      if (Array.isArray(data)) {
        events.value = data;
      } else {
        events.value = (data as { results: WriterEvent[] }).results;
        eventsPagination.value = {
          ...eventsPagination.value,
          page,
          count: (data as { count: number }).count,
        };
      }
    } catch {
      // non-critical
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchPayoutRequests() {
    try {
      const { data } = await walletsApi.payoutRequests({ page_size: 20 });
      payoutRequests.value = Array.isArray(data) ? data : data.results;
    } catch {
      // non-critical
    }
  }

  async function requestPayout(payload: PayoutRequestPayload) {
    const ui = useUiStore();
    isMutating.value = true;
    error.value = "";
    notice.value = "";
    try {
      await walletsApi.requestPayout(payload);
      notice.value = "Payout request submitted.";
      ui.toast("Payout request submitted.", "success");
      await fetchPayoutRequests();
    } catch (caught) {
      error.value = "Unable to submit payout request.";
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function scheduleUnavailability(payload: { start_at: string; end_at?: string | null; reason?: string }) {
    const ui = useUiStore();
    isMutating.value = true;
    error.value = "";
    notice.value = "";
    try {
      const { data } = await writerApi.createAvailabilityWindow(payload);
      if (availability.value) {
        availability.value = {
          ...availability.value,
          upcoming_windows: [...(availability.value.upcoming_windows ?? []), data],
        };
      }
      notice.value = "Unavailability window scheduled.";
      ui.toast("Unavailability window scheduled.", "info");
    } catch (caught) {
      error.value = "Unable to schedule that unavailability window.";
      ui.toast("Unable to schedule that unavailability window.", "error");
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function cancelAvailabilityWindow(windowId: number | string) {
    const ui = useUiStore();
    isMutating.value = true;
    error.value = "";
    notice.value = "";
    try {
      await writerApi.cancelAvailabilityWindow(windowId);
      if (availability.value) {
        const active = availability.value.active_window;
        availability.value = {
          active_window: active?.id === windowId ? null : active,
          upcoming_windows: (availability.value.upcoming_windows ?? []).filter(
            (w) => w.id !== windowId,
          ),
        };
      }
      notice.value = "Availability window cancelled.";
      ui.toast("Availability window cancelled.", "success");
    } catch (caught) {
      error.value = "Unable to cancel that window.";
      ui.toast("Unable to cancel that window.", "error");
      throw caught;
    } finally {
      isMutating.value = false;
    }
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
    eventsPagination,
    poolOrders,
    poolPagination,
    assignments,
    assignmentsPagination,
    payoutRequests,
    isLoading,
    isPoolLoading,
    isAssignmentsLoading,
    isMutating,
    error,
    poolError,
    assignmentsError,
    notice,
    isUnavailable,
    isAcceptingOrders,
    hydrate,
    fetchPoolOrders,
    removePoolOrder,
    fetchAssignments,
    fetchEvents,
    fetchPayoutRequests,
    requestPayout,
    saveProfile,
    toggleAcceptingOrders,
    scheduleUnavailability,
    cancelAvailabilityWindow,
    expressInterest,
    takeOrder,
    withdrawInterest,
  };
});
