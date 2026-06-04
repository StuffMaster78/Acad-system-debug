<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  AlertTriangle,
  ArrowRight,
  Building2,
  CheckCircle2,
  Clock,
  ClipboardList,
  CreditCard,
  FileText,
  Headphones,
  History,
  RefreshCw,
  Search,
  ShieldAlert,
  Sparkles,
  UserCheck,
  Users,
} from "@lucide/vue";
import BaseModal from "@/components/ui/BaseModal.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import {
  operationsCommandApi,
  type OperationsCommandEvent,
  type OperationsCommandItem,
  type OperationsCommandResponse,
  type OperationsPriority,
} from "@/api/operationsCommand";
import { useAuthStore } from "@/stores/auth";
import { useUiStore } from "@/stores/ui";
import { useWebsitesStore } from "@/stores/websites";

const auth = useAuthStore();
const ui = useUiStore();
const route = useRoute();
const router = useRouter();
const websites = useWebsitesStore();

const isLoading = ref(false);
const error = ref("");
const generatedAt = ref<string | null>(null);
const response = ref<OperationsCommandResponse | null>(null);
const selectedWebsiteId = ref("");
const selectedDomain = ref("all");
const selectedPriority = ref("all");
const selectedOwner = ref<"all" | "mine" | "unassigned">("all");
const query = ref("");
const isMutating = ref(false);
const isHistoryLoading = ref(false);
const actionDialog = ref<{
  open: boolean;
  action: "snooze" | "resolve";
  item: OperationsCommandItem | null;
  note: string;
  snooze_hours: number;
}>({
  open: false,
  action: "resolve",
  item: null,
  note: "",
  snooze_hours: 24,
});
const historyDialog = ref<{
  open: boolean;
  item: OperationsCommandItem | null;
  events: OperationsCommandEvent[];
}>({
  open: false,
  item: null,
  events: [],
});

const isSuperadmin = computed(() => auth.role === "superadmin");
const routePrefix = computed(() => (route.path.startsWith("/superadmin") ? "/superadmin" : "/admin"));

const summary = computed(() => response.value?.summary ?? {
  critical: 0,
  high: 0,
  medium: 0,
  low: 0,
  total: 0,
  orders_at_risk: 0,
  payments_need_attention: 0,
  writer_reviews: 0,
  cms_alerts: 0,
  support_escalations: 0,
  assigned: 0,
  unassigned: 0,
});

const domains = computed(() => {
  const values = new Set(response.value?.items.map((item) => item.domain) ?? []);
  return ["all", ...Array.from(values).sort()];
});

const filteredItems = computed(() => {
  const needle = query.value.trim().toLowerCase();
  return (response.value?.items ?? []).filter((item) => {
    if (selectedDomain.value !== "all" && item.domain !== selectedDomain.value) return false;
    if (selectedPriority.value !== "all" && item.priority !== selectedPriority.value) return false;
    if (selectedOwner.value === "mine" && item.state?.assigned_to_id !== auth.user?.id) return false;
    if (selectedOwner.value === "unassigned" && item.state?.assigned_to_id) return false;
    if (!needle) return true;
    return [
      item.title,
      item.description,
      item.entity.label,
      item.website?.name,
      item.website?.domain,
      item.domain,
      item.priority,
    ].some((value) => String(value ?? "").toLowerCase().includes(needle));
  });
});

const priorityOptions: Array<"all" | OperationsPriority> = ["all", "critical", "high", "medium", "low"];

const summaryTiles = computed(() => [
  { label: "Critical", value: summary.value.critical, tone: "critical", icon: ShieldAlert },
  { label: "High", value: summary.value.high, tone: "high", icon: AlertTriangle },
  { label: "Payments", value: summary.value.payments_need_attention, tone: "payment", icon: CreditCard },
  { label: "Total", value: summary.value.total, tone: "neutral", icon: ClipboardList },
]);

