<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import {
  CheckCircle2, Plus, RefreshCw, Save, ShieldCheck, Trash2, X,
} from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { api, apiPath } from "@/api/client";
import { useAuthStore } from "@/stores/auth";
import { usePortalContextStore } from "@/stores/portalContext";
import { useWebsitesStore } from "@/stores/websites";

const auth    = useAuthStore();
const portal  = usePortalContextStore();
const websites = useWebsitesStore();

// ── Tabs ──────────────────────────────────────────────────────────────────────
type Tab = "levels" | "tips";
const activeTab = ref<Tab>("levels");

const notice = ref<{ type: "success" | "error"; msg: string } | null>(null);
function toast(type: "success" | "error", msg: string) {
  notice.value = { type, msg };
  setTimeout(() => { notice.value = null; }, 4000);
}

const isSuperadmin = computed(() => auth.role === "superadmin");
const selectedWebsiteId = ref<number | null>(null);
const websiteParams = computed(() =>
  isSuperadmin.value && selectedWebsiteId.value ? { website_id: selectedWebsiteId.value } : undefined,
);
const selectedWebsiteLabel = computed(() => {
  if (selectedWebsiteId.value) return websites.labelById(selectedWebsiteId.value);
  if (portal.website) return `${portal.website.name} (${portal.website.domain})`;
  if (isSuperadmin.value) return "Select a website";
  return "Current website";
});
const needsWebsiteSelection = computed(() => isSuperadmin.value && !selectedWebsiteId.value);

// ═══════════════════════════════════════════════════════════════════════════════
// WRITER LEVELS
// ═══════════════════════════════════════════════════════════════════════════════

interface WriterLevel {
  id: number; name: string; description: string; display_order: number;
  is_active: boolean; is_default: boolean; settings_id: number | null;
}

interface LevelSettings {
  id: number; level_id: number; level_name: string;
  // Pay rates
  base_pay_per_page: string; base_pay_per_slide: string; base_pay_per_chart: string;
  additional_page_pay: string; additional_slide_pay: string; additional_chart_pay: string;
  // Tip
  tip_percentage: string;
  // Capacity
  max_active_orders: number; max_manual_takes: number; max_pending_assignments: number;
  // Urgency
  urgent_time_threshold_hours: number; urgent_order_surcharge: string; urgent_multiplier: string;
  // Eligibility
  min_completed_orders: number; min_rating: string;
  min_successful_takes: number; min_completion_rate: string | null;
  max_revision_rate: string | null; max_lateness_rate: string | null;
  max_warnings: number;
  is_active: boolean;
}

const levels       = ref<WriterLevel[]>([]);
const allSettings  = ref<LevelSettings[]>([]);
const levelsLoading = ref(false);
const selectedLevel = ref<WriterLevel | null>(null);

const selectedSettings = computed(() =>
  selectedLevel.value
    ? allSettings.value.find(s => s.level_id === selectedLevel.value!.id) ?? null
    : null,
);

const levelDraft     = reactive({ name: "", description: "", display_order: 0, is_active: true, is_default: false });
const settingsDraft  = reactive<Partial<LevelSettings>>({});
const editingLevelId = ref<number | null>(null);
const savingLevel    = ref(false);
const savingSettings = ref(false);
const levelForm      = ref(false);
const deleteConfirm  = ref<number | null>(null);

async function loadLevels() {
  if (needsWebsiteSelection.value) {
    levels.value = [];
    allSettings.value = [];
    selectedLevel.value = null;
    return;
  }
  levelsLoading.value = true;
  try {
    const [lr, sr] = await Promise.all([
      api.get<WriterLevel[]>(apiPath("/writer-management/levels/"), { params: websiteParams.value }),
      api.get<LevelSettings[]>(apiPath("/writer-management/level-settings/"), { params: websiteParams.value }),
    ]);
    levels.value = Array.isArray(lr.data) ? lr.data : (lr.data as any).results ?? [];
    allSettings.value = Array.isArray(sr.data) ? sr.data : (sr.data as any).results ?? [];
    if (levels.value.length && !selectedLevel.value) selectLevel(levels.value[0]);
  } catch { toast("error", "Failed to load writer levels."); }
  finally { levelsLoading.value = false; }
}

function selectLevel(level: WriterLevel) {
  selectedLevel.value = level;
  const s = allSettings.value.find(x => x.level_id === level.id);
  if (s) Object.assign(settingsDraft, { ...s });
}

