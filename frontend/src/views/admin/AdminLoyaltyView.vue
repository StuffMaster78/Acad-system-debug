<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
  ArrowLeftRight,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Gift,
  Loader2,
  Minus,
  Plus,
  RefreshCw,
  Settings,
  Tag,
  Trash2,
  X,
  XCircle,
  Zap,
} from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { adminLoyaltyApi } from "@/api/adminLoyalty";
import type {
  LoyaltyConversionConfig,
  LoyaltyTier,
  Milestone,
  RedemptionCategory,
  RedemptionItem,
  RedemptionRequest,
} from "@/api/adminLoyalty";

// ── Tabs ──────────────────────────────────────────────────────────────────────

type Tab = "redemptions" | "operations" | "catalog" | "config";
const activeTab = ref<Tab>("redemptions");

// ── Redemption Queue ──────────────────────────────────────────────────────────

const requests = ref<RedemptionRequest[]>([]);
const requestsLoading = ref(false);
const requestsFilter = ref<"" | "pending" | "approved" | "rejected" | "cancelled">("pending");
const expandedRequest = ref<number | null>(null);
const actioningId = ref<number | null>(null);
const rejectDialogId = ref<number | null>(null);
const rejectReason = ref("");
const requestFeedback = ref("");
const requestError = ref("");

async function loadRequests() {
  requestsLoading.value = true;
  try {
    const params: Record<string, unknown> = {};
    if (requestsFilter.value) params.status = requestsFilter.value;
    const { data } = await adminLoyaltyApi.redemptionRequests(params);
    requests.value = Array.isArray(data) ? data : (data as { results: RedemptionRequest[] }).results ?? [];
  } finally {
    requestsLoading.value = false;
  }
}

async function approve(id: number) {
  actioningId.value = id;
  requestFeedback.value = "";
  requestError.value = "";
  try {
    const { data } = await adminLoyaltyApi.approveRedemption(id);
    const idx = requests.value.findIndex((r) => r.id === id);
    if (idx !== -1) requests.value[idx] = data;
    requestFeedback.value = `Redemption #${id} approved.`;
  } catch {
    requestError.value = "Failed to approve redemption.";
  } finally {
    actioningId.value = null;
  }
}

async function submitReject() {
  if (!rejectDialogId.value) return;
  const id = rejectDialogId.value;
  actioningId.value = id;
  try {
    const { data } = await adminLoyaltyApi.rejectRedemption(id, rejectReason.value || "Rejected by admin");
    const idx = requests.value.findIndex((r) => r.id === id);
    if (idx !== -1) requests.value[idx] = data;
    rejectDialogId.value = null;
    rejectReason.value = "";
    requestFeedback.value = `Redemption #${id} rejected.`;
  } catch {
    requestError.value = "Failed to reject redemption.";
  } finally {
    actioningId.value = null;
  }
}

const pendingCount = computed(() => requests.value.filter((r) => r.status === "pending").length);

// ── Point Operations ──────────────────────────────────────────────────────────

type OpMode = "award" | "deduct" | "transfer" | "convert";
const opMode = ref<OpMode>("award");
const opLoading = ref(false);
const opFeedback = ref("");
const opError = ref("");
const opForm = ref({
  clientId: "",
  toClientId: "",
  points: "",
  reason: "",
});

async function submitOp() {
  opFeedback.value = "";
  opError.value = "";
  const clientId = Number(opForm.value.clientId);
  const points = Number(opForm.value.points);
  if (!clientId || !points || points < 1) {
    opError.value = "Client ID and a positive point value are required.";
    return;
  }
  opLoading.value = true;
  try {
    let msg = "";
    if (opMode.value === "award") {
      const { data } = await adminLoyaltyApi.awardPoints(clientId, points, opForm.value.reason);
      msg = data.message ?? `Awarded ${points} pts to client ${clientId}`;
    } else if (opMode.value === "deduct") {
      const { data } = await adminLoyaltyApi.deductPoints(clientId, points, opForm.value.reason);
      msg = data.message ?? `Deducted ${points} pts from client ${clientId}`;
    } else if (opMode.value === "transfer") {
      const toId = Number(opForm.value.toClientId);
      if (!toId) { opError.value = "Destination client ID required."; return; }
      const { data } = await adminLoyaltyApi.transferPoints(clientId, toId, points, opForm.value.reason);
      msg = data.message ?? `Transferred ${points} pts from ${clientId} to ${toId}`;
    } else {
      const { data } = await adminLoyaltyApi.forceConvert(clientId, points);
      msg = data.message ?? `Converted ${points} pts for client ${clientId}`;
    }
    opFeedback.value = msg;
    opForm.value = { clientId: "", toClientId: "", points: "", reason: "" };
  } catch {
    opError.value = "Operation failed. Check client ID and points.";
  } finally {
    opLoading.value = false;
  }
}

// ── Tiers ─────────────────────────────────────────────────────────────────────