const pulseTiles = computed(() => [
  { label: "Orders", value: summary.value.orders_at_risk },
  { label: "Writers", value: summary.value.writer_reviews },
  { label: "Assigned", value: summary.value.assigned },
  { label: "Unassigned", value: summary.value.unassigned },
  { label: "CMS", value: summary.value.cms_alerts },
  { label: "Support", value: summary.value.support_escalations },
]);

const toneClasses: Record<string, string> = {
  critical: "border-rose-200 bg-rose-50 text-rose-900",
  high: "border-amber-200 bg-amber-50 text-amber-900",
  payment: "border-sky-200 bg-sky-50 text-sky-900",
  neutral: "border-slate-200 bg-white text-ink",
};

const priorityClasses: Record<OperationsPriority, string> = {
  critical: "border-rose-200 bg-rose-50 text-rose-700",
  high: "border-amber-200 bg-amber-50 text-amber-800",
  medium: "border-sky-200 bg-sky-50 text-sky-700",
  low: "border-slate-200 bg-slate-50 text-slate-700",
};

const stateClasses: Record<string, string> = {
  active: "border-slate-200 bg-slate-50 text-slate-700",
  acknowledged: "border-emerald-200 bg-emerald-50 text-emerald-700",
  snoozed: "border-indigo-200 bg-indigo-50 text-indigo-700",
  resolved: "border-slate-200 bg-slate-50 text-slate-500",
};

const domainIcons = {
  orders: ClipboardList,
  payments: CreditCard,
  writers: Users,
  cms: FileText,
  support: Headphones,
  classes: Building2,
  special_orders: Sparkles,
};

const ACTION_LABELS: Record<string, string> = {
  route_to_staffing:  "Route to Staffing",
  assign_writer:      "Assign Writer",
  release_to_pool:    "Release to Pool",
  submit_for_qa:      "Submit to QA",
  approve_delivery:   "Approve Delivery",
  return_to_writer:   "Return to Writer",
  approve_order:      "Approve Order",
  request_revision:   "Request Revision",
  raise_dispute:      "Raise Dispute",
  cancel_order:       "Cancel",
  archive_order:      "Archive",
};

function domainLabel(value: string) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function actionLabel(action: string) {
  return ACTION_LABELS[action] ?? action.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
}

