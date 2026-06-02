<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import {
  Activity, ArrowDownLeft, ArrowUpRight, BadgeDollarSign,
  ChevronLeft, ChevronRight, CircleDollarSign, ClipboardList,
  CreditCard, DollarSign, HandCoins, RefreshCw, Scale,
  ShieldAlert, TrendingDown, TrendingUp, Wallet, Zap,
} from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import { adminPaymentsApi } from "@/api/adminPayments";
import { adminCompensationApi } from "@/api/adminCompensation";
import { adminWalletsApi } from "@/api/adminWallets";
import { billingApi } from "@/api/billing";
import { useAuthStore } from "@/stores/auth";
import { useWebsitesStore } from "@/stores/websites";

const auth = useAuthStore();
const websitesStore = useWebsitesStore();
const route = useRoute();

// ── Tabs ──────────────────────────────────────────────────────────────────────
type Tab = "overview" | "client" | "writer" | "tips" | "fines" | "wallets" | "advances";
const tab = ref<Tab>("overview");

const tabs: { key: Tab; label: string; icon: typeof DollarSign }[] = [
  { key: "overview",  label: "Overview",            icon: Activity },
  { key: "client",    label: "Client Transactions", icon: CreditCard },
  { key: "writer",    label: "Writer Payments",      icon: HandCoins },
  { key: "tips",      label: "Tips",                 icon: BadgeDollarSign },
  { key: "fines",     label: "Fines",                icon: ShieldAlert },
  { key: "wallets",   label: "Wallets",              icon: Wallet },
  { key: "advances",  label: "Advances",             icon: CircleDollarSign },
];

// ── Shared helpers ────────────────────────────────────────────────────────────
function money(v?: string | number | null) {
  if (v == null || v === "") return "$0.00";
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(Number(v));
}
function fmtDate(v?: string | null) {
  if (!v) return "—";
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", year: "numeric" }).format(new Date(v));
}
function fmtPeriod(start?: string, end?: string) {
  if (!start || !end) return "—";
  const s = new Intl.DateTimeFormat("en", { month: "short", day: "numeric" }).format(new Date(start));
  const e = new Intl.DateTimeFormat("en", { month: "short", day: "numeric", year: "numeric" }).format(new Date(end));
  return `${s} – ${e}`;
}

function statusTone(s: string): "success" | "warning" | "danger" | "neutral" {
  const map: Record<string, "success" | "warning" | "danger" | "neutral"> = {
    paid: "success", succeeded: "success", posted: "success", confirmed: "success",
    settled: "success", active: "success", approved: "success", resolved: "success",
    completed: "success", done: "success", matured: "success",
    pending: "warning", issued: "warning", open: "warning", processing: "warning",
    draft: "neutral", pending_confirmation: "warning", closed: "neutral",
    failed: "danger", cancelled: "danger", expired: "danger", voided: "danger",
    reversed: "danger", rejected: "danger", suspended: "danger",
  };
  return map[s?.toLowerCase()] ?? "neutral";
}

// ── Pagination helper ─────────────────────────────────────────────────────────
const PAGE_SIZE = 25;
function usePager<T>(data: ReturnType<typeof ref<T[]>>) {
  const page = ref(1);
  const total = computed(() => Math.ceil((data.value?.length ?? 0) / PAGE_SIZE));
  const paged = computed(() => (data.value ?? []).slice((page.value - 1) * PAGE_SIZE, page.value * PAGE_SIZE));
  return { page, total, paged };
}

// ── Overview ──────────────────────────────────────────────────────────────────
const overview = ref<Record<string, any> | null>(null);
const overviewLoading = ref(false);

async function loadOverview() {
  overviewLoading.value = true;
  try {
    if (auth.isPreviewSession) {
      overview.value = {
        total_revenue: "48250.00", revenue_30d: "12100.00",
        pending_payouts: "8340.00", writer_wallet_total: "21500.00",
        client_wallet_total: "9200.00", tips_30d: "1480.00", tips_total: "6320.00",
        fines_30d: "340.00", fines_total: "2100.00", advances_outstanding: "4500.00",
        refunds_30d: "880.00",
      };
      return;
    }
    const [dash, tipDash] = await Promise.allSettled([
      adminPaymentsApi.financialOverview(),
      adminPaymentsApi.tipDashboard(),
    ]);
    overview.value = {
      ...(dash.status === "fulfilled" ? dash.value.data : {}),
      tips_total: tipDash.status === "fulfilled" ? (tipDash.value.data as any)?.total_amount : null,
    };
  } finally {
    overviewLoading.value = false;
  }
}

// ── Client Transactions ───────────────────────────────────────────────────────
const invoices = ref<any[]>([]);
const invoiceLoading = ref(false);
const invoiceStatus = ref("");
const invoicePurpose = ref("");
const invoiceSearch = ref("");
const invoiceWebsite = ref<number | "">("");
const invoicePage = ref(1);
const invoiceTotal = ref(0);
const invoiceTotalPages = computed(() => Math.max(1, Math.ceil(invoiceTotal.value / PAGE_SIZE)));

async function loadInvoices() {
  invoiceLoading.value = true;
  try {
    if (auth.isPreviewSession) {
      const statuses = ["paid", "issued", "expired", "cancelled", "draft"];
      const purposes = ["ORDER_PAYMENT", "CLASS_PURCHASE", "SPECIAL_ORDER", "ADVANCE_REPAYMENT", "OTHER"];
      invoices.value = Array.from({ length: 40 }, (_, i) => ({
        id: 1000 + i,
        reference: `INV-${String(1000 + i).padStart(5, "0")}`,
        client_email: `client${i % 8}@example.com`,
        client_username: `client_${i % 8}`,
        amount: (Math.random() * 400 + 20).toFixed(2),
        currency: "USD",
        purpose: purposes[i % purposes.length],
        status: statuses[i % statuses.length],
        paid_at: i % 3 === 0 ? new Date(Date.now() - i * 3600000 * 24).toISOString() : null,
        created_at: new Date(Date.now() - i * 3600000 * 48).toISOString(),
      }));
      invoiceTotal.value = 40;
      return;
    }
    const params: Record<string, unknown> = { page: invoicePage.value, page_size: PAGE_SIZE };
    if (invoiceStatus.value) params.status = invoiceStatus.value;
    if (invoicePurpose.value) params.purpose = invoicePurpose.value;
    if (invoiceSearch.value) params.search = invoiceSearch.value;
    if (invoiceWebsite.value) params.website_id = invoiceWebsite.value;
    const { data } = await billingApi.invoices(params);
    invoices.value = Array.isArray(data) ? data : (data as any).results ?? [];
    invoiceTotal.value = Array.isArray(data) ? data.length : (data as any).count ?? 0;
  } finally {
    invoiceLoading.value = false;
  }
}

