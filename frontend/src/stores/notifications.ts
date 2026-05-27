import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { notificationsApi, type NotificationChannelPref, type NotificationPreferences, type DndConfig } from "@/api/notifications";

export interface NotificationItem {
  id?: number | string;
  title?: string;
  message?: string;
  created_at?: string;
  is_read?: boolean;
  [key: string]: unknown;
}

function defaultPrefs(): Record<string, NotificationChannelPref> {
  return {
    order_updates: { in_app: true, email: true },
    messages: { in_app: true, email: false },
    payments: { in_app: true, email: true },
    support: { in_app: true, email: true },
    system: { in_app: true, email: false },
  };
}

export const useNotificationStore = defineStore("notifications", () => {
  const items = ref<NotificationItem[]>([]);
  const isLoading = ref(false);
  const page = ref(1);
  const total = ref(0);
  const pageSize = 20;
  const filter = ref<"all" | "unread" | "settings">("all");

  const prefs = ref<Record<string, NotificationChannelPref>>(defaultPrefs());
  const prefsLoading = ref(false);
  const prefsSaving = ref(false);
  const prefsError = ref("");
  const prefsSaved = ref(false);

  const dnd = ref<DndConfig>({
    enabled: false,
    quiet_hours_enabled: false,
    quiet_hours_start: "22:00",
    quiet_hours_end: "07:00",
  });

  const isDndActive = computed(() => {
    if (!dnd.value.enabled) return false;
    if (!dnd.value.quiet_hours_enabled) return true;
    const now = new Date();
    const cur = now.getHours() * 60 + now.getMinutes();
    const [sh, sm] = dnd.value.quiet_hours_start.split(":").map(Number);
    const [eh, em] = dnd.value.quiet_hours_end.split(":").map(Number);
    const start = sh * 60 + sm;
    const end = eh * 60 + em;
    return start <= end ? cur >= start && cur < end : cur >= start || cur < end;
  });

  const unreadCount = computed(
    () => items.value.filter((item) => !item.is_read).length,
  );

  const filteredItems = computed(() =>
    filter.value === "unread" ? items.value.filter((item) => !item.is_read) : items.value,
  );

  const hasMore = computed(() => items.value.length < total.value);

  async function fetchNotifications() {
    isLoading.value = true;
    page.value = 1;
    try {
      const { data } = await notificationsApi.list({ page: 1, page_size: pageSize });
      const raw = data as { results?: NotificationItem[]; count?: number } | NotificationItem[];
      if (Array.isArray(raw)) {
        items.value = raw;
        total.value = raw.length;
      } else {
        items.value = raw.results ?? [];
        total.value = raw.count ?? items.value.length;
      }
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
      const raw = data as { results?: NotificationItem[]; count?: number } | NotificationItem[];
      const newItems = Array.isArray(raw) ? raw : (raw.results ?? []);
      const newTotal = Array.isArray(raw) ? total.value : (raw.count ?? total.value);
      items.value = [...items.value, ...newItems];
      total.value = newTotal;
      page.value = nextPage;
    } finally {
      isLoading.value = false;
    }
  }

  async function markRead(id: number | string) {
    items.value = items.value.map((item) =>
      String(item.id) === String(id) ? { ...item, is_read: true } : item,
    );
    try {
      await notificationsApi.markRead(id);
    } catch {
      // optimistic — don't revert on failure
    }
  }

  async function markAllRead() {
    const unread = items.value.filter((item) => !item.is_read && item.id);
    items.value = items.value.map((item) => ({ ...item, is_read: true }));
    await Promise.allSettled(unread.map((item) => notificationsApi.markRead(item.id!)));
  }

  function push(notification: NotificationItem) {
    if (isDndActive.value) return;
    items.value = [notification, ...items.value].slice(0, 100);
    total.value = Math.max(total.value, items.value.length);
  }

  async function fetchPreferences() {
    prefsLoading.value = true;
    prefsError.value = "";
    try {
      const { data } = await notificationsApi.getPreferences();
      const defaults = defaultPrefs();
      for (const key of Object.keys(defaults)) {
        const fetched = (data as NotificationPreferences)[key] as NotificationChannelPref | undefined;
        prefs.value[key] = {
          in_app: fetched?.in_app ?? defaults[key].in_app,
          email: fetched?.email ?? defaults[key].email,
        };
      }
      const fetchedDnd = (data as NotificationPreferences)["dnd"] as DndConfig | undefined;
      if (fetchedDnd) {
        dnd.value = {
          enabled: fetchedDnd.enabled ?? false,
          quiet_hours_enabled: fetchedDnd.quiet_hours_enabled ?? false,
          quiet_hours_start: fetchedDnd.quiet_hours_start ?? "22:00",
          quiet_hours_end: fetchedDnd.quiet_hours_end ?? "07:00",
        };
      }
    } catch {
      prefsError.value = "Could not load preferences from server — using defaults.";
    } finally {
      prefsLoading.value = false;
    }
  }

  function togglePref(category: string, channel: "in_app" | "email") {
    if (!prefs.value[category]) prefs.value[category] = { in_app: true, email: false };
    prefs.value[category][channel] = !prefs.value[category][channel];
    prefsSaved.value = false;
  }

  async function savePreferences() {
    prefsSaving.value = true;
    prefsError.value = "";
    prefsSaved.value = false;
    try {
      await notificationsApi.updatePreferences({ ...prefs.value, dnd: dnd.value });
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
    prefs,
    prefsLoading,
    prefsSaving,
    prefsError,
    prefsSaved,
    dnd,
    isDndActive,
    unreadCount,
    filteredItems,
    hasMore,
    fetchNotifications,
    loadMore,
    markRead,
    markAllRead,
    push,
    fetchPreferences,
    togglePref,
    savePreferences,
  };
});