const tiers = ref<LoyaltyTier[]>([]);
const tiersLoading = ref(false);
const showTierForm = ref(false);
const tierFormLoading = ref(false);
const tierForm = ref({ name: "", min_points: "", max_points: "", multiplier: "1.0", benefits: "", is_active: true });
const tierError = ref("");

async function loadTiers() {
  tiersLoading.value = true;
  try {
    const { data } = await adminLoyaltyApi.tiers();
    tiers.value = Array.isArray(data) ? data : (data as { results: LoyaltyTier[] }).results ?? [];
  } finally {
    tiersLoading.value = false;
  }
}

async function submitTier() {
  tierError.value = "";
  if (!tierForm.value.name || !tierForm.value.min_points) {
    tierError.value = "Name and minimum points are required.";
    return;
  }
  tierFormLoading.value = true;
  try {
    await adminLoyaltyApi.createTier({
      name: tierForm.value.name,
      min_points: Number(tierForm.value.min_points),
      max_points: tierForm.value.max_points ? Number(tierForm.value.max_points) : null,
      multiplier: Number(tierForm.value.multiplier) || 1,
      benefits: tierForm.value.benefits || null,
      is_active: tierForm.value.is_active,
    });
    showTierForm.value = false;
    tierForm.value = { name: "", min_points: "", max_points: "", multiplier: "1.0", benefits: "", is_active: true };
    await loadTiers();
  } catch {
    tierError.value = "Failed to create tier.";
  } finally {
    tierFormLoading.value = false;
  }
}

async function deleteTier(id: number) {
  if (!confirm("Delete this tier?")) return;
  await adminLoyaltyApi.deleteTier(id);
  await loadTiers();
}

// ── Milestones ────────────────────────────────────────────────────────────────

const milestones = ref<Milestone[]>([]);
const milestonesLoading = ref(false);
const showMilestoneForm = ref(false);
const milestoneFormLoading = ref(false);
const milestoneForm = ref({ name: "", description: "", points_required: "", reward_points: "", is_active: true });
const milestoneError = ref("");

async function loadMilestones() {
  milestonesLoading.value = true;
  try {
    const { data } = await adminLoyaltyApi.milestones();
    milestones.value = Array.isArray(data) ? data : (data as { results: Milestone[] }).results ?? [];
  } finally {
    milestonesLoading.value = false;
  }
}

async function submitMilestone() {
  milestoneError.value = "";
  if (!milestoneForm.value.name || !milestoneForm.value.points_required) {
    milestoneError.value = "Name and points required are required.";
    return;
  }
  milestoneFormLoading.value = true;
  try {
    await adminLoyaltyApi.createMilestone({
      name: milestoneForm.value.name,
      description: milestoneForm.value.description || null,
      points_required: Number(milestoneForm.value.points_required),
      reward_points: Number(milestoneForm.value.reward_points) || 0,
      is_active: milestoneForm.value.is_active,
    });
    showMilestoneForm.value = false;
    milestoneForm.value = { name: "", description: "", points_required: "", reward_points: "", is_active: true };
    await loadMilestones();
  } catch {
    milestoneError.value = "Failed to create milestone.";
  } finally {
    milestoneFormLoading.value = false;
  }
}

// ── Redemption Catalog ────────────────────────────────────────────────────────

const categories = ref<RedemptionCategory[]>([]);
const catalogItems = ref<RedemptionItem[]>([]);
const catalogLoading = ref(false);
const showItemForm = ref(false);
const itemFormLoading = ref(false);
const itemForm = ref({
  category: "",
  name: "",
  description: "",
  points_required: "",
  redemption_type: "discount_code",
  discount_code: "",
  discount_percentage: "",
  stock_quantity: "",
  max_per_client: "",
  is_active: true,
});
const itemError = ref("");

async function loadCatalog() {
  catalogLoading.value = true;
  try {
    const [catRes, itemRes] = await Promise.all([
      adminLoyaltyApi.redemptionCategories(),
      adminLoyaltyApi.redemptionItems(),
    ]);
    categories.value = Array.isArray(catRes.data) ? catRes.data : (catRes.data as { results: RedemptionCategory[] }).results ?? [];
    catalogItems.value = Array.isArray(itemRes.data) ? itemRes.data : (itemRes.data as { results: RedemptionItem[] }).results ?? [];
  } finally {
    catalogLoading.value = false;
  }
}