const pagedInvoices = computed(() =>
  auth.isPreviewSession
    ? invoices.value.slice((invoicePage.value - 1) * PAGE_SIZE, invoicePage.value * PAGE_SIZE)
    : invoices.value
);

watch([invoiceStatus, invoicePurpose, invoiceSearch, invoiceWebsite], () => { invoicePage.value = 1; loadInvoices(); });
watch(invoicePage, loadInvoices);

// ── Writer Payments (bi-weekly windows) ───────────────────────────────────────
const windows = ref<any[]>([]);
const windowsLoading = ref(false);
const windowsPage = ref(1);
const windowsTotal = ref(0);
const windowsTotalPages = computed(() => Math.max(1, Math.ceil(windowsTotal.value / PAGE_SIZE)));
const windowFilter = ref("all");
const expandedWindow = ref<number | null>(null);
const windowDetail = ref<Record<number, any>>({});

async function loadWindows() {
  windowsLoading.value = true;
  try {
    if (auth.isPreviewSession) {
      const statuses = ["DONE", "CLOSED", "PROCESSING", "OPEN"];
      const now = Date.now();
      windows.value = Array.from({ length: 12 }, (_, i) => ({
        id: 100 + i,
        cycle_type: "BIWEEKLY",
        start_date: new Date(now - (i * 14 + 14) * 86400000).toISOString().slice(0, 10),
        end_date: new Date(now - i * 14 * 86400000).toISOString().slice(0, 10),
        status: statuses[i % statuses.length],
        writer_count: Math.floor(Math.random() * 18) + 2,
        gross_total: (Math.random() * 12000 + 2000).toFixed(2),
        net_payable: (Math.random() * 9000 + 1500).toFixed(2),
        settled_count: Math.floor(Math.random() * 12),
      }));
      windowsTotal.value = 12;
      return;
    }
    const params: Record<string, unknown> = { page: windowsPage.value, page_size: PAGE_SIZE, cycle_type: "BIWEEKLY" };
    if (windowFilter.value !== "all") params.status = windowFilter.value;
    const { data } = await adminCompensationApi.windows(params);
    windows.value = Array.isArray(data) ? data : (data as any).results ?? [];
    windowsTotal.value = Array.isArray(data) ? data.length : (data as any).count ?? 0;
  } finally {
    windowsLoading.value = false;
  }
}

async function toggleWindow(id: number) {
  if (expandedWindow.value === id) { expandedWindow.value = null; return; }
  expandedWindow.value = id;
  if (!windowDetail.value[id]) {
    if (auth.isPreviewSession) {
      windowDetail.value[id] = {
        writers: Array.from({ length: 5 }, (_, j) => ({
          writer_id: 200 + j,
          writer_username: `writer_${200 + j}`,
          gross_earnings: (Math.random() * 2000 + 500).toFixed(2),
          deductions: (Math.random() * 200).toFixed(2),
          net_payable: (Math.random() * 1800 + 400).toFixed(2),
          status: j < 3 ? "SETTLED" : "PENDING",
        })),
      };
    } else {
      try {
        const { data } = await adminCompensationApi.windowSummary(id);
        windowDetail.value[id] = data;
      } catch { windowDetail.value[id] = null; }
    }
  }
}

watch([windowFilter, windowsPage], loadWindows);

// ── Tips ──────────────────────────────────────────────────────────────────────
const tips = ref<any[]>([]);
const tipsLoading = ref(false);
const tipStatus = ref("");
const tipWebsite = ref<number | "">("");
const tipPage = ref(1);
const tipTotal = ref(0);
const tipTotalPages = computed(() => Math.max(1, Math.ceil(tipTotal.value / PAGE_SIZE)));

async function loadTips() {
  tipsLoading.value = true;
  try {
    if (auth.isPreviewSession) {
      tips.value = Array.from({ length: 30 }, (_, i) => ({
        id: 500 + i,
        public_id: `tip-${500 + i}`,
        sender_username: `client_${i % 5}`,
        receiver_username: `writer_${i % 6}`,
        gross_amount: (Math.random() * 50 + 5).toFixed(2),
        writer_share_cents: Math.floor(Math.random() * 3500 + 400),
        platform_fee_cents: Math.floor(Math.random() * 500 + 50),
        source_type: i % 3 === 0 ? "DIRECT" : "ORDER",
        status: ["SUCCEEDED", "PENDING", "FAILED"][i % 3],
        is_settled: i % 2 === 0,
        created_at: new Date(Date.now() - i * 3600000 * 36).toISOString(),
      }));
      tipTotal.value = 30;
      return;
    }
    const params: Record<string, unknown> = { page: tipPage.value, page_size: PAGE_SIZE };
    if (tipStatus.value) params.status = tipStatus.value;
    if (tipWebsite.value) params.website_id = tipWebsite.value;
    const { data } = await adminPaymentsApi.tipList(params);
    tips.value = Array.isArray(data) ? data : (data as any).results ?? [];
    tipTotal.value = Array.isArray(data) ? data.length : (data as any).count ?? 0;
  } finally {
    tipsLoading.value = false;
  }
}

watch([tipStatus, tipWebsite, tipPage], loadTips);

// ── Fines ─────────────────────────────────────────────────────────────────────
const fines = ref<any[]>([]);
const finesLoading = ref(false);
const fineStatus = ref("");
const finePage = ref(1);
const fineTotal = ref(0);
const fineTotalPages = computed(() => Math.max(1, Math.ceil(fineTotal.value / PAGE_SIZE)));

async function loadFines() {
  finesLoading.value = true;
  try {
    if (auth.isPreviewSession) {
      const statuses = ["ISSUED", "RESOLVED", "WAIVED", "VOIDED"];
      fines.value = Array.from({ length: 25 }, (_, i) => ({
        id: 700 + i,
        writer_username: `writer_${i % 6}`,
        order_reference: `ORD-${(10000 + i * 7).toString()}`,
        amount: (Math.random() * 80 + 5).toFixed(2),
        reason: ["Late delivery", "No submission", "Policy violation", "Quality issue"][i % 4],
        status: statuses[i % statuses.length],
        imposed_at: new Date(Date.now() - i * 3600000 * 48).toISOString(),
        has_appeal: i % 5 === 0,
      }));
      fineTotal.value = 25;
      return;
    }
    const params: Record<string, unknown> = { page: finePage.value, page_size: PAGE_SIZE };
    if (fineStatus.value) params.status = fineStatus.value;
    const { data } = await adminPaymentsApi.finesList(params);
    fines.value = Array.isArray(data) ? data : (data as any).results ?? [];
    fineTotal.value = Array.isArray(data) ? data.length : (data as any).count ?? 0;
  } finally {
    finesLoading.value = false;
  }
}

