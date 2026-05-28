<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  BarChart3,
  Bell,
  BookOpen,
  Briefcase,
  CalendarDays,
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
  Sparkles,
  TrendingUp,
  Wallet,
  Zap,
} from "@lucide/vue";
import type { Component } from "vue";
import MetricTile from "@/components/ui/MetricTile.vue";
import { dashboards } from "@/config/dashboard";
import { groupedNavigationByRole } from "@/config/navigation";
import { useDashboardData } from "@/composables/useDashboardData";
import type { UserRole } from "@/types/roles";

const props = defineProps<{ role: UserRole }>();

const router = useRouter();
const dashboard = dashboards[props.role];
const { isLoading, error, metrics, workItems, primaryActionTo, load } = useDashboardData(props.role);

onMounted(() => {
  load().catch(() => undefined);
});

// Greeting based on time of day
const greeting = computed(() => {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 17) return "Good afternoon";
  return "Good evening";
});

// Flatten nav groups into quick-nav items (first 8, skipping home)
const quickNavItems = computed(() => {
  const groups = groupedNavigationByRole[props.role];
  return groups.flatMap((g) => g.items).slice(1, 9);
});

// Role theme colours
const roleTheme: Record<UserRole, { gradient: string; badge: string; icon: string }> = {
  client:     { gradient: "from-violet-600 to-indigo-600", badge: "bg-violet-100 text-violet-700", icon: "👤" },
  writer:     { gradient: "from-emerald-600 to-teal-600",  badge: "bg-emerald-100 text-emerald-700", icon: "✍️" },
  editor:     { gradient: "from-sky-600 to-blue-600",      badge: "bg-sky-100 text-sky-700", icon: "🖊️" },
  support:    { gradient: "from-amber-500 to-orange-500",  badge: "bg-amber-100 text-amber-700", icon: "🎧" },
  admin:      { gradient: "from-slate-700 to-slate-900",   badge: "bg-slate-100 text-slate-700", icon: "⚙️" },
  superadmin: { gradient: "from-rose-600 to-pink-600",     badge: "bg-rose-100 text-rose-700", icon: "🛡️" },
};

const theme = computed(() => roleTheme[props.role]);

// Status badge colours for work items
function workStatusClass(status: string): string {
  const s = status.toLowerCase();
  if (["done", "paid", "completed", "approved", "ready"].some((k) => s.includes(k)))
    return "bg-emerald-100 text-emerald-700";
  if (["escalated", "risk", "overdue", "blocked"].some((k) => s.includes(k)))
    return "bg-rose-100 text-rose-700";
  if (["action", "review", "respond", "now", "reply", "pay"].some((k) => s.includes(k)))
    return "bg-amber-100 text-amber-700";
  return "bg-blue-100 text-blue-700";
}