async function submitItem() {
  itemError.value = "";
  if (!itemForm.value.name || !itemForm.value.points_required || !itemForm.value.category) {
    itemError.value = "Category, name, and points required.";
    return;
  }
  itemFormLoading.value = true;
  try {
    await adminLoyaltyApi.createItem({
      category: Number(itemForm.value.category),
      name: itemForm.value.name,
      description: itemForm.value.description || null,
      points_required: Number(itemForm.value.points_required),
      redemption_type: itemForm.value.redemption_type,
      discount_code: itemForm.value.discount_code || null,
      discount_percentage: itemForm.value.discount_percentage || null,
      stock_quantity: itemForm.value.stock_quantity ? Number(itemForm.value.stock_quantity) : null,
      max_per_client: itemForm.value.max_per_client ? Number(itemForm.value.max_per_client) : null,
      is_active: itemForm.value.is_active,
    });
    showItemForm.value = false;
    itemForm.value = { category: "", name: "", description: "", points_required: "", redemption_type: "discount_code", discount_code: "", discount_percentage: "", stock_quantity: "", max_per_client: "", is_active: true };
    await loadCatalog();
  } catch {
    itemError.value = "Failed to create item.";
  } finally {
    itemFormLoading.value = false;
  }
}

async function deleteItem(id: number) {
  if (!confirm("Delete this redemption item?")) return;
  await adminLoyaltyApi.deleteItem(id);
  await loadCatalog();
}

// ── Config ────────────────────────────────────────────────────────────────────

const configs = ref<LoyaltyConversionConfig[]>([]);
const configLoading = ref(false);
const savingConfigId = ref<number | null>(null);
const configEdits = ref<Record<number, Partial<LoyaltyConversionConfig>>>({});

async function loadConfig() {
  configLoading.value = true;
  try {
    const { data } = await adminLoyaltyApi.conversionConfigs();
    configs.value = Array.isArray(data) ? data : (data as { results: LoyaltyConversionConfig[] }).results ?? [];
  } finally {
    configLoading.value = false;
  }
}

function editConfig(id: number, field: keyof LoyaltyConversionConfig, value: unknown) {
  if (!configEdits.value[id]) configEdits.value[id] = {};
  (configEdits.value[id] as Record<string, unknown>)[field] = value;
}

