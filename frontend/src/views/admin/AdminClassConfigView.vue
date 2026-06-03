<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { BookOpen, Plus, RefreshCw, Save } from "@lucide/vue";
import { classesApi } from "@/api/classes";
import { useAuthStore } from "@/stores/auth";
import { usePortalContextStore } from "@/stores/portalContext";
import { useWebsitesStore } from "@/stores/websites";
import type { ClassServiceConfig } from "@/types/classes";

type Draft = {
  id: number | null;
  name: string;
  slug: string;
  description: string;
  service_type: string;
  pricing_mode: "quote" | "package";
  base_price: string;
  currency: string;
  deposit_percentage: string;
  quote_expiry_hours: number;
  requires_portal_access: boolean;
  allow_installments: boolean;
  require_deposit_before_start: boolean;
  is_active: boolean;
  display_order: number;
};

type DurationRow = { key: string; label: string; weeks: number | null; description: string };
type WorkloadRow = { key: string; label: string; complexity: string; description: string; price_hint: string };
type TaskRow = { key: string; label: string; description: string; required: boolean };
type RequiredFieldRow = { value: string };

const emptyDurations = [
  { key: "4_weeks", label: "4 weeks", weeks: 4 },
  { key: "8_weeks", label: "8 weeks", weeks: 8 },
  { key: "12_weeks", label: "12 weeks", weeks: 12 },
  { key: "semester", label: "Full semester", weeks: 16 },
];
const emptyWorkloads = [
  { key: "light", label: "Light", complexity: "low" },
  { key: "standard", label: "Standard", complexity: "medium" },
  { key: "heavy", label: "Heavy", complexity: "high" },
];
const emptyTasks = [
  { key: "assignments", label: "Assignments" },
  { key: "discussions", label: "Discussion posts" },
  { key: "quizzes", label: "Quizzes" },
];

const configs = ref<ClassServiceConfig[]>([]);
const durationRows = ref<DurationRow[]>([]);
const workloadRows = ref<WorkloadRow[]>([]);
const taskRows = ref<TaskRow[]>([]);
const requiredFieldRows = ref<RequiredFieldRow[]>([]);
const selectedId = ref<number | null>(null);
const isLoading = ref(false);
const isSaving = ref(false);
const error = ref("");
const notice = ref("");
const selectedWebsiteId = ref<number | null>(null);

const auth = useAuthStore();
const portal = usePortalContextStore();
const websites = useWebsitesStore();

const draft = reactive<Draft>({
  id: null,
  name: "",
  slug: "",
  description: "",
  service_type: "full_class",
  pricing_mode: "quote",
  base_price: "0.00",
  currency: "USD",
  deposit_percentage: "50.00",
  quote_expiry_hours: 72,
  requires_portal_access: true,
  allow_installments: true,
  require_deposit_before_start: true,
  is_active: true,
  display_order: 0,
});

const activeConfigs = computed(() => configs.value.filter((cfg) => cfg.is_active));
const isSuperadmin = computed(() => auth.role === "superadmin");
const websiteParams = computed(() =>
  isSuperadmin.value && selectedWebsiteId.value ? { website_id: selectedWebsiteId.value } : undefined,
);
const selectedWebsiteLabel = computed(() => {
  if (selectedWebsiteId.value) return websites.labelById(selectedWebsiteId.value);
  if (portal.website) return `${portal.website.name} (${portal.website.domain})`;
  const config = configs.value[0];
  if (config?.website_name || config?.website_domain) {
    return config.website_domain ? `${config.website_name || config.website_domain} (${config.website_domain})` : config.website_name || "Current website";
  }
  return "Current website";
});

function configWebsiteLabel(cfg: ClassServiceConfig): string {
  if (cfg.website) return websites.labelById(cfg.website);
  if (cfg.website_name || cfg.website_domain) {
    return cfg.website_domain ? `${cfg.website_name || cfg.website_domain} (${cfg.website_domain})` : cfg.website_name || "Current website";
  }
  return selectedWebsiteLabel.value;
}