watch([fineStatus, finePage], loadFines);

// ── Wallets ───────────────────────────────────────────────────────────────────
const wallets = ref<any[]>([]);
const walletsLoading = ref(false);
const walletType = ref("all");
const walletSearch = ref("");
const walletWebsite = ref<number | "">("");
const walletPage = ref(1);
const walletTotal = ref(0);
const walletTotalPages = computed(() => Math.max(1, Math.ceil(walletTotal.value / PAGE_SIZE)));

async function loadWallets() {
  walletsLoading.value = true;
  try {
    if (auth.isPreviewSession) {
      const types = ["client", "writer", "system"];
      wallets.value = Array.from({ length: 30 }, (_, i) => ({
        id: 300 + i,
        owner_username: `user_${300 + i}`,
        owner_email: `user${300 + i}@example.com`,
        wallet_type: types[i % 3],
        currency: "USD",
        available_balance: (Math.random() * 3000).toFixed(2),
        pending_balance: (Math.random() * 400).toFixed(2),
        total_credited: (Math.random() * 8000 + 1000).toFixed(2),
        total_debited: (Math.random() * 6000).toFixed(2),
        status: i % 10 === 0 ? "SUSPENDED" : "ACTIVE",
      }));
      walletTotal.value = 30;
      return;
    }
    const params: Record<string, unknown> = { page: walletPage.value, page_size: PAGE_SIZE };
    if (walletType.value !== "all") params.wallet_type = walletType.value;
    if (walletSearch.value) params.search = walletSearch.value;
    if (walletWebsite.value) params.website_id = walletWebsite.value;
    const { data } = await adminWalletsApi.wallets(params);
    wallets.value = Array.isArray(data) ? data : (data as any).results ?? [];
    walletTotal.value = Array.isArray(data) ? data.length : (data as any).count ?? 0;
  } finally {
    walletsLoading.value = false;
  }
}

watch([walletType, walletSearch, walletWebsite, walletPage], loadWallets);

// ── Advances ──────────────────────────────────────────────────────────────────
const advances = ref<any[]>([]);
const advancesLoading = ref(false);
const advanceStatus = ref("all");
const advancePage = ref(1);
const advanceTotal = ref(0);
const advanceTotalPages = computed(() => Math.max(1, Math.ceil(advanceTotal.value / PAGE_SIZE)));

async function loadAdvances() {
  advancesLoading.value = true;
  try {
    if (auth.isPreviewSession) {
      const statuses = ["PENDING", "APPROVED", "REJECTED", "RECOVERED"];
      advances.value = Array.from({ length: 15 }, (_, i) => ({
        id: 400 + i,
        writer_username: `writer_${i % 6}`,
        requested_amount: (Math.random() * 500 + 100).toFixed(2),
        approved_amount: i % 4 !== 1 ? (Math.random() * 400 + 80).toFixed(2) : null,
        recovered_amount: (Math.random() * 200).toFixed(2),
        outstanding_balance: (Math.random() * 300).toFixed(2),
        status: statuses[i % statuses.length],
        created_at: new Date(Date.now() - i * 3600000 * 72).toISOString(),
      }));
      advanceTotal.value = 15;
      return;
    }
    const params: Record<string, unknown> = { page: advancePage.value, page_size: PAGE_SIZE };
    if (advanceStatus.value !== "all") params.status = advanceStatus.value;
    const { data } = await adminCompensationApi.advances(params);
    advances.value = Array.isArray(data) ? data : (data as any).results ?? [];
    advanceTotal.value = Array.isArray(data) ? data.length : (data as any).count ?? 0;
  } finally {
    advancesLoading.value = false;
  }
}

watch([advanceStatus, advancePage], loadAdvances);

// ── Tab change → load data ────────────────────────────────────────────────────
watch(tab, (t) => {
  if (t === "client" && !invoices.value.length) loadInvoices();
  if (t === "writer" && !windows.value.length) loadWindows();
  if (t === "tips" && !tips.value.length) loadTips();
  if (t === "fines" && !fines.value.length) loadFines();
  if (t === "wallets" && !wallets.value.length) loadWallets();
  if (t === "advances" && !advances.value.length) loadAdvances();
});

onMounted(() => { websitesStore.ensure(); loadOverview(); });

// ── Purpose label ─────────────────────────────────────────────────────────────
const purposeLabel: Record<string, string> = {
  ORDER_PAYMENT: "Order", CLASS_PURCHASE: "Class", SPECIAL_ORDER: "Special Order",
  ADVANCE_REPAYMENT: "Advance Repayment", OTHER: "Other",
};
</script>