async function saveConfig(id: number) {
  savingConfigId.value = id;
  try {
    const updated = await adminLoyaltyApi.updateConversionConfig(id, configEdits.value[id] ?? {});
    const idx = configs.value.findIndex((c) => c.id === id);
    if (idx !== -1) configs.value[idx] = updated.data;
    delete configEdits.value[id];
  } finally {
    savingConfigId.value = null;
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function requestStatusTone(s: string): "success" | "warning" | "danger" | "neutral" {
  if (["approved", "fulfilled"].includes(s)) return "success";
  if (["pending"].includes(s)) return "warning";
  if (["rejected", "cancelled"].includes(s)) return "danger";
  return "neutral";
}

function fmt(v: string | null | undefined): string {
  if (!v) return "—";
  return new Date(v).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

// ── Init ─────────────────────────────────────────────────────────────────────

onMounted(async () => {
  await Promise.all([loadRequests(), loadTiers(), loadMilestones(), loadCatalog(), loadConfig()]);
});
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold text-neutral-900">Loyalty Management</h1>
        <p class="text-sm text-neutral-500 mt-0.5">Redemption queue, point operations, tier rules, and conversion config</p>
      </div>
      <button
        class="inline-flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-lg border border-neutral-200 hover:bg-neutral-50 transition-colors"
        @click="loadRequests(); loadTiers(); loadMilestones(); loadCatalog(); loadConfig()"
      >
        <RefreshCw class="size-4" />
        Refresh
      </button>
    </div>

    <!-- Tabs -->
    <div class="flex border-b border-neutral-200 gap-6 overflow-x-auto">
      <button
        v-for="tab in [
          { key: 'redemptions', label: 'Redemption Queue', icon: Gift },
          { key: 'operations', label: 'Point Operations', icon: Zap },
          { key: 'catalog', label: 'Tiers & Catalog', icon: Tag },
          { key: 'config', label: 'Config', icon: Settings },
        ]"
        :key="tab.key"
        class="flex items-center gap-1.5 pb-3 text-sm font-medium border-b-2 transition-colors -mb-px whitespace-nowrap"
        :class="activeTab === tab.key
          ? 'border-neutral-900 text-neutral-900'
          : 'border-transparent text-neutral-500 hover:text-neutral-700'"
        @click="activeTab = tab.key as Tab"
      >
        <component :is="tab.icon" class="size-4" />
        {{ tab.label }}
        <span v-if="tab.key === 'redemptions' && pendingCount" class="ml-1 text-xs px-1.5 py-0.5 rounded-full bg-amber-100 text-amber-700 font-semibold">{{ pendingCount }}</span>
      </button>
    </div>

    <!-- ── REDEMPTION QUEUE ───────────────────────────────────────────────────── -->
    <template v-if="activeTab === 'redemptions'">
      <!-- Filters -->
      <div class="flex flex-wrap items-center gap-3">
        <div class="flex rounded-lg border border-neutral-200 overflow-hidden text-xs">
          <button
            v-for="f in (['pending', 'approved', 'rejected', 'cancelled', ''] as const)"
            :key="String(f)"
            class="px-3 py-1.5 capitalize transition-colors border-r border-neutral-200 last:border-r-0"
            :class="requestsFilter === f ? 'bg-neutral-900 text-white' : 'hover:bg-neutral-50 text-neutral-600'"
            @click="requestsFilter = f; loadRequests()"
          >
            {{ f === '' ? 'All' : f }}
          </button>
        </div>
      </div>

      <!-- Feedback -->
      <div v-if="requestFeedback" class="flex items-center justify-between px-4 py-2 rounded-lg bg-signal-50 border border-signal-200 text-sm text-signal-800">
        {{ requestFeedback }}
        <button @click="requestFeedback = ''"><X class="size-4" /></button>
      </div>
      <div v-if="requestError" class="flex items-center justify-between px-4 py-2 rounded-lg bg-berry-50 border border-berry-200 text-sm text-berry-800">
        {{ requestError }}
        <button @click="requestError = ''"><X class="size-4" /></button>
      </div>

      <!-- Reject dialog -->
      <div v-if="rejectDialogId !== null" class="rounded-xl border border-berry-200 bg-berry-50 p-4 space-y-3">
        <div class="flex items-center justify-between">
          <p class="text-sm font-semibold text-berry-800">Reject redemption #{{ rejectDialogId }}</p>
          <button @click="rejectDialogId = null; rejectReason = ''"><X class="size-4 text-berry-400" /></button>
        </div>
        <input v-model="rejectReason" type="text" placeholder="Rejection reason"
          class="w-full text-sm px-3 py-2 rounded-lg border border-berry-200 bg-white focus:outline-none focus:ring-2 focus:ring-berry-400" />
        <div class="flex gap-2">
          <button
            class="text-sm px-3 py-1.5 rounded-lg bg-berry-600 text-white hover:bg-berry-700 disabled:opacity-50 transition-colors"
            :disabled="actioningId === rejectDialogId"
            @click="submitReject"
          >
            <Loader2 v-if="actioningId === rejectDialogId" class="size-3.5 animate-spin inline mr-1" />
            Confirm reject
          </button>
          <button class="text-sm px-3 py-1.5 rounded-lg border border-neutral-200 hover:bg-neutral-50" @click="rejectDialogId = null; rejectReason = ''">
            Dismiss
          </button>
        </div>
      </div>

      <!-- Table -->
      <div class="bg-white rounded-xl border border-neutral-200 overflow-hidden">
        <div v-if="requestsLoading" class="p-8 flex justify-center"><Loader2 class="size-7 text-neutral-300 animate-spin" /></div>
        <div v-else-if="requests.length === 0" class="p-8 text-center text-sm text-neutral-400">No redemption requests found.</div>
        <div v-else class="divide-y divide-neutral-100">
          <div v-for="r in requests" :key="r.id">
            <div
              class="flex items-center gap-4 px-4 py-3 hover:bg-neutral-50 transition-colors cursor-pointer"
              @click="expandedRequest = expandedRequest === r.id ? null : r.id"
            >
              <component :is="expandedRequest === r.id ? ChevronDown : ChevronRight" class="size-4 text-neutral-400 shrink-0" />
              <span class="font-mono text-xs text-neutral-400 w-10 shrink-0">#{{ r.id }}</span>
              <StatusPill :label="r.status" :tone="requestStatusTone(r.status)" />
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-neutral-900 truncate">{{ r.item_name ?? `Item #${r.item}` }}</p>
                <p class="text-xs text-neutral-400">{{ r.client_username ?? `Client #${r.client}` }} · {{ r.points_used }} pts</p>
              </div>
              <p class="text-xs text-neutral-400 shrink-0">{{ fmt(r.requested_at) }}</p>
              <!-- Actions -->
              <div class="flex items-center gap-1.5 shrink-0" @click.stop>
                <button
                  v-if="r.status === 'pending'"
                  class="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-lg bg-signal-600 text-white hover:bg-signal-700 disabled:opacity-50 transition-colors"
                  :disabled="actioningId === r.id"
                  @click="approve(r.id)"
                >
                  <Loader2 v-if="actioningId === r.id" class="size-3 animate-spin" />
                  <CheckCircle2 v-else class="size-3" />
                  Approve
                </button>
                <button
                  v-if="r.status === 'pending'"
                  class="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-lg border border-berry-200 text-berry-700 hover:bg-berry-50 disabled:opacity-50 transition-colors"
                  :disabled="actioningId === r.id"
                  @click="rejectDialogId = r.id; rejectReason = ''"
                >
                  <XCircle class="size-3" />
                  Reject
                </button>
              </div>
            </div>
            <!-- Expanded -->
            <div v-if="expandedRequest === r.id" class="px-12 pb-4 pt-2 bg-neutral-50 border-t border-neutral-100">
              <div class="grid grid-cols-3 gap-4 text-xs">
                <div><p class="text-neutral-400 uppercase tracking-wide">Item points</p><p class="text-neutral-800 mt-0.5">{{ r.item_points ?? "—" }}</p></div>
                <div><p class="text-neutral-400 uppercase tracking-wide">Points used</p><p class="text-neutral-800 mt-0.5">{{ r.points_used }}</p></div>
                <div><p class="text-neutral-400 uppercase tracking-wide">Fulfillment code</p><p class="font-mono text-neutral-800 mt-0.5">{{ r.fulfillment_code ?? "—" }}</p></div>
                <div v-if="r.approved_by_username"><p class="text-neutral-400 uppercase tracking-wide">Approved by</p><p class="text-neutral-800 mt-0.5">{{ r.approved_by_username }}</p></div>
                <div v-if="r.rejection_reason" class="col-span-2"><p class="text-neutral-400 uppercase tracking-wide">Rejection reason</p><p class="text-berry-700 mt-0.5">{{ r.rejection_reason }}</p></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- ── POINT OPERATIONS ───────────────────────────────────────────────────── -->
    <template v-if="activeTab === 'operations'">
      <!-- Mode selector -->
      <div class="flex rounded-lg border border-neutral-200 overflow-hidden text-sm w-fit">
        <button
          v-for="mode in [
            { key: 'award', label: 'Award', icon: Plus },
            { key: 'deduct', label: 'Deduct', icon: Minus },
            { key: 'transfer', label: 'Transfer', icon: ArrowLeftRight },
            { key: 'convert', label: 'Force Convert', icon: Zap },
          ]"
          :key="mode.key"
          class="flex items-center gap-1.5 px-4 py-2 transition-colors border-r border-neutral-200 last:border-r-0"
          :class="opMode === mode.key ? 'bg-neutral-900 text-white' : 'hover:bg-neutral-50 text-neutral-600'"
          @click="opMode = mode.key as OpMode; opFeedback = ''; opError = ''"
        >
          <component :is="mode.icon" class="size-4" />
          {{ mode.label }}
        </button>
      </div>

      <!-- Form -->
      <div class="bg-white rounded-xl border border-neutral-200 p-6 max-w-lg space-y-4">
        <h3 class="text-sm font-semibold text-neutral-900 capitalize">{{ opMode }} Points</h3>

        <label class="block space-y-1">
          <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">
            {{ opMode === 'transfer' ? 'From Client ID' : 'Client ID' }}
          </span>
          <input v-model="opForm.clientId" type="number" placeholder="e.g. 42"
            class="w-full text-sm px-3 py-2 rounded-lg border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-neutral-900" />
        </label>

        <label v-if="opMode === 'transfer'" class="block space-y-1">
          <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">To Client ID</span>
          <input v-model="opForm.toClientId" type="number" placeholder="e.g. 99"
            class="w-full text-sm px-3 py-2 rounded-lg border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-neutral-900" />
        </label>

        <label class="block space-y-1">
          <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">Points</span>
          <input v-model="opForm.points" type="number" min="1" placeholder="e.g. 500"
            class="w-full text-sm px-3 py-2 rounded-lg border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-neutral-900" />
        </label>

        <label v-if="opMode !== 'convert'" class="block space-y-1">
          <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">Reason</span>
          <input v-model="opForm.reason" type="text" placeholder="e.g. Loyalty bonus for milestone"
            class="w-full text-sm px-3 py-2 rounded-lg border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-neutral-900" />
        </label>

        <div v-if="opFeedback" class="text-sm text-signal-700 bg-signal-50 border border-signal-200 px-3 py-2 rounded-lg">{{ opFeedback }}</div>
        <div v-if="opError" class="text-sm text-berry-700 bg-berry-50 border border-berry-200 px-3 py-2 rounded-lg">{{ opError }}</div>

        <button
          class="inline-flex items-center gap-1.5 text-sm px-4 py-2 rounded-lg bg-neutral-900 text-white hover:bg-neutral-800 disabled:opacity-50 transition-colors"
          :disabled="opLoading"
          @click="submitOp"
        >
          <Loader2 v-if="opLoading" class="size-4 animate-spin" />
          <Zap v-else class="size-4" />
          Execute
        </button>
      </div>
    </template>

    <!-- ── TIERS & CATALOG ────────────────────────────────────────────────────── -->
    <template v-if="activeTab === 'catalog'">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Tiers -->
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-semibold text-neutral-900">Loyalty Tiers</h3>
            <button class="inline-flex items-center gap-1 text-xs px-2.5 py-1.5 rounded-lg bg-neutral-900 text-white hover:bg-neutral-800 transition-colors" @click="showTierForm = !showTierForm">
              <Plus class="size-3.5" />Add tier
            </button>
          </div>
          <!-- Tier form -->
          <div v-if="showTierForm" class="bg-white rounded-xl border border-neutral-200 p-4 space-y-3">
            <div class="grid grid-cols-2 gap-3">
              <label class="col-span-2 space-y-1">
                <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">Name *</span>
                <input v-model="tierForm.name" type="text" placeholder="e.g. Gold" class="w-full text-sm px-3 py-2 rounded-lg border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-neutral-900" />
              </label>
              <label class="space-y-1">
                <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">Min pts *</span>
                <input v-model="tierForm.min_points" type="number" class="w-full text-sm px-3 py-2 rounded-lg border border-neutral-200 focus:outline-none" />
              </label>
              <label class="space-y-1">
                <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">Max pts</span>
                <input v-model="tierForm.max_points" type="number" placeholder="∞" class="w-full text-sm px-3 py-2 rounded-lg border border-neutral-200 focus:outline-none" />
              </label>
              <label class="space-y-1">
                <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">Multiplier</span>
                <input v-model="tierForm.multiplier" type="number" step="0.1" class="w-full text-sm px-3 py-2 rounded-lg border border-neutral-200 focus:outline-none" />
              </label>
              <label class="flex items-center gap-2 text-sm self-end pb-2">
                <input v-model="tierForm.is_active" type="checkbox" class="rounded" />Active
              </label>
            </div>
            <p v-if="tierError" class="text-xs text-berry-600">{{ tierError }}</p>
            <div class="flex gap-2">
              <button class="text-sm px-3 py-1.5 rounded-lg bg-neutral-900 text-white hover:bg-neutral-800 disabled:opacity-50 transition-colors" :disabled="tierFormLoading" @click="submitTier">
                <Loader2 v-if="tierFormLoading" class="size-3.5 animate-spin inline mr-1" />Create
              </button>
              <button class="text-sm px-3 py-1.5 rounded-lg border border-neutral-200 hover:bg-neutral-50" @click="showTierForm = false">Cancel</button>
            </div>
          </div>
          <!-- Tier table -->
          <div class="bg-white rounded-xl border border-neutral-200 overflow-hidden">
            <div v-if="tiersLoading" class="p-6 flex justify-center"><Loader2 class="size-6 text-neutral-300 animate-spin" /></div>
            <div v-else-if="tiers.length === 0" class="p-6 text-center text-sm text-neutral-400">No tiers defined.</div>
            <table v-else class="w-full text-sm">
              <thead class="bg-neutral-50 border-b border-neutral-100">
                <tr>
                  <th class="text-left px-4 py-2 text-xs font-medium text-neutral-500 uppercase tracking-wide">Name</th>
                  <th class="text-left px-4 py-2 text-xs font-medium text-neutral-500 uppercase tracking-wide">Points</th>
                  <th class="text-left px-4 py-2 text-xs font-medium text-neutral-500 uppercase tracking-wide">×</th>
                  <th class="px-4 py-2" />
                </tr>
              </thead>
              <tbody class="divide-y divide-neutral-50">
                <tr v-for="t in tiers" :key="t.id" class="hover:bg-neutral-50">
                  <td class="px-4 py-2">
                    <div class="font-medium text-neutral-900">{{ String(t.name) }}</div>
                    <StatusPill :label="t.is_active ? 'active' : 'inactive'" :tone="t.is_active ? 'success' : 'neutral'" />
                  </td>
                  <td class="px-4 py-2 text-neutral-600 text-xs">{{ t.min_points }}{{ t.max_points ? `–${t.max_points}` : '+' }}</td>
                  <td class="px-4 py-2 text-neutral-600">{{ t.multiplier }}x</td>
                  <td class="px-4 py-2 text-right">
                    <button class="p-1 rounded hover:bg-red-50 text-neutral-400 hover:text-berry-600" @click="deleteTier(t.id)"><Trash2 class="size-4" /></button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Milestones -->
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-semibold text-neutral-900">Milestones</h3>
            <button class="inline-flex items-center gap-1 text-xs px-2.5 py-1.5 rounded-lg bg-neutral-900 text-white hover:bg-neutral-800 transition-colors" @click="showMilestoneForm = !showMilestoneForm">
              <Plus class="size-3.5" />Add
            </button>
          </div>
          <div v-if="showMilestoneForm" class="bg-white rounded-xl border border-neutral-200 p-4 space-y-3">
            <div class="grid grid-cols-2 gap-3">
              <label class="col-span-2 space-y-1">
                <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">Name *</span>
                <input v-model="milestoneForm.name" type="text" class="w-full text-sm px-3 py-2 rounded-lg border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-neutral-900" />
              </label>
              <label class="space-y-1">
                <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">Points required *</span>
                <input v-model="milestoneForm.points_required" type="number" class="w-full text-sm px-3 py-2 rounded-lg border border-neutral-200 focus:outline-none" />
              </label>
              <label class="space-y-1">
                <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">Reward points</span>
                <input v-model="milestoneForm.reward_points" type="number" class="w-full text-sm px-3 py-2 rounded-lg border border-neutral-200 focus:outline-none" />
              </label>
            </div>
            <p v-if="milestoneError" class="text-xs text-berry-600">{{ milestoneError }}</p>
            <div class="flex gap-2">
              <button class="text-sm px-3 py-1.5 rounded-lg bg-neutral-900 text-white hover:bg-neutral-800 disabled:opacity-50" :disabled="milestoneFormLoading" @click="submitMilestone">
                <Loader2 v-if="milestoneFormLoading" class="size-3.5 animate-spin inline mr-1" />Create
              </button>
              <button class="text-sm px-3 py-1.5 rounded-lg border border-neutral-200 hover:bg-neutral-50" @click="showMilestoneForm = false">Cancel</button>
            </div>
          </div>
          <div class="bg-white rounded-xl border border-neutral-200 overflow-hidden">
            <div v-if="milestonesLoading" class="p-6 flex justify-center"><Loader2 class="size-6 text-neutral-300 animate-spin" /></div>
            <div v-else-if="milestones.length === 0" class="p-6 text-center text-sm text-neutral-400">No milestones defined.</div>
            <div v-else class="divide-y divide-neutral-100">
              <div v-for="m in milestones" :key="m.id" class="flex items-center gap-3 px-4 py-3">
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-neutral-900">{{ String(m.name) }}</p>
                  <p class="text-xs text-neutral-400">{{ m.points_required }} pts required · +{{ m.reward_points }} reward pts</p>
                </div>
                <StatusPill :label="m.is_active ? 'active' : 'inactive'" :tone="m.is_active ? 'success' : 'neutral'" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Redemption items -->
      <div class="space-y-3 mt-2">
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-semibold text-neutral-900">Redemption Catalog</h3>
          <button class="inline-flex items-center gap-1 text-xs px-2.5 py-1.5 rounded-lg bg-neutral-900 text-white hover:bg-neutral-800 transition-colors" @click="showItemForm = !showItemForm">
            <Plus class="size-3.5" />Add item
          </button>
        </div>

        <div v-if="showItemForm" class="bg-white rounded-xl border border-neutral-200 p-4 space-y-3">
          <div class="grid grid-cols-2 gap-3">
            <label class="space-y-1">
              <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">Category *</span>
              <select v-model="itemForm.category" class="w-full text-sm px-3 py-2 rounded-lg border border-neutral-200 bg-white">
                <option value="">Select category…</option>
                <option v-for="c in categories" :key="c.id" :value="String(c.id)">{{ c.name }}</option>
              </select>
            </label>
            <label class="space-y-1">
              <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">Name *</span>
              <input v-model="itemForm.name" type="text" class="w-full text-sm px-3 py-2 rounded-lg border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-neutral-900" />
            </label>
            <label class="space-y-1">
              <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">Points required *</span>
              <input v-model="itemForm.points_required" type="number" class="w-full text-sm px-3 py-2 rounded-lg border border-neutral-200 focus:outline-none" />
            </label>
            <label class="space-y-1">
              <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">Type</span>
              <select v-model="itemForm.redemption_type" class="w-full text-sm px-3 py-2 rounded-lg border border-neutral-200 bg-white">
                <option value="discount_code">Discount code</option>
                <option value="wallet_credit">Wallet credit</option>
                <option value="free_order">Free order</option>
                <option value="physical">Physical</option>
              </select>
            </label>
            <label v-if="itemForm.redemption_type === 'discount_code'" class="space-y-1">
              <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">Discount code</span>
              <input v-model="itemForm.discount_code" type="text" class="w-full text-sm px-3 py-2 rounded-lg border border-neutral-200 focus:outline-none" />
            </label>
            <label v-if="itemForm.redemption_type === 'discount_code'" class="space-y-1">
              <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">Discount %</span>
              <input v-model="itemForm.discount_percentage" type="number" step="0.01" class="w-full text-sm px-3 py-2 rounded-lg border border-neutral-200 focus:outline-none" />
            </label>
            <label class="space-y-1">
              <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">Stock qty</span>
              <input v-model="itemForm.stock_quantity" type="number" placeholder="∞" class="w-full text-sm px-3 py-2 rounded-lg border border-neutral-200 focus:outline-none" />
            </label>
            <label class="space-y-1">
              <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">Max per client</span>
              <input v-model="itemForm.max_per_client" type="number" placeholder="∞" class="w-full text-sm px-3 py-2 rounded-lg border border-neutral-200 focus:outline-none" />
            </label>
          </div>
          <p v-if="itemError" class="text-xs text-berry-600">{{ itemError }}</p>
          <div class="flex gap-2">
            <button class="text-sm px-3 py-1.5 rounded-lg bg-neutral-900 text-white hover:bg-neutral-800 disabled:opacity-50" :disabled="itemFormLoading" @click="submitItem">
              <Loader2 v-if="itemFormLoading" class="size-3.5 animate-spin inline mr-1" />Create
            </button>
            <button class="text-sm px-3 py-1.5 rounded-lg border border-neutral-200 hover:bg-neutral-50" @click="showItemForm = false">Cancel</button>
          </div>
        </div>

        <div v-if="catalogLoading" class="p-6 flex justify-center"><Loader2 class="size-7 text-neutral-300 animate-spin" /></div>
        <div v-else-if="catalogItems.length === 0" class="bg-white rounded-xl border border-neutral-200 p-6 text-center text-sm text-neutral-400">No redemption items. Add one above.</div>
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="item in catalogItems" :key="item.id" class="bg-white rounded-xl border border-neutral-200 p-4 space-y-2">
            <div class="flex items-start justify-between gap-2">
              <div>
                <p class="text-sm font-semibold text-neutral-900">{{ item.name }}</p>
                <p class="text-xs text-neutral-400">{{ item.category_name }}</p>
              </div>
              <div class="flex items-center gap-1 shrink-0">
                <StatusPill :label="item.is_active ? 'active' : 'inactive'" :tone="item.is_active ? 'success' : 'neutral'" />
                <button class="p-1 rounded hover:bg-red-50 text-neutral-400 hover:text-berry-600" @click="deleteItem(item.id)"><Trash2 class="size-3.5" /></button>
              </div>
            </div>
            <div class="flex items-center gap-3 text-xs text-neutral-500">
              <span class="font-semibold text-neutral-800">{{ item.points_required }} pts</span>
              <span class="capitalize">{{ item.redemption_type.replace('_', ' ') }}</span>
              <span v-if="item.discount_percentage">{{ item.discount_percentage }}% off</span>
            </div>
            <div class="text-xs text-neutral-400">
              {{ item.total_redemptions }} redeemed
              <span v-if="item.stock_quantity !== null">· {{ item.stock_quantity }} in stock</span>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- ── CONFIG ─────────────────────────────────────────────────────────────── -->
    <template v-if="activeTab === 'config'">
      <div v-if="configLoading" class="p-8 flex justify-center"><Loader2 class="size-7 text-neutral-300 animate-spin" /></div>
      <div v-else-if="configs.length === 0" class="bg-white rounded-xl border border-neutral-200 p-8 text-center text-sm text-neutral-400">
        No conversion configs found.
      </div>
      <div v-else class="space-y-4">
        <div
          v-for="cfg in configs"
          :key="cfg.id"
          class="bg-white rounded-xl border border-neutral-200 p-6 space-y-4"
        >
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-semibold text-neutral-900">Conversion Config #{{ cfg.id }}</h3>
            <StatusPill :label="cfg.active ? 'active' : 'inactive'" :tone="cfg.active ? 'success' : 'neutral'" />
          </div>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-4">
            <label class="space-y-1">
              <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">Conversion rate (pts → $)</span>
              <input
                :value="configEdits[cfg.id]?.conversion_rate ?? cfg.conversion_rate"
                type="number" step="0.01"
                class="w-full text-sm px-3 py-2 rounded-lg border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-neutral-900"
                @input="editConfig(cfg.id, 'conversion_rate', ($event.target as HTMLInputElement).value)"
              />
            </label>
            <label class="space-y-1">
              <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">Min conversion pts</span>
              <input
                :value="configEdits[cfg.id]?.min_conversion_points ?? cfg.min_conversion_points"
                type="number"
                class="w-full text-sm px-3 py-2 rounded-lg border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-neutral-900"
                @input="editConfig(cfg.id, 'min_conversion_points', Number(($event.target as HTMLInputElement).value))"
              />
            </label>
            <label class="space-y-1">
              <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">Max conversion limit</span>
              <input
                :value="configEdits[cfg.id]?.max_conversion_limit ?? cfg.max_conversion_limit ?? ''"
                type="number" placeholder="None"
                class="w-full text-sm px-3 py-2 rounded-lg border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-neutral-900"
                @input="editConfig(cfg.id, 'max_conversion_limit', Number(($event.target as HTMLInputElement).value) || null)"
              />
            </label>
          </div>
          <label class="flex items-center gap-2 text-sm">
            <input
              :checked="configEdits[cfg.id]?.active ?? cfg.active"
              type="checkbox"
              class="rounded"
              @change="editConfig(cfg.id, 'active', ($event.target as HTMLInputElement).checked)"
            />
            Active
          </label>
          <button
            v-if="configEdits[cfg.id]"
            class="inline-flex items-center gap-1.5 text-sm px-4 py-2 rounded-lg bg-neutral-900 text-white hover:bg-neutral-800 disabled:opacity-50 transition-colors"
            :disabled="savingConfigId === cfg.id"
            @click="saveConfig(cfg.id)"
          >
            <Loader2 v-if="savingConfigId === cfg.id" class="size-4 animate-spin" />
            Save changes
          </button>
        </div>
      </div>
    </template>
  </div>
</template>
