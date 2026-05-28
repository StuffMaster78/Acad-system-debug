<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from "vue";
import { RouterLink, RouterView, useRoute } from "vue-router";
import { ChevronRight, LogOut, Menu, Settings, X } from "@lucide/vue";
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

const props = defineProps<{ role: UserRole }>();

const route = useRoute();
const auth = useAuthStore();
const ui = useUiStore();
const { isConnected } = useNotifications();
const navGroups = computed(() => groupedNavigationByRole[props.role]);
const userMenuOpen = ref(false);
const userMenuRoot = ref<HTMLElement | null>(null);
const openGroups = ref<Set<string>>(new Set());

// Role accent colours — used for active nav indicator and role badge
const roleStyle: Record<UserRole, { accent: string; muted: string; label: string }> = {
  client:     { accent: "#7c3aed", muted: "#f5f3ff", label: "Client portal" },
  writer:     { accent: "#047857", muted: "#ecfdf5", label: "Writer workspace" },
  editor:     { accent: "#0369a1", muted: "#f0f9ff", label: "Editor workspace" },
  support:    { accent: "#b45309", muted: "#fffbeb", label: "Support desk" },
  admin:      { accent: "#334155", muted: "#f1f5f9", label: "Admin console" },
  superadmin: { accent: "#be123c", muted: "#fff1f2", label: "Superadmin" },
};

const theme = computed(() => roleStyle[props.role]);

