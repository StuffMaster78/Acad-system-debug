<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from "vue";
import { RouterLink, RouterView, useRoute } from "vue-router";
import { ChevronRight, LogOut, Menu, Settings, X } from "@lucide/vue";
import ActivityShortcut from "@/components/layout/ActivityShortcut.vue";
import GlobalSearch from "@/components/layout/GlobalSearch.vue";
import SidebarChart from "@/components/layout/SidebarChart.vue";
import NotificationBell from "@/components/layout/NotificationBell.vue";
import UserAvatar from "@/components/ui/UserAvatar.vue";
import WalletBalancePill from "@/components/wallet/WalletBalancePill.vue";
import { groupedNavigationByRole } from "@/config/navigation";
import { useAuthStore } from "@/stores/auth";
import { useUiStore } from "@/stores/ui";
import { useNotificationActions } from "@/composables/useNotificationActions";
import { useNotifications } from "@/composables/useNotifications";
import type { UserRole } from "@/types/roles";

const props = defineProps<{ role: UserRole }>();

const route = useRoute();
const auth = useAuthStore();
const ui = useUiStore();
const { isConnected } = useNotifications();
useNotificationActions();
const navGroups = computed(() => groupedNavigationByRole[props.role]);

const userMenuOpen = ref(false);
const userMenuRoot = ref<HTMLElement | null>(null);
const brandMenuOpen = ref(false);
const brandMenuRoot = ref<HTMLElement | null>(null);
const openGroups = ref<Set<string>>(new Set());

const roleLabel: Record<UserRole, string> = {
  client:     "Client portal",
  writer:     "Writer workspace",
  editor:     "Editor workspace",
  support:    "Support desk",
  admin:      "Admin console",
  superadmin: "Superadmin",
};

const theme = computed(() => ({ label: roleLabel[props.role] }));

function initOpenGroups() {
  navGroups.value.forEach((group) => openGroups.value.add(group.label));
}

watch(navGroups, initOpenGroups, { immediate: true });

watch(
  () => route.path,
  () => {
    navGroups.value.forEach((group) => {
      if (group.items.some((item) => isActive(item.to))) openGroups.value.add(group.label);
    });
  },
  { immediate: true },
);

function toggleGroup(label: string) {
  if (openGroups.value.has(label)) openGroups.value.delete(label);
  else openGroups.value.add(label);
}

function isActive(path: string) {
  if (path === `/${props.role}`) return route.path === path;
  return route.path === path || route.path.startsWith(`${path}/`);
}

function handleOutsideClicks(event: MouseEvent) {
  if (userMenuRoot.value && !userMenuRoot.value.contains(event.target as Node))
    userMenuOpen.value = false;
  if (brandMenuRoot.value && !brandMenuRoot.value.contains(event.target as Node))
    brandMenuOpen.value = false;
}

