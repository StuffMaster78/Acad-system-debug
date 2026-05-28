<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { Bell, CheckCheck, MoonStar } from "@lucide/vue";
import { useAuthStore } from "@/stores/auth";
import { useNotificationStore } from "@/stores/notifications";

const auth = useAuthStore();
const notificationsRoute = computed(() => `/${auth.role ?? "client"}/notifications`);

const notifications = useNotificationStore();
const open = ref(false);
const root = ref<HTMLElement | null>(null);

function formatDate(value?: string) {
  if (!value) return "Just now";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

async function toggle() {
  open.value = !open.value;
  if (open.value && !notifications.items.length) {
    await notifications.fetchNotifications();
  }
}

function onOutsideClick(event: MouseEvent) {
  if (root.value && !root.value.contains(event.target as Node)) {
    open.value = false;
  }
}

onMounted(() => {
  document.addEventListener("mousedown", onOutsideClick);
  notifications.fetchNotifications().catch(() => undefined);
});

onUnmounted(() => {
  document.removeEventListener("mousedown", onOutsideClick);
});
</script>

<template>
  <div ref="root" class="relative">
    <button
      class="focus-ring relative inline-flex h-10 w-10 items-center justify-center rounded-md border border-slate-200 bg-white"
      type="button"
      :title="notifications.isDndActive ? 'Notifications (Do Not Disturb active)' : 'Notifications'"
      @click="toggle"
    >
      <Bell class="h-5 w-5" :class="notifications.isDndActive ? 'text-slate-400' : ''" />
      <MoonStar
        v-if="notifications.isDndActive"
        class="absolute -right-1 -top-1 h-4 w-4 text-slate-600"
      />
      <span
        v-else-if="notifications.unreadCount"
        class="absolute -right-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-berry px-1 text-xs font-semibold text-white"
      >
        {{ notifications.unreadCount > 99 ? "99+" : notifications.unreadCount }}
      </span>
    </button>

    <section
      v-if="open"
      class="absolute right-0 top-12 z-30 w-80 overflow-hidden rounded-md border border-slate-200 bg-white"
    >
      <div class="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <p class="text-sm font-semibold text-ink">Notifications</p>
        <button
          v-if="notifications.unreadCount"
          class="focus-ring inline-flex items-center gap-1.5 rounded text-xs font-semibold text-signal hover:underline"
          type="button"
          @click="notifications.markAllRead()"
        >
          <CheckCheck class="h-3.5 w-3.5" />
          Mark all read
        </button>
      </div>

      <div v-if="notifications.isLoading" class="px-4 py-6 text-center text-sm text-graphite">
        Loading…
      </div>

      <div v-else-if="notifications.items.length" class="max-h-96 divide-y divide-slate-100 overflow-y-auto">
        <button
          v-for="item in notifications.items.slice(0, 20)"
          :key="String(item.id ?? item.created_at ?? item.message)"
          class="w-full px-4 py-3 text-left transition hover:bg-slate-50"
          :class="item.is_read ? 'opacity-60' : ''"
          type="button"
          @click="item.id && !item.is_read && notifications.markRead(item.id)"
        >
          <div class="flex items-start gap-2">
            <span
              class="mt-1.5 h-2 w-2 shrink-0 rounded-full"
              :class="item.is_read ? 'bg-transparent' : 'bg-signal'"
            />
            <div class="min-w-0">
              <p class="text-sm font-semibold text-ink">{{ item.title || "Update" }}</p>
              <p class="mt-1 text-sm leading-5 text-graphite">{{ item.message || "New platform event" }}</p>
              <p class="mt-2 text-xs text-slate-400">{{ formatDate(item.created_at) }}</p>
            </div>
          </div>
        </button>
      </div>

      <p v-else class="px-4 py-6 text-center text-sm text-graphite">No notifications yet.</p>

      <div class="border-t border-slate-200 px-4 py-3">
        <RouterLink
          class="focus-ring block text-center text-xs font-semibold text-signal hover:underline"
          :to="notificationsRoute"
          @click="open = false"
        >
          See all notifications
        </RouterLink>
      </div>
    </section>
  </div>
</template>