function openNewLevel() {
  if (needsWebsiteSelection.value) {
    toast("error", "Select a website before creating writer levels.");
    return;
  }
  editingLevelId.value = null;
  Object.assign(levelDraft, {
    name: "", description: "",
    display_order: Math.max(0, ...levels.value.map(l => l.display_order)) + 1,
    is_active: true, is_default: false,
  });
  levelForm.value = true;
}

function openEditLevel(level: WriterLevel) {
  editingLevelId.value = level.id;
  Object.assign(levelDraft, level);
  levelForm.value = true;
}

async function saveLevel() {
  if (!levelDraft.name.trim()) return;
  savingLevel.value = true;
  try {
    if (editingLevelId.value) {
      await api.patch(apiPath(`/writer-management/levels/${editingLevelId.value}/`), levelDraft, {
        params: websiteParams.value,
      });
      toast("success", `"${levelDraft.name}" updated.`);
    } else {
      await api.post(apiPath("/writer-management/levels/"), levelDraft, {
        params: websiteParams.value,
      });
      toast("success", `"${levelDraft.name}" created.`);
    }
    levelForm.value = false;
    await loadLevels();
  } catch (err: unknown) {
    const detail = (err as any)?.response?.data?.detail ?? "Failed to save level.";
    toast("error", detail);
  } finally { savingLevel.value = false; }
}

async function deleteLevel(id: number) {
  try {
    await api.delete(apiPath(`/writer-management/levels/${id}/`), { params: websiteParams.value });
    deleteConfirm.value = null;
    if (selectedLevel.value?.id === id) selectedLevel.value = null;
    await loadLevels();
    toast("success", "Level deleted.");
  } catch (err: unknown) {
    const detail = (err as any)?.response?.data?.detail ?? "Cannot delete this level.";
    toast("error", detail);
    deleteConfirm.value = null;
  }
}

async function saveSettings() {
  if (needsWebsiteSelection.value) {
    toast("error", "Select a website before saving writer pay settings.");
    return;
  }
  const s = selectedSettings.value;
  if (!s) return;
  savingSettings.value = true;
  try {
    await api.patch(apiPath(`/writer-management/level-settings/${s.id}/`), settingsDraft, {
      params: websiteParams.value,
    });
    await loadLevels();
    toast("success", "Settings saved.");
  } catch { toast("error", "Failed to save settings."); }
  finally { savingSettings.value = false; }
}

// ═══════════════════════════════════════════════════════════════════════════════
// TIP POLICIES
// ═══════════════════════════════════════════════════════════════════════════════

interface TipPolicy {
  id: number; name: string; slug: string; description: string;
  writer_percentage: number; platform_percentage: number;
  minimum_tip_amount: string; risk_review_threshold: string;
  maximum_tip_frequency_per_day: number;
  allow_wallet_tips: boolean; allow_external_tips: boolean;
  require_manual_review: boolean; is_active: boolean; created_at: string;
}

const policies      = ref<TipPolicy[]>([]);
const policyLoading = ref(false);
const savingPolicy  = ref(false);
const activating    = ref<number | null>(null);
const policyModal   = ref(false);
const editingPolicyId = ref<number | null>(null);

const policyDraft = reactive({
  name: "", description: "",
  writer_percentage: "90.00", platform_percentage: "10.00",
  minimum_tip_amount: "1.00", risk_review_threshold: "500.00",
  maximum_tip_frequency_per_day: 10,
  allow_wallet_tips: true, allow_external_tips: true, require_manual_review: false,
});

const activePolicy = computed(() => policies.value.find(p => p.is_active) ?? null);

async function loadPolicies() {
  policyLoading.value = true;
  try {
    const { data } = await api.get<TipPolicy[]>(apiPath("/tips/admin/policy/"));
    policies.value = Array.isArray(data) ? data : (data as any).results ?? [];
  } catch { toast("error", "Failed to load tip policies."); }
  finally { policyLoading.value = false; }
}

function openNewPolicy() {
  editingPolicyId.value = null;
  Object.assign(policyDraft, {
    name: "", description: "",
    writer_percentage: "90.00", platform_percentage: "10.00",
    minimum_tip_amount: "1.00", risk_review_threshold: "500.00",
    maximum_tip_frequency_per_day: 10,
    allow_wallet_tips: true, allow_external_tips: true, require_manual_review: false,
  });
  policyModal.value = true;
}