<template>
  <div class="space-y-6">

    <!-- Page header -->
    <div class="flex items-end justify-between">
      <div>
        <p class="text-sm font-semibold uppercase text-signal">Finance</p>
        <h1 class="mt-1 text-3xl font-semibold text-ink">Financial Center</h1>
        <p class="mt-1.5 text-sm text-graphite">
          Unified view of all platform money flows — client payments, writer payouts, tips, fines, wallets, and advances.
        </p>
      </div>
    </div>

    <!-- Tab bar -->
    <nav class="flex gap-1 overflow-x-auto rounded-xl border border-slate-200 bg-slate-50 p-1">
      <button
        v-for="t in tabs"
        :key="t.key"
        class="focus-ring flex shrink-0 items-center gap-1.5 rounded-lg px-3.5 py-2 text-xs font-semibold transition-all"
        :class="tab === t.key ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
        type="button"
        @click="tab = t.key"
      >
        <component :is="t.icon" class="h-3.5 w-3.5" />
        {{ t.label }}
      </button>
    </nav>

    <!-- ═══════════════════════════════════════════════════════════════════════ -->
    <!-- OVERVIEW TAB                                                           -->
    <!-- ═══════════════════════════════════════════════════════════════════════ -->
    <template v-if="tab === 'overview'">
      <div v-if="overviewLoading" class="py-20"><LoadingSpinner label="Loading financial summary…" /></div>
      <div v-else class="space-y-6">

        <!-- KPI grid -->
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div class="rounded-xl border border-slate-200 bg-white p-5">
            <div class="flex items-center gap-2 text-xs font-semibold uppercase text-graphite">
              <TrendingUp class="h-3.5 w-3.5" /> Total revenue
            </div>
            <p class="mt-3 text-2xl font-bold text-ink">{{ money(overview?.total_revenue ?? overview?.platform_revenue) }}</p>
            <p class="mt-1 text-xs text-graphite">{{ money(overview?.revenue_30d) }} in last 30 days</p>
          </div>
          <div class="rounded-xl border border-emerald-200 bg-emerald-50 p-5">
            <div class="flex items-center gap-2 text-xs font-semibold uppercase text-graphite">
              <HandCoins class="h-3.5 w-3.5" /> Pending payouts
            </div>
            <p class="mt-3 text-2xl font-bold text-ink">{{ money(overview?.pending_payouts) }}</p>
            <p class="mt-1 text-xs text-graphite">Owed to writers, not yet settled</p>
          </div>
          <div class="rounded-xl border border-slate-200 bg-white p-5">
            <div class="flex items-center gap-2 text-xs font-semibold uppercase text-graphite">
              <Wallet class="h-3.5 w-3.5" /> Client wallets
            </div>
            <p class="mt-3 text-2xl font-bold text-ink">{{ money(overview?.client_wallet_total) }}</p>
            <p class="mt-1 text-xs text-graphite">Total available across all clients</p>
          </div>
          <div class="rounded-xl border border-slate-200 bg-white p-5">
            <div class="flex items-center gap-2 text-xs font-semibold uppercase text-graphite">
              <Wallet class="h-3.5 w-3.5" /> Writer wallets
            </div>
            <p class="mt-3 text-2xl font-bold text-ink">{{ money(overview?.writer_wallet_total) }}</p>
            <p class="mt-1 text-xs text-graphite">Total held in writer wallets</p>
          </div>
        </div>

        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div class="rounded-xl border border-amber-200 bg-amber-50 p-5">
            <div class="flex items-center gap-2 text-xs font-semibold uppercase text-graphite">
              <BadgeDollarSign class="h-3.5 w-3.5" /> Tips (30d)
            </div>
            <p class="mt-3 text-2xl font-bold text-ink">{{ money(overview?.tips_30d) }}</p>
            <p class="mt-1 text-xs text-graphite">{{ money(overview?.tips_total) }} all-time</p>
          </div>
          <div class="rounded-xl border border-rose-200 bg-rose-50 p-5">
            <div class="flex items-center gap-2 text-xs font-semibold uppercase text-graphite">
              <ShieldAlert class="h-3.5 w-3.5" /> Fines (30d)
            </div>
            <p class="mt-3 text-2xl font-bold text-ink">{{ money(overview?.fines_30d) }}</p>
            <p class="mt-1 text-xs text-graphite">{{ money(overview?.fines_total) }} all-time</p>
          </div>
          <div class="rounded-xl border border-slate-200 bg-white p-5">
            <div class="flex items-center gap-2 text-xs font-semibold uppercase text-graphite">
              <CircleDollarSign class="h-3.5 w-3.5" /> Advances outstanding
            </div>
            <p class="mt-3 text-2xl font-bold text-ink">{{ money(overview?.advances_outstanding) }}</p>
            <p class="mt-1 text-xs text-graphite">Unrecovered writer advances</p>
          </div>
          <div class="rounded-xl border border-slate-200 bg-white p-5">
            <div class="flex items-center gap-2 text-xs font-semibold uppercase text-graphite">
              <TrendingDown class="h-3.5 w-3.5" /> Refunds (30d)
            </div>
            <p class="mt-3 text-2xl font-bold text-ink">{{ money(overview?.refunds_30d) }}</p>
            <p class="mt-1 text-xs text-graphite">Client refunds processed</p>
          </div>
        </div>

        <!-- Quick nav to tabs -->
        <div class="grid gap-3 sm:grid-cols-3 lg:grid-cols-6">
          <button
            v-for="t in tabs.slice(1)"
            :key="t.key"
            class="flex items-center gap-2 rounded-xl border border-slate-200 bg-white p-4 text-left transition-colors hover:border-signal hover:bg-slate-50"
            type="button"
            @click="tab = t.key"
          >
            <component :is="t.icon" class="h-4 w-4 text-signal" />
            <span class="text-sm font-semibold text-ink">{{ t.label }}</span>
          </button>
        </div>
      </div>
    </template>

    <!-- ═══════════════════════════════════════════════════════════════════════ -->
    <!-- CLIENT TRANSACTIONS TAB                                                -->
    <!-- ═══════════════════════════════════════════════════════════════════════ -->
    <template v-else-if="tab === 'client'">
      <div class="rounded-xl border border-slate-200 bg-white">
        <!-- Filters -->
        <div class="flex flex-wrap items-center gap-3 border-b border-slate-200 px-4 py-3">
          <div class="flex items-center gap-2 text-sm font-semibold text-ink">
            <CreditCard class="h-4 w-4 text-signal" /> Client Transactions
          </div>
          <div class="ml-auto flex flex-wrap gap-2">
            <input
              v-model="invoiceSearch"
              class="focus-ring h-9 rounded-lg border border-slate-200 bg-slate-50 px-3 text-xs"
              placeholder="Search reference, email…"
              type="search"
            />
            <select v-model="invoiceStatus" class="focus-ring h-9 rounded-lg border border-slate-200 bg-white px-2 text-xs">
              <option value="">All statuses</option>
              <option value="paid">Paid</option>
              <option value="issued">Issued</option>
              <option value="draft">Draft</option>
              <option value="expired">Expired</option>
              <option value="cancelled">Cancelled</option>
            </select>
            <select v-model="invoicePurpose" class="focus-ring h-9 rounded-lg border border-slate-200 bg-white px-2 text-xs">
              <option value="">All types</option>
              <option value="ORDER_PAYMENT">Order</option>
              <option value="CLASS_PURCHASE">Class</option>
              <option value="SPECIAL_ORDER">Special Order</option>
              <option value="ADVANCE_REPAYMENT">Advance Repayment</option>
            </select>
            <select v-model="invoiceWebsite" class="focus-ring h-9 rounded-lg border border-slate-200 bg-white px-2 text-xs">
              <option value="">All websites</option>
              <option v-for="ws in websitesStore.list" :key="ws.id" :value="ws.id">{{ ws.name || ws.domain }}</option>
            </select>
            <button class="focus-ring h-9 rounded-lg border border-slate-200 bg-white px-2 text-xs" @click="loadInvoices">
              <RefreshCw class="h-3.5 w-3.5" />
            </button>
          </div>
        </div>

        <div v-if="invoiceLoading" class="py-16"><LoadingSpinner label="Loading transactions…" /></div>
        <div v-else-if="!pagedInvoices.length" class="py-16 text-center text-sm text-graphite">
          No transactions found for the current filters.
        </div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-full text-sm">
            <thead class="bg-slate-50 text-xs font-semibold uppercase tracking-wide text-graphite">
              <tr>
                <th class="whitespace-nowrap px-4 py-3 text-left">Reference</th>
                <th class="whitespace-nowrap px-4 py-3 text-left">Client</th>
                <th class="whitespace-nowrap px-4 py-3 text-left">Website</th>
                <th class="whitespace-nowrap px-4 py-3 text-left">Type</th>
                <th class="whitespace-nowrap px-4 py-3 text-right">Amount</th>
                <th class="whitespace-nowrap px-4 py-3 text-center">Status</th>
                <th class="whitespace-nowrap px-4 py-3 text-right">Date</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="inv in pagedInvoices" :key="inv.id" class="hover:bg-slate-50">
                <td class="px-4 py-3 font-mono text-xs text-graphite">{{ inv.reference }}</td>
                <td class="px-4 py-3">
                  <p class="font-medium text-ink">{{ inv.client_username || inv.client_email }}</p>
                  <p v-if="inv.client_email && inv.client_username" class="text-xs text-graphite">{{ inv.client_email }}</p>
                </td>
                <td class="px-4 py-3">
                  <span class="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700">
                    {{ inv.website_name || websitesStore.nameById(inv.website_id ?? inv.website) }}
                  </span>
                </td>
                <td class="px-4 py-3 text-graphite">{{ purposeLabel[inv.purpose] || inv.purpose || '—' }}</td>
                <td class="px-4 py-3 text-right font-semibold text-ink">{{ money(inv.amount) }}</td>
                <td class="px-4 py-3 text-center">
                  <StatusPill :label="inv.status" :tone="statusTone(inv.status)" />
                </td>
                <td class="px-4 py-3 text-right text-graphite">{{ fmtDate(inv.paid_at || inv.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="invoiceTotalPages > 1" class="flex items-center justify-between border-t border-slate-200 px-4 py-3">
          <p class="text-xs text-graphite">Page {{ invoicePage }} of {{ invoiceTotalPages }} · {{ invoiceTotal }} records</p>
          <div class="flex gap-2">
            <button class="focus-ring inline-flex h-8 w-8 items-center justify-center rounded-md border border-slate-200 bg-white disabled:opacity-40" :disabled="invoicePage <= 1" @click="invoicePage--"><ChevronLeft class="h-4 w-4" /></button>
            <button class="focus-ring inline-flex h-8 w-8 items-center justify-center rounded-md border border-slate-200 bg-white disabled:opacity-40" :disabled="invoicePage >= invoiceTotalPages" @click="invoicePage++"><ChevronRight class="h-4 w-4" /></button>
          </div>
        </div>
      </div>
    </template>

    <!-- ═══════════════════════════════════════════════════════════════════════ -->
    <!-- WRITER PAYMENTS TAB                                                    -->
    <!-- ═══════════════════════════════════════════════════════════════════════ -->
    <template v-else-if="tab === 'writer'">
      <div class="rounded-xl border border-slate-200 bg-white">
        <div class="flex flex-wrap items-center gap-3 border-b border-slate-200 px-4 py-3">
          <div class="flex items-center gap-2 text-sm font-semibold text-ink">
            <HandCoins class="h-4 w-4 text-signal" /> Bi-Weekly Payment Windows
          </div>
          <div class="ml-auto flex gap-2">
            <select v-model="windowFilter" class="focus-ring h-9 rounded-lg border border-slate-200 bg-white px-2 text-xs">
              <option value="all">All windows</option>
              <option value="OPEN">Open</option>
              <option value="CLOSED">Closed</option>
              <option value="PROCESSING">Processing</option>
              <option value="DONE">Done</option>
            </select>
            <button class="focus-ring h-9 rounded-lg border border-slate-200 bg-white px-2" @click="loadWindows">
              <RefreshCw class="h-3.5 w-3.5" />
            </button>
          </div>
        </div>

        <div v-if="windowsLoading" class="py-16"><LoadingSpinner label="Loading payment windows…" /></div>
        <div v-else-if="!windows.length" class="py-16 text-center text-sm text-graphite">No payment windows found.</div>
        <div v-else class="divide-y divide-slate-100">
          <div v-for="win in windows" :key="win.id">
            <!-- Window row -->
            <button
              class="flex w-full items-center gap-4 px-4 py-3 text-left transition-colors hover:bg-slate-50"
              type="button"
              @click="toggleWindow(win.id)"
            >
              <div class="min-w-0 flex-1">
                <div class="flex flex-wrap items-center gap-3">
                  <span class="font-semibold text-ink">{{ fmtPeriod(win.start_date, win.end_date) }}</span>
                  <StatusPill :label="win.status?.toLowerCase()" :tone="statusTone(win.status)" />
                  <span class="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-graphite">{{ win.cycle_type || 'Biweekly' }}</span>
                </div>
                <div class="mt-1 flex flex-wrap gap-4 text-xs text-graphite">
                  <span>{{ win.writer_count ?? '—' }} writers</span>
                  <span>Gross: <strong class="text-ink">{{ money(win.gross_total) }}</strong></span>
                  <span>Net payable: <strong class="text-ink">{{ money(win.net_payable) }}</strong></span>
                  <span v-if="win.settled_count != null">{{ win.settled_count }} settled</span>
                </div>
              </div>
              <ChevronRight class="h-4 w-4 shrink-0 text-graphite transition-transform" :class="expandedWindow === win.id ? 'rotate-90' : ''" />
            </button>

            <!-- Expanded per-writer breakdown -->
            <div v-if="expandedWindow === win.id" class="border-t border-slate-100 bg-slate-50 px-4 py-3">
              <div v-if="!windowDetail[win.id]" class="py-4 text-center text-xs text-graphite animate-pulse">Loading breakdown…</div>
              <table v-else-if="windowDetail[win.id]?.writers?.length" class="min-w-full text-xs">
                <thead class="text-graphite font-semibold uppercase tracking-wide">
                  <tr>
                    <th class="py-2 text-left pr-4">Writer</th>
                    <th class="py-2 text-right pr-4">Gross</th>
                    <th class="py-2 text-right pr-4">Deductions</th>
                    <th class="py-2 text-right pr-4">Net payable</th>
                    <th class="py-2 text-center">Status</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-200">
                  <tr v-for="wr in windowDetail[win.id].writers" :key="wr.writer_id">
                    <td class="py-2 pr-4 font-medium text-ink">@{{ wr.writer_username }}</td>
                    <td class="py-2 pr-4 text-right">{{ money(wr.gross_earnings) }}</td>
                    <td class="py-2 pr-4 text-right text-rose-600">{{ money(wr.deductions) }}</td>
                    <td class="py-2 pr-4 text-right font-semibold text-ink">{{ money(wr.net_payable) }}</td>
                    <td class="py-2 text-center"><StatusPill :label="wr.status?.toLowerCase()" :tone="statusTone(wr.status)" /></td>
                  </tr>
                </tbody>
              </table>
              <p v-else class="py-4 text-center text-xs text-graphite">No writer breakdown available.</p>
            </div>
          </div>
        </div>

        <div v-if="windowsTotalPages > 1" class="flex items-center justify-between border-t border-slate-200 px-4 py-3">
          <p class="text-xs text-graphite">Page {{ windowsPage }} of {{ windowsTotalPages }}</p>
          <div class="flex gap-2">
            <button class="focus-ring inline-flex h-8 w-8 items-center justify-center rounded-md border border-slate-200 bg-white disabled:opacity-40" :disabled="windowsPage <= 1" @click="windowsPage--"><ChevronLeft class="h-4 w-4" /></button>
            <button class="focus-ring inline-flex h-8 w-8 items-center justify-center rounded-md border border-slate-200 bg-white disabled:opacity-40" :disabled="windowsPage >= windowsTotalPages" @click="windowsPage++"><ChevronRight class="h-4 w-4" /></button>
          </div>
        </div>
      </div>
    </template>

    <!-- ═══════════════════════════════════════════════════════════════════════ -->
    <!-- TIPS TAB                                                               -->
    <!-- ═══════════════════════════════════════════════════════════════════════ -->
    <template v-else-if="tab === 'tips'">
      <div class="rounded-xl border border-slate-200 bg-white">
        <div class="flex flex-wrap items-center gap-3 border-b border-slate-200 px-4 py-3">
          <div class="flex items-center gap-2 text-sm font-semibold text-ink">
            <BadgeDollarSign class="h-4 w-4 text-signal" /> Tips
          </div>
          <div class="ml-auto flex gap-2">
            <select v-model="tipStatus" class="focus-ring h-9 rounded-lg border border-slate-200 bg-white px-2 text-xs">
              <option value="">All statuses</option>
              <option value="SUCCEEDED">Succeeded</option>
              <option value="PENDING">Pending</option>
              <option value="FAILED">Failed</option>
            </select>
            <select v-model="tipWebsite" class="focus-ring h-9 rounded-lg border border-slate-200 bg-white px-2 text-xs">
              <option value="">All websites</option>
              <option v-for="ws in websitesStore.list" :key="ws.id" :value="ws.id">{{ ws.name || ws.domain }}</option>
            </select>
            <button class="focus-ring h-9 rounded-lg border border-slate-200 bg-white px-2" @click="loadTips">
              <RefreshCw class="h-3.5 w-3.5" />
            </button>
          </div>
        </div>

        <div v-if="tipsLoading" class="py-16"><LoadingSpinner label="Loading tips…" /></div>
        <div v-else-if="!tips.length" class="py-16 text-center text-sm text-graphite">No tips found.</div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-full text-sm">
            <thead class="bg-slate-50 text-xs font-semibold uppercase tracking-wide text-graphite">
              <tr>
                <th class="whitespace-nowrap px-4 py-3 text-left">From</th>
                <th class="whitespace-nowrap px-4 py-3 text-left">To (writer)</th>
                <th class="whitespace-nowrap px-4 py-3 text-left">Website</th>
                <th class="whitespace-nowrap px-4 py-3 text-left">Source</th>
                <th class="whitespace-nowrap px-4 py-3 text-right">Gross</th>
                <th class="whitespace-nowrap px-4 py-3 text-right">Writer share</th>
                <th class="whitespace-nowrap px-4 py-3 text-right">Platform fee</th>
                <th class="whitespace-nowrap px-4 py-3 text-center">Status</th>
                <th class="whitespace-nowrap px-4 py-3 text-center">Settled</th>
                <th class="whitespace-nowrap px-4 py-3 text-right">Date</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="tip in tips" :key="tip.id" class="hover:bg-slate-50">
                <td class="px-4 py-3 text-graphite">@{{ tip.sender_username || tip.sender?.username || '—' }}</td>
                <td class="px-4 py-3 font-medium text-ink">@{{ tip.receiver_username || tip.receiver?.username || '—' }}</td>
                <td class="px-4 py-3">
                  <span class="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700">
                    {{ tip.website_name || websitesStore.nameById(tip.website_id) }}
                  </span>
                </td>
                <td class="px-4 py-3 text-xs text-graphite">{{ tip.source_type || '—' }}</td>
                <td class="px-4 py-3 text-right font-semibold text-ink">{{ money(tip.gross_amount) }}</td>
                <td class="px-4 py-3 text-right text-emerald-700">{{ tip.writer_share_cents != null ? money(tip.writer_share_cents / 100) : '—' }}</td>
                <td class="px-4 py-3 text-right text-graphite">{{ tip.platform_fee_cents != null ? money(tip.platform_fee_cents / 100) : '—' }}</td>
                <td class="px-4 py-3 text-center"><StatusPill :label="tip.status?.toLowerCase()" :tone="statusTone(tip.status)" /></td>
                <td class="px-4 py-3 text-center">
                  <StatusPill :label="tip.is_settled ? 'settled' : 'unsettled'" :tone="tip.is_settled ? 'success' : 'warning'" />
                </td>
                <td class="px-4 py-3 text-right text-graphite">{{ fmtDate(tip.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="tipTotalPages > 1" class="flex items-center justify-between border-t border-slate-200 px-4 py-3">
          <p class="text-xs text-graphite">Page {{ tipPage }} of {{ tipTotalPages }} · {{ tipTotal }} tips</p>
          <div class="flex gap-2">
            <button class="focus-ring inline-flex h-8 w-8 items-center justify-center rounded-md border border-slate-200 bg-white disabled:opacity-40" :disabled="tipPage <= 1" @click="tipPage--"><ChevronLeft class="h-4 w-4" /></button>
            <button class="focus-ring inline-flex h-8 w-8 items-center justify-center rounded-md border border-slate-200 bg-white disabled:opacity-40" :disabled="tipPage >= tipTotalPages" @click="tipPage++"><ChevronRight class="h-4 w-4" /></button>
          </div>
        </div>
      </div>
    </template>

    <!-- ═══════════════════════════════════════════════════════════════════════ -->
    <!-- FINES TAB                                                              -->
    <!-- ═══════════════════════════════════════════════════════════════════════ -->
    <template v-else-if="tab === 'fines'">
      <div class="rounded-xl border border-slate-200 bg-white">
        <div class="flex flex-wrap items-center gap-3 border-b border-slate-200 px-4 py-3">
          <div class="flex items-center gap-2 text-sm font-semibold text-ink">
            <ShieldAlert class="h-4 w-4 text-signal" /> Writer Fines
          </div>
          <div class="ml-auto flex gap-2">
            <select v-model="fineStatus" class="focus-ring h-9 rounded-lg border border-slate-200 bg-white px-2 text-xs">
              <option value="">All statuses</option>
              <option value="ISSUED">Issued</option>
              <option value="RESOLVED">Resolved</option>
              <option value="WAIVED">Waived</option>
              <option value="VOIDED">Voided</option>
            </select>
            <button class="focus-ring h-9 rounded-lg border border-slate-200 bg-white px-2" @click="loadFines">
              <RefreshCw class="h-3.5 w-3.5" />
            </button>
          </div>
        </div>

        <div v-if="finesLoading" class="py-16"><LoadingSpinner label="Loading fines…" /></div>
        <div v-else-if="!fines.length" class="py-16 text-center text-sm text-graphite">No fines found.</div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-full text-sm">
            <thead class="bg-slate-50 text-xs font-semibold uppercase tracking-wide text-graphite">
              <tr>
                <th class="whitespace-nowrap px-4 py-3 text-left">Writer</th>
                <th class="whitespace-nowrap px-4 py-3 text-left">Order</th>
                <th class="whitespace-nowrap px-4 py-3 text-left">Reason</th>
                <th class="whitespace-nowrap px-4 py-3 text-right">Amount</th>
                <th class="whitespace-nowrap px-4 py-3 text-center">Status</th>
                <th class="whitespace-nowrap px-4 py-3 text-center">Appeal</th>
                <th class="whitespace-nowrap px-4 py-3 text-right">Imposed</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="fine in fines" :key="fine.id" class="hover:bg-slate-50">
                <td class="px-4 py-3 font-medium text-ink">@{{ fine.writer_username || fine.order?.assigned_writer?.username || '—' }}</td>
                <td class="px-4 py-3 font-mono text-xs text-graphite">{{ fine.order_reference || fine.order?.reference || '—' }}</td>
                <td class="px-4 py-3 text-graphite max-w-xs truncate">{{ fine.reason || '—' }}</td>
                <td class="px-4 py-3 text-right font-semibold text-rose-600">{{ money(fine.amount) }}</td>
                <td class="px-4 py-3 text-center"><StatusPill :label="fine.status?.toLowerCase()" :tone="statusTone(fine.status)" /></td>
                <td class="px-4 py-3 text-center">
                  <StatusPill v-if="fine.has_appeal" label="appeal" tone="warning" />
                  <span v-else class="text-xs text-slate-300">—</span>
                </td>
                <td class="px-4 py-3 text-right text-graphite">{{ fmtDate(fine.imposed_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="fineTotalPages > 1" class="flex items-center justify-between border-t border-slate-200 px-4 py-3">
          <p class="text-xs text-graphite">Page {{ finePage }} of {{ fineTotalPages }} · {{ fineTotal }} fines</p>
          <div class="flex gap-2">
            <button class="focus-ring inline-flex h-8 w-8 items-center justify-center rounded-md border border-slate-200 bg-white disabled:opacity-40" :disabled="finePage <= 1" @click="finePage--"><ChevronLeft class="h-4 w-4" /></button>
            <button class="focus-ring inline-flex h-8 w-8 items-center justify-center rounded-md border border-slate-200 bg-white disabled:opacity-40" :disabled="finePage >= fineTotalPages" @click="finePage++"><ChevronRight class="h-4 w-4" /></button>
          </div>
        </div>
      </div>
    </template>

    <!-- ═══════════════════════════════════════════════════════════════════════ -->
    <!-- WALLETS TAB                                                            -->
    <!-- ═══════════════════════════════════════════════════════════════════════ -->
    <template v-else-if="tab === 'wallets'">
      <div class="rounded-xl border border-slate-200 bg-white">
        <div class="flex flex-wrap items-center gap-3 border-b border-slate-200 px-4 py-3">
          <div class="flex items-center gap-2 text-sm font-semibold text-ink">
            <Wallet class="h-4 w-4 text-signal" /> All Wallets
          </div>
          <div class="ml-auto flex flex-wrap gap-2">
            <input
              v-model="walletSearch"
              class="focus-ring h-9 rounded-lg border border-slate-200 bg-slate-50 px-3 text-xs"
              placeholder="Search user…"
              type="search"
            />
            <select v-model="walletType" class="focus-ring h-9 rounded-lg border border-slate-200 bg-white px-2 text-xs">
              <option value="all">All types</option>
              <option value="client">Client</option>
              <option value="writer">Writer</option>
              <option value="system">System</option>
            </select>
            <select v-model="walletWebsite" class="focus-ring h-9 rounded-lg border border-slate-200 bg-white px-2 text-xs">
              <option value="">All websites</option>
              <option v-for="ws in websitesStore.list" :key="ws.id" :value="ws.id">{{ ws.name || ws.domain }}</option>
            </select>
            <button class="focus-ring h-9 rounded-lg border border-slate-200 bg-white px-2" @click="loadWallets">
              <RefreshCw class="h-3.5 w-3.5" />
            </button>
          </div>
        </div>

        <div v-if="walletsLoading" class="py-16"><LoadingSpinner label="Loading wallets…" /></div>
        <div v-else-if="!wallets.length" class="py-16 text-center text-sm text-graphite">No wallets found.</div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-full text-sm">
            <thead class="bg-slate-50 text-xs font-semibold uppercase tracking-wide text-graphite">
              <tr>
                <th class="whitespace-nowrap px-4 py-3 text-left">Owner</th>
                <th class="whitespace-nowrap px-4 py-3 text-left">Website</th>
                <th class="whitespace-nowrap px-4 py-3 text-left">Type</th>
                <th class="whitespace-nowrap px-4 py-3 text-right">Available</th>
                <th class="whitespace-nowrap px-4 py-3 text-right">Pending</th>
                <th class="whitespace-nowrap px-4 py-3 text-right">Total in</th>
                <th class="whitespace-nowrap px-4 py-3 text-right">Total out</th>
                <th class="whitespace-nowrap px-4 py-3 text-center">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="w in wallets" :key="w.id" class="hover:bg-slate-50">
                <td class="px-4 py-3">
                  <p class="font-medium text-ink">{{ w.owner_username || w.owner?.username || '—' }}</p>
                  <p class="text-xs text-graphite">{{ w.owner_email || w.owner?.email || '' }}</p>
                </td>
                <td class="px-4 py-3">
                  <span class="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700">
                    {{ w.website_name || websitesStore.nameById(w.website_id) }}
                  </span>
                </td>
                <td class="px-4 py-3">
                  <StatusPill :label="(w.wallet_type || '—').toLowerCase()" :tone="w.wallet_type === 'client' ? 'success' : w.wallet_type === 'writer' ? 'neutral' : 'warning'" />
                </td>
                <td class="px-4 py-3 text-right font-semibold text-ink">{{ money(w.available_balance) }}</td>
                <td class="px-4 py-3 text-right text-amber-600">{{ money(w.pending_balance) }}</td>
                <td class="px-4 py-3 text-right text-emerald-700">
                  <ArrowDownLeft class="inline h-3 w-3" /> {{ money(w.total_credited) }}
                </td>
                <td class="px-4 py-3 text-right text-rose-600">
                  <ArrowUpRight class="inline h-3 w-3" /> {{ money(w.total_debited) }}
                </td>
                <td class="px-4 py-3 text-center">
                  <StatusPill :label="(w.status || 'active').toLowerCase()" :tone="statusTone(w.status || 'active')" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="walletTotalPages > 1" class="flex items-center justify-between border-t border-slate-200 px-4 py-3">
          <p class="text-xs text-graphite">Page {{ walletPage }} of {{ walletTotalPages }} · {{ walletTotal }} wallets</p>
          <div class="flex gap-2">
            <button class="focus-ring inline-flex h-8 w-8 items-center justify-center rounded-md border border-slate-200 bg-white disabled:opacity-40" :disabled="walletPage <= 1" @click="walletPage--"><ChevronLeft class="h-4 w-4" /></button>
            <button class="focus-ring inline-flex h-8 w-8 items-center justify-center rounded-md border border-slate-200 bg-white disabled:opacity-40" :disabled="walletPage >= walletTotalPages" @click="walletPage++"><ChevronRight class="h-4 w-4" /></button>
          </div>
        </div>
      </div>
    </template>

    <!-- ═══════════════════════════════════════════════════════════════════════ -->
    <!-- ADVANCES TAB                                                           -->
    <!-- ═══════════════════════════════════════════════════════════════════════ -->
    <template v-else-if="tab === 'advances'">
      <div class="rounded-xl border border-slate-200 bg-white">
        <div class="flex flex-wrap items-center gap-3 border-b border-slate-200 px-4 py-3">
          <div class="flex items-center gap-2 text-sm font-semibold text-ink">
            <CircleDollarSign class="h-4 w-4 text-signal" /> Writer Advances
          </div>
          <div class="ml-auto flex gap-2">
            <select v-model="advanceStatus" class="focus-ring h-9 rounded-lg border border-slate-200 bg-white px-2 text-xs">
              <option value="all">All statuses</option>
              <option value="PENDING">Pending</option>
              <option value="APPROVED">Approved</option>
              <option value="REJECTED">Rejected</option>
              <option value="RECOVERED">Recovered</option>
            </select>
            <button class="focus-ring h-9 rounded-lg border border-slate-200 bg-white px-2" @click="loadAdvances">
              <RefreshCw class="h-3.5 w-3.5" />
            </button>
          </div>
        </div>

        <div v-if="advancesLoading" class="py-16"><LoadingSpinner label="Loading advances…" /></div>
        <div v-else-if="!advances.length" class="py-16 text-center text-sm text-graphite">No advance requests found.</div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-full text-sm">
            <thead class="bg-slate-50 text-xs font-semibold uppercase tracking-wide text-graphite">
              <tr>
                <th class="whitespace-nowrap px-4 py-3 text-left">Writer</th>
                <th class="whitespace-nowrap px-4 py-3 text-right">Requested</th>
                <th class="whitespace-nowrap px-4 py-3 text-right">Approved</th>
                <th class="whitespace-nowrap px-4 py-3 text-right">Recovered</th>
                <th class="whitespace-nowrap px-4 py-3 text-right">Outstanding</th>
                <th class="whitespace-nowrap px-4 py-3 text-center">Status</th>
                <th class="whitespace-nowrap px-4 py-3 text-right">Date</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="adv in advances" :key="adv.id" class="hover:bg-slate-50">
                <td class="px-4 py-3 font-medium text-ink">@{{ adv.writer_username || adv.writer?.username || '—' }}</td>
                <td class="px-4 py-3 text-right text-graphite">{{ money(adv.requested_amount) }}</td>
                <td class="px-4 py-3 text-right text-emerald-700">{{ adv.approved_amount ? money(adv.approved_amount) : '—' }}</td>
                <td class="px-4 py-3 text-right text-ink">{{ money(adv.recovered_amount) }}</td>
                <td class="px-4 py-3 text-right font-semibold" :class="Number(adv.outstanding_balance) > 0 ? 'text-amber-600' : 'text-graphite'">
                  {{ money(adv.outstanding_balance) }}
                </td>
                <td class="px-4 py-3 text-center"><StatusPill :label="adv.status?.toLowerCase()" :tone="statusTone(adv.status)" /></td>
                <td class="px-4 py-3 text-right text-graphite">{{ fmtDate(adv.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="advanceTotalPages > 1" class="flex items-center justify-between border-t border-slate-200 px-4 py-3">
          <p class="text-xs text-graphite">Page {{ advancePage }} of {{ advanceTotalPages }} · {{ advanceTotal }} records</p>
          <div class="flex gap-2">
            <button class="focus-ring inline-flex h-8 w-8 items-center justify-center rounded-md border border-slate-200 bg-white disabled:opacity-40" :disabled="advancePage <= 1" @click="advancePage--"><ChevronLeft class="h-4 w-4" /></button>
            <button class="focus-ring inline-flex h-8 w-8 items-center justify-center rounded-md border border-slate-200 bg-white disabled:opacity-40" :disabled="advancePage >= advanceTotalPages" @click="advancePage++"><ChevronRight class="h-4 w-4" /></button>
          </div>
        </div>
      </div>
    </template>

  </div>
</template>
