<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  Bell,
  Briefcase,
  CheckCircle2,
  ClipboardList,
  Clock,
  CreditCard,
  DollarSign,
  Gauge,
  Home,
  Inbox,
  MessageSquare,
  ShieldAlert,
  TrendingUp,
  Wallet,
  Zap,
} from "@lucide/vue";
import type { Component } from "vue";
import MetricTile from "@/components/ui/MetricTile.vue";
import { dashboards } from "@/config/dashboard";
import { groupedNavigationByRole } from "@/config/navigation";
import { useDashboardData } from "@/composables/useDashboardData";
import { useAuthStore } from "@/stores/auth";
import type { UserRole } from "@/types/roles";

const props = defineProps<{ role: UserRole }>();

const router = useRouter();
const auth = useAuthStore();
const dashboard = dashboards[props.role];
const { isLoading, error, metrics, workItems, primaryActionTo, load } = useDashboardData(props.role);

const isFirstVisit = ref(false);

onMounted(() => {
  const key = `ws-visited-${auth.user?.id ?? "guest"}`;
  if (!localStorage.getItem(key)) {
    isFirstVisit.value = true;
    localStorage.setItem(key, "1");
  }
  load().catch(() => undefined);
});

const firstName = computed(() => {
  const name = auth.user?.full_name;
  if (!name) return "";
  return name.split(" ")[0];
});

const greeting = computed(() => {
  if (isFirstVisit.value) return firstName.value ? `Welcome, ${firstName.value}` : "Welcome";
  const h = new Date().getHours();
  const base = h < 12 ? "Good morning" : h < 17 ? "Good afternoon" : "Good evening";
  return firstName.value ? `${base}, ${firstName.value}` : base;
});

const quickNavItems = computed(() => {
  const groups = groupedNavigationByRole[props.role];
  return groups.flatMap((g) => g.items).slice(1, 9);
});

function workStatusClass(status: string): string {
  const s = status.toLowerCase();
  if (["done", "paid", "completed", "approved", "ready"].some((k) => s.includes(k)))
    return "bg-emerald-100 text-emerald-700";
  if (["escalated", "risk", "overdue", "blocked"].some((k) => s.includes(k)))
    return "bg-rose-100 text-rose-700";
  if (["action", "review", "respond", "now", "reply", "pay"].some((k) => s.includes(k)))
    return "bg-amber-100 text-amber-700";
  return "bg-slate-100 text-slate-600";
}

const ICON_MAP: Record<string, Component> = {
  orders: ClipboardList, wallet: Wallet, messages: MessageSquare,
  earnings: DollarSign, balance: Wallet, status: Activity,
  assignments: Briefcase, completed: CheckCircle2,
  "open orders": ClipboardList, "qa items": Gauge,
  "open tickets": Bell, escalations: AlertTriangle,
  "active sites": Home, "risk flags": ShieldAlert,
  "revenue today": TrendingUp, "queue health": Gauge,
  "qa queue": Gauge, "support load": ShieldAlert,
  "paid today": CreditCard,
  "current window": DollarSign, "pending balance": Clock,
  "orders completed": CheckCircle2,
  "avg review time": Clock, "returned drafts": Inbox,
  "ready delivery": CheckCircle2,
  "avg first reply": Clock, "saved replies": MessageSquare,
};

function metricIcon(label: string): Component | undefined {
  return ICON_MAP[label.toLowerCase()];
}
</script>