function openEditPolicy(policy: TipPolicy) {
  editingPolicyId.value = policy.id;
  Object.assign(policyDraft, {
    name:                   policy.name,
    description:            policy.description,
    writer_percentage:      String(policy.writer_percentage),
    platform_percentage:    String(policy.platform_percentage),
    minimum_tip_amount:     policy.minimum_tip_amount,
    risk_review_threshold:  policy.risk_review_threshold,
    maximum_tip_frequency_per_day: policy.maximum_tip_frequency_per_day,
    allow_wallet_tips:      policy.allow_wallet_tips,
    allow_external_tips:    policy.allow_external_tips,
    require_manual_review:  policy.require_manual_review,
  });
  policyModal.value = true;
}

// Auto-balance: when writer % changes, platform % = 100 - writer %
watch(() => policyDraft.writer_percentage, (v) => {
  const n = parseFloat(v);
  if (!isNaN(n) && n >= 0 && n <= 100) {
    policyDraft.platform_percentage = (100 - n).toFixed(2);
  }
});

async function savePolicy() {
  savingPolicy.value = true;
  try {
    if (editingPolicyId.value) {
      await api.patch(apiPath(`/tips/admin/policy/${editingPolicyId.value}/`), policyDraft);
      toast("success", "Policy updated.");
    } else {
      await api.post(apiPath("/tips/admin/policy/"), policyDraft);
      toast("success", "Policy created.");
    }
    policyModal.value = false;
    await loadPolicies();
  } catch (err: unknown) {
    const detail = (err as any)?.response?.data?.detail ?? "Failed to save policy.";
    toast("error", detail);
  } finally { savingPolicy.value = false; }
}

async function activatePolicy(id: number) {
  activating.value = id;
  try {
    await api.post(apiPath(`/tips/admin/policy/${id}/activate/`), {});
    await loadPolicies();
    toast("success", "Policy activated.");
  } catch { toast("error", "Failed to activate policy."); }
  finally { activating.value = null; }
}

async function switchWebsite() {
  selectedLevel.value = null;
  await loadLevels();
}

// ── Init ──────────────────────────────────────────────────────────────────────
onMounted(async () => {
  await websites.ensure();
  selectedWebsiteId.value = portal.website?.id ?? (isSuperadmin.value ? null : websites.list[0]?.id ?? null);
  await loadLevels();
});
watch(activeTab, (t) => { if (t === "tips" && !policies.value.length) loadPolicies(); });
</script>

