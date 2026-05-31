import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { notificationsApi, type MasterPreferences, type NotificationItem } from "@/api/notifications";

export type { NotificationItem };

function hourToTime(h: number): string {
  return `${String(h).padStart(2, "0")}:00`;
}

function timeToHour(t: string): number {
  return parseInt(t.split(":")[0], 10);
}

export const useNotificationStore = defineStore("notifications", () => {
  const items = ref<NotificationItem[]>([]);
  const isLoading = ref(false);
  const page = ref(1);
  const total = ref(0);
  const pageSize = 20;
  const filter = ref<"all" | "unread" | "settings">("all");

  // Master channel toggles (mapped from/to backend)
  const emailEnabled = ref(true);
  const inAppEnabled = ref(true);

  // DND — stored as display strings (HH:MM) for the time inputs
  const dndEnabled = ref(false);
  const dndStart = ref("22:00");
  const dndEnd = ref("07:00");

  // Preference UI state
  const prefsLoading = ref(false);
  const prefsSaving = ref(false);
  const prefsError = ref("");
  const prefsSaved = ref(false);

  const isDndActive = computed(() => {
    if (!dndEnabled.value) return false;
    const now = new Date();
    const cur = now.getHours() * 60 + now.getMinutes();
    const [sh] = dndStart.value.split(":").map(Number);
    const [eh] = dndEnd.value.split(":").map(Number);
    const start = sh * 60;
    const end = eh * 60;
    return start <= end ? cur >= start && cur < end : cur >= start || cur < end;
  });

  const unreadCount = computed(() => items.value.filter((n) => !n.is_read).length);
  const filteredItems = computed(() =>
    filter.value === "unread" ? items.value.filter((n) => !n.is_read) : items.value,
  );
  const hasMore = computed(() => items.value.length < total.value);

  async function fetchNotifications() {
    isLoading.value = true;
    page.value = 1;
    try {
      const { data } = await notificationsApi.list({ page: 1, page_size: pageSize });
      items.value = data.results ?? [];
      total.value = data.count ?? items.value.length;
    } catch {
      // Degrade silently — bell still renders, just shows empty state.
      // Common for staff roles without a website context on first load.
      items.value = [];
      total.value = 0;
    } finally {
      isLoading.value = false;
    }
  }

  async function loadMore() {
    if (!hasMore.value || isLoading.value) return;
    isLoading.value = true;
    const nextPage = page.value + 1;
    try {
      const { data } = await notificationsApi.list({ page: nextPage, page_size: pageSize });
      items.value = [...items.value, ...(data.results ?? [])];
      total.value = data.count ?? total.value;
      page.value = nextPage;
    } finally {
      isLoading.value = false;
    }
  }

  async function markRead(id: number | string) {
    items.value = items.value.map((n) =>
      String(n.id) === String(id) ? { ...n, is_read: true } : n,
    );
    try {
      await notificationsApi.markRead(id);
    } catch {
      // optimistic — don't revert on failure
    }
  }

  async function markAllRead() {
    items.value = items.value.map((n) => ({ ...n, is_read: true }));
    try {
      await notificationsApi.markAllRead();
    } catch {
      // optimistic — don't revert on failure
    }
  }

  function push(notification: NotificationItem) {
    if (isDndActive.value) return;
    items.value = [notification, ...items.value].slice(0, 100);
    total.value = Math.max(total.value, items.value.length);
  }

  async function pollUnreadCount(): Promise<NotificationItem | null> {
    try {
      const { data } = await notificationsApi.poll();
      // Sync unread count without refetching the whole list
      if (typeof data.unread_count === "number") {
        const currentUnread = items.value.filter((n) => !n.is_read).length;
        if (data.unread_count > currentUnread && data.latest && !isDndActive.value) {
          push(data.latest);
        }
      }
      return data.latest ?? null;
    } catch {
      return null;
    }
  }

  async function fetchPreferences() {
    prefsLoading.value = true;
    prefsError.value = "";
    try {
      const { data } = await notificationsApi.getPreferences();
      emailEnabled.value = data.email_enabled ?? true;
      inAppEnabled.value = data.in_app_enabled ?? true;
      dndEnabled.value = data.dnd_enabled ?? false;
      dndStart.value = hourToTime(data.dnd_start_hour ?? 22);
      dndEnd.value = hourToTime(data.dnd_end_hour ?? 7);
    } catch {
      prefsError.value = "Could not load preferences from server — using defaults.";
    } finally {
      prefsLoading.value = false;
    }
  }

  async function savePreferences() {
    prefsSaving.value = true;
    prefsError.value = "";
    prefsSaved.value = false;
    const payload: Partial<MasterPreferences> = {
      email_enabled: emailEnabled.value,
      in_app_enabled: inAppEnabled.value,
      dnd_enabled: dndEnabled.value,
      dnd_start_hour: timeToHour(dndStart.value),
      dnd_end_hour: timeToHour(dndEnd.value),
    };
    try {
      await notificationsApi.updatePreferences(payload);
      prefsSaved.value = true;
    } catch {
      prefsError.value = "Could not save preferences. Please try again.";
    } finally {
      prefsSaving.value = false;
    }
  }

  return {
    items,
    isLoading,
    page,
    total,
    filter,
    emailEnabled,
    inAppEnabled,
    dndEnabled,
    dndStart,
    dndEnd,
    prefsLoading,
    prefsSaving,
    prefsError,
    prefsSaved,
    isDndActive,
    unreadCount,
    filteredItems,
    hasMore,
    fetchNotifications,
    loadMore,
    markRead,
    markAllRead,
    push,
    pollUnreadCount,
    fetchPreferences,
    savePreferences,
  };
});