document.addEventListener("mousedown", handleOutsideClicks);
onUnmounted(() => document.removeEventListener("mousedown", handleOutsideClicks));
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-ink">

    <!-- Mobile overlay -->
    <div
      v-if="ui.sidebarOpen"
      class="fixed inset-0 z-20 bg-black/60 lg:hidden"
      role="presentation"
      @click="ui.closeSidebar()"
    />

    <!-- ── Sidebar ──────────────────────────────────────────────────────── -->
    <aside
      class="fixed inset-y-0 left-0 z-30 flex flex-col bg-zinc-950 transition-all duration-200 lg:z-20 lg:translate-x-0"
      :class="[
        ui.sidebarCollapsed ? 'w-14' : 'w-[220px]',
        ui.sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
      ]"
    >
      <!-- Brand bar -->
      <div
        class="flex h-11 shrink-0 items-center border-b border-white/[0.06]"
        :class="ui.sidebarCollapsed ? 'justify-center' : 'justify-between px-3'"
      >
        <div ref="brandMenuRoot" class="relative">
          <button
            class="flex h-7 w-7 items-center justify-center rounded bg-white/[0.08] text-[10px] font-bold text-white transition-colors hover:bg-white/[0.14]"
            type="button"
            :title="ui.sidebarCollapsed ? 'WritingSystem — ' + theme.label : undefined"
            @click="brandMenuOpen = !brandMenuOpen"
          >
            WS
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
              v-if="brandMenuOpen"
              class="absolute left-0 top-9 z-50 w-52 overflow-hidden rounded-lg border border-white/[0.08] bg-zinc-900 shadow-xl"
            >
              <div class="border-b border-white/[0.06] px-3.5 py-3">
                <p class="text-sm font-semibold text-zinc-100">WritingSystem</p>
                <p class="mt-0.5 text-xs text-zinc-500">{{ theme.label }}</p>
              </div>
              <div class="p-1">
                <RouterLink
                  :to="`/${role}/account`"
                  class="flex items-center gap-2 rounded px-3 py-1.5 text-[13px] text-zinc-400 transition-colors hover:bg-white/[0.06] hover:text-zinc-100"
                  @click="brandMenuOpen = false"
                >
                  <Settings class="h-3.5 w-3.5" />
                  Account settings
                </RouterLink>
                <button
                  class="flex w-full items-center gap-2 rounded px-3 py-1.5 text-[13px] text-zinc-400 transition-colors hover:bg-white/[0.06] hover:text-rose-400"
                  type="button"
                  @click="auth.logout(); brandMenuOpen = false"
                >
                  <LogOut class="h-3.5 w-3.5" />
                  Sign out
                </button>
              </div>
            </div>
          </Transition>
        </div>

        <!-- Mobile close (only when expanded) -->
        <button
          v-if="!ui.sidebarCollapsed"
          class="flex h-6 w-6 items-center justify-center rounded text-zinc-600 transition-colors hover:bg-white/[0.06] hover:text-zinc-300 lg:hidden"
          type="button"
          @click="ui.closeSidebar()"
        >
          <X class="h-3.5 w-3.5" />
        </button>
      </div>

      <!-- Scrollable nav -->
      <nav
        class="flex-1 overflow-y-auto py-2"
        :class="ui.sidebarCollapsed ? 'px-1.5' : 'px-2'"
        aria-label="Main navigation"
      >
        <!-- Collapsed: icon rail -->
        <template v-if="ui.sidebarCollapsed">
          <div v-for="group in navGroups" :key="group.label" class="mb-1">
            <RouterLink
              v-for="item in group.items"
              :key="item.to"
              :to="item.to"
              :title="item.label"
              class="mb-px flex h-9 w-full items-center justify-center rounded-md transition-colors"
              :class="isActive(item.to)
                ? 'bg-white/[0.08] text-white'
                : 'text-zinc-600 hover:bg-white/[0.04] hover:text-zinc-300'"
              @click="ui.closeSidebar()"
            >
              <component :is="item.icon" class="h-4 w-4 shrink-0" aria-hidden="true" />
            </RouterLink>
            <div class="mx-auto my-1.5 w-5 border-t border-white/[0.04]" />
          </div>
        </template>

        <!-- Expanded: grouped accordion -->
        <template v-else>
          <div v-for="group in navGroups" :key="group.label" class="mb-3">
            <button
              type="button"
              class="flex w-full items-center px-2.5 py-1"
              @click="toggleGroup(group.label)"
            >
              <span class="text-[10px] font-semibold uppercase tracking-widest text-zinc-600">
                {{ group.label }}
              </span>
              <ChevronRight
                class="ml-auto h-2.5 w-2.5 text-zinc-700 transition-transform duration-150"
                :class="openGroups.has(group.label) ? 'rotate-90' : ''"
              />
            </button>

            <div v-show="openGroups.has(group.label)" class="mt-0.5 space-y-px">
              <RouterLink
                v-for="item in group.items"
                :key="item.to"
                :to="item.to"
                class="focus-ring group flex items-center gap-2.5 rounded-md px-2.5 py-[7px] text-[13px] font-medium transition-colors"
                :class="isActive(item.to)
                  ? 'bg-white/[0.08] text-white'
                  : 'text-zinc-400 hover:bg-white/[0.04] hover:text-zinc-100'"
                @click="ui.closeSidebar()"
              >
                <component
                  :is="item.icon"
                  class="h-[14px] w-[14px] shrink-0 transition-colors"
                  :class="isActive(item.to) ? 'text-white' : 'text-zinc-600 group-hover:text-zinc-400'"
                  aria-hidden="true"
                />
                {{ item.label }}
              </RouterLink>
            </div>
          </div>
        </template>
      </nav>

      <!-- Sidebar chart — admin / superadmin only, expanded only -->
      <SidebarChart
        v-if="(role === 'admin' || role === 'superadmin') && !ui.sidebarCollapsed"
        :role="role"
      />

      <!-- Footer -->
      <div class="shrink-0 space-y-px border-t border-white/[0.06] p-2">

        <!-- Collapse toggle (desktop only) -->
        <button
          class="hidden w-full items-center gap-2 rounded-md px-2.5 py-1.5 text-[12px] font-medium text-zinc-600 transition-colors hover:bg-white/[0.04] hover:text-zinc-300 lg:flex"
          :class="ui.sidebarCollapsed ? 'justify-center' : ''"
          type="button"
          :title="ui.sidebarCollapsed ? 'Expand sidebar' : undefined"
          @click="ui.toggleSidebarCollapse()"
        >
          <ChevronRight
            class="h-3.5 w-3.5 shrink-0 transition-transform duration-200"
            :class="ui.sidebarCollapsed ? '' : 'rotate-180'"
          />
          <span v-if="!ui.sidebarCollapsed">Collapse</span>
        </button>

        <!-- User row -->
        <RouterLink
          :to="`/${role}/account`"
          class="focus-ring flex items-center gap-2.5 rounded-md px-2.5 py-2 transition-colors hover:bg-white/[0.04]"
          :class="ui.sidebarCollapsed ? 'justify-center' : ''"
          :title="ui.sidebarCollapsed ? (auth.user?.full_name || auth.user?.email) : undefined"
          @click="ui.closeSidebar()"
        >
          <UserAvatar :user="auth.user" size="sm" />
          <div v-if="!ui.sidebarCollapsed" class="min-w-0 flex-1">
            <p class="truncate text-[13px] font-medium leading-tight text-zinc-200">
              {{ auth.user?.full_name || auth.user?.email }}
            </p>
            <p class="mt-px text-[10px] capitalize text-zinc-500">{{ role }}</p>
          </div>
          <Settings v-if="!ui.sidebarCollapsed" class="h-[13px] w-[13px] shrink-0 text-zinc-700" aria-hidden="true" />
        </RouterLink>

        <!-- Sign out -->
        <button
          class="focus-ring flex w-full items-center gap-2 rounded-md px-2.5 py-1.5 text-[12px] font-medium text-zinc-600 transition-colors hover:bg-white/[0.04] hover:text-zinc-300"
          :class="ui.sidebarCollapsed ? 'justify-center' : ''"
          :title="ui.sidebarCollapsed ? 'Sign out' : undefined"
          type="button"
          @click="auth.logout()"
        >
          <LogOut class="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
          <span v-if="!ui.sidebarCollapsed">Sign out</span>
        </button>
      </div>
    </aside>

    <!-- ── Main area ───────────────────────────────────────────────────── -->
    <div
      class="transition-[padding] duration-200"
      :class="ui.sidebarCollapsed ? 'lg:pl-14' : 'lg:pl-[220px]'"
    >
      <!-- Header -->
      <header class="sticky top-0 z-10 flex items-center border-b border-slate-200 bg-white/95 px-4 py-3 backdrop-blur-sm lg:px-6">
        <!-- Mobile burger -->
        <button
          class="focus-ring mr-3 inline-flex h-8 w-8 shrink-0 items-center justify-center rounded border border-slate-200 text-graphite hover:bg-slate-50 lg:hidden"
          type="button"
          title="Open navigation"
          @click="ui.toggleSidebar()"
        >
          <Menu class="h-4 w-4" />
        </button>

        <!-- Search — takes all remaining space -->
        <GlobalSearch :role="role" class="min-w-0 flex-1" />

        <!-- Right cluster: utilities -->
        <div class="ml-4 flex items-center gap-3">
          <WalletBalancePill />
          <ActivityShortcut :role="role" />
          <NotificationBell />

          <!-- Live status -->
          <span
            class="hidden items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-medium md:inline-flex"
            :class="isConnected
              ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
              : 'border-slate-200 bg-slate-50 text-slate-500'"
          >
            <span
              class="h-1.5 w-1.5 rounded-full"
              :class="isConnected ? 'bg-emerald-400' : 'bg-slate-300'"
            />
            {{ isConnected ? "Live" : "Offline" }}
          </span>
        </div>

        <!-- Divider -->
        <div class="mx-4 h-5 w-px shrink-0 bg-slate-200" />

        <!-- Avatar — pinned to far right -->
        <div ref="userMenuRoot" class="relative shrink-0">
            <button
              class="focus-ring flex h-8 w-8 items-center justify-center rounded-full ring-2 ring-transparent transition-all hover:ring-slate-200"
              type="button"
              :title="auth.user?.full_name || auth.user?.email"
              @click="userMenuOpen = !userMenuOpen"
            >
              <UserAvatar :user="auth.user" size="sm" />
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
                class="absolute right-0 top-10 z-30 w-52 overflow-hidden rounded-lg border border-slate-200 bg-white shadow-lg"
              >
                <div class="border-b border-slate-100 px-3.5 py-2.5">
                  <p class="truncate text-[13px] font-semibold text-ink">
                    {{ auth.user?.full_name || auth.user?.email }}
                  </p>
                  <p class="mt-px truncate text-[11px] text-graphite">{{ auth.user?.email }}</p>
                </div>
                <RouterLink
                  class="flex items-center gap-2 px-3.5 py-2 text-[13px] font-medium text-graphite transition-colors hover:bg-slate-50 hover:text-ink"
                  :to="`/${role}/account`"
                  @click="userMenuOpen = false"
                >
                  <Settings class="h-3.5 w-3.5" />
                  My account
                </RouterLink>
                <button
                  class="flex w-full items-center gap-2 border-t border-slate-100 px-3.5 py-2 text-[13px] font-medium text-graphite transition-colors hover:bg-rose-50 hover:text-berry"
                  type="button"
                  @click="auth.logout()"
                >
                  <LogOut class="h-3.5 w-3.5" />
                  Sign out
                </button>
              </div>
            </Transition>
          </div>
      </header>

      <!-- Page content -->
      <main class="mx-auto w-full max-w-7xl px-4 py-4 lg:px-5">
        <RouterView />
      </main>
    </div>
  </div>
</template>
