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

watch(selectedWebsiteId, () => {
  loadCommandCenter().catch(() => undefined);
});

onMounted(async () => {
  if (isSuperadmin.value) await websites.ensure();
  await loadCommandCenter();
});
</script>

<template>
  <div class="space-y-6">
    <section class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase text-signal">Operations</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Command center</h1>
        <div class="mt-2 flex flex-wrap items-center gap-2 text-sm text-graphite">
          <span>{{ response?.scope.is_cross_tenant ? "All websites" : response?.scope.website_name || "Current website" }}</span>
          <span class="text-slate-300">/</span>
          <span>Updated {{ dateLabel(generatedAt) }}</span>
        </div>
      </div>

      <div class="flex flex-col gap-2 sm:flex-row sm:items-center">
        <select
          v-if="isSuperadmin"
          v-model="selectedWebsiteId"
          class="focus-ring h-11 min-w-56 rounded-md border border-slate-200 bg-white px-3 text-sm"
        >
          <option value="">All websites</option>
          <option v-for="site in websites.list" :key="site.id" :value="String(site.id)">
            {{ websites.labelById(site.id) }}
          </option>
        </select>
        <button
          class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold text-ink"
          type="button"
          :disabled="isLoading"
          @click="loadCommandCenter"
        >
          <RefreshCw class="h-4 w-4" :class="{ 'animate-spin': isLoading }" />
          Refresh
        </button>
      </div>
    </section>

    <p v-if="error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ error }}
    </p>

    <section class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      <div
        v-for="tile in summaryTiles"
        :key="tile.label"
        class="rounded-md border p-4"
        :class="toneClasses[tile.tone]"
      >
        <div class="flex items-center justify-between gap-3">
          <span class="text-sm font-medium">{{ tile.label }}</span>
          <component :is="tile.icon" class="h-5 w-5" />
        </div>
        <p class="mt-3 text-3xl font-semibold">{{ tile.value }}</p>
      </div>
    </section>

    <section class="grid gap-6 xl:grid-cols-[minmax(0,1fr)_320px]">
      <div class="space-y-4">
        <div class="flex flex-col gap-3 rounded-md border border-slate-200 bg-white p-4 lg:flex-row lg:items-center">
          <div class="relative flex-1">
            <Search class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              v-model="query"
              class="focus-ring h-10 w-full rounded-md border border-slate-200 pl-9 pr-3 text-sm"
              type="search"
              placeholder="Search queue"
            >
          </div>
          <select v-model="selectedDomain" class="focus-ring h-10 rounded-md border border-slate-200 bg-white px-3 text-sm">
            <option v-for="domain in domains" :key="domain" :value="domain">
              {{ domain === "all" ? "All domains" : domainLabel(domain) }}
            </option>
          </select>
          <select v-model="selectedPriority" class="focus-ring h-10 rounded-md border border-slate-200 bg-white px-3 text-sm">
            <option v-for="priority in priorityOptions" :key="priority" :value="priority">
              {{ priority === "all" ? "All priority" : domainLabel(priority) }}
            </option>
          </select>
          <select v-model="selectedOwner" class="focus-ring h-10 rounded-md border border-slate-200 bg-white px-3 text-sm">
            <option value="all">All owners</option>
            <option value="mine">Mine</option>
            <option value="unassigned">Unassigned</option>
          </select>
        </div>

        <div v-if="isLoading" class="flex min-h-64 items-center justify-center rounded-md border border-slate-200 bg-white">
          <LoadingSpinner label="Loading operations" />
        </div>

        <div v-else-if="filteredItems.length" class="space-y-3">
          <article
            v-for="item in filteredItems"
            :key="item.id"
            class="rounded-md border border-slate-200 bg-white p-4"
          >
            <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div class="min-w-0">
                <div class="flex flex-wrap items-center gap-2">
                  <span
                    class="inline-flex items-center gap-1 rounded-md border px-2 py-1 text-xs font-semibold"
                    :class="priorityClasses[item.priority]"
                  >
                    {{ domainLabel(item.priority) }}
                  </span>
                  <span class="inline-flex items-center gap-1 rounded-md border border-slate-200 bg-slate-50 px-2 py-1 text-xs font-medium text-slate-700">
                    <component :is="domainIcons[item.domain as keyof typeof domainIcons] || ClipboardList" class="h-3.5 w-3.5" />
                    {{ domainLabel(item.domain) }}
                  </span>
                  <span v-if="item.website" class="text-xs text-graphite">{{ item.website.name }}</span>
                  <span
                    v-if="item.state?.assigned_to"
                    class="inline-flex items-center gap-1 rounded-md border border-violet-200 bg-violet-50 px-2 py-1 text-xs font-medium text-violet-700"
                  >
                    <UserCheck class="h-3.5 w-3.5" />
                    {{ item.state.assigned_to }}
                  </span>
                  <span
                    v-if="item.state?.status && item.state.status !== 'active'"
                    class="inline-flex items-center gap-1 rounded-md border px-2 py-1 text-xs font-medium"
                    :class="stateClasses[item.state.status]"
                  >
                    {{ domainLabel(item.state.status) }}
                  </span>
                </div>
                <h2 class="mt-3 text-lg font-semibold text-ink">{{ item.title }}</h2>
                <p class="mt-1 text-sm leading-6 text-graphite">{{ item.description }}</p>
                <p v-if="item.state?.note" class="mt-2 rounded-md bg-slate-50 px-3 py-2 text-xs leading-5 text-slate-700">
                  {{ item.state.note }}
                </p>
                <div class="mt-3 flex flex-wrap gap-2">
                  <span
                    v-for="meta in item.meta"
                    :key="`${item.id}-${meta.label}`"
                    class="rounded-md bg-slate-50 px-2.5 py-1 text-xs text-slate-700"
                  >
                    {{ meta.label }}: {{ meta.value }}
                  </span>
                  <span class="rounded-md bg-slate-50 px-2.5 py-1 text-xs text-slate-700">
                    Due: {{ dateLabel(item.due_at) }}
                  </span>
                  <span class="rounded-md bg-slate-50 px-2.5 py-1 text-xs text-slate-700">
                    Score: {{ item.score }}
                  </span>
                </div>
                <div v-if="item.available_actions?.length" class="mt-2 flex flex-wrap gap-1.5">
                  <span
                    v-for="action in item.available_actions"
                    :key="`${item.id}-action-${action}`"
                    class="rounded-full border border-indigo-200 bg-indigo-50 px-2.5 py-0.5 text-xs font-medium text-indigo-700"
                  >
                    {{ actionLabel(action) }}
                  </span>
                </div>
              </div>
              <div class="flex shrink-0 flex-wrap gap-2 lg:justify-end">
                <button
                  v-if="item.state?.assigned_to_id === auth.user?.id"
                  class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-ink"
                  type="button"
                  :disabled="isMutating"
                  @click="setItemAssignment(item, 'release')"
                >
                  Release
                </button>
                <button
                  v-else
                  class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-violet-200 bg-violet-50 px-3 text-sm font-semibold text-violet-800"
                  type="button"
                  :disabled="isMutating"
                  @click="setItemAssignment(item, 'claim')"
                >
                  <UserCheck class="h-4 w-4" />
                  Claim
                </button>
                <button
                  class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-ink"
                  type="button"
                  :disabled="isMutating"
                  @click="acknowledgeItem(item)"
                >
                  <CheckCircle2 class="h-4 w-4" />
                  Ack
                </button>
                <button
                  class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-ink"
                  type="button"
                  @click="openHistoryDialog(item)"
                >
                  <History class="h-4 w-4" />
                  History
                </button>
                <button
                  class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-ink"
                  type="button"
                  :disabled="isMutating"
                  @click="openActionDialog(item, 'snooze')"
                >
                  <Clock class="h-4 w-4" />
                  Snooze
                </button>
                <button
                  class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-emerald-200 bg-emerald-50 px-3 text-sm font-semibold text-emerald-800"
                  type="button"
                  :disabled="isMutating"
                  @click="openActionDialog(item, 'resolve')"
                >
                  Resolve
                </button>
                <button
                  class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md bg-ink px-4 text-sm font-semibold text-white"
                  type="button"
                  @click="openItem(item)"
                >
                  {{ item.action_label }}
                  <ArrowRight class="h-4 w-4" />
                </button>
              </div>
            </div>
          </article>
        </div>

        <div v-else class="rounded-md border border-slate-200 bg-white px-6 py-12 text-center">
          <p class="text-base font-semibold text-ink">No active operational items</p>
          <p class="mt-2 text-sm text-graphite">The current filters are clear.</p>
        </div>
      </div>

      <aside class="space-y-4">
        <section class="rounded-md border border-slate-200 bg-white p-4">
          <h2 class="text-base font-semibold text-ink">Pulse</h2>
          <div class="mt-4 grid grid-cols-2 gap-3">
            <div v-for="tile in pulseTiles" :key="tile.label" class="rounded-md bg-slate-50 p-3">
              <p class="text-xs font-medium text-graphite">{{ tile.label }}</p>
              <p class="mt-2 text-2xl font-semibold text-ink">{{ tile.value }}</p>
            </div>
          </div>
        </section>

        <section class="rounded-md border border-slate-200 bg-white p-4">
          <h2 class="text-base font-semibold text-ink">Priority mix</h2>
          <div class="mt-4 space-y-3">
            <button
              v-for="priority in priorityOptions.filter((item) => item !== 'all')"
              :key="priority"
              class="focus-ring flex w-full items-center justify-between rounded-md border px-3 py-2 text-sm"
              :class="selectedPriority === priority ? priorityClasses[priority as OperationsPriority] : 'border-slate-200 bg-white text-slate-700'"
              type="button"
              @click="selectedPriority = priority"
            >
              <span>{{ domainLabel(priority) }}</span>
              <span>{{ summary[priority as OperationsPriority] }}</span>
            </button>
          </div>
        </section>
      </aside>
    </section>

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
          <select
            v-model.number="actionDialog.snooze_hours"
            class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
          >
            <option :value="4">4 hours</option>
            <option :value="24">1 day</option>
            <option :value="72">3 days</option>
            <option :value="168">1 week</option>
          </select>
        </label>
        <label class="block">
          <span class="text-sm font-medium text-ink">Note</span>
          <textarea
            v-model="actionDialog.note"
            class="focus-ring mt-1 min-h-28 w-full resize-none rounded-md border border-slate-200 px-3 py-2 text-sm"
            :placeholder="actionDialog.action === 'snooze' ? 'Why can this wait?' : 'What was handled?'"
          />
        </label>
      </form>
      <template #footer>
        <div class="flex justify-end gap-2">
          <button
            class="focus-ring inline-flex h-10 items-center justify-center rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold text-ink"
            type="button"
            @click="closeActionDialog"
          >
            Cancel
          </button>
          <button
            class="focus-ring inline-flex h-10 items-center justify-center rounded-md bg-ink px-4 text-sm font-semibold text-white"
            type="button"
            :disabled="isMutating"
            @click="submitItemAction"
          >
            {{ actionDialog.action === 'snooze' ? 'Snooze' : 'Resolve' }}
          </button>
        </div>
      </template>
    </BaseModal>

    <BaseModal
      :open="historyDialog.open"
      title="Item history"
      :description="historyDialog.item?.title || ''"
      size="lg"
      @close="closeHistoryDialog"
    >
      <div v-if="isHistoryLoading" class="py-10">
        <LoadingSpinner label="Loading history" />
      </div>
      <div v-else-if="historyDialog.events.length" class="space-y-3">
        <article
          v-for="event in historyDialog.events"
          :key="event.id"
          class="rounded-md border border-slate-200 bg-white p-4"
        >
          <div class="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <p class="text-sm font-semibold text-ink">{{ domainLabel(event.action) }}</p>
              <p class="mt-1 text-xs text-graphite">
                {{ event.actor || "System" }}
                <template v-if="event.from_status || event.to_status">
                  / {{ domainLabel(event.from_status || "none") }} to {{ domainLabel(event.to_status || "none") }}
                </template>
              </p>
            </div>
            <span class="text-xs text-graphite">{{ dateLabel(event.created_at) }}</span>
          </div>
          <p v-if="event.note" class="mt-3 rounded-md bg-slate-50 px-3 py-2 text-sm leading-6 text-slate-700">
            {{ event.note }}
          </p>
          <div class="mt-3 flex flex-wrap gap-2 text-xs text-slate-600">
            <span
              v-if="event.metadata.assigned_to"
              class="rounded-md bg-violet-50 px-2.5 py-1 text-violet-700"
            >
              Assigned: {{ event.metadata.assigned_to }}
            </span>
            <span
              v-if="event.metadata.snoozed_until"
              class="rounded-md bg-indigo-50 px-2.5 py-1 text-indigo-700"
            >
              Snoozed until: {{ dateLabel(String(event.metadata.snoozed_until)) }}
            </span>
          </div>
        </article>
      </div>
      <div v-else class="rounded-md border border-slate-200 bg-slate-50 px-5 py-10 text-center">
        <p class="text-sm font-semibold text-ink">No history yet</p>
        <p class="mt-1 text-sm text-graphite">Actions will appear here as staff work the item.</p>
      </div>
    </BaseModal>
  </div>
</template>
