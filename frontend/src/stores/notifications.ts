import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { notificationsApi } from "@/api/notifications";

export interface NotificationItem {
  id?: number | string;
  title?: string;
  message?: string;
  created_at?: string;
  is_read?: boolean;
  [key: string]: unknown;
}

export const useNotificationStore = defineStore("notifications", () => {
  const items = ref<NotificationItem[]>([]);
  const isLoading = ref(false);

  const unreadCount = computed(
    () => items.value.filter((item) => !item.is_read).length,
  );

  async function fetchNotifications() {
    isLoading.value = true;
    try {
      const { data } = await notificationsApi.list();
      items.value = data.results ?? data;
    } finally {
      isLoading.value = false;
    }
  }

  function push(notification: NotificationItem) {
    items.value = [notification, ...items.value].slice(0, 100);
  }

  return {
    items,
    isLoading,
    unreadCount,
    fetchNotifications,
    push,
  };
});
