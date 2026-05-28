<script setup lang="ts">
import { onMounted } from "vue";
import { Bell, CheckCheck, Loader2, MoonStar, RefreshCw, Settings2 } from "@lucide/vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { useNotificationStore } from "@/stores/notifications";
import type { UserRole } from "@/types/roles";

defineProps<{ role: UserRole }>();

const notifications = useNotificationStore();


function formatDate(value?: string) {
  if (!value) return "Just now";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

onMounted(() => {
  notifications.fetchNotifications().catch(() => undefined);
  notifications.fetchPreferences().catch(() => undefined);
});
</script>

<template>
  <div class="space-y-4">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">{{ role }}</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Notifications</h1>
        <p class="mt-2 max-w-2xl text-sm text-graphite">
          Platform alerts, order updates, messages, and system notices.
        </p>
      </div>

      <div class="flex flex-wrap items-center gap-2">
        <button
          v-if="notifications.filter !== 'settings' && notifications.unreadCount > 0"
          class="focus-ring inline-flex items-center gap-2 rounded-md border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold disabled:opacity-60"
          type="button"
          :disabled="notifications.isLoading"
          @click="notifications.markAllRead()"
        >
          <CheckCheck class="h-4 w-4" />
          Mark all read
        </button>
        <button
          v-if="notifications.filter !== 'settings'"
          class="focus-ring inline-flex items-center gap-2 rounded-md border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold disabled:opacity-60"
          type="button"
          :disabled="notifications.isLoading"
          @click="notifications.fetchNotifications()"
        >
          <RefreshCw class="h-4 w-4" :class="notifications.isLoading ? 'animate-spin' : ''" />
          Refresh
        </button>
      </div>
    </section>

    <div class="flex items-center gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1 w-fit">
      <button
        class="focus-ring rounded-md px-4 py-2 text-xs font-semibold transition-colors"
        :class="notifications.filter === 'all' ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
        type="button"
        @click="notifications.filter = 'all'"
      >
        All
        <span
          v-if="notifications.total"
          class="ml-1.5 rounded-full bg-slate-200 px-1.5 py-0.5 text-xs font-semibold text-graphite"
        >
          {{ notifications.total }}
        </span>
      </button>
      <button
        class="focus-ring rounded-md px-4 py-2 text-xs font-semibold transition-colors"
        :class="notifications.filter === 'unread' ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
        type="button"
        @click="notifications.filter = 'unread'"
      >
        Unread
        <span
          v-if="notifications.unreadCount"
          class="ml-1.5 rounded-full bg-berry px-1.5 py-0.5 text-xs font-semibold text-white"
        >
          {{ notifications.unreadCount }}
        </span>
      </button>
      <button
        class="focus-ring inline-flex items-center gap-1.5 rounded-md px-4 py-2 text-xs font-semibold transition-colors"
        :class="notifications.filter === 'settings' ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
        type="button"
        @click="notifications.filter = 'settings'"
      >
        <Settings2 class="h-3.5 w-3.5" />
        Settings
      </button>
    </div>

    <!-- Notification settings panel -->
    <template v-if="notifications.filter === 'settings'">
      <div
        v-if="notifications.prefsError"
        class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
      >
        {{ notifications.prefsError }}
      </div>

      <!-- Do Not Disturb card -->
      <section class="overflow-hidden rounded-lg border border-slate-200 bg-white">
        <div class="border-b border-slate-200 px-5 py-4">
          <div class="flex items-center gap-2">
            <MoonStar class="h-4 w-4 text-graphite" />
            <h2 class="text-base font-semibold text-ink">Do Not Disturb</h2>
            <span
              v-if="notifications.isDndActive"
              class="rounded-full bg-slate-800 px-2 py-0.5 text-xs font-semibold text-white"
            >
              Active
            </span>
          </div>
          <p class="mt-1 text-sm text-graphite">Silence incoming notifications. Quiet hours apply automatically.</p>
        </div>

        <div class="divide-y divide-slate-100">
          <!-- Master DND toggle -->
          <div class="flex items-center justify-between px-5 py-4">
            <div>
              <p class="text-sm font-medium text-ink">Enable Do Not Disturb</p>
              <p class="mt-0.5 text-xs text-graphite">No new notifications will appear while active</p>
            </div>
            <button
              class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-signal focus-visible:ring-offset-2"
              :class="notifications.dndEnabled ? 'bg-signal' : 'bg-slate-300'"
              type="button"
              role="switch"
              :aria-checked="notifications.dndEnabled"
              aria-label="Enable Do Not Disturb"
              @click="notifications.dndEnabled = !notifications.dndEnabled"
            >
              <span
                class="pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                :class="notifications.dndEnabled ? 'translate-x-5' : 'translate-x-0'"
              />
            </button>
          </div>

          <!-- Quiet hours time range -->
          <div
            v-if="notifications.dndEnabled"
            class="grid grid-cols-2 gap-4 px-5 py-4"
          >
            <div>
              <label class="block text-xs font-semibold text-graphite mb-1.5" for="qh-start">Quiet hours start</label>
              <input
                id="qh-start"
                v-model="notifications.dndStart"
                type="time"
                class="focus-ring h-9 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-graphite mb-1.5" for="qh-end">Quiet hours end</label>
              <input
                id="qh-end"
                v-model="notifications.dndEnd"
                type="time"
                class="focus-ring h-9 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
              />
            </div>
          </div>
        </div>
      </section>

      <!-- Channel preferences -->
      <section class="overflow-hidden rounded-lg border border-slate-200 bg-white">
        <div class="border-b border-slate-200 px-5 py-4">
          <h2 class="text-base font-semibold text-ink">Delivery channels</h2>
          <p class="mt-1 text-sm text-graphite">
            Choose how you receive notifications across all event types.
          </p>
        </div>

        <div v-if="notifications.prefsLoading" class="space-y-px">
          <div v-for="n in 2" :key="n" class="animate-pulse border-b border-slate-100 px-5 py-4">
            <div class="flex items-center justify-between gap-8">
              <div class="flex-1 space-y-2">
                <div class="h-3.5 w-1/3 rounded bg-slate-200" />
                <div class="h-3 w-1/2 rounded bg-slate-100" />
              </div>
              <div class="h-6 w-11 rounded-full bg-slate-200" />
            </div>
          </div>
        </div>

        <template v-else>
          <div class="divide-y divide-slate-100">
            <!-- In-app toggle -->
            <div class="flex items-center justify-between px-5 py-4">
              <div>
                <p class="text-sm font-medium text-ink">In-app notifications</p>
                <p class="mt-0.5 text-xs text-graphite">Show alerts and the notification bell inside the platform</p>
              </div>
              <button
                class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-signal focus-visible:ring-offset-2"
                :class="notifications.inAppEnabled ? 'bg-signal' : 'bg-slate-300'"
                type="button"
                role="switch"
                :aria-checked="notifications.inAppEnabled"
                aria-label="Enable in-app notifications"
                @click="notifications.inAppEnabled = !notifications.inAppEnabled"
              >
                <span
                  class="pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                  :class="notifications.inAppEnabled ? 'translate-x-5' : 'translate-x-0'"
                />
              </button>
            </div>

            <!-- Email toggle -->
            <div class="flex items-center justify-between px-5 py-4">
              <div>
                <p class="text-sm font-medium text-ink">Email notifications</p>
                <p class="mt-0.5 text-xs text-graphite">Receive notification emails for key events (order updates, payments)</p>
              </div>
              <button
                class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-signal focus-visible:ring-offset-2"
                :class="notifications.emailEnabled ? 'bg-signal' : 'bg-slate-300'"
                type="button"
                role="switch"
                :aria-checked="notifications.emailEnabled"
                aria-label="Enable email notifications"
                @click="notifications.emailEnabled = !notifications.emailEnabled"
              >
                <span
                  class="pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                  :class="notifications.emailEnabled ? 'translate-x-5' : 'translate-x-0'"
                />
              </button>
            </div>
          </div>

          <div class="flex items-center gap-4 border-t border-slate-200 px-5 py-4">
            <button
              class="focus-ring inline-flex items-center gap-2 rounded-md bg-ink px-4 py-2.5 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
              type="button"
              :disabled="notifications.prefsSaving"
              @click="notifications.savePreferences()"
            >
              <Loader2 v-if="notifications.prefsSaving" class="h-4 w-4 animate-spin" />
              Save preferences
            </button>
            <p v-if="notifications.prefsSaved" class="text-sm font-medium text-signal">
              Preferences saved.
            </p>
          </div>
        </template>
      </section>
    </template>

    <!-- Notification list -->
    <div v-else class="rounded-lg border border-slate-200 bg-white">
      <div v-if="notifications.isLoading && !notifications.items.length" class="space-y-px">
        <div
          v-for="n in 6"
          :key="n"
          class="animate-pulse border-b border-slate-100 px-5 py-4"
          aria-hidden="true"
        >
          <div class="flex gap-3">
            <div class="mt-1 h-2 w-2 shrink-0 rounded-full bg-slate-200" />
            <div class="flex-1 space-y-2">
              <div class="h-4 w-1/2 rounded bg-slate-200" />
              <div class="h-3 w-3/4 rounded bg-slate-100" />
              <div class="h-3 w-1/4 rounded bg-slate-100" />
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="!notifications.filteredItems.length" class="p-10">
        <EmptyState
          :icon="Bell"
          :title="notifications.filter === 'unread' ? 'All caught up' : 'No notifications yet'"
          :message="notifications.filter === 'unread'
            ? 'You have no unread notifications.'
            : 'Platform alerts and order updates will appear here.'"
        />
      </div>

      <div v-else class="divide-y divide-slate-100">
        <button
          v-for="item in notifications.filteredItems"
          :key="String(item.id)"
          class="focus-ring grid w-full gap-2 px-5 py-4 text-left transition-colors hover:bg-slate-50"
          :class="item.is_read ? 'opacity-70' : ''"
          type="button"
          @click="item.id && !item.is_read && notifications.markRead(item.id)"
        >
          <div class="flex items-start gap-3">
            <span
              class="mt-1.5 h-2 w-2 shrink-0 rounded-full transition-colors"
              :class="item.is_read ? 'bg-slate-200' : 'bg-signal'"
              aria-hidden="true"
            />
            <div class="min-w-0 flex-1">
              <p class="font-semibold text-ink" :class="item.is_read ? 'font-normal' : ''">
                {{ item.title || "Notification" }}
              </p>
              <p v-if="item.message" class="mt-1 text-sm leading-6 text-graphite">
                {{ item.message }}
              </p>
              <p class="mt-2 text-xs text-slate-400">{{ formatDate(item.created_at) }}</p>
            </div>
          </div>
        </button>
      </div>

      <div
        v-if="notifications.hasMore && !notifications.isLoading"
        class="border-t border-slate-100 px-5 py-4 text-center"
      >
        <button
          class="focus-ring inline-flex items-center gap-2 rounded-md border border-slate-200 px-4 py-2 text-sm font-semibold text-ink hover:bg-slate-50 disabled:opacity-60"
          type="button"
          @click="notifications.loadMore()"
        >
          Load more
        </button>
      </div>

      <div
        v-if="notifications.isLoading && notifications.items.length"
        class="border-t border-slate-100 px-5 py-4 text-center"
      >
        <Loader2 class="mx-auto h-5 w-5 animate-spin text-slate-400" />
      </div>
    </div>
  </div>
</template>
