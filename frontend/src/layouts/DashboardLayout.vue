<script setup lang="ts">
import { computed, onUnmounted, ref } from "vue";
import { RouterLink, RouterView, useRoute } from "vue-router";
import { LogOut, Menu, Settings } from "@lucide/vue";
import ActivityShortcut from "@/components/layout/ActivityShortcut.vue";
import GlobalSearch from "@/components/layout/GlobalSearch.vue";
import NotificationBell from "@/components/layout/NotificationBell.vue";
import UserAvatar from "@/components/ui/UserAvatar.vue";
import WalletBalancePill from "@/components/wallet/WalletBalancePill.vue";
import { navigationByRole } from "@/config/navigation";
import { useAuthStore } from "@/stores/auth";
import { useUiStore } from "@/stores/ui";
import { useNotifications } from "@/composables/useNotifications";
import type { UserRole } from "@/types/roles";

const props = defineProps<{
  role: UserRole;
}>();

const route = useRoute();
const auth = useAuthStore();
const ui = useUiStore();
const { isConnected } = useNotifications();
const navItems = computed(() => navigationByRole[props.role]);
const userMenuOpen = ref(false);
const userMenuRoot = ref<HTMLElement | null>(null);

function isActive(path: string) {
  if (path === `/${props.role}`) return route.path === path;
  return route.path === path || route.path.startsWith(`${path}/`);
}

function onUserMenuOutsideClick(event: MouseEvent) {
  if (userMenuRoot.value && !userMenuRoot.value.contains(event.target as Node)) {
    userMenuOpen.value = false;
  }
}

document.addEventListener("mousedown", onUserMenuOutsideClick);
onUnmounted(() => document.removeEventListener("mousedown", onUserMenuOutsideClick));
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-ink">
    <div
      v-if="ui.sidebarOpen"
      class="fixed inset-0 z-20 bg-ink/30 lg:hidden"
      role="presentation"
      @click="ui.closeSidebar()"
    />
    <aside
      class="fixed inset-y-0 left-0 z-30 w-72 border-r border-slate-200 bg-white transition-transform lg:z-20 lg:translate-x-0"
      :class="ui.sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
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
          @click="ui.toggleSidebar()"
        >
          <Menu class="h-5 w-5" />
        </button>
        <GlobalSearch :role="role" />
        <div class="flex items-center gap-2">
          <WalletBalancePill />
          <ActivityShortcut :role="role" />
          <NotificationBell />
          <span
            class="hidden rounded-md border px-2 py-1 text-xs font-medium md:inline-flex"
            :class="isConnected ? 'border-emerald-200 text-signal' : 'border-slate-200 text-slate-500'"
          >
            {{ isConnected ? "Live" : "Offline" }}
          </span>

          <div ref="userMenuRoot" class="relative">
            <button
              class="focus-ring inline-flex h-10 items-center gap-2 rounded-md border border-slate-200 bg-white px-2 pr-3 text-sm font-medium"
              type="button"
              @click="userMenuOpen = !userMenuOpen"
            >
              <UserAvatar :user="auth.user" size="sm" />
              <span class="hidden max-w-32 truncate md:inline">{{ auth.user?.full_name || auth.user?.email }}</span>
            </button>

            <div
              v-if="userMenuOpen"
              class="absolute right-0 top-12 z-30 w-52 overflow-hidden rounded-md border border-slate-200 bg-white shadow-panel"
            >
              <div class="border-b border-slate-100 px-4 py-3">
                <p class="truncate text-sm font-semibold text-ink">{{ auth.user?.full_name || auth.user?.email }}</p>
                <p class="mt-0.5 truncate text-xs text-graphite">{{ auth.user?.email }}</p>
              </div>
              <RouterLink
                class="flex items-center gap-2.5 px-4 py-2.5 text-sm font-medium text-ink hover:bg-slate-50"
                :to="`/${role}/account`"
                @click="userMenuOpen = false"
              >
                <Settings class="h-4 w-4 text-graphite" />
                My account
              </RouterLink>
              <button
                class="flex w-full items-center gap-2.5 border-t border-slate-100 px-4 py-2.5 text-sm font-medium text-berry hover:bg-rose-50"
                type="button"
                @click="auth.logout()"
              >
                <LogOut class="h-4 w-4" />
                Sign out
              </button>
            </div>
          </div>
        </div>
      </header>

      <main class="mx-auto w-full max-w-7xl px-4 py-6 lg:px-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>
