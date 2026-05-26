import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { activityApi } from "@/api/activity";
import { useAuthStore } from "@/stores/auth";
import type { ActivityEvent } from "@/types/activity";

type ListResponse<T> = T[] | { results: T[] };

function normalizeList<T>(data: ListResponse<T>): T[] {
  return Array.isArray(data) ? data : data.results;
}

function previewEvents(role: string): ActivityEvent[] {
  const now = Date.now();
  return [
    {
      id: "preview-1",
      verb: "file.uploaded",
      actor_type: "writer",
      severity: "success",
      audiences: [role],
      title: "Writer #10001 uploaded a draft",
      summary: "A draft was uploaded for Order #1042 and is visible to the client, writer, and staff working the order.",
      metadata: { order_id: 1042 },
      occurred_at: new Date(now - 1000 * 60 * 16).toISOString(),
      created_at: new Date(now - 1000 * 60 * 16).toISOString(),
      card: {
        id: "preview-1",
        verb: "file.uploaded",
        severity: "success",
        title: "Writer #10001 uploaded a draft",
        summary: "A draft was uploaded for Order #1042.",
        metadata: { order_id: 1042 },
        occurred_at: new Date(now - 1000 * 60 * 16).toISOString(),
        actor: { type: "user", id: "10001", label: "writer #10001" },
        target: { type: "order", id: "1042", label: "Order #1042" },
      },
    },
    {
      id: "preview-2",
      verb: "message.sent",
      actor_type: "client",
      severity: "info",
      audiences: [role],
      title: "Client sent a message",
      summary: "A client replied in the order thread. The assigned writer can see the same activity item.",
      metadata: { order_id: 1042 },
      occurred_at: new Date(now - 1000 * 60 * 42).toISOString(),
      created_at: new Date(now - 1000 * 60 * 42).toISOString(),
      card: {
        id: "preview-2",
        verb: "message.sent",
        severity: "info",
        title: "Client sent a message",
        summary: "A client replied in the order thread.",
        metadata: { order_id: 1042 },
        occurred_at: new Date(now - 1000 * 60 * 42).toISOString(),
        actor: { type: "user", id: "101", label: "Nadia Morgan" },
        target: { type: "order", id: "1042", label: "Order #1042" },
      },
    },
    {
      id: "preview-3",
      verb: "order.paid",
      actor_type: "client",
      severity: "success",
      audiences: [role],
      title: "Order payment received",
      summary: "Payment posted and order moved into the staffing workflow.",
      metadata: { order_id: 1043 },
      occurred_at: new Date(now - 1000 * 60 * 90).toISOString(),
      created_at: new Date(now - 1000 * 60 * 90).toISOString(),
      card: {
        id: "preview-3",
        verb: "order.paid",
        severity: "success",
        title: "Order payment received",
        summary: "Payment posted and order moved into the staffing workflow.",
        metadata: { order_id: 1043 },
        occurred_at: new Date(now - 1000 * 60 * 90).toISOString(),
        actor: { type: "user", id: "101", label: "Nadia Morgan" },
        target: { type: "order", id: "1043", label: "Order #1043" },
      },
    },
  ];
}

export const useActivityStore = defineStore("activity", () => {
  const events = ref<ActivityEvent[]>([]);
  const query = ref("");
  const severity = ref<"all" | "info" | "success" | "warning" | "critical">("all");
  const isLoading = ref(false);
  const error = ref("");

  const filteredEvents = computed(() => {
    const needle = query.value.trim().toLowerCase();
    return events.value.filter((event) => {
      const severityMatches = severity.value === "all" || event.severity === severity.value;
      const textMatches =
        !needle ||
        [
          event.title,
          event.summary,
          event.verb,
          event.actor_type,
          event.card?.actor?.label,
          event.card?.target?.label,
        ].some((value) => String(value ?? "").toLowerCase().includes(needle));
      return severityMatches && textMatches;
    });
  });

  async function hydrate() {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        events.value = previewEvents(auth.role ?? "client");
        return;
      }

      const { data } = await activityApi.feed({ page_size: 50 });
      events.value = normalizeList(data);
    } catch (caught) {
      error.value = "Unable to load activity.";
      throw caught;
    } finally {
      isLoading.value = false;
    }
  }

  async function markRead(eventId: string) {
    const auth = useAuthStore();
    if (auth.isPreviewSession) return;
    await activityApi.markRead(eventId);
  }

  return {
    events,
    query,
    severity,
    isLoading,
    error,
    filteredEvents,
    hydrate,
    markRead,
  };
});