function resetRows() {
  durationRows.value = emptyDurations.map((row) => ({ ...row, description: "" }));
  workloadRows.value = emptyWorkloads.map((row) => ({ ...row, description: "", price_hint: "" }));
  taskRows.value = emptyTasks.map((row) => ({ ...row, description: "", required: false }));
  requiredFieldRows.value = ["title", "subject", "academic_level", "starts_on", "ends_on"].map((value) => ({ value }));
}

function addDuration() {
  durationRows.value.push({ key: "", label: "", weeks: null, description: "" });
}

function addWorkload() {
  workloadRows.value.push({ key: "", label: "", complexity: "medium", description: "", price_hint: "" });
}

function addTask() {
  taskRows.value.push({ key: "", label: "", description: "", required: false });
}

function addRequiredField() {
  requiredFieldRows.value.push({ value: "" });
}

function cleanRows() {
  return {
    duration_options: durationRows.value
      .filter((row) => row.key.trim() && row.label.trim())
      .map((row) => ({
        key: row.key.trim(),
        label: row.label.trim(),
        ...(row.weeks ? { weeks: row.weeks } : {}),
        ...(row.description.trim() ? { description: row.description.trim() } : {}),
      })),
    workload_options: workloadRows.value
      .filter((row) => row.key.trim() && row.label.trim())
      .map((row) => ({
        key: row.key.trim(),
        label: row.label.trim(),
        complexity: row.complexity || "medium",
        ...(row.description.trim() ? { description: row.description.trim() } : {}),
        ...(row.price_hint.trim() ? { price_hint: row.price_hint.trim() } : {}),
      })),
    task_options: taskRows.value
      .filter((row) => row.key.trim() && row.label.trim())
      .map((row) => ({
        key: row.key.trim(),
        label: row.label.trim(),
        required: row.required,
        ...(row.description.trim() ? { description: row.description.trim() } : {}),
      })),
    required_fields: requiredFieldRows.value
      .map((row) => row.value.trim())
      .filter(Boolean),
  };
}

function resetDraft() {
  selectedId.value = null;
  Object.assign(draft, {
    id: null,
    name: "",
    slug: "",
    description: "",
    service_type: "full_class",
    pricing_mode: "quote",
    base_price: "0.00",
    currency: "USD",
    deposit_percentage: "50.00",
    quote_expiry_hours: 72,
    requires_portal_access: true,
    allow_installments: true,
    require_deposit_before_start: true,
    is_active: true,
    display_order: 0,
  });
  resetRows();
}

function editConfig(cfg: ClassServiceConfig) {
  selectedId.value = cfg.id;
  Object.assign(draft, {
    id: cfg.id,
    name: cfg.name,
    slug: cfg.slug,
    description: cfg.description,
    service_type: cfg.service_type,
    pricing_mode: cfg.pricing_mode,
    base_price: cfg.base_price,
    currency: cfg.currency,
    deposit_percentage: cfg.deposit_percentage,
    quote_expiry_hours: cfg.quote_expiry_hours,
    requires_portal_access: cfg.requires_portal_access,
    allow_installments: cfg.allow_installments,
    require_deposit_before_start: cfg.require_deposit_before_start,
    is_active: cfg.is_active,
    display_order: cfg.display_order,
  });
  durationRows.value = cfg.duration_options.map((row) => ({
    key: row.key,
    label: row.label,
    weeks: row.weeks ?? null,
    description: row.description ?? "",
  }));
  workloadRows.value = cfg.workload_options.map((row) => ({
    key: row.key,
    label: row.label,
    complexity: row.complexity ?? "medium",
    description: row.description ?? "",
    price_hint: row.price_hint ?? "",
  }));
  taskRows.value = cfg.task_options.map((row) => ({
    key: row.key,
    label: row.label,
    description: row.description ?? "",
    required: Boolean(row.required),
  }));
  requiredFieldRows.value = cfg.required_fields.map((value) => ({ value }));
}

async function load() {
  isLoading.value = true;
  error.value = "";
  try {
    const { data } = await classesApi.configs(websiteParams.value);
    configs.value = data;
    const selected = data.find((cfg) => cfg.id === selectedId.value) ?? data[0];
    if (selected) editConfig(selected);
    else resetDraft();
  } catch {
    error.value = "Unable to load class configs.";
    configs.value = [];
  } finally {
    isLoading.value = false;
  }
}

