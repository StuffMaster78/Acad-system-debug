<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { TrendingDown, TrendingUp, RefreshCw, AlertTriangle } from "@lucide/vue";
import WebsiteSelectorBar from "@/components/ui/WebsiteSelectorBar.vue";
import { api, apiPath } from "@/api/client";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();

// ── Filters ───────────────────────────────────────────────────────────────────
const filters = reactive({
  period: "month" as "month" | "quarter" | "year" | "cycle",
  year: new Date().getFullYear(),
  month: new Date().getMonth() + 1,
  quarter: Math.ceil((new Date().getMonth() + 1) / 3),
  cycle_id: null as number | null,
  website_id: null as number | null,
});

// ── Data ──────────────────────────────────────────────────────────────────────
interface ProfitData {
  period_label: string;
  period: string;
  date_range: { from: string; to: string };
  website_id: string | null;
  revenue: {
    gross_client_payments: string;
    refunds_issued: string;
    wallet_credits_issued: string;
    net_revenue: string;
  };
  expenditure: {
    writer_payouts: string;
    writer_bonuses: string;
    writer_tips: string;
    fines_recovered: string;
    total_expenditure: string;
  };
  profit: string;
  margin_pct: string;
}

const data = ref<ProfitData | null>(null);
const loading = ref(false);
const error = ref("");

const isProfit = computed(() => parseFloat(data.value?.profit ?? "0") >= 0);
const margin = computed(() => parseFloat(data.value?.margin_pct ?? "0"));

const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

const years = computed(() => {
  const y = new Date().getFullYear();
  return [y, y - 1, y - 2, y - 3];
});

function money(v: string | undefined) {
  if (!v) return "$0.00";
  const n = parseFloat(v);
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(n);
}