function dateLabel(value: string | null) {
  if (!value) return "Not set";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function actionUrl(item: OperationsCommandItem) {
  if (routePrefix.value === "/superadmin") return item.action_url.replace(/^\/admin/, "/superadmin");
  return item.action_url;
}

function openItem(item: OperationsCommandItem) {
  router.push(actionUrl(item)).catch(() => undefined);
}

function selectedWebsiteForAction(item: OperationsCommandItem) {
  return item.website?.id ?? (selectedWebsiteId.value ? Number(selectedWebsiteId.value) : null);
}

function openActionDialog(item: OperationsCommandItem, action: "snooze" | "resolve") {
  actionDialog.value = {
    open: true,
    action,
    item,
    note: item.state?.note ?? "",
    snooze_hours: action === "snooze" ? 24 : 0,
  };
}

function closeActionDialog() {
  actionDialog.value.open = false;
}

function closeHistoryDialog() {
  historyDialog.value.open = false;
}

async function openHistoryDialog(item: OperationsCommandItem) {
  historyDialog.value = { open: true, item, events: [] };
  isHistoryLoading.value = true;
  try {
    const { data } = await operationsCommandApi.history(item.id);
    historyDialog.value.events = data.events;
  } catch {
    ui.toast("Unable to load item history.", "error");
  } finally {
    isHistoryLoading.value = false;
  }
}

async function acknowledgeItem(item: OperationsCommandItem) {
  isMutating.value = true;
  try {
    await operationsCommandApi.act({
      item_id: item.id,
      action: "acknowledge",
      domain: item.domain,
      website_id: selectedWebsiteForAction(item),
      entity: item.entity,
    });
    ui.toast("Item acknowledged.", "success");
    await loadCommandCenter();
  } catch {
    ui.toast("Unable to acknowledge item.", "error");
  } finally {
    isMutating.value = false;
  }
}

async function setItemAssignment(item: OperationsCommandItem, action: "claim" | "release") {
  isMutating.value = true;
  try {
    await operationsCommandApi.act({
      item_id: item.id,
      action,
      domain: item.domain,
      website_id: selectedWebsiteForAction(item),
      entity: item.entity,
    });
    ui.toast(action === "claim" ? "Item claimed." : "Item released.", "success");
    await loadCommandCenter();
  } catch {
    ui.toast(action === "claim" ? "Unable to claim item." : "Unable to release item.", "error");
  } finally {
    isMutating.value = false;
  }
}

async function submitItemAction() {
  const item = actionDialog.value.item;
  if (!item) return;
  isMutating.value = true;
  try {
    await operationsCommandApi.act({
      item_id: item.id,
      action: actionDialog.value.action,
      domain: item.domain,
      website_id: selectedWebsiteForAction(item),
      entity: item.entity,
      note: actionDialog.value.note,
      snooze_hours: actionDialog.value.action === "snooze" ? actionDialog.value.snooze_hours : undefined,
    });
    ui.toast(actionDialog.value.action === "snooze" ? "Item snoozed." : "Item resolved.", "success");
    closeActionDialog();
    await loadCommandCenter();
  } catch {
    ui.toast("Unable to update item.", "error");
  } finally {
    isMutating.value = false;
  }
}

async function loadCommandCenter() {
  isLoading.value = true;
  error.value = "";
  try {
    const websiteId = selectedWebsiteId.value ? Number(selectedWebsiteId.value) : null;
    const { data } = await operationsCommandApi.get({ website_id: websiteId });
    response.value = data;
    generatedAt.value = data.generated_at;
  } catch {
    error.value = "Unable to load the operations command center.";
  } finally {
    isLoading.value = false;
  }
}

// ── Expanded card state ──────────────────────────────────────────────────────
const expandedItemId = ref<string | null>(null);
function toggleExpand(id: string) {
  expandedItemId.value = expandedItemId.value === id ? null : id;
}

// ── Countdown helper ─────────────────────────────────────────────────────────
function countdown(dueAt: string | null): { label: string; cls: string } {
  if (!dueAt) return { label: "", cls: "" };
  const h = (new Date(dueAt).getTime() - Date.now()) / 3_600_000;
  if (h < 0) return { label: `OVERDUE ${Math.round(Math.abs(h))}h`, cls: "text-rose-600 font-bold" };
  if (h < 2)  return { label: `${Math.round(h * 60)}m left`, cls: "text-rose-500 font-semibold" };
  if (h < 24) return { label: `${Math.round(h)}h left`, cls: "text-amber-600 font-semibold" };
  return { label: `${Math.round(h / 24)}d left`, cls: "text-graphite" };
}

// ── Priority left border ─────────────────────────────────────────────────────
const priorityBorder: Record<string, string> = {
  critical: "border-l-4 border-l-rose-500",
  high:     "border-l-4 border-l-amber-400",
  medium:   "border-l-4 border-l-sky-400",
  low:      "border-l-4 border-slate-200",
};

// ── Domain breakdown for sidebar ─────────────────────────────────────────────
const domainBreakdown = computed(() => {
  const counts: Record<string, number> = {};
  for (const item of response.value?.items ?? []) {
    if (item.state?.status === "resolved") continue;
    counts[item.domain] = (counts[item.domain] ?? 0) + 1;
  }
  return Object.entries(counts).sort((a, b) => b[1] - a[1]);
});

// ── Active-only filter toggle ────────────────────────────────────────────────
const showResolved = ref(false);
const enhancedFilteredItems = computed(() => {
  return filteredItems.value.filter(item =>
    showResolved.value ? true : item.state?.status !== "resolved"
  );
});

// ── Triage dropdown state ────────────────────────────────────────────────────
const triageOpenId = ref<string | null>(null);
function toggleTriage(id: string) {
  triageOpenId.value = triageOpenId.value === id ? null : id;
}

// ── Health score ─────────────────────────────────────────────────────────────
const healthScore = computed(() => {
  const total = summary.value.total;
  if (!total) return 100;
  const weight = summary.value.critical * 4 + summary.value.high * 2 + summary.value.medium;
  return Math.max(0, Math.round(100 - (weight / (total * 4)) * 100));
});

watch(selectedWebsiteId, () => {
  loadCommandCenter().catch(() => undefined);
});

onMounted(async () => {
  if (isSuperadmin.value) await websites.ensure();
  await loadCommandCenter();
});
</script>

<template>
  <div class="min-h-screen bg-slate-50/60">

    <!-- ── Page header ──────────────────────────────────────────────────── -->
    <div class="sticky top-0 z-20 border-b border-slate-200 bg-white/95 backdrop-blur-sm px-6 py-4">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 class="text-lg font-bold text-ink">Operations Command Center</h1>
          <p class="mt-0.5 text-xs text-graphite">
            {{ response?.scope.is_cross_tenant ? "All websites" : response?.scope.website_name || "Current website" }}
            &middot; Updated {{ dateLabel(generatedAt) }}
          </p>
        </div>
        <div class="flex items-center gap-2">
          <select v-if="isSuperadmin" v-model="selectedWebsiteId"
            class="focus-ring h-9 rounded-md border border-slate-200 bg-white px-3 text-sm">
            <option value="">All websites</option>
            <option v-for="site in websites.list" :key="site.id" :value="String(site.id)">
              {{ websites.labelById(site.id) }}
            </option>
          </select>
          <button class="focus-ring inline-flex h-9 items-center gap-1.5 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-graphite hover:text-ink"
            :disabled="isLoading" @click="loadCommandCenter">
            <RefreshCw class="h-4 w-4" :class="{ 'animate-spin': isLoading }" /> Refresh
          </button>
        </div>
      </div>
    </div>

    <div class="px-6 py-5 space-y-5">

      <!-- ── Health + KPI strip ────────────────────────────────────────── -->
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <!-- Health bar -->
        <div class="mb-4 flex items-center justify-between gap-4">
          <div class="flex items-center gap-2">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">System health</span>
            <span class="text-sm font-bold" :class="healthScore >= 80 ? 'text-signal' : healthScore >= 50 ? 'text-amber-600' : 'text-rose-600'">
              {{ healthScore }}%
            </span>
          </div>
          <span class="text-xs text-graphite">{{ summary.total }} active items</span>
        </div>
        <div class="mb-4 h-2 w-full overflow-hidden rounded-full bg-slate-100">
          <div class="flex h-full rounded-full overflow-hidden">
            <div class="bg-rose-500 transition-all" :style="{ width: `${summary.total ? (summary.critical / summary.total) * 100 : 0}%` }" />
            <div class="bg-amber-400 transition-all" :style="{ width: `${summary.total ? (summary.high / summary.total) * 100 : 0}%` }" />
            <div class="bg-sky-400 transition-all" :style="{ width: `${summary.total ? (summary.medium / summary.total) * 100 : 0}%` }" />
            <div class="bg-slate-200 flex-1 transition-all" />
          </div>
        </div>
        <!-- KPI tiles -->
        <div class="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-8">
          <button v-for="p in (['critical','high','medium','low'] as const)" :key="p"
            class="rounded-lg border px-3 py-2.5 text-left transition-all hover:shadow-sm"
            :class="[
              selectedPriority === p ? priorityClasses[p] : 'border-slate-200 bg-slate-50',
              selectedPriority === p ? 'ring-1 ring-inset' : '',
            ]"
            @click="selectedPriority = selectedPriority === p ? 'all' : p">
            <p class="text-[10px] font-semibold uppercase tracking-wide opacity-70 capitalize">{{ p }}</p>
            <p class="mt-1 text-2xl font-bold">{{ summary[p] }}</p>
          </button>
          <div class="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5">
            <p class="text-[10px] font-semibold uppercase tracking-wide text-graphite">Payments</p>
            <p class="mt-1 text-2xl font-bold text-sky-700">{{ summary.payments_need_attention }}</p>
          </div>
          <div class="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5">
            <p class="text-[10px] font-semibold uppercase tracking-wide text-graphite">Unassigned</p>
            <p class="mt-1 text-2xl font-bold text-graphite">{{ summary.unassigned }}</p>
          </div>
          <div class="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5">
            <p class="text-[10px] font-semibold uppercase tracking-wide text-graphite">Support</p>
            <p class="mt-1 text-2xl font-bold text-graphite">{{ summary.support_escalations }}</p>
          </div>
          <div class="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5">
            <p class="text-[10px] font-semibold uppercase tracking-wide text-graphite">Writers</p>
            <p class="mt-1 text-2xl font-bold text-graphite">{{ summary.writer_reviews }}</p>
          </div>
        </div>
      </div>

      <p v-if="error" class="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">{{ error }}</p>

      <!-- ── Main 2-col ────────────────────────────────────────────────── -->
      <div class="grid gap-5 xl:grid-cols-[1fr_280px]">

        <!-- Queue -->
        <div class="space-y-3">

          <!-- Filter bar -->
          <div class="flex flex-wrap items-center gap-2 rounded-xl border border-slate-200 bg-white p-3">
            <div class="relative flex-1 min-w-40">
              <Search class="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
              <input v-model="query" type="search" placeholder="Search items..."
                class="focus-ring h-8 w-full rounded-md border border-slate-200 pl-8 pr-2 text-sm" />
            </div>
            <select v-model="selectedDomain" class="focus-ring h-8 rounded-md border border-slate-200 bg-white px-2 text-sm">
              <option v-for="d in domains" :key="d" :value="d">{{ d === 'all' ? 'All domains' : domainLabel(d) }}</option>
            </select>
            <select v-model="selectedOwner" class="focus-ring h-8 rounded-md border border-slate-200 bg-white px-2 text-sm">
              <option value="all">All owners</option>
              <option value="mine">Mine</option>
              <option value="unassigned">Unassigned</option>
            </select>
            <label class="flex items-center gap-1.5 text-xs text-graphite cursor-pointer ml-auto">
              <input v-model="showResolved" type="checkbox" class="rounded" />
              Show resolved
            </label>
            <span class="text-xs text-graphite">{{ enhancedFilteredItems.length }} items</span>
          </div>

          <!-- Loading skeleton -->
          <div v-if="isLoading" class="space-y-2">
            <div v-for="n in 4" :key="n" class="h-16 animate-pulse rounded-xl bg-slate-100" />
          </div>

          <!-- Empty state -->
          <div v-else-if="!enhancedFilteredItems.length" class="rounded-xl border border-dashed border-slate-200 py-16 text-center">
            <ShieldAlert class="mx-auto h-8 w-8 text-slate-300" />
            <p class="mt-3 text-sm font-semibold text-ink">Queue is clear</p>
            <p class="mt-1 text-xs text-graphite">No operational items match the current filters.</p>
          </div>

          <!-- Item cards -->
          <div v-else class="space-y-2">
            <article
              v-for="item in enhancedFilteredItems"
              :key="item.id"
              class="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden transition-shadow hover:shadow-md"
              :class="priorityBorder[item.priority]"
            >
              <!-- Compact row (always visible) -->
              <div class="flex items-center gap-3 px-4 py-3 cursor-pointer select-none"
                @click="toggleExpand(item.id)">
                <!-- Domain icon -->
                <component
                  :is="domainIcons[item.domain as keyof typeof domainIcons] || ClipboardList"
                  class="h-4 w-4 shrink-0 text-graphite"
                />
                <!-- Title + meta -->
                <div class="min-w-0 flex-1">
                  <div class="flex flex-wrap items-center gap-2">
                    <p class="truncate text-sm font-semibold text-ink">{{ item.title }}</p>
                    <span v-if="item.state?.status && item.state.status !== 'active'"
                      class="rounded-full px-2 py-0.5 text-[10px] font-semibold capitalize"
                      :class="stateClasses[item.state.status]">
                      {{ item.state.status }}
                    </span>
                    <span v-if="item.state?.assigned_to"
                      class="flex items-center gap-0.5 rounded-full bg-violet-50 px-2 py-0.5 text-[10px] font-medium text-violet-700">
                      <UserCheck class="h-2.5 w-2.5" />{{ item.state.assigned_to }}
                    </span>
                  </div>
                  <p class="mt-0.5 flex flex-wrap items-center gap-2 text-xs text-graphite">
                    <span class="capitalize">{{ domainLabel(item.domain) }}</span>
                    <span v-if="item.website" class="text-slate-400">{{ item.website.name }}</span>
                  </p>
                </div>
                <!-- Due countdown -->
                <div class="shrink-0 text-right">
                  <p v-if="item.due_at" class="text-xs" :class="countdown(item.due_at).cls">
                    {{ countdown(item.due_at).label }}
                  </p>
                  <p class="text-[10px] text-slate-400">{{ dateLabel(item.due_at) }}</p>
                </div>
                <!-- Primary actions (always visible) -->
                <div class="flex shrink-0 items-center gap-1.5 pl-2" @click.stop>
                  <!-- Triage dropdown -->
                  <div class="relative">
                    <button
                      class="focus-ring flex h-8 items-center gap-1 rounded-md border border-slate-200 bg-white px-2 text-xs font-semibold text-graphite hover:border-slate-300"
                      :disabled="isMutating"
                      @click="toggleTriage(item.id)">
                      <Clock class="h-3.5 w-3.5" /> Triage
                    </button>
                    <div v-if="triageOpenId === item.id"
                      class="absolute right-0 top-full z-30 mt-1 w-44 rounded-xl border border-slate-200 bg-white shadow-xl">
                      <button class="flex w-full items-center gap-2 rounded-t-xl px-3 py-2 text-xs hover:bg-slate-50"
                        @click="acknowledgeItem(item); triageOpenId = null">
                        <CheckCircle2 class="h-3.5 w-3.5 text-signal" /> Acknowledge
                      </button>
                      <button class="flex w-full items-center gap-2 px-3 py-2 text-xs hover:bg-slate-50"
                        @click="openActionDialog(item, 'snooze'); triageOpenId = null">
                        <Clock class="h-3.5 w-3.5 text-sky-500" /> Snooze
                      </button>
                      <button class="flex w-full items-center gap-2 px-3 py-2 text-xs hover:bg-slate-50"
                        @click="openHistoryDialog(item); triageOpenId = null">
                        <History class="h-3.5 w-3.5 text-slate-400" /> History
                      </button>
                      <button class="flex w-full items-center gap-2 rounded-b-xl px-3 py-2 text-xs text-emerald-700 hover:bg-emerald-50"
                        @click="openActionDialog(item, 'resolve'); triageOpenId = null">
                        <CheckCircle2 class="h-3.5 w-3.5" /> Resolve
                      </button>
                    </div>
                  </div>
                  <!-- Claim / Release -->
                  <button
                    v-if="item.state?.assigned_to_id === auth.user?.id"
                    class="focus-ring h-8 rounded-md border border-slate-200 bg-white px-2 text-xs font-semibold text-graphite"
                    :disabled="isMutating" @click="setItemAssignment(item, 'release')">
                    Release
                  </button>
                  <button v-else
                    class="focus-ring h-8 rounded-md border border-violet-200 bg-violet-50 px-2 text-xs font-semibold text-violet-700"
                    :disabled="isMutating" @click="setItemAssignment(item, 'claim')">
                    Claim
                  </button>
                  <!-- Open CTA -->
                  <button
                    class="focus-ring flex h-8 items-center gap-1 rounded-md bg-ink px-3 text-xs font-semibold text-white hover:bg-ink/90"
                    @click="openItem(item)">
                    {{ item.action_label }} <ArrowRight class="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>

              <!-- Expanded details -->
              <div v-if="expandedItemId === item.id"
                class="border-t border-slate-100 bg-slate-50/60 px-4 py-3 space-y-3">
                <p class="text-sm leading-6 text-graphite">{{ item.description }}</p>
                <div v-if="item.state?.note" class="rounded-md border border-slate-200 bg-white px-3 py-2 text-xs text-slate-700">
                  <span class="font-semibold">Note:</span> {{ item.state.note }}
                </div>
                <!-- Meta chips -->
                <div class="flex flex-wrap gap-1.5">
                  <span v-for="m in item.meta" :key="m.label"
                    class="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs text-slate-600">
                    {{ m.label }}: {{ m.value }}
                  </span>
                </div>
                <!-- Available actions -->
                <div v-if="item.available_actions?.length" class="flex flex-wrap gap-1.5">
                  <span class="text-xs font-semibold text-graphite">Actions:</span>
                  <span v-for="action in item.available_actions" :key="action"
                    class="rounded-full border border-signal/30 bg-signal/5 px-2.5 py-0.5 text-xs font-medium text-signal">
                    {{ actionLabel(action) }}
                  </span>
                </div>
              </div>
            </article>
          </div>
        </div>

        <!-- Sidebar -->
        <aside class="space-y-4">

          <!-- Domain breakdown -->
          <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <h3 class="text-xs font-bold uppercase tracking-wide text-graphite mb-3">By domain</h3>
            <div class="space-y-1.5">
              <button
                v-for="[domain, count] in domainBreakdown"
                :key="domain"
                class="flex w-full items-center justify-between rounded-lg px-3 py-2 text-sm transition-colors"
                :class="selectedDomain === domain
                  ? 'bg-ink text-white'
                  : 'hover:bg-slate-50 text-graphite'"
                @click="selectedDomain = selectedDomain === domain ? 'all' : domain"
              >
                <div class="flex items-center gap-2">
                  <component :is="domainIcons[domain as keyof typeof domainIcons] || ClipboardList" class="h-4 w-4" />
                  <span class="capitalize">{{ domainLabel(domain) }}</span>
                </div>
                <span class="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-bold text-slate-600"
                  :class="selectedDomain === domain ? 'bg-white/20 text-white' : ''">
                  {{ count }}
                </span>
              </button>
              <button v-if="selectedDomain !== 'all'"
                class="flex w-full items-center justify-center gap-1 rounded-lg border border-dashed border-slate-200 py-1.5 text-xs text-graphite hover:bg-slate-50"
                @click="selectedDomain = 'all'">
                Clear filter
              </button>
            </div>
          </div>

          <!-- Quick assignments -->
          <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <h3 class="text-xs font-bold uppercase tracking-wide text-graphite mb-3">Workload</h3>
            <div class="space-y-2">
              <div class="flex items-center justify-between text-sm">
                <span class="text-graphite">Unassigned</span>
                <button class="font-semibold text-amber-600"
                  @click="selectedOwner = selectedOwner === 'unassigned' ? 'all' : 'unassigned'">
                  {{ summary.unassigned }}
                </button>
              </div>
              <div class="flex items-center justify-between text-sm">
                <span class="text-graphite">Assigned to me</span>
                <button class="font-semibold text-signal"
                  @click="selectedOwner = selectedOwner === 'mine' ? 'all' : 'mine'">
                  {{ summary.assigned }}
                </button>
              </div>
              <div class="flex items-center justify-between text-sm">
                <span class="text-graphite">Orders at risk</span>
                <span class="font-semibold text-rose-600">{{ summary.orders_at_risk }}</span>
              </div>
              <div class="flex items-center justify-between text-sm">
                <span class="text-graphite">CMS alerts</span>
                <span class="font-semibold text-graphite">{{ summary.cms_alerts }}</span>
              </div>
            </div>
          </div>

          <!-- Priority quick-filter -->
          <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <h3 class="text-xs font-bold uppercase tracking-wide text-graphite mb-3">Priority filter</h3>
            <div class="space-y-1.5">
              <button v-for="p in (['critical','high','medium','low'] as const)" :key="p"
                class="flex w-full items-center justify-between rounded-lg px-3 py-2 text-sm font-medium transition-colors"
                :class="selectedPriority === p ? priorityClasses[p] : 'hover:bg-slate-50 text-graphite'"
                @click="selectedPriority = selectedPriority === p ? 'all' : p">
                <span class="capitalize">{{ p }}</span>
                <span>{{ summary[p] }}</span>
              </button>
            </div>
          </div>

        </aside>
      </div>
    </div>
  </div>

  <!-- Triage click-outside handler -->
  <div v-if="triageOpenId" class="fixed inset-0 z-20" @click="triageOpenId = null" />

  <!-- Snooze / Resolve modal -->
  <BaseModal
    :open="actionDialog.open"
    :title="actionDialog.action === 'snooze' ? 'Snooze item' : 'Resolve item'"
    :description="actionDialog.item?.title || ''"
    size="md"
    @close="closeActionDialog"
  >
    <form class="space-y-4" @submit.prevent="submitItemAction">
      <label v-if="actionDialog.action === 'snooze'" class="block">
        <span class="text-sm font-medium text-ink">Snooze for</span>
        <select v-model.number="actionDialog.snooze_hours"
          class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm">
          <option :value="4">4 hours</option>
          <option :value="24">1 day</option>
          <option :value="72">3 days</option>
          <option :value="168">1 week</option>
        </select>
      </label>
      <label class="block">
        <span class="text-sm font-medium text-ink">Note</span>
        <textarea v-model="actionDialog.note" rows="3"
          class="focus-ring mt-1 min-h-24 w-full resize-none rounded-md border border-slate-200 px-3 py-2 text-sm"
          :placeholder="actionDialog.action === 'snooze' ? 'Why can this wait?' : 'What was handled?'" />
      </label>
    </form>
    <template #footer>
      <div class="flex justify-end gap-2">
        <button class="focus-ring h-10 rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold"
          @click="closeActionDialog">Cancel</button>
        <button class="focus-ring h-10 rounded-md bg-ink px-4 text-sm font-semibold text-white disabled:opacity-50"
          :disabled="isMutating" @click="submitItemAction">
          {{ actionDialog.action === 'snooze' ? 'Snooze' : 'Mark resolved' }}
        </button>
      </div>
    </template>
  </BaseModal>

  <!-- History modal -->
  <BaseModal
    :open="historyDialog.open"
    title="Item history"
    :description="historyDialog.item?.title || ''"
    size="lg"
    @close="closeHistoryDialog"
  >
    <div v-if="isHistoryLoading" class="py-10 text-center text-sm text-graphite">Loading history...</div>
    <div v-else-if="historyDialog.events.length" class="space-y-2">
      <div v-for="event in historyDialog.events" :key="event.id"
        class="rounded-lg border border-slate-100 px-4 py-3">
        <div class="flex items-start justify-between gap-3">
          <div>
            <p class="text-sm font-semibold text-ink">{{ domainLabel(event.action) }}</p>
            <p class="mt-0.5 text-xs text-graphite">
              {{ event.actor || "System" }}
              <template v-if="event.from_status || event.to_status">
                &rarr; {{ domainLabel(event.to_status || "none") }}
              </template>
            </p>
          </div>
          <span class="text-xs text-graphite whitespace-nowrap">{{ dateLabel(event.created_at) }}</span>
        </div>
        <p v-if="event.note" class="mt-2 rounded-md bg-slate-50 px-3 py-2 text-xs text-slate-700">
          {{ event.note }}
        </p>
      </div>
    </div>
    <div v-else class="py-10 text-center">
      <p class="text-sm font-semibold text-ink">No history yet</p>
      <p class="mt-1 text-xs text-graphite">Actions will appear here as staff work the item.</p>
    </div>
  </BaseModal>
</template>