async function save() {
  if (!draft.name.trim() || !draft.slug.trim()) {
    error.value = "Name and slug are required.";
    return;
  }
  isSaving.value = true;
  error.value = "";
  notice.value = "";
  try {
    const rows = cleanRows();
    const payload = {
      name: draft.name,
      slug: draft.slug,
      description: draft.description,
      service_type: draft.service_type,
      pricing_mode: draft.pricing_mode,
      base_price: draft.base_price,
      currency: draft.currency,
      deposit_percentage: draft.deposit_percentage,
      quote_expiry_hours: draft.quote_expiry_hours,
      requires_portal_access: draft.requires_portal_access,
      allow_installments: draft.allow_installments,
      require_deposit_before_start: draft.require_deposit_before_start,
      is_active: draft.is_active,
      display_order: draft.display_order,
      ...rows,
    };
    const { data } = draft.id
      ? await classesApi.updateConfig(draft.id, payload, websiteParams.value)
      : await classesApi.createConfig(payload, websiteParams.value);
    notice.value = "Class config saved.";
    await load();
    editConfig(data);
  } catch (caught) {
    error.value = caught instanceof Error ? caught.message : "Unable to save class config.";
  } finally {
    isSaving.value = false;
  }
}

async function switchWebsite() {
  resetDraft();
  await load();
}

onMounted(async () => {
  await websites.ensure();
  selectedWebsiteId.value = portal.website?.id ?? websites.list[0]?.id ?? null;
  await load();
});
</script>

