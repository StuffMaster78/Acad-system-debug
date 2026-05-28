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

const roleLabel: Record<UserRole, string> = {
  client:     "Client portal",
  writer:     "Writer workspace",
  editor:     "Editor workspace",
  support:    "Support desk",
  admin:      "Admin console",
  superadmin: "Superadmin",
};

const theme = computed(() => ({ label: roleLabel[props.role] }));

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
      class="fixed inset-0 z-20 bg-black/60 lg:hidden"
      role="presentation"
      @click="ui.closeSidebar()"
    />

    <!-- ── Sidebar ──────────────────────────────────────────────────────── -->
    <aside
      class="fixed inset-y-0 left-0 z-30 flex w-[220px] flex-col bg-zinc-950 transition-transform duration-200 lg:z-20 lg:translate-x-0"
      :class="ui.sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <!-- Brand -->
      <div class="flex h-11 shrink-0 items-center gap-2.5 border-b border-white/[0.06] px-3.5">
        <div class="flex h-6 w-6 shrink-0 items-center justify-center rounded bg-white/[0.08] text-[10px] font-bold text-white">
          WS
        </div>
        <div class="min-w-0 flex-1">
          <p class="truncate text-[13px] font-semibold leading-none tracking-tight text-zinc-100">WritingSystem</p>
          <p class="mt-0.5 truncate text-[10px] text-zinc-500">{{ theme.label }}</p>
        </div>
        <button
          class="flex h-6 w-6 items-center justify-center rounded text-zinc-600 transition-colors hover:bg-white/[0.06] hover:text-zinc-300 lg:hidden"
          type="button"
          @click="ui.closeSidebar()"
        >
          <X class="h-3.5 w-3.5" />
        </button>
      </div>

      <!-- Scrollable nav -->
      <nav class="flex-1 overflow-y-auto px-2 py-2" aria-label="Main navigation">
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
      </nav>

      <!-- User footer -->
      <div class="shrink-0 space-y-px border-t border-white/[0.06] p-2">
        <RouterLink
          :to="`/${role}/account`"
          class="focus-ring flex items-center gap-2.5 rounded-md px-2.5 py-2 transition-colors hover:bg-white/[0.04]"
          @click="ui.closeSidebar()"
        >
          <UserAvatar :user="auth.user" size="sm" />
          <div class="min-w-0 flex-1">
            <p class="truncate text-[13px] font-medium leading-tight text-zinc-200">
              {{ auth.user?.full_name || auth.user?.email }}
            </p>
            <p class="mt-px text-[10px] capitalize text-zinc-500">{{ role }}</p>
          </div>
          <Settings class="h-[13px] w-[13px] shrink-0 text-zinc-700" aria-hidden="true" />
        </RouterLink>
        <button
          class="focus-ring flex w-full items-center gap-2 rounded-md px-2.5 py-1.5 text-[12px] font-medium text-zinc-600 transition-colors hover:bg-white/[0.04] hover:text-zinc-300"
          type="button"
          @click="auth.logout()"
        >
          <LogOut class="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
          Sign out
        </button>
      </div>
    </aside>

    <!-- ── Main area ───────────────────────────────────────────────────── -->
    <div class="lg:pl-[220px]">

      <!-- Header -->
      <header class="sticky top-0 z-10 flex h-12 items-center gap-3 border-b border-slate-200 bg-white/95 px-4 backdrop-blur-sm lg:px-5">
        <button
          class="focus-ring inline-flex h-8 w-8 items-center justify-center rounded border border-slate-200 text-graphite hover:bg-slate-50 lg:hidden"
          type="button"
          title="Open navigation"
          @click="ui.toggleSidebar()"
        >
          <Menu class="h-3.5 w-3.5" />
        </button>

        <GlobalSearch :role="role" class="flex-1" />

        <div class="flex items-center gap-1.5">
          <WalletBalancePill />
          <ActivityShortcut :role="role" />
          <NotificationBell />

          <!-- Live status -->
          <span
            class="hidden items-center gap-1 rounded-full border px-2 py-0.5 text-[11px] font-medium md:inline-flex"
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
              class="focus-ring inline-flex h-8 items-center gap-2 rounded border border-slate-200 bg-white pl-1.5 pr-2.5 text-[13px] font-medium transition-colors hover:bg-slate-50"
              type="button"
              @click="userMenuOpen = !userMenuOpen"
            >
              <UserAvatar :user="auth.user" size="sm" />
              <span class="hidden max-w-28 truncate md:inline text-ink">
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
        </div>
      </header>

      <!-- Page content -->
      <main class="mx-auto w-full max-w-7xl px-4 py-4 lg:px-5">
        <RouterView />
      </main>
    </div>
  </div>
</template>
