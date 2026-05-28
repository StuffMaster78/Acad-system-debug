<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from "vue";
import { RouterLink, RouterView, useRoute } from "vue-router";
import { ChevronRight, LogOut, Menu, Settings, UserCircle } from "@lucide/vue";
import ActivityShortcut from "@/components/layout/ActivityShortcut.vue";
import GlobalSearch from "@/components/layout/GlobalSearch.vue";
import NotificationBell from "@/components/layout/NotificationBell.vue";
import UserAvatar from "@/components/ui/UserAvatar.vue";
import WalletBalancePill from "@/components/wallet/WalletBalancePill.vue";
import { groupedNavigationByRole } from "@/config/navigation";
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
const navGroups = computed(() => groupedNavigationByRole[props.role]);
const userMenuOpen = ref(false);
const userMenuRoot = ref<HTMLElement | null>(null);

// Track which groups are open — auto-open the group containing the active route
const openGroups = ref<Set<string>>(new Set());

function syncOpenGroups() {
  navGroups.value.forEach((group) => {
    const hasActive = group.items.some((item) => isActive(item.to));
    if (hasActive) openGroups.value.add(group.label);
  });
}

watch(() => route.path, syncOpenGroups, { immediate: true });

function toggleGroup(label: string) {
  if (openGroups.value.has(label)) openGroups.value.delete(label);
  else openGroups.value.add(label);
}

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
      class="fixed inset-y-0 left-0 z-30 flex w-72 flex-col border-r border-slate-200 bg-white transition-transform lg:z-20 lg:translate-x-0"
      :class="ui.sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <!-- Brand -->
      <div class="flex h-16 shrink-0 items-center border-b border-slate-200 px-5">
        <RouterLink to="/" class="text-base font-semibold tracking-normal">
          Writing System
        </RouterLink>
      </div>

      <!-- Scrollable nav -->
      <nav class="flex-1 overflow-y-auto px-3 py-4 space-y-0.5">
        <div v-for="group in navGroups" :key="group.label">
          <!-- Group header -->
          <button
            type="button"
            class="flex w-full items-center justify-between rounded-md px-2.5 py-1.5 text-xs font-semibold uppercase tracking-wider text-slate-400 hover:text-slate-600 transition-colors"
            @click="toggleGroup(group.label)"
          >
            <span>{{ group.label }}</span>
            <ChevronRight
              class="h-3.5 w-3.5 transition-transform duration-200"
              :class="openGroups.has(group.label) ? 'rotate-90' : ''"
            />
          </button>

          <!-- Group items -->
          <div v-show="openGroups.has(group.label)" class="mt-0.5 space-y-0.5 mb-2">
            <RouterLink
              v-for="item in group.items"
              :key="item.to"
              :to="item.to"
              class="focus-ring flex min-h-9 items-center gap-3 rounded-md px-3 text-sm font-medium text-graphite"
              :class="isActive(item.to) ? 'bg-mist text-ink' : 'hover:bg-slate-100'"
            >
              <component :is="item.icon" class="h-4 w-4 shrink-0" aria-hidden="true" />
              <span>{{ item.label }}</span>
            </RouterLink>
          </div>
        </div>
      </nav>

      <!-- Pinned bottom strip -->
      <div class="shrink-0 border-t border-slate-200 px-3 py-3 space-y-1">
        <RouterLink
          :to="`/${role}/account`"
          class="focus-ring flex min-h-10 items-center gap-3 rounded-md px-3 text-sm font-medium text-graphite hover:bg-slate-100"
          :class="isActive(`/${role}/account`) ? 'bg-mist text-ink' : ''"
        >
          <UserCircle class="h-4 w-4 shrink-0 text-graphite" aria-hidden="true" />
          <span>My account</span>
        </RouterLink>
        <button
          class="focus-ring flex w-full min-h-10 items-center gap-3 rounded-md px-3 text-sm font-medium text-graphite hover:bg-rose-50 hover:text-berry"
          type="button"
          @click="auth.logout()"
        >
          <LogOut class="h-4 w-4 shrink-0" aria-hidden="true" />
          <span>Sign out</span>
        </button>
      </div>
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