<template>
  <div class="min-h-full bg-slate-50 p-6">
    <div class="mx-auto max-w-7xl space-y-5">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-xl font-bold text-ink">Class Management</h1>
          <p class="text-sm text-graphite">Preset client-facing class services, scope choices, and payment policy.</p>
          <p class="mt-1 text-xs font-medium text-graphite">Website: {{ selectedWebsiteLabel }}</p>
        </div>
        <div class="flex flex-wrap items-center justify-end gap-2">
          <label v-if="isSuperadmin" class="min-w-64 text-xs font-medium text-graphite">
            Manage website
            <select
              v-model.number="selectedWebsiteId"
              class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-ink focus-ring"
              @change="switchWebsite"
            >
              <option v-for="site in websites.options" :key="site.value" :value="site.value">{{ site.label }}</option>
            </select>
          </label>
          <button class="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-graphite hover:text-ink" @click="resetDraft">
            <Plus class="size-4" /> New preset
          </button>
          <button class="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-graphite hover:text-ink" @click="load">
            <RefreshCw class="size-4" :class="{ 'animate-spin': isLoading }" /> Refresh
          </button>
        </div>
      </div>

      <div class="grid gap-3 sm:grid-cols-3">
        <div class="rounded-lg border border-slate-200 bg-white p-4">
          <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Active presets</p>
          <p class="mt-1 text-2xl font-bold text-ink">{{ activeConfigs.length }}</p>
        </div>
        <div class="rounded-lg border border-slate-200 bg-white p-4">
          <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Total presets</p>
          <p class="mt-1 text-2xl font-bold text-ink">{{ configs.length }}</p>
        </div>
        <div class="rounded-lg border border-slate-200 bg-white p-4">
          <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Selected</p>
          <p class="mt-1 truncate text-lg font-bold text-ink">{{ draft.name || "New preset" }}</p>
        </div>
      </div>

      <div v-if="error" class="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</div>
      <div v-if="notice" class="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ notice }}</div>

      <div class="grid gap-5 lg:grid-cols-[22rem_1fr]">
        <section class="overflow-hidden rounded-lg border border-slate-200 bg-white">
          <div class="border-b border-slate-100 px-4 py-3">
            <h2 class="text-sm font-semibold text-ink">Presets</h2>
          </div>
          <div v-if="isLoading" class="py-12 text-center text-graphite">Loading…</div>
          <div v-else-if="!configs.length" class="py-12 text-center">
            <BookOpen class="mx-auto mb-3 size-9 text-slate-300" />
            <p class="text-sm text-graphite">No presets yet.</p>
          </div>
          <button
            v-for="cfg in configs"
            v-else
            :key="cfg.id"
            class="block w-full border-b border-slate-50 px-4 py-3 text-left hover:bg-slate-50"
            :class="{ 'bg-berry/5': selectedId === cfg.id }"
            @click="editConfig(cfg)"
          >
            <p class="font-medium text-ink">{{ cfg.name }}</p>
            <p class="mt-0.5 text-xs text-graphite">{{ cfg.pricing_mode }} · {{ cfg.duration_options.length }} durations · {{ cfg.task_options.length }} tasks</p>
            <p class="mt-1 text-xs text-slate-400">{{ configWebsiteLabel(cfg) }}</p>
          </button>
        </section>

        <section class="rounded-lg border border-slate-200 bg-white p-5">
          <div class="mb-4 flex items-center justify-between">
            <div>
              <h2 class="text-sm font-semibold text-ink">{{ draft.id ? "Edit preset" : "Create preset" }}</h2>
              <p class="mt-0.5 text-xs text-graphite">{{ selectedWebsiteLabel }}</p>
            </div>
            <button class="inline-flex items-center gap-2 rounded-lg bg-berry px-4 py-2 text-sm font-semibold text-white hover:bg-berry/90 disabled:opacity-60" :disabled="isSaving" @click="save">
              <Save class="size-4" /> {{ isSaving ? "Saving…" : "Save preset" }}
            </button>
          </div>

          <div class="grid gap-4 sm:grid-cols-2">
            <label class="text-sm">
              <span class="mb-1 block font-medium text-ink">Name</span>
              <input v-model="draft.name" class="w-full rounded-lg border border-slate-200 px-3 py-2 focus-ring" />
            </label>
            <label class="text-sm">
              <span class="mb-1 block font-medium text-ink">Slug</span>
              <input v-model="draft.slug" class="w-full rounded-lg border border-slate-200 px-3 py-2 focus-ring" />
            </label>
            <label class="text-sm">
              <span class="mb-1 block font-medium text-ink">Service type</span>
              <input v-model="draft.service_type" class="w-full rounded-lg border border-slate-200 px-3 py-2 focus-ring" />
            </label>
            <label class="text-sm">
              <span class="mb-1 block font-medium text-ink">Pricing mode</span>
              <select v-model="draft.pricing_mode" class="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 focus-ring">
                <option value="quote">Quote after review</option>
                <option value="package">Package estimate</option>
              </select>
            </label>
            <label class="text-sm sm:col-span-2">
              <span class="mb-1 block font-medium text-ink">Description</span>
              <textarea v-model="draft.description" rows="3" class="w-full rounded-lg border border-slate-200 px-3 py-2 focus-ring" />
            </label>
            <label class="text-sm">
              <span class="mb-1 block font-medium text-ink">Base price</span>
              <input v-model="draft.base_price" class="w-full rounded-lg border border-slate-200 px-3 py-2 focus-ring" />
            </label>
            <label class="text-sm">
              <span class="mb-1 block font-medium text-ink">Currency</span>
              <input v-model="draft.currency" class="w-full rounded-lg border border-slate-200 px-3 py-2 focus-ring" />
            </label>
            <label class="text-sm">
              <span class="mb-1 block font-medium text-ink">Deposit %</span>
              <input v-model="draft.deposit_percentage" class="w-full rounded-lg border border-slate-200 px-3 py-2 focus-ring" />
            </label>
            <label class="text-sm">
              <span class="mb-1 block font-medium text-ink">Quote expiry hours</span>
              <input v-model.number="draft.quote_expiry_hours" type="number" class="w-full rounded-lg border border-slate-200 px-3 py-2 focus-ring" />
            </label>
          </div>

          <div class="mt-4 grid gap-3 sm:grid-cols-2">
            <label class="flex items-center gap-2 text-sm text-graphite"><input v-model="draft.is_active" type="checkbox" class="rounded accent-berry" /> Active</label>
            <label class="flex items-center gap-2 text-sm text-graphite"><input v-model="draft.requires_portal_access" type="checkbox" class="rounded accent-berry" /> Requires portal access</label>
            <label class="flex items-center gap-2 text-sm text-graphite"><input v-model="draft.allow_installments" type="checkbox" class="rounded accent-berry" /> Allow installments</label>
            <label class="flex items-center gap-2 text-sm text-graphite"><input v-model="draft.require_deposit_before_start" type="checkbox" class="rounded accent-berry" /> Require deposit before start</label>
          </div>

          <div class="mt-5 space-y-5">
            <div class="rounded-lg border border-slate-200 p-4">
              <div class="mb-3 flex items-center justify-between">
                <h3 class="text-sm font-semibold text-ink">Duration Options</h3>
                <button class="text-xs font-medium text-berry hover:underline" @click="addDuration">Add duration</button>
              </div>
              <div class="space-y-2">
                <div v-for="(row, index) in durationRows" :key="index" class="grid gap-2 sm:grid-cols-[1fr_1fr_6rem_1.5fr_2rem]">
                  <input v-model="row.key" placeholder="key" class="rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring" />
                  <input v-model="row.label" placeholder="Label" class="rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring" />
                  <input v-model.number="row.weeks" type="number" placeholder="Weeks" class="rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring" />
                  <input v-model="row.description" placeholder="Description" class="rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring" />
                  <button class="rounded-lg border border-slate-200 text-slate-400 hover:text-rose-600" @click="durationRows.splice(index, 1)">x</button>
                </div>
              </div>
            </div>

            <div class="rounded-lg border border-slate-200 p-4">
              <div class="mb-3 flex items-center justify-between">
                <h3 class="text-sm font-semibold text-ink">Workload Options</h3>
                <button class="text-xs font-medium text-berry hover:underline" @click="addWorkload">Add workload</button>
              </div>
              <div class="space-y-2">
                <div v-for="(row, index) in workloadRows" :key="index" class="grid gap-2 sm:grid-cols-[1fr_1fr_9rem_1.5fr_1fr_2rem]">
                  <input v-model="row.key" placeholder="key" class="rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring" />
                  <input v-model="row.label" placeholder="Label" class="rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring" />
                  <select v-model="row.complexity" class="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus-ring">
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="very_high">Very high</option>
                  </select>
                  <input v-model="row.description" placeholder="Description" class="rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring" />
                  <input v-model="row.price_hint" placeholder="Price hint" class="rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring" />
                  <button class="rounded-lg border border-slate-200 text-slate-400 hover:text-rose-600" @click="workloadRows.splice(index, 1)">x</button>
                </div>
              </div>
            </div>

            <div class="rounded-lg border border-slate-200 p-4">
              <div class="mb-3 flex items-center justify-between">
                <h3 class="text-sm font-semibold text-ink">Task Options</h3>
                <button class="text-xs font-medium text-berry hover:underline" @click="addTask">Add task</button>
              </div>
              <div class="space-y-2">
                <div v-for="(row, index) in taskRows" :key="index" class="grid gap-2 sm:grid-cols-[1fr_1fr_1.5fr_7rem_2rem]">
                  <input v-model="row.key" placeholder="key" class="rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring" />
                  <input v-model="row.label" placeholder="Label" class="rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring" />
                  <input v-model="row.description" placeholder="Description" class="rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring" />
                  <label class="flex items-center gap-2 text-sm text-graphite"><input v-model="row.required" type="checkbox" class="rounded accent-berry" /> Required</label>
                  <button class="rounded-lg border border-slate-200 text-slate-400 hover:text-rose-600" @click="taskRows.splice(index, 1)">x</button>
                </div>
              </div>
            </div>

            <div class="rounded-lg border border-slate-200 p-4">
              <div class="mb-3 flex items-center justify-between">
                <h3 class="text-sm font-semibold text-ink">Required Fields</h3>
                <button class="text-xs font-medium text-berry hover:underline" @click="addRequiredField">Add field</button>
              </div>
              <div class="grid gap-2 sm:grid-cols-2">
                <div v-for="(row, index) in requiredFieldRows" :key="index" class="grid grid-cols-[1fr_2rem] gap-2">
                  <input v-model="row.value" placeholder="field_name" class="rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring" />
                  <button class="rounded-lg border border-slate-200 text-slate-400 hover:text-rose-600" @click="requiredFieldRows.splice(index, 1)">x</button>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>
