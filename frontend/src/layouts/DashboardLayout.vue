<script setup lang="ts">
import { computed } from "vue";
import { RouterLink, RouterView, useRoute } from "vue-router";
import { Bell, LogOut, Menu, Search } from "@lucide/vue";
import { navigationByRole } from "@/config/navigation";
import { useAuthStore } from "@/stores/auth";
import { useNotifications } from "@/composables/useNotifications";
import type { UserRole } from "@/types/roles";

const props = defineProps<{
  role: UserRole;
}>();

const route = useRoute();
const auth = useAuthStore();
const { notifications, isConnected } = useNotifications();
const navItems = computed(() => navigationByRole[props.role]);

function isActive(path: string) {
  if (path === `/${props.role}`) return route.path === path;
  return route.path === path || route.path.startsWith(`${path}/`);
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-ink">
    <aside
      class="fixed inset-y-0 left-0 z-20 hidden w-72 border-r border-slate-200 bg-white lg:block"
    >
      <div class="flex h-16 items-center border-b border-slate-200 px-5">
        <RouterLink to="/" class="text-base font-semibold tracking-normal">
          Writing System
        </RouterLink>
      </div>
      <nav class="space-y-1 px-3 py-4">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="focus-ring flex min-h-11 items-center gap-3 rounded-md px-3 text-sm font-medium text-graphite"
          :class="isActive(item.to) ? 'bg-mist text-ink' : 'hover:bg-slate-100'"
        >
          <component :is="item.icon" class="h-4 w-4" aria-hidden="true" />
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>
    </aside>

    <div class="lg:pl-72">
      <header
        class="sticky top-0 z-10 flex h-16 items-center gap-3 border-b border-slate-200 bg-white/95 px-4 backdrop-blur lg:px-6"
      >
        <button
          class="focus-ring inline-flex h-10 w-10 items-center justify-center rounded-md border border-slate-200 lg:hidden"
          type="button"
          title="Open navigation"
        >
          <Menu class="h-5 w-5" />
        </button>
        <div class="relative max-w-xl flex-1">
          <Search
            class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
          />
          <input
            class="focus-ring h-10 w-full rounded-md border border-slate-200 bg-slate-50 pl-9 pr-3 text-sm"
            placeholder="Search orders, users, tickets, files"
            type="search"
          />
        </div>
        <div class="flex items-center gap-2">
          <button
            class="focus-ring relative inline-flex h-10 w-10 items-center justify-center rounded-md border border-slate-200 bg-white"
            type="button"
            title="Notifications"
          >
            <Bell class="h-5 w-5" />
            <span
              v-if="notifications.unreadCount"
              class="absolute -right-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-berry px-1 text-xs font-semibold text-white"
            >
              {{ notifications.unreadCount }}
            </span>
          </button>
          <span
            class="hidden rounded-md border px-2 py-1 text-xs font-medium md:inline-flex"
            :class="isConnected ? 'border-emerald-200 text-signal' : 'border-slate-200 text-slate-500'"
          >
            {{ isConnected ? "Live" : "Offline" }}
          </span>
          <button
            class="focus-ring inline-flex h-10 w-10 items-center justify-center rounded-md border border-slate-200 bg-white"
            type="button"
            title="Sign out"
            @click="auth.logout()"
          >
            <LogOut class="h-5 w-5" />
          </button>
        </div>
      </header>

      <main class="mx-auto w-full max-w-7xl px-4 py-6 lg:px-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>