<template>
  <div class="min-h-screen bg-gray-50">

    <!-- Header -->
    <div class="bg-white border-b border-gray-200 px-6 py-5">
      <div class="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 class="text-xl font-semibold text-gray-900">Writer Pay &amp; Levels</h1>
          <p class="text-sm text-gray-500 mt-0.5">Manage writer tier hierarchy, pay rates, capacity limits, and tip splits.</p>
          <p class="mt-1 text-xs font-medium text-gray-500">Website: {{ selectedWebsiteLabel }}</p>
        </div>
        <label v-if="isSuperadmin" class="min-w-72 text-xs font-medium text-gray-500">
          Manage website
          <select
            v-model.number="selectedWebsiteId"
            class="mt-1 w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-200"
            @change="switchWebsite"
          >
            <option :value="null" disabled>Select a website</option>
            <option v-for="site in websites.options" :key="site.value" :value="site.value">
              {{ site.label }}
            </option>
          </select>
        </label>
      </div>

      <!-- Tabs -->
      <div class="flex gap-1 mt-4">
        <button
          v-for="t in [{ key: 'levels', label: 'Writer Levels & Pay Rates' }, { key: 'tips', label: 'Tip Policy' }]"
          :key="t.key"
          class="flex items-center gap-1.5 px-4 py-2 text-sm font-medium rounded-lg transition-colors"
          :class="activeTab === t.key ? 'bg-indigo-600 text-white' : 'text-gray-600 hover:bg-gray-100'"
          @click="activeTab = t.key as Tab"
        >{{ t.label }}</button>
      </div>
    </div>

    <!-- Notice -->
    <div
      v-if="notice"
      class="mx-6 mt-4 px-4 py-3 rounded-lg text-sm font-medium"
      :class="notice.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'"
    >{{ notice.msg }}</div>

    <!-- ══ WRITER LEVELS TAB ══════════════════════════════════════════════════ -->
    <div v-if="activeTab === 'levels'" class="flex h-[calc(100vh-165px)]">

      <!-- Left: level list -->
      <div class="w-64 border-r border-gray-200 bg-white overflow-y-auto flex-shrink-0">
        <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100">
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Tiers</span>
          <button
            class="text-xs text-indigo-600 hover:underline flex items-center gap-1 disabled:cursor-not-allowed disabled:text-gray-300 disabled:no-underline"
            :disabled="needsWebsiteSelection"
            @click="openNewLevel"
          >
            <Plus class="w-3.5 h-3.5" /> Add
          </button>
        </div>
        <div v-if="levelsLoading" class="flex justify-center py-8"><RefreshCw class="w-5 h-5 text-gray-400 animate-spin" /></div>
        <div v-else class="divide-y divide-gray-50">
          <button
            v-for="level in levels"
            :key="level.id"
            class="w-full text-left px-4 py-3 hover:bg-gray-50 transition-colors"
            :class="selectedLevel?.id === level.id ? 'bg-indigo-50' : ''"
            @click="selectLevel(level)"
          >
            <div class="flex items-center justify-between gap-2">
              <span class="font-medium text-gray-900 text-sm">{{ level.name }}</span>
              <span v-if="level.is_default" class="text-xs text-indigo-600 font-semibold">default</span>
              <span v-if="!level.is_active" class="text-xs text-gray-400">off</span>
            </div>
            <p class="text-xs text-gray-400 mt-0.5">Order {{ level.display_order }}</p>
          </button>
        </div>
      </div>

      <!-- Right: settings editor -->
      <div v-if="selectedLevel" class="flex-1 overflow-y-auto p-6 space-y-6">

        <!-- Level meta actions -->
        <div class="flex items-start justify-between gap-4">
          <div>
            <h2 class="text-lg font-semibold text-gray-900">{{ selectedLevel.name }}</h2>
            <p v-if="selectedLevel.description" class="text-sm text-gray-500 mt-0.5">{{ selectedLevel.description }}</p>
          </div>
          <div class="flex gap-2">
            <button class="flex items-center gap-1.5 px-3 py-1.5 text-xs border border-gray-300 rounded-lg hover:bg-gray-50" @click="openEditLevel(selectedLevel)">
              Edit tier
            </button>
            <button
              v-if="!selectedLevel.is_default"
              class="flex items-center gap-1.5 px-3 py-1.5 text-xs text-red-600 border border-red-200 rounded-lg hover:bg-red-50"
              @click="deleteConfirm === selectedLevel.id ? deleteLevel(selectedLevel.id) : (deleteConfirm = selectedLevel.id)"
            >
              <Trash2 class="w-3.5 h-3.5" />
              {{ deleteConfirm === selectedLevel.id ? 'Confirm delete' : 'Delete' }}
            </button>
            <button v-if="deleteConfirm === selectedLevel.id" class="text-xs text-gray-500 hover:text-gray-700" @click="deleteConfirm = null">Cancel</button>
          </div>
        </div>

        <!-- Settings form -->
        <div v-if="selectedSettings" class="space-y-5">

          <!-- Pay rates -->
          <section class="rounded-xl border border-gray-200 bg-white p-5">
            <h3 class="text-sm font-semibold text-gray-900 mb-1">Pay rates (USD)</h3>
            <p class="text-xs text-gray-400 mb-4">
              Base rates apply to each unit within the agreed scope. Additional rates apply to each unit beyond the original scope.
            </p>

            <!-- Base rates row -->
            <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-3">Base pay — within scope</p>
            <div class="grid gap-4 sm:grid-cols-3 mb-5">
              <label v-for="f in [
                { key: 'base_pay_per_page',  label: 'Per page',  hint: 'Each written page in the order' },
                { key: 'base_pay_per_slide', label: 'Per slide', hint: 'Each presentation slide' },
                { key: 'base_pay_per_chart', label: 'Per chart', hint: 'Each chart or figure' },
              ]" :key="f.key" class="block space-y-1">
                <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">{{ f.label }}</span>
                <div class="relative">
                  <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">$</span>
                  <input v-model="(settingsDraft as any)[f.key]" type="number" min="0" step="0.01"
                    class="h-9 w-full rounded-lg border border-gray-300 pl-6 pr-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
                <p class="text-xs text-gray-400">{{ f.hint }}</p>
              </label>
            </div>

            <!-- Additional rates row -->
            <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-3">Additional pay — beyond original scope</p>
            <div class="grid gap-4 sm:grid-cols-3">
              <label v-for="f in [
                { key: 'additional_page_pay',  label: 'Per extra page',  hint: 'Pages added after the order starts' },
                { key: 'additional_slide_pay', label: 'Per extra slide', hint: 'Slides added after the order starts' },
                { key: 'additional_chart_pay', label: 'Per extra chart', hint: 'Charts added after the order starts' },
              ]" :key="f.key" class="block space-y-1">
                <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">{{ f.label }}</span>
                <div class="relative">
                  <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">$</span>
                  <input v-model="(settingsDraft as any)[f.key]" type="number" min="0" step="0.01"
                    class="h-9 w-full rounded-lg border border-gray-300 pl-6 pr-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
                <p class="text-xs text-gray-400">{{ f.hint }}</p>
              </label>
            </div>
          </section>

          <!-- Tip retention -->
          <section class="rounded-xl border border-amber-100 bg-amber-50 p-5">
            <h3 class="text-sm font-semibold text-gray-900 mb-1">Tip retention</h3>
            <p class="text-xs text-amber-700 mb-4">
              Defines the % of each client tip that the writer keeps at this tier.
              Set to 100 to pass the full tip to the writer. Overrides the global Tip Policy for this tier.
            </p>
            <div class="grid gap-4 sm:grid-cols-3">
              <label class="block space-y-1">
                <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Writer keeps (%)</span>
                <div class="relative">
                  <input v-model="settingsDraft.tip_percentage" type="number" min="0" max="100" step="0.01"
                    class="h-9 w-full rounded-lg border border-amber-200 bg-white px-3 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400" />
                  <span class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">%</span>
                </div>
                <p class="text-xs text-amber-700">Platform keeps {{ settingsDraft.tip_percentage ? (100 - parseFloat(settingsDraft.tip_percentage as string)).toFixed(2) : '?' }}%</p>
              </label>
            </div>
          </section>

          <!-- Capacity -->
          <section class="rounded-xl border border-gray-200 bg-white p-5">
            <h3 class="text-sm font-semibold text-gray-900 mb-1">Capacity limits</h3>
            <p class="text-xs text-gray-400 mb-4">Controls how many orders a writer at this tier can handle simultaneously.</p>
            <div class="grid gap-4 sm:grid-cols-3">
              <label v-for="f in [
                { key: 'max_active_orders',       label: 'Max concurrent active orders', hint: 'Total in-progress orders at any one time' },
                { key: 'max_manual_takes',         label: 'Max manual self-takes',        hint: 'Orders the writer can claim on their own per cycle' },
                { key: 'max_pending_assignments',  label: 'Max pending assignments',      hint: 'Queued system-assigned offers awaiting acceptance' },
              ]" :key="f.key" class="block space-y-1">
                <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">{{ f.label }}</span>
                <input v-model.number="(settingsDraft as any)[f.key]" type="number" min="0"
                  class="h-9 w-full rounded-lg border border-gray-300 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                <p class="text-xs text-gray-400">{{ f.hint }}</p>
              </label>
            </div>
          </section>

          <!-- Urgency -->
          <section class="rounded-xl border border-gray-200 bg-white p-5">
            <h3 class="text-sm font-semibold text-gray-900 mb-1">Urgency settings</h3>
            <p class="text-xs text-gray-400 mb-4">Orders due in fewer than the threshold hours are treated as urgent and earn the surcharge + multiplier.</p>
            <div class="grid gap-4 sm:grid-cols-3">
              <label class="block space-y-1">
                <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Urgency threshold (hrs)</span>
                <input v-model.number="settingsDraft.urgent_time_threshold_hours" type="number" min="1"
                  class="h-9 w-full rounded-lg border border-gray-300 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                <p class="text-xs text-gray-400">Orders due in &lt; this many hours are urgent</p>
              </label>
              <label class="block space-y-1">
                <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Flat surcharge (USD)</span>
                <div class="relative">
                  <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">$</span>
                  <input v-model="settingsDraft.urgent_order_surcharge" type="number" min="0" step="0.01"
                    class="h-9 w-full rounded-lg border border-gray-300 pl-6 pr-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
                <p class="text-xs text-gray-400">Added flat to earnings for urgent orders</p>
              </label>
              <label class="block space-y-1">
                <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Urgency multiplier (×)</span>
                <input v-model="settingsDraft.urgent_multiplier" type="number" min="1" step="0.01"
                  class="h-9 w-full rounded-lg border border-gray-300 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                <p class="text-xs text-gray-400">Multiplied against base pay for urgent orders</p>
              </label>
            </div>
          </section>

          <!-- Promotion eligibility -->
          <section class="rounded-xl border border-gray-200 bg-white p-5">
            <h3 class="text-sm font-semibold text-gray-900 mb-1">Promotion eligibility</h3>
            <p class="text-xs text-gray-400 mb-4">
              Minimum standards a writer must meet to be promoted into this tier.
              Rate fields are optional — leave blank to impose no limit.
            </p>

            <!-- Required thresholds -->
            <div class="grid gap-4 sm:grid-cols-3 mb-5">
              <label class="block space-y-1">
                <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Min completed orders</span>
                <input v-model.number="settingsDraft.min_completed_orders" type="number" min="0"
                  class="h-9 w-full rounded-lg border border-gray-300 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                <p class="text-xs text-gray-400">Total orders finished before this tier</p>
              </label>
              <label class="block space-y-1">
                <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Min rating (0–10)</span>
                <input v-model="settingsDraft.min_rating" type="number" min="0" max="10" step="0.01"
                  class="h-9 w-full rounded-lg border border-gray-300 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                <p class="text-xs text-gray-400">Average client rating required</p>
              </label>
              <label class="block space-y-1">
                <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Min successful self-takes</span>
                <input v-model.number="settingsDraft.min_successful_takes" type="number" min="0"
                  class="h-9 w-full rounded-lg border border-gray-300 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                <p class="text-xs text-gray-400">Manually claimed orders completed without incident</p>
              </label>
            </div>

            <!-- Optional rate caps -->
            <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-3">Quality rate limits (optional)</p>
            <div class="grid gap-4 sm:grid-cols-3">
              <label class="block space-y-1">
                <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Min completion rate (%)</span>
                <div class="relative">
                  <input
                    :value="settingsDraft.min_completion_rate ?? ''"
                    @input="(e: any) => { settingsDraft.min_completion_rate = e.target.value === '' ? null : e.target.value }"
                    type="number" min="0" max="100" step="0.01" placeholder="No minimum"
                    class="h-9 w-full rounded-lg border border-gray-300 px-3 pr-7 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                  <span class="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 text-xs">%</span>
                </div>
                <p class="text-xs text-gray-400">% of assigned orders the writer must complete</p>
              </label>
              <label class="block space-y-1">
                <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Max revision rate (%)</span>
                <div class="relative">
                  <input
                    :value="settingsDraft.max_revision_rate ?? ''"
                    @input="(e: any) => { settingsDraft.max_revision_rate = e.target.value === '' ? null : e.target.value }"
                    type="number" min="0" max="100" step="0.01" placeholder="No limit"
                    class="h-9 w-full rounded-lg border border-gray-300 px-3 pr-7 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                  <span class="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 text-xs">%</span>
                </div>
                <p class="text-xs text-gray-400">Max % of orders that can be sent for revision</p>
              </label>
              <label class="block space-y-1">
                <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Max lateness rate (%)</span>
                <div class="relative">
                  <input
                    :value="settingsDraft.max_lateness_rate ?? ''"
                    @input="(e: any) => { settingsDraft.max_lateness_rate = e.target.value === '' ? null : e.target.value }"
                    type="number" min="0" max="100" step="0.01" placeholder="No limit"
                    class="h-9 w-full rounded-lg border border-gray-300 px-3 pr-7 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                  <span class="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 text-xs">%</span>
                </div>
                <p class="text-xs text-gray-400">Max % of orders submitted past deadline</p>
              </label>
            </div>

            <!-- Warnings cap -->
            <div class="mt-5 max-w-xs">
              <label class="block space-y-1">
                <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Max active warnings</span>
                <input v-model.number="settingsDraft.max_warnings" type="number" min="0"
                  class="h-9 w-full rounded-lg border border-gray-300 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                <p class="text-xs text-gray-400">Writers with more than this many active warnings become eligible for demotion from this tier</p>
              </label>
            </div>
          </section>

          <!-- Save button -->
          <div class="flex justify-end">
            <button
              :disabled="savingSettings"
              class="flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 disabled:opacity-50"
              @click="saveSettings"
            >
              <RefreshCw v-if="savingSettings" class="w-4 h-4 animate-spin" />
              <Save v-else class="w-4 h-4" />
              Save settings for {{ selectedLevel.name }}
            </button>
          </div>
        </div>
      </div>

      <div v-else class="flex-1 flex flex-col items-center justify-center text-gray-400 p-12">
        <p class="text-sm">Select a tier from the left to edit its settings.</p>
      </div>
    </div>

    <!-- ══ TIP POLICY TAB ═════════════════════════════════════════════════════ -->
    <div v-else class="p-6 space-y-5 max-w-3xl">

      <div class="flex items-center justify-between">
        <p class="text-sm text-gray-500">
          One policy is active at a time. The active policy determines the writer/platform split for all tips.
          <span v-if="activePolicy" class="ml-1 font-medium text-green-700">Current: {{ activePolicy.name }} ({{ activePolicy.writer_percentage }}% writer)</span>
        </p>
        <div class="flex gap-2">
          <button class="flex items-center gap-1.5 rounded-lg border border-gray-300 px-3 py-2 text-sm hover:bg-gray-50" @click="loadPolicies">
            <RefreshCw class="w-4 h-4" :class="policyLoading ? 'animate-spin' : ''" />
          </button>
          <button class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700" @click="openNewPolicy">
            <Plus class="w-4 h-4" /> New policy
          </button>
        </div>
      </div>

      <div v-if="policyLoading" class="flex justify-center py-12">
        <RefreshCw class="w-6 h-6 text-gray-400 animate-spin" />
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="policy in policies"
          :key="policy.id"
          class="rounded-xl border bg-white p-5"
          :class="policy.is_active ? 'border-green-300 ring-1 ring-green-200' : 'border-gray-200'"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <p class="font-semibold text-gray-900">{{ policy.name }}</p>
                <StatusPill v-if="policy.is_active" label="Active" tone="success" />
              </div>
              <p v-if="policy.description" class="text-sm text-gray-500 mt-0.5">{{ policy.description }}</p>
            </div>
            <div class="flex gap-2 flex-shrink-0">
              <button
                v-if="!policy.is_active"
                :disabled="activating === policy.id"
                class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-green-700 border border-green-200 rounded-lg hover:bg-green-50 disabled:opacity-50"
                @click="activatePolicy(policy.id)"
              >
                <RefreshCw v-if="activating === policy.id" class="w-3 h-3 animate-spin" />
                <CheckCircle2 v-else class="w-3 h-3" />
                Activate
              </button>
              <button class="text-xs px-3 py-1.5 border border-gray-200 rounded-lg hover:bg-gray-50" @click="openEditPolicy(policy)">
                Edit
              </button>
            </div>
          </div>

          <!-- Policy details grid -->
          <div class="mt-4 grid gap-3 sm:grid-cols-4 text-sm">
            <div class="rounded-lg bg-gray-50 p-3 text-center">
              <p class="text-xs text-gray-500">Writer keeps</p>
              <p class="text-lg font-bold text-green-700 mt-0.5">{{ policy.writer_percentage }}%</p>
            </div>
            <div class="rounded-lg bg-gray-50 p-3 text-center">
              <p class="text-xs text-gray-500">Platform takes</p>
              <p class="text-lg font-bold text-gray-700 mt-0.5">{{ policy.platform_percentage }}%</p>
            </div>
            <div class="rounded-lg bg-gray-50 p-3 text-center">
              <p class="text-xs text-gray-500">Minimum tip</p>
              <p class="text-lg font-bold text-gray-700 mt-0.5">${{ policy.minimum_tip_amount }}</p>
            </div>
            <div class="rounded-lg bg-gray-50 p-3 text-center">
              <p class="text-xs text-gray-500">Max per day</p>
              <p class="text-lg font-bold text-gray-700 mt-0.5">{{ policy.maximum_tip_frequency_per_day }}</p>
            </div>
          </div>

          <div class="mt-3 flex flex-wrap gap-2">
            <span v-if="policy.allow_wallet_tips"    class="inline-flex items-center gap-1 rounded-full bg-blue-50 px-2 py-0.5 text-xs text-blue-700"><ShieldCheck class="w-3 h-3" />Wallet tips</span>
            <span v-if="policy.allow_external_tips"  class="inline-flex items-center gap-1 rounded-full bg-blue-50 px-2 py-0.5 text-xs text-blue-700"><ShieldCheck class="w-3 h-3" />External tips</span>
            <span v-if="policy.require_manual_review" class="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2 py-0.5 text-xs text-amber-700">Manual review required</span>
          </div>
        </div>

        <div v-if="!policies.length" class="py-12 text-center text-gray-400 text-sm">
          No tip policies yet. Create one to set the writer/platform split.
        </div>
      </div>
    </div>

    <!-- ── Level form modal ────────────────────────────────────────────────── -->
    <div v-if="levelForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-6 space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="font-semibold text-gray-900">{{ editingLevelId ? 'Edit tier' : 'New writer tier' }}</h3>
          <button @click="levelForm = false"><X class="w-5 h-5 text-gray-400 hover:text-gray-600" /></button>
        </div>
        <label class="block space-y-1">
          <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Tier name *</span>
          <input v-model="levelDraft.name" type="text" placeholder="e.g. Expert"
            class="w-full h-10 rounded-lg border border-gray-300 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        </label>
        <label class="block space-y-1">
          <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Description</span>
          <textarea v-model="levelDraft.description" rows="2"
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none" />
        </label>
        <label class="block space-y-1">
          <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Display order (lower = higher rank)</span>
          <input v-model.number="levelDraft.display_order" type="number" min="0"
            class="w-full h-10 rounded-lg border border-gray-300 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        </label>
        <div class="flex gap-4">
          <label class="flex items-center gap-2 text-sm cursor-pointer">
            <input v-model="levelDraft.is_active" type="checkbox" class="rounded border-gray-300 text-indigo-600" /> Active
          </label>
          <label class="flex items-center gap-2 text-sm cursor-pointer">
            <input v-model="levelDraft.is_default" type="checkbox" class="rounded border-gray-300 text-indigo-600" /> Default for new writers
          </label>
        </div>
        <div class="flex gap-2 justify-end pt-2">
          <button class="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50" @click="levelForm = false">Cancel</button>
          <button
            :disabled="savingLevel || !levelDraft.name.trim()"
            class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
            @click="saveLevel"
          >
            <RefreshCw v-if="savingLevel" class="w-4 h-4 animate-spin inline mr-1" />
            {{ editingLevelId ? 'Save changes' : 'Create tier' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ── Tip policy modal ────────────────────────────────────────────────── -->
    <div v-if="policyModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 overflow-y-auto py-8">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 p-6 space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="font-semibold text-gray-900">{{ editingPolicyId ? 'Edit tip policy' : 'New tip policy' }}</h3>
          <button @click="policyModal = false"><X class="w-5 h-5 text-gray-400 hover:text-gray-600" /></button>
        </div>

        <label class="block space-y-1">
          <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Policy name *</span>
          <input v-model="policyDraft.name" type="text" placeholder="e.g. Standard 90/10 split"
            class="w-full h-10 rounded-lg border border-gray-300 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        </label>

        <label class="block space-y-1">
          <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Description</span>
          <input v-model="policyDraft.description" type="text"
            class="w-full h-10 rounded-lg border border-gray-300 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        </label>

        <!-- Split row -->
        <div class="grid grid-cols-2 gap-3">
          <label class="block space-y-1">
            <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Writer keeps (%)</span>
            <div class="relative">
              <input v-model="policyDraft.writer_percentage" type="number" min="0" max="100" step="0.01"
                class="w-full h-10 rounded-lg border border-gray-300 px-3 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              <span class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">%</span>
            </div>
          </label>
          <label class="block space-y-1">
            <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Platform takes (%)</span>
            <div class="relative">
              <input :value="policyDraft.platform_percentage" readonly
                class="w-full h-10 rounded-lg border border-gray-200 bg-gray-50 px-3 pr-8 text-sm text-gray-500" />
              <span class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">%</span>
            </div>
          </label>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <label class="block space-y-1">
            <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Minimum tip ($)</span>
            <div class="relative">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">$</span>
              <input v-model="policyDraft.minimum_tip_amount" type="number" min="0" step="0.01"
                class="w-full h-10 rounded-lg border border-gray-300 pl-6 pr-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
          </label>
          <label class="block space-y-1">
            <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Review threshold ($)</span>
            <div class="relative">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">$</span>
              <input v-model="policyDraft.risk_review_threshold" type="number" min="0" step="0.01"
                class="w-full h-10 rounded-lg border border-gray-300 pl-6 pr-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
          </label>
        </div>

        <label class="block space-y-1">
          <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Max tips per client per day</span>
          <input v-model.number="policyDraft.maximum_tip_frequency_per_day" type="number" min="1"
            class="w-full h-10 rounded-lg border border-gray-300 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        </label>

        <div class="flex flex-wrap gap-4 text-sm">
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="policyDraft.allow_wallet_tips" type="checkbox" class="rounded border-gray-300 text-indigo-600" />
            Allow wallet tips
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="policyDraft.allow_external_tips" type="checkbox" class="rounded border-gray-300 text-indigo-600" />
            Allow external tips
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="policyDraft.require_manual_review" type="checkbox" class="rounded border-gray-300 text-indigo-600" />
            Require manual review
          </label>
        </div>

        <div class="flex gap-2 justify-end pt-2">
          <button class="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50" @click="policyModal = false">Cancel</button>
          <button
            :disabled="savingPolicy || !policyDraft.name.trim()"
            class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
            @click="savePolicy"
          >
            <RefreshCw v-if="savingPolicy" class="w-4 h-4 animate-spin inline mr-1" />
            {{ editingPolicyId ? 'Save changes' : 'Create policy' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>