function pct(v: string | undefined) {
  return v ? `${parseFloat(v).toFixed(1)}%` : "0%";
}

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const params: Record<string, unknown> = {
      period: filters.period,
      year: filters.year,
      month: filters.month,
      quarter: filters.quarter,
    };
    if (filters.cycle_id) params.cycle_id = filters.cycle_id;
    if (filters.website_id) params.website_id = filters.website_id;
    const { data: d } = await api.get<ProfitData>(apiPath("/ledger/profit-summary/"), { params });
    data.value = d;
  } catch {
    error.value = "Could not load profit summary. Check that the ledger has data for this period.";
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<template>
  <div class="space-y-6 p-6">
    <!-- Header -->
    <div class="flex flex-col gap-1 border-b border-slate-200 pb-5">
      <p class="text-xs font-semibold uppercase tracking-widest text-signal">
        {{ auth.role === "superadmin" ? "Superadmin" : "Admin" }} · Finance
      </p>
      <h1 class="text-3xl font-bold text-ink">Platform P&amp;L Summary</h1>
      <p class="text-sm text-graphite">
        Net platform profit after deducting writer payouts, bonuses, tips, and refunds from gross client revenue.
      </p>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap items-end gap-4 rounded-xl border border-slate-200 bg-white p-5">
      <div class="space-y-1">
        <label class="text-xs font-semibold uppercase tracking-wide text-graphite">Period</label>
        <select v-model="filters.period" class="focus-ring h-9 rounded-lg border border-slate-200 bg-white px-3 text-sm text-ink">
          <option value="month">Monthly</option>
          <option value="quarter">Quarterly</option>
          <option value="year">Annual</option>
          <option value="cycle">Settlement Cycle</option>
        </select>
      </div>

      <div class="space-y-1">
        <label class="text-xs font-semibold uppercase tracking-wide text-graphite">Year</label>
        <select v-model.number="filters.year" class="focus-ring h-9 rounded-lg border border-slate-200 bg-white px-3 text-sm text-ink">
          <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
        </select>
      </div>

      <div v-if="filters.period === 'month'" class="space-y-1">
        <label class="text-xs font-semibold uppercase tracking-wide text-graphite">Month</label>
        <select v-model.number="filters.month" class="focus-ring h-9 rounded-lg border border-slate-200 bg-white px-3 text-sm text-ink">
          <option v-for="(m, i) in MONTHS" :key="i" :value="i + 1">{{ m }}</option>
        </select>
      </div>

      <div v-if="filters.period === 'quarter'" class="space-y-1">
        <label class="text-xs font-semibold uppercase tracking-wide text-graphite">Quarter</label>
        <select v-model.number="filters.quarter" class="focus-ring h-9 rounded-lg border border-slate-200 bg-white px-3 text-sm text-ink">
          <option value="1">Q1 (Jan–Mar)</option>
          <option value="2">Q2 (Apr–Jun)</option>
          <option value="3">Q3 (Jul–Sep)</option>
          <option value="4">Q4 (Oct–Dec)</option>
        </select>
      </div>

      <div v-if="filters.period === 'cycle'" class="space-y-1">
        <label class="text-xs font-semibold uppercase tracking-wide text-graphite">Cycle ID</label>
        <input
          v-model.number="filters.cycle_id"
          type="number" min="1" placeholder="e.g. 12"
          class="focus-ring h-9 w-28 rounded-lg border border-slate-200 px-3 text-sm text-ink"
        />
      </div>

      <div class="space-y-1">
        <label class="text-xs font-semibold uppercase tracking-wide text-graphite">Website</label>
        <WebsiteSelectorBar v-model="filters.website_id" class="h-9" />
      </div>

      <button
        class="inline-flex h-9 items-center gap-1.5 rounded-lg bg-ink px-4 text-sm font-semibold text-white hover:bg-ink/90 disabled:opacity-50 transition-colors"
        :disabled="loading"
        @click="load"
      >
        <RefreshCw class="h-3.5 w-3.5" :class="loading ? 'animate-spin' : ''" />
        {{ loading ? "Loading…" : "Refresh" }}
      </button>
    </div>

    <!-- Error -->
    <div v-if="error" class="flex items-center gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
      <AlertTriangle class="h-5 w-5 shrink-0 text-amber-500" />
      {{ error }}
    </div>

    <!-- Results -->
    <template v-if="data && !loading">
      <!-- Period header -->
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-xl font-bold text-ink">{{ data.period_label }}</h2>
          <p class="text-xs text-graphite mt-0.5">{{ data.date_range.from }} → {{ data.date_range.to }}</p>
        </div>
        <div
          class="flex items-center gap-2 rounded-xl px-5 py-3 text-lg font-black"
          :class="isProfit ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-rose-50 text-rose-700 border border-rose-200'"
        >
          <TrendingUp v-if="isProfit" class="h-5 w-5" />
          <TrendingDown v-else class="h-5 w-5" />
          {{ money(data.profit) }}
          <span class="text-sm font-semibold opacity-70">{{ pct(data.margin_pct) }} margin</span>
        </div>
      </div>

      <!-- KPI grid -->
      <div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div class="rounded-xl border border-slate-200 bg-white p-5 space-y-1">
          <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Gross Revenue</p>
          <p class="text-2xl font-black text-ink">{{ money(data.revenue.gross_client_payments) }}</p>
          <p class="text-xs text-graphite">Client payments collected</p>
        </div>
        <div class="rounded-xl border border-slate-200 bg-white p-5 space-y-1">
          <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Net Revenue</p>
          <p class="text-2xl font-black text-signal">{{ money(data.revenue.net_revenue) }}</p>
          <p class="text-xs text-graphite">After refunds &amp; credits</p>
        </div>
        <div class="rounded-xl border border-slate-200 bg-white p-5 space-y-1">
          <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Total Expenditure</p>
          <p class="text-2xl font-black text-ink">{{ money(data.expenditure.total_expenditure) }}</p>
          <p class="text-xs text-graphite">Payouts + bonuses + tips</p>
        </div>
        <div
          class="rounded-xl border p-5 space-y-1"
          :class="isProfit ? 'border-emerald-200 bg-emerald-50' : 'border-rose-200 bg-rose-50'"
        >
          <p class="text-xs font-semibold uppercase tracking-wide" :class="isProfit ? 'text-emerald-700' : 'text-rose-700'">Net Profit</p>
          <p class="text-2xl font-black" :class="isProfit ? 'text-emerald-800' : 'text-rose-800'">{{ money(data.profit) }}</p>
          <p class="text-xs" :class="isProfit ? 'text-emerald-700' : 'text-rose-700'">{{ pct(data.margin_pct) }} net margin</p>
        </div>
      </div>

      <!-- Two-column breakdown -->
      <div class="grid gap-5 lg:grid-cols-2">

        <!-- Revenue breakdown -->
        <div class="rounded-xl border border-slate-200 bg-white">
          <div class="border-b border-slate-100 px-5 py-4">
            <h3 class="font-semibold text-ink">Revenue breakdown</h3>
          </div>
          <div class="divide-y divide-slate-50">
            <div class="flex items-center justify-between px-5 py-3 text-sm">
              <span class="text-graphite">Gross client payments</span>
              <span class="font-mono font-semibold text-ink">{{ money(data.revenue.gross_client_payments) }}</span>
            </div>
            <div class="flex items-center justify-between px-5 py-3 text-sm">
              <span class="text-graphite">Refunds issued</span>
              <span class="font-mono font-semibold text-rose-600">-{{ money(data.revenue.refunds_issued) }}</span>
            </div>
            <div class="flex items-center justify-between px-5 py-3 text-sm">
              <span class="text-graphite">Support wallet credits</span>
              <span class="font-mono font-semibold text-rose-600">-{{ money(data.revenue.wallet_credits_issued) }}</span>
            </div>
            <div class="flex items-center justify-between px-5 py-4 text-sm font-bold border-t border-slate-200 bg-slate-50 rounded-b-xl">
              <span class="text-ink">Net Revenue</span>
              <span class="font-mono text-signal">{{ money(data.revenue.net_revenue) }}</span>
            </div>
          </div>
        </div>

        <!-- Expenditure breakdown -->
        <div class="rounded-xl border border-slate-200 bg-white">
          <div class="border-b border-slate-100 px-5 py-4">
            <h3 class="font-semibold text-ink">Expenditure breakdown</h3>
          </div>
          <div class="divide-y divide-slate-50">
            <div class="flex items-center justify-between px-5 py-3 text-sm">
              <span class="text-graphite">Writer payouts</span>
              <span class="font-mono font-semibold text-ink">{{ money(data.expenditure.writer_payouts) }}</span>
            </div>
            <div class="flex items-center justify-between px-5 py-3 text-sm">
              <span class="text-graphite">Writer bonuses</span>
              <span class="font-mono font-semibold text-ink">{{ money(data.expenditure.writer_bonuses) }}</span>
            </div>
            <div class="flex items-center justify-between px-5 py-3 text-sm">
              <span class="text-graphite">Tip settlements</span>
              <span class="font-mono font-semibold text-ink">{{ money(data.expenditure.writer_tips) }}</span>
            </div>
            <div class="flex items-center justify-between px-5 py-3 text-sm">
              <span class="text-graphite">Fines recovered (offset)</span>
              <span class="font-mono font-semibold text-emerald-600">-{{ money(data.expenditure.fines_recovered) }}</span>
            </div>
            <div class="flex items-center justify-between px-5 py-4 text-sm font-bold border-t border-slate-200 bg-slate-50 rounded-b-xl">
              <span class="text-ink">Total Expenditure</span>
              <span class="font-mono text-ink">{{ money(data.expenditure.total_expenditure) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Margin bar -->
      <div class="rounded-xl border border-slate-200 bg-white p-5 space-y-3">
        <div class="flex items-center justify-between">
          <h3 class="font-semibold text-ink">Margin visualisation</h3>
          <span class="text-sm font-bold" :class="isProfit ? 'text-emerald-700' : 'text-rose-600'">
            {{ pct(data.margin_pct) }} net margin
          </span>
        </div>
        <div class="h-5 rounded-full bg-slate-100 overflow-hidden flex">
          <div
            class="h-full rounded-full transition-all duration-700"
            :class="isProfit ? 'bg-emerald-500' : 'bg-rose-500'"
            :style="{ width: Math.min(Math.abs(margin), 100) + '%' }"
          />
        </div>
        <div class="flex justify-between text-xs text-graphite">
          <span>0%</span>
          <span>50%</span>
          <span>100%</span>
        </div>
      </div>
    </template>

    <!-- Skeleton -->
    <div v-if="loading" class="space-y-5 animate-pulse">
      <div class="h-24 rounded-xl bg-slate-100" />
      <div class="grid grid-cols-4 gap-4">
        <div v-for="i in 4" :key="i" class="h-28 rounded-xl bg-slate-100" />
      </div>
      <div class="grid grid-cols-2 gap-5">
        <div class="h-52 rounded-xl bg-slate-100" />
        <div class="h-52 rounded-xl bg-slate-100" />
      </div>
    </div>
  </div>
</template>