// Icon lookup for metrics
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
  <div class="space-y-6">

    <!-- ── Hero banner ─────────────────────────────────────────────────────── -->
    <div
      class="relative overflow-hidden rounded-2xl bg-gradient-to-r p-6 text-white shadow-lg"
      :class="theme.gradient"
    >
      <!-- Subtle radial highlight -->
      <div class="pointer-events-none absolute -right-12 -top-12 h-48 w-48 rounded-full bg-white/10" />
      <div class="pointer-events-none absolute -bottom-8 right-24 h-32 w-32 rounded-full bg-white/5" />

      <div class="relative flex flex-wrap items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="text-sm font-medium text-white/70">{{ greeting }}</span>
            <span class="rounded-full px-2.5 py-0.5 text-xs font-semibold" :class="theme.badge">
              {{ role }}
            </span>
          </div>
          <h1 class="text-2xl font-bold leading-tight">{{ dashboard.title }}</h1>
          <p class="mt-1.5 max-w-xl text-sm leading-relaxed text-white/80">{{ dashboard.subtitle }}</p>
        </div>

        <button
          class="flex items-center gap-2 rounded-xl bg-white/15 px-5 py-2.5 text-sm font-semibold backdrop-blur transition hover:bg-white/25 active:scale-95"
          type="button"
          @click="router.push(primaryActionTo)"
        >
          <Zap class="h-4 w-4" />
          {{ dashboard.primaryAction }}
        </button>
      </div>
    </div>

    <!-- Error banner -->
    <p
      v-if="error"
      class="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
    >
      {{ error }} — showing last known data.
    </p>

    <!-- ── Metric tiles ──────────────────────────────────────────────────── -->
    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <template v-if="isLoading">
        <div
          v-for="n in 4"
          :key="n"
          class="h-24 animate-pulse rounded-xl border border-slate-200 bg-white"
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

    <!-- ── Main grid ────────────────────────────────────────────────────────── -->
    <div class="grid gap-5 xl:grid-cols-[minmax(0,1.6fr)_minmax(280px,1fr)]">

      <!-- Priority work -->
      <div class="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div class="flex items-center justify-between border-b border-slate-100 px-5 py-3.5">
          <div class="flex items-center gap-2">
            <Clock class="h-4 w-4 text-slate-400" />
            <h2 class="text-sm font-semibold text-ink">Priority work</h2>
          </div>
          <span v-if="!isLoading" class="text-xs text-graphite">{{ workItems.length }} item{{ workItems.length === 1 ? '' : 's' }}</span>
        </div>

        <!-- Loading skeleton -->
        <div v-if="isLoading" class="divide-y divide-slate-100 animate-pulse" aria-hidden="true">
          <div v-for="n in 3" :key="n" class="px-5 py-4 space-y-2">
            <div class="h-3.5 w-3/4 rounded bg-slate-100" />
            <div class="h-3 w-1/2 rounded bg-slate-100" />
          </div>
        </div>

        <!-- Work items -->
        <div v-else-if="workItems.length" class="divide-y divide-slate-100">
          <article
            v-for="(item, i) in workItems"
            :key="i"
            class="flex items-center justify-between gap-4 px-5 py-4 hover:bg-slate-50 transition-colors"
          >
            <div class="flex items-center gap-3 min-w-0">
              <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-xs font-bold text-graphite">
                {{ i + 1 }}
              </div>
              <div class="min-w-0">
                <p class="text-sm font-semibold text-ink truncate">{{ item.title }}</p>
                <p class="text-xs text-graphite mt-0.5 truncate">{{ item.meta }}</p>
              </div>
            </div>
            <span
              class="shrink-0 rounded-full px-2.5 py-0.5 text-xs font-semibold"
              :class="workStatusClass(item.status)"
            >
              {{ item.status }}
            </span>
          </article>
        </div>

        <div v-else class="px-5 py-10 text-center">
          <CheckCircle2 class="mx-auto mb-2 h-8 w-8 text-emerald-400" />
          <p class="text-sm font-medium text-graphite">All clear — nothing urgent right now</p>
        </div>
      </div>

      <!-- Quick navigation grid -->
      <div class="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div class="flex items-center gap-2 border-b border-slate-100 px-5 py-3.5">
          <Gauge class="h-4 w-4 text-slate-400" />
          <h2 class="text-sm font-semibold text-ink">Quick access</h2>
        </div>

        <div class="grid grid-cols-2 gap-1 p-3">
          <RouterLink
            v-for="item in quickNavItems"
            :key="item.to"
            :to="item.to"
            class="group flex items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm font-medium text-graphite hover:bg-slate-50 hover:text-ink transition-colors"
          >
            <div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-slate-100 group-hover:bg-slate-200 transition-colors">
              <component :is="item.icon" class="h-3.5 w-3.5" aria-hidden="true" />
            </div>
            <span class="truncate text-xs">{{ item.label }}</span>
          </RouterLink>
        </div>

        <div class="border-t border-slate-100 px-4 py-3">
          <button
            class="flex w-full items-center justify-center gap-1.5 rounded-lg py-2 text-xs font-semibold text-indigo-600 hover:bg-indigo-50 transition-colors"
            type="button"
            @click="router.push(primaryActionTo)"
          >
            {{ dashboard.primaryAction }}
            <ArrowRight class="h-3.5 w-3.5" />
          </button>
        </div>
      </div>
    </div>

  </div>
</template>