<template>
  <div class="space-y-4">

    <!-- Page header -->
    <div class="flex items-start justify-between gap-4">
      <div>
        <h1 class="text-xl font-semibold tracking-tight text-ink">{{ greeting }}</h1>
        <p class="mt-0.5 max-w-xl text-sm text-graphite">
          {{ isFirstVisit ? "Here's your workspace — everything you need is in the sidebar." : dashboard.subtitle }}
        </p>
      </div>
      <button
        class="focus-ring flex shrink-0 items-center gap-2 rounded-md bg-ink px-3.5 py-2 text-sm font-medium text-white transition-colors hover:bg-slate-800"
        type="button"
        @click="router.push(primaryActionTo)"
      >
        <Zap class="h-3.5 w-3.5" />
        {{ dashboard.primaryAction }}
      </button>
    </div>

    <!-- Error banner -->
    <p
      v-if="error"
      class="rounded-lg border border-amber-200 bg-amber-50 px-4 py-2.5 text-sm text-amber-900"
    >
      {{ error }} — showing last known data.
    </p>

    <!-- Metric tiles -->
    <section class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      <template v-if="isLoading">
        <div
          v-for="n in 4"
          :key="n"
          class="h-20 animate-pulse rounded-lg border border-slate-200 bg-white"
          aria-hidden="true"
        />
      </template>
      <template v-else>
        <MetricTile
          v-for="metric in metrics"
          :key="metric.label"
          :metric="metric"
          :icon="metricIcon(metric.label)"
        />
      </template>
    </section>

    <!-- Main grid -->
    <div class="grid gap-4 xl:grid-cols-[minmax(0,1.6fr)_minmax(260px,1fr)]">

      <!-- Priority work -->
      <div class="overflow-hidden rounded-lg border border-slate-200 bg-white">
        <div class="flex items-center justify-between border-b border-slate-100 px-4 py-3">
          <div class="flex items-center gap-2">
            <Clock class="h-3.5 w-3.5 text-slate-400" />
            <h2 class="text-sm font-semibold text-ink">Priority work</h2>
          </div>
          <span v-if="!isLoading" class="text-xs text-graphite">{{ workItems.length }} item{{ workItems.length === 1 ? '' : 's' }}</span>
        </div>

        <div v-if="isLoading" class="animate-pulse divide-y divide-slate-100" aria-hidden="true">
          <div v-for="n in 3" :key="n" class="space-y-2 px-4 py-3">
            <div class="h-3 w-3/4 rounded bg-slate-100" />
            <div class="h-2.5 w-1/2 rounded bg-slate-100" />
          </div>
        </div>

        <div v-else-if="workItems.length" class="divide-y divide-slate-100">
          <article
            v-for="(item, i) in workItems"
            :key="i"
            class="flex items-center justify-between gap-4 px-4 py-3 transition-colors hover:bg-slate-50"
          >
            <div class="flex min-w-0 items-center gap-3">
              <span class="shrink-0 text-xs font-medium tabular-nums text-slate-400">{{ String(i + 1).padStart(2, '0') }}</span>
              <div class="min-w-0">
                <p class="truncate text-sm font-medium text-ink">{{ item.title }}</p>
                <p class="mt-0.5 truncate text-xs text-graphite">{{ item.meta }}</p>
              </div>
            </div>
            <span class="shrink-0 rounded px-1.5 py-0.5 text-xs font-medium" :class="workStatusClass(item.status)">
              {{ item.status }}
            </span>
          </article>
        </div>

        <div v-else class="px-4 py-10 text-center">
          <CheckCircle2 class="mx-auto mb-2 h-7 w-7 text-emerald-400" />
          <p class="text-sm text-graphite">All clear — nothing urgent</p>
        </div>
      </div>

      <!-- Quick access -->
      <div class="overflow-hidden rounded-lg border border-slate-200 bg-white">
        <div class="flex items-center gap-2 border-b border-slate-100 px-4 py-3">
          <Gauge class="h-3.5 w-3.5 text-slate-400" />
          <h2 class="text-sm font-semibold text-ink">Quick access</h2>
        </div>

        <div class="grid grid-cols-2 gap-px bg-slate-100">
          <RouterLink
            v-for="item in quickNavItems"
            :key="item.to"
            :to="item.to"
            class="group flex items-center gap-2 bg-white px-3 py-2.5 text-xs font-medium text-graphite transition-colors hover:bg-slate-50 hover:text-ink"
          >
            <component :is="item.icon" class="h-3.5 w-3.5 shrink-0 text-slate-400 group-hover:text-slate-600" aria-hidden="true" />
            <span class="truncate">{{ item.label }}</span>
          </RouterLink>
        </div>

        <div class="border-t border-slate-100 px-4 py-2.5">
          <button
            class="flex w-full items-center justify-center gap-1.5 rounded py-1.5 text-xs font-medium text-slate-500 transition-colors hover:bg-slate-50 hover:text-ink"
            type="button"
            @click="router.push(primaryActionTo)"
          >
            {{ dashboard.primaryAction }}
            <ArrowRight class="h-3 w-3" />
          </button>
        </div>
      </div>
    </div>

  </div>
</template>
