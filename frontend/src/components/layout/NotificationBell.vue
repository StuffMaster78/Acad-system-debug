<script setup lang="ts">
import { ref } from "vue";
import { Bell } from "@lucide/vue";
import { useNotificationStore } from "@/stores/notifications";

const notifications = useNotificationStore();
const open = ref(false);

function formatDate(value?: string) {
  if (!value) return "Now";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}
</script>

<template>
  <div class="relative">
    <button
      class="focus-ring relative inline-flex h-10 w-10 items-center justify-center rounded-md border border-slate-200 bg-white"
      type="button"
      title="Notifications"
      @click="open = !open"
    >
      <Bell class="h-5 w-5" />
      <span
        v-if="notifications.unreadCount"
        class="absolute -right-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-berry px-1 text-xs font-semibold text-white"
      >
        {{ notifications.unreadCount }}
      </span>
    </button>

    <section
      v-if="open"
      class="absolute right-0 top-12 z-30 w-80 rounded-md border border-slate-200 bg-white shadow-panel"
    >
      <div class="border-b border-slate-200 px-4 py-3">
        <p class="text-sm font-semibold text-ink">Notifications</p>
      </div>
      <div v-if="notifications.items.length" class="max-h-96 divide-y divide-slate-100 overflow-y-auto">
        <article
          v-for="item in notifications.items.slice(0, 8)"
          :key="item.id ?? item.created_at ?? item.message"
          class="px-4 py-3"
        >
          <p class="text-sm font-semibold text-ink">{{ item.title || "Update" }}</p>
          <p class="mt-1 text-sm leading-5 text-graphite">{{ item.message || "New platform event" }}</p>
          <p class="mt-2 text-xs text-graphite">{{ formatDate(item.created_at) }}</p>
        </article>
      </div>
      <p v-else class="px-4 py-6 text-center text-sm text-graphite">No notifications yet.</p>
    </section>
  </div>
</template>