function syncOpenGroups() {
  navGroups.value.forEach((group) => {
    if (group.items.some((item) => isActive(item.to))) openGroups.value.add(group.label);
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
  if (userMenuRoot.value && !userMenuRoot.value.contains(event.target as Node))
    userMenuOpen.value = false;
}

document.addEventListener("mousedown", onUserMenuOutsideClick);
onUnmounted(() => document.removeEventListener("mousedown", onUserMenuOutsideClick));
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-ink">

    <!-- Mobile overlay -->
    <div
      v-if="ui.sidebarOpen"
      class="fixed inset-0 z-20 bg-ink/40 backdrop-blur-sm lg:hidden"
      role="presentation"
      @click="ui.closeSidebar()"
    />

    <!-- ── Sidebar ──────────────────────────────────────────────────────────── -->
    <aside
      class="fixed inset-y-0 left-0 z-30 flex w-72 flex-col bg-white shadow-[1px_0_0_0_#e2e8f0] transition-transform lg:z-20 lg:translate-x-0"
      :class="ui.sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <!-- Role accent strip -->
      <div class="h-0.5 w-full shrink-0" :style="{ background: theme.accent }" />

      <!-- Brand -->
      <div class="flex h-15 shrink-0 items-center gap-3 border-b border-slate-100 px-4 py-3.5">
        <div
          class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-white text-xs font-bold tracking-tight select-none"
          :style="{ background: theme.accent }"
        >
          WS
        </div>
        <div class="min-w-0 flex-1">
          <p class="text-sm font-bold text-ink tracking-tight leading-none">Writing System</p>
          <p class="mt-0.5 text-[10px] font-medium leading-none" :style="{ color: theme.accent }">
            {{ theme.label }}
          </p>
        </div>
        <button
          class="flex h-7 w-7 items-center justify-center rounded-md text-slate-400 hover:bg-slate-100 hover:text-ink lg:hidden"
          type="button"
          @click="ui.closeSidebar()"
        >
          <X class="h-4 w-4" />
        </button>
      </div>

      <!-- Scrollable nav -->
      <nav class="flex-1 overflow-y-auto px-3 py-3 space-y-0.5" aria-label="Main navigation">
        <div v-for="group in navGroups" :key="group.label" class="mb-1">
          <button
            type="button"
            class="flex w-full items-center justify-between rounded-md px-2.5 py-1.5 text-[10px] font-semibold uppercase tracking-widest text-slate-400 hover:text-slate-600 transition-colors"
            @click="toggleGroup(group.label)"
          >
            <span>{{ group.label }}</span>
            <ChevronRight
              class="h-3 w-3 transition-transform duration-200"
              :class="openGroups.has(group.label) ? 'rotate-90' : ''"
            />
          </button>

          <div v-show="openGroups.has(group.label)" class="mt-0.5 space-y-0.5">
            <RouterLink
              v-for="item in group.items"
              :key="item.to"
              :to="item.to"
              class="focus-ring group flex min-h-9 items-center gap-2.5 rounded-md pl-2 pr-3 text-sm font-medium transition-colors border-l-[3px]"
              :class="isActive(item.to)
                ? 'text-ink'
                : 'border-transparent text-graphite hover:bg-slate-50 hover:text-ink'"
              :style="isActive(item.to)
                ? { borderLeftColor: theme.accent, backgroundColor: theme.muted, color: 'inherit' }
                : {}"
            >
              <component
                :is="item.icon"
                class="h-4 w-4 shrink-0 transition-colors"
                :class="isActive(item.to) ? '' : 'text-slate-400 group-hover:text-graphite'"
                :style="isActive(item.to) ? { color: theme.accent } : {}"
                aria-hidden="true"
              />
              <span>{{ item.label }}</span>
            </RouterLink>
          </div>
        </div>
      </nav>

      <!-- User footer -->
      <div class="shrink-0 border-t border-slate-100 p-3">
        <RouterLink
          :to="`/${role}/account`"
          class="focus-ring flex items-center gap-3 rounded-lg p-2.5 transition-colors hover:bg-slate-50"
          @click="ui.closeSidebar()"
        >
          <UserAvatar :user="auth.user" size="sm" />
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-semibold text-ink leading-tight">
              {{ auth.user?.full_name || auth.user?.email }}
            </p>
            <p class="mt-0.5 text-xs text-graphite capitalize">{{ role }}</p>
          </div>
          <Settings class="h-3.5 w-3.5 shrink-0 text-slate-400" aria-hidden="true" />
        </RouterLink>
        <button
          class="focus-ring mt-1 flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium text-graphite transition-colors hover:bg-rose-50 hover:text-berry"
          type="button"
          @click="auth.logout()"
        >
          <LogOut class="h-4 w-4 shrink-0" aria-hidden="true" />
          <span>Sign out</span>
        </button>
      </div>
    </aside>

    <!-- ── Main area ─────────────────────────────────────────────────────────── -->
    <div class="lg:pl-72">

      <!-- Header -->
      <header class="sticky top-0 z-10 flex h-14 items-center gap-3 border-b border-slate-200 bg-white/95 px-4 backdrop-blur-sm lg:px-6">
        <button
          class="focus-ring inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-200 text-graphite hover:bg-slate-50 lg:hidden"
          type="button"
          title="Open navigation"
          @click="ui.toggleSidebar()"
        >
          <Menu class="h-4 w-4" />
        </button>

        <GlobalSearch :role="role" class="flex-1" />

        <div class="flex items-center gap-1.5">
          <WalletBalancePill />
          <ActivityShortcut :role="role" />
          <NotificationBell />

          <!-- Live status -->
          <span
            class="hidden items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium md:inline-flex"
            :class="isConnected
              ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
              : 'border-slate-200 bg-slate-50 text-slate-500'"
          >
            <span
              class="h-1.5 w-1.5 rounded-full"
              :class="isConnected ? 'bg-emerald-500' : 'bg-slate-400'"
            />
            {{ isConnected ? "Live" : "Offline" }}
          </span>

          <!-- User menu -->
          <div ref="userMenuRoot" class="relative">
            <button
              class="focus-ring inline-flex h-9 items-center gap-2 rounded-lg border border-slate-200 bg-white pl-1.5 pr-3 text-sm font-medium transition-colors hover:bg-slate-50"
              type="button"
              @click="userMenuOpen = !userMenuOpen"
            >
              <UserAvatar :user="auth.user" size="sm" />
              <span class="hidden max-w-32 truncate md:inline text-ink">
                {{ auth.user?.full_name || auth.user?.email }}
              </span>
            </button>

            <Transition
              enter-active-class="transition duration-100 ease-out"
              enter-from-class="opacity-0 scale-95 -translate-y-1"
              enter-to-class="opacity-100 scale-100 translate-y-0"
              leave-active-class="transition duration-75 ease-in"
              leave-from-class="opacity-100 scale-100"
              leave-to-class="opacity-0 scale-95"
            >
              <div
                v-if="userMenuOpen"
                class="absolute right-0 top-11 z-30 w-56 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-lg"
              >
                <div class="px-4 py-3.5 border-b border-slate-100">
                  <p class="truncate text-sm font-semibold text-ink">{{ auth.user?.full_name || auth.user?.email }}</p>
                  <p class="mt-0.5 truncate text-xs text-graphite">{{ auth.user?.email }}</p>
                </div>
                <RouterLink
                  class="flex items-center gap-2.5 px-4 py-2.5 text-sm font-medium text-graphite transition-colors hover:bg-slate-50 hover:text-ink"
                  :to="`/${role}/account`"
                  @click="userMenuOpen = false"
                >
                  <Settings class="h-4 w-4" />
                  My account
                </RouterLink>
                <button
                  class="flex w-full items-center gap-2.5 border-t border-slate-100 px-4 py-2.5 text-sm font-medium text-graphite transition-colors hover:bg-rose-50 hover:text-berry"
                  type="button"
                  @click="auth.logout()"
                >
                  <LogOut class="h-4 w-4" />
                  Sign out
                </button>
              </div>
            </Transition>
          </div>
        </div>
      </header>

      <!-- Page content -->
      <main class="mx-auto w-full max-w-7xl px-4 py-6 lg:px-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>
