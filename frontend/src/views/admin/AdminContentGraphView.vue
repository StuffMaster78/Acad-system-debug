<template>
  <div class="space-y-6 p-6">

    <!-- Header -->
    <div class="flex items-start justify-between gap-4">
      <div>
        <h1 class="text-xl font-bold text-ink">Content Graph Intelligence</h1>
        <p class="mt-0.5 text-sm text-graphite">
          Funnel attribution, content health, and linking intelligence across all topic pillars.
        </p>
      </div>
      <button
        class="focus-ring inline-flex items-center gap-2 rounded-md border border-slate-200 px-3 py-2 text-xs font-semibold text-graphite hover:bg-slate-50"
        :disabled="isLoading"
        @click="refresh"
      >
        <RefreshCw class="size-3.5" :class="isLoading ? 'animate-spin' : ''" />
        Refresh
      </button>
    </div>

    <!-- Dashboard summary cards -->
    <div v-if="dashboard" class="grid grid-cols-2 gap-4 lg:grid-cols-4">
      <div class="rounded-xl border border-slate-200 bg-white p-5">
        <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Total pillars</p>
        <p class="mt-2 text-3xl font-extrabold text-ink">{{ dashboard.funnels.total_pillars }}</p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-white p-5">
        <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Revenue (30d)</p>
        <p class="mt-2 text-3xl font-extrabold text-ink">${{ fmt(dashboard.funnels.total_revenue_30d) }}</p>
        <p class="mt-0.5 text-xs text-graphite">{{ dashboard.funnels.total_conversions_30d }} conversions</p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-white p-5">
        <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Blog traffic (30d)</p>
        <p class="mt-2 text-3xl font-extrabold text-ink">{{ dashboard.funnels.total_blog_traffic_30d.toLocaleString() }}</p>
        <p class="mt-0.5 text-xs text-graphite">Avg {{ dashboard.funnels.avg_funnel_conversion_rate.toFixed(1) }}% conv. rate</p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-white p-5">
        <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Freshness alerts</p>
        <p class="mt-2 text-3xl font-extrabold" :class="dashboard.freshness.critical > 0 ? 'text-rose-600' : 'text-ink'">
          {{ dashboard.freshness.total_unresolved }}
        </p>
        <p v-if="dashboard.freshness.critical > 0" class="mt-0.5 text-xs text-rose-600">
          {{ dashboard.freshness.critical }} critical
        </p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-slate-200">
      <nav class="flex gap-1">
        <button
          v-for="t in TABS"
          :key="t.key"
          class="rounded-t-lg border-b-2 px-4 py-2.5 text-sm font-medium transition-colors"
          :class="tab === t.key ? 'border-berry text-berry' : 'border-transparent text-graphite hover:text-ink'"
          @click="tab = t.key"
        >
          {{ t.label }}
          <span v-if="t.key === 'freshness' && dashboard?.freshness.total_unresolved" class="ml-1.5 rounded-full bg-rose-500 px-1.5 py-0.5 text-xs font-bold text-white">
            {{ dashboard.freshness.total_unresolved }}
          </span>
        </button>
      </nav>
    </div>

    <!-- ── Tab: Pillars overview ──────────────────────────────────────────── -->
    <template v-if="tab === 'pillars'">
      <div v-if="isLoadingPillars" class="grid gap-4 sm:grid-cols-2 animate-pulse">
        <div v-for="n in 4" :key="n" class="rounded-xl border border-slate-200 bg-white p-5 space-y-3">
          <div class="h-4 w-2/3 rounded bg-slate-200" />
          <div class="h-3 w-full rounded bg-slate-100" />
        </div>
      </div>
      <div v-else-if="!pillars.length" class="py-16 text-center text-sm text-graphite">
        No content pillars yet. Create a pillar in Wagtail admin to start tracking funnels.
      </div>
      <div v-else class="grid gap-4 sm:grid-cols-2">
        <div
          v-for="pillar in pillars"
          :key="pillar.id"
          class="group cursor-pointer rounded-xl border border-slate-200 bg-white p-5 transition-all hover:border-berry/40 hover:shadow-md"
          @click="openPillar(pillar.slug)"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <p class="font-bold text-ink group-hover:text-berry transition-colors truncate">{{ pillar.name }}</p>
              <p v-if="pillar.service_page" class="mt-0.5 text-xs text-graphite">
                → {{ (pillar.service_page as any).title }}
              </p>
            </div>
            <div class="shrink-0 text-right">
              <p class="text-lg font-extrabold text-ink">${{ pillar.attributed_revenue_30d ?? 0 }}</p>
              <p class="text-xs text-graphite">30d revenue</p>
            </div>
          </div>
          <div class="mt-4 grid grid-cols-3 gap-3 border-t border-slate-100 pt-3 text-center text-xs">
            <div>
              <p class="font-bold text-ink">{{ pillar.spoke_count ?? 0 }}</p>
              <p class="text-graphite">spokes</p>
            </div>
            <div>
              <p class="font-bold text-ink">{{ pillar.total_clicks_30d ?? 0 }}</p>
              <p class="text-graphite">clicks</p>
            </div>
            <div>
              <p class="font-bold text-ink">{{ pillar.total_conversions_30d ?? 0 }}</p>
              <p class="text-graphite">orders</p>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- ── Tab: Funnel analytics ──────────────────────────────────────────── -->
    <template v-else-if="tab === 'funnel'">
      <!-- Pillar selector -->
      <div class="flex flex-wrap gap-2">
        <button
          v-for="p in pillars"
          :key="p.id"
          class="rounded-full border px-3 py-1 text-xs font-medium transition-colors"
          :class="selectedPillarSlug === p.slug
            ? 'border-berry bg-berry text-white'
            : 'border-slate-200 bg-white text-graphite hover:border-slate-300'"
          @click="loadFunnel(p.slug)"
        >{{ p.name }}</button>
      </div>

      <div v-if="isLoadingFunnel" class="py-16 text-center animate-pulse">
        <div class="mx-auto h-4 w-40 rounded bg-slate-200" />
      </div>

      <div v-else-if="!funnel" class="py-16 text-center text-sm text-graphite">
        Select a pillar above to view its funnel report.
      </div>

      <div v-else class="space-y-4">
        <h2 class="text-lg font-bold text-ink">{{ funnel.pillar.name }}</h2>

        <!-- Funnel stages as horizontal flow -->
        <div class="grid gap-4 lg:grid-cols-3">
          <!-- Top of funnel -->
          <div class="rounded-xl border border-blue-200 bg-blue-50 p-5">
            <p class="mb-3 text-xs font-semibold uppercase tracking-wide text-blue-600">Top of funnel — Awareness</p>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between"><span class="text-graphite">Spoke posts</span><span class="font-bold text-ink">{{ funnel.top_of_funnel.spoke_count }}</span></div>
              <div class="flex justify-between"><span class="text-graphite">Blog traffic (30d)</span><span class="font-bold text-ink">{{ funnel.top_of_funnel.total_traffic_30d.toLocaleString() }}</span></div>
              <div v-if="funnel.hub_post" class="flex justify-between"><span class="text-graphite">Hub traffic</span><span class="font-bold text-ink">{{ funnel.top_of_funnel.hub_traffic_30d.toLocaleString() }}</span></div>
            </div>
          </div>

          <!-- Middle -->
          <div class="rounded-xl border border-amber-200 bg-amber-50 p-5">
            <p class="mb-3 text-xs font-semibold uppercase tracking-wide text-amber-600">Middle — Consideration</p>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between"><span class="text-graphite">Blog→Service clicks</span><span class="font-bold text-ink">{{ funnel.middle.total_blog_to_service_clicks }}</span></div>
              <div class="flex justify-between"><span class="text-graphite">Link CTR</span><span class="font-bold text-ink">{{ funnel.middle.click_through_rate }}%</span></div>
              <div class="flex justify-between"><span class="text-graphite">Active routes</span><span class="font-bold text-ink">{{ funnel.middle.routes_count }}</span></div>
            </div>
            <div v-if="funnel.middle.best_route" class="mt-3 rounded-lg bg-white/60 p-3 text-xs">
              <p class="font-semibold text-emerald-700">Best route</p>
              <p class="mt-0.5 text-graphite">{{ funnel.middle.best_route.blog_title }}</p>
              <p class="text-graphite">{{ funnel.middle.best_route.clicks }} clicks · {{ funnel.middle.best_route.ctr }}% CTR</p>
            </div>
          </div>

          <!-- Bottom -->
          <div class="rounded-xl border border-emerald-200 bg-emerald-50 p-5">
            <p class="mb-3 text-xs font-semibold uppercase tracking-wide text-emerald-600">Bottom — Conversion</p>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between"><span class="text-graphite">Service sessions</span><span class="font-bold text-ink">{{ funnel.bottom.service_page_sessions.toLocaleString() }}</span></div>
              <div class="flex justify-between"><span class="text-graphite">Orders</span><span class="font-bold text-ink">{{ funnel.bottom.orders }}</span></div>
              <div class="flex justify-between"><span class="text-graphite">Conv. rate</span><span class="font-bold text-ink">{{ funnel.bottom.conversion_rate }}%</span></div>
              <div class="flex justify-between"><span class="text-graphite">Revenue (30d)</span><span class="font-extrabold text-emerald-700">${{ funnel.bottom.revenue }}</span></div>
            </div>
            <div class="mt-3 rounded-lg bg-white/60 p-3 text-xs">
              <span class="text-graphite">Revenue/visitor: </span>
              <span class="font-bold text-ink">${{ funnel.efficiency.revenue_per_blog_visitor.toFixed(4) }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- ── Tab: Freshness alerts ──────────────────────────────────────────── -->
    <template v-else-if="tab === 'freshness'">
      <div class="flex gap-2 mb-4">
        <button
          v-for="f in [['unresolved', 'Unresolved'], ['resolved', 'Resolved']]"
          :key="f[0]"
          class="rounded-full border px-3 py-1 text-xs font-medium transition-colors"
          :class="freshnessFilter === f[0]
            ? 'border-berry bg-berry text-white'
            : 'border-slate-200 bg-white text-graphite hover:border-slate-300'"
          @click="loadFreshnessAlerts(f[0] as 'unresolved' | 'resolved')"
        >{{ f[1] }}</button>
      </div>

      <div v-if="isLoadingAlerts" class="space-y-3 animate-pulse">
        <div v-for="n in 4" :key="n" class="h-16 rounded-xl bg-slate-100" />
      </div>
      <div v-else-if="!alerts.length" class="py-16 text-center">
        <CheckCircle class="mx-auto mb-3 size-10 text-signal" />
        <p class="text-sm font-semibold text-ink">All clear — no {{ freshnessFilter }} alerts.</p>
      </div>
      <div v-else class="space-y-3">
        <div
          v-for="alert in alerts"
          :key="alert.id"
          class="rounded-xl border bg-white p-4"
          :class="alert.severity >= 4 ? 'border-rose-200' : alert.severity >= 3 ? 'border-amber-200' : 'border-slate-200'"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <span
                  class="rounded-full px-2 py-0.5 text-xs font-bold"
                  :class="alert.severity >= 4 ? 'bg-rose-100 text-rose-700' : alert.severity >= 3 ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-graphite'"
                >
                  {{ severityLabel(alert.severity) }}
                </span>
                <span class="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-graphite capitalize">
                  {{ alert.alert_type.replace(/_/g, " ") }}
                </span>
              </div>
              <p v-if="alert.page_title" class="mt-1.5 font-semibold text-ink">{{ alert.page_title }}</p>
              <p class="mt-0.5 text-sm text-graphite">{{ alert.detail }}</p>
              <p class="mt-1 text-xs text-slate-400">Raised {{ fmtDate(alert.raised_at) }}</p>
            </div>
            <div v-if="!alert.resolved_at" class="flex shrink-0 gap-2">
              <button
                v-if="!alert.acknowledged_at"
                class="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-graphite hover:bg-slate-50"
                @click="acknowledgeAlert(alert.id)"
              >Acknowledge</button>
              <button
                class="rounded-lg bg-signal px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-700"
                @click="resolveAlert(alert.id)"
              >Resolve</button>
            </div>
            <span v-else class="shrink-0 text-xs text-signal">Resolved</span>
          </div>
        </div>
      </div>
    </template>

    <!-- ── Tab: Content health ────────────────────────────────────────────── -->
    <template v-else-if="tab === 'health'">
      <div class="flex flex-wrap gap-2 mb-4">
        <button
          v-for="m in HEALTH_METRICS"
          :key="m.value"
          class="rounded-full border px-3 py-1.5 text-xs font-medium transition-colors"
          :class="healthMetric === m.value
            ? 'border-berry bg-berry text-white'
            : 'border-slate-200 bg-white text-graphite hover:border-slate-300'"
          @click="loadTopPerformers(m.value)"
        >{{ m.label }}</button>
      </div>

      <div class="grid gap-4 lg:grid-cols-2">
        <!-- Top performers -->
        <div class="rounded-xl border border-slate-200 bg-white overflow-hidden">
          <div class="border-b border-slate-200 bg-slate-50 px-4 py-3">
            <p class="text-xs font-semibold text-graphite uppercase tracking-wide">Top performers</p>
          </div>
          <div v-if="isLoadingHealth" class="p-4 animate-pulse space-y-3">
            <div v-for="n in 5" :key="n" class="h-10 rounded bg-slate-100" />
          </div>
          <div v-else class="divide-y divide-slate-100">
            <div v-for="snap in topPerformers" :key="snap.id" class="flex items-center gap-3 px-4 py-3">
              <div class="min-w-0 flex-1">
                <p class="truncate text-sm font-medium text-ink">{{ snap.page_title }}</p>
                <p class="text-xs text-graphite">{{ snap.page_url }}</p>
              </div>
              <div class="shrink-0 text-right">
                <p class="text-sm font-bold text-ink">
                  <template v-if="healthMetric === 'clicks'">{{ snap.gsc_clicks_30d.toLocaleString() }} clicks</template>
                  <template v-else-if="healthMetric === 'views'">{{ snap.ga4_page_views_30d.toLocaleString() }} views</template>
                  <template v-else-if="healthMetric === 'conversions'">{{ snap.internal_conversions_30d }} orders</template>
                  <template v-else>${{ snap.attributed_revenue_30d }}</template>
                </p>
              </div>
            </div>
            <div v-if="!topPerformers.length" class="px-4 py-8 text-center text-sm text-graphite">
              No performance data yet. Run the nightly snapshot task first.
            </div>
          </div>
        </div>

        <!-- Needs attention -->
        <div class="rounded-xl border border-slate-200 bg-white overflow-hidden">
          <div class="border-b border-slate-200 bg-slate-50 px-4 py-3">
            <p class="text-xs font-semibold text-graphite uppercase tracking-wide">Needs attention</p>
          </div>
          <div v-if="isLoadingHealth" class="p-4 animate-pulse space-y-3">
            <div v-for="n in 5" :key="n" class="h-14 rounded bg-slate-100" />
          </div>
          <div v-else class="divide-y divide-slate-100">
            <div v-for="snap in worstPerformers" :key="snap.id" class="px-4 py-3">
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <p class="truncate text-sm font-medium text-ink">{{ snap.page_title }}</p>
                  <span class="inline-flex rounded-full bg-rose-100 px-2 py-0.5 text-xs font-semibold text-rose-700 capitalize mt-1">
                    {{ snap.diagnosis.replace(/_/g, " ") }}
                  </span>
                </div>
                <div class="shrink-0 text-right text-xs text-graphite">
                  <p>pos. {{ snap.gsc_avg_position_30d.toFixed(0) }}</p>
                  <p>{{ (snap.gsc_avg_ctr_30d * 100).toFixed(1) }}% CTR</p>
                </div>
              </div>
            </div>
            <div v-if="!worstPerformers.length" class="px-4 py-8 text-center text-sm text-graphite">
              All pages are healthy.
            </div>
          </div>
        </div>
      </div>
    </template>

  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { CheckCircle, RefreshCw } from "@lucide/vue";
import {
  cmsIntelligenceApi,
  type ContentPillar, type FreshnessAlert,
  type FunnelReport, type IntelligenceDashboard, type PerformanceSnapshot,
} from "@/api/cms";

const TABS = [
  { key: "pillars" as const, label: "Pillars" },
  { key: "funnel"  as const, label: "Funnel" },
  { key: "freshness" as const, label: "Freshness" },
  { key: "health" as const, label: "Content health" },
];

const HEALTH_METRICS = [
  { label: "Clicks",      value: "clicks"      as const },
  { label: "Page views",  value: "views"       as const },
  { label: "Conversions", value: "conversions" as const },
  { label: "Revenue",     value: "revenue"     as const },
];

const tab            = ref<"pillars" | "funnel" | "freshness" | "health">("pillars");
const isLoading      = ref(false);
const dashboard      = ref<IntelligenceDashboard | null>(null);

// Pillars
const pillars        = ref<ContentPillar[]>([]);
const isLoadingPillars = ref(false);

// Funnel
const selectedPillarSlug = ref<string | null>(null);
const funnel         = ref<FunnelReport | null>(null);
const isLoadingFunnel = ref(false);

// Freshness
const alerts         = ref<FreshnessAlert[]>([]);
const freshnessFilter = ref<"unresolved" | "resolved">("unresolved");
const isLoadingAlerts = ref(false);

// Health
const topPerformers  = ref<PerformanceSnapshot[]>([]);
const worstPerformers = ref<PerformanceSnapshot[]>([]);
const healthMetric   = ref<"clicks" | "views" | "conversions" | "revenue">("clicks");
const isLoadingHealth = ref(false);

// ── Load functions ────────────────────────────────────────────────────────

async function loadDashboard() {
  try {
    const { data } = await cmsIntelligenceApi.dashboard();
    dashboard.value = data;
  } catch { /* non-fatal */ }
}

async function loadPillars() {
  isLoadingPillars.value = true;
  try {
    const { data } = await cmsIntelligenceApi.pillars();
    pillars.value = Array.isArray(data) ? data : (data as any).results ?? [];
  } catch { pillars.value = []; }
  finally { isLoadingPillars.value = false; }
}

async function loadFunnel(slug: string) {
  selectedPillarSlug.value = slug;
  isLoadingFunnel.value = true;
  funnel.value = null;
  tab.value = "funnel";
  try {
    const { data } = await cmsIntelligenceApi.pillarFunnel(slug);
    funnel.value = data;
  } catch { /* error in UI */ }
  finally { isLoadingFunnel.value = false; }
}

async function loadFreshnessAlerts(status: "unresolved" | "resolved" = "unresolved") {
  freshnessFilter.value = status;
  isLoadingAlerts.value = true;
  try {
    const { data } = await cmsIntelligenceApi.freshnessAlerts(status);
    alerts.value = (data as any).results ?? (Array.isArray(data) ? data : []);
  } catch { alerts.value = []; }
  finally { isLoadingAlerts.value = false; }
}

async function loadTopPerformers(metric: typeof healthMetric.value = "clicks") {
  healthMetric.value = metric;
  isLoadingHealth.value = true;
  try {
    const [topRes, worstRes] = await Promise.all([
      cmsIntelligenceApi.topPerformers(metric),
      cmsIntelligenceApi.worstPerformers(),
    ]);
    topPerformers.value   = Array.isArray(topRes.data) ? topRes.data : [];
    worstPerformers.value = Array.isArray(worstRes.data) ? worstRes.data : [];
  } catch { /* empty states */ }
  finally { isLoadingHealth.value = false; }
}

async function acknowledgeAlert(id: number) {
  try {
    await cmsIntelligenceApi.acknowledgeAlert(id);
    await loadFreshnessAlerts(freshnessFilter.value);
  } catch { /* non-fatal */ }
}

async function resolveAlert(id: number) {
  const resolution = prompt("Resolution notes:");
  if (resolution === null) return;
  try {
    await cmsIntelligenceApi.resolveAlert(id, resolution);
    await loadFreshnessAlerts(freshnessFilter.value);
    await loadDashboard();
  } catch { /* non-fatal */ }
}

function openPillar(slug: string) {
  loadFunnel(slug);
}

async function refresh() {
  isLoading.value = true;
  await Promise.all([loadDashboard(), loadPillars(), loadFreshnessAlerts()]);
  isLoading.value = false;
}

// ── Helpers ───────────────────────────────────────────────────────────────

function fmt(v: string | number | undefined): string {
  const n = Number(v ?? 0);
  return Number.isNaN(n) ? "0" : n.toLocaleString(undefined, { maximumFractionDigits: 0 });
}

function fmtDate(v: string) {
  return new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(v));
}

function severityLabel(s: number): string {
  if (s >= 5) return "Critical";
  if (s >= 4) return "High";
  if (s >= 3) return "Medium";
  return "Low";
}

onMounted(async () => {
  await Promise.all([loadDashboard(), loadPillars(), loadFreshnessAlerts()]);
  await loadTopPerformers();
});
</script>
