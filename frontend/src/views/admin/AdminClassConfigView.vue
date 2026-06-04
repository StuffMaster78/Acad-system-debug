<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import {
  BookOpen, ChevronRight, Plus, RefreshCw, Save, Settings, Trash2, X,
} from "@lucide/vue";
import { classesApi } from "@/api/classes";
import { useAuthStore } from "@/stores/auth";
import { usePortalContextStore } from "@/stores/portalContext";
import { useWebsitesStore } from "@/stores/websites";
import type { ClassServiceConfig } from "@/types/classes";

// ── Types ─────────────────────────────────────────────────────────────────────
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
type DurationRow  = { key: string; label: string; weeks: number | null; description: string };
type WorkloadRow  = { key: string; label: string; complexity: string; description: string; price_hint: string };
type TaskRow      = { key: string; label: string; description: string; required: boolean };
type RequiredFieldRow = { value: string };

// ── Default row seeds ─────────────────────────────────────────────────────────
const emptyDurations = [
  { key: "4_weeks",  label: "4 weeks",       weeks: 4  },
  { key: "8_weeks",  label: "8 weeks",       weeks: 8  },
  { key: "12_weeks", label: "12 weeks",      weeks: 12 },
  { key: "semester", label: "Full semester", weeks: 16 },
];
const emptyWorkloads = [
  { key: "light",    label: "Light",    complexity: "low"    },
  { key: "standard", label: "Standard", complexity: "medium" },
  { key: "heavy",    label: "Heavy",    complexity: "high"   },
];
const emptyTasks = [
  { key: "assignments",  label: "Assignments"      },
  { key: "discussions",  label: "Discussion posts" },
  { key: "quizzes",      label: "Quizzes"          },
];

// ── State ─────────────────────────────────────────────────────────────────────
const configs           = ref<ClassServiceConfig[]>([]);
const durationRows      = ref<DurationRow[]>([]);
const workloadRows      = ref<WorkloadRow[]>([]);
const taskRows          = ref<TaskRow[]>([]);
const requiredFieldRows = ref<RequiredFieldRow[]>([]);
const selectedId        = ref<number | null>(null);
const isLoading         = ref(false);
const isSaving          = ref(false);
const error             = ref("");
const notice            = ref("");
const selectedWebsiteId = ref<number | null>(null);
const confirmDelete     = ref<number | null>(null);

const auth    = useAuthStore();
const portal  = usePortalContextStore();
const websites = useWebsitesStore();

const activeConfigs  = computed(() => configs.value.filter((c) => c.is_active));
const isSuperadmin   = computed(() => auth.role === "superadmin");
const websiteParams  = computed(() =>
  isSuperadmin.value && selectedWebsiteId.value ? { website_id: selectedWebsiteId.value } : undefined
);

// ── Helpers ───────────────────────────────────────────────────────────────────
function configWebsiteLabel(cfg: ClassServiceConfig): string {
  if (cfg.website) return websites.labelById(cfg.website);
  if (cfg.website_name || cfg.website_domain)
    return cfg.website_domain ? `${cfg.website_name || cfg.website_domain}` : cfg.website_name || "";
  return "";
}

function resetRows() {
  durationRows.value  = emptyDurations.map((r) => ({ ...r, description: "" }));
  workloadRows.value  = emptyWorkloads.map((r) => ({ ...r, description: "", price_hint: "" }));
  taskRows.value      = emptyTasks.map((r)    => ({ ...r, description: "", required: false }));
  requiredFieldRows.value = ["title", "subject", "academic_level", "starts_on", "ends_on"].map((v) => ({ value: v }));
}

function resetDraft() {
  selectedId.value = null;
  Object.assign(draft, {
    id: null, name: "", slug: "", description: "", service_type: "full_class",
    pricing_mode: "quote", base_price: "0.00", currency: "USD",
    deposit_percentage: "50.00", quote_expiry_hours: 72,
    requires_portal_access: true, allow_installments: true,
    require_deposit_before_start: true, is_active: true, display_order: 0,
  });
  resetRows();
}

function editConfig(cfg: ClassServiceConfig) {
  selectedId.value = cfg.id;
  Object.assign(draft, {
    id: cfg.id, name: cfg.name, slug: cfg.slug, description: cfg.description,
    service_type: cfg.service_type, pricing_mode: cfg.pricing_mode,
    base_price: cfg.base_price, currency: cfg.currency,
    deposit_percentage: cfg.deposit_percentage,
    quote_expiry_hours: cfg.quote_expiry_hours,
    requires_portal_access: cfg.requires_portal_access,
    allow_installments: cfg.allow_installments,
    require_deposit_before_start: cfg.require_deposit_before_start,
    is_active: cfg.is_active, display_order: cfg.display_order,
  });
  durationRows.value  = cfg.duration_options.map((r) => ({ key: r.key, label: r.label, weeks: r.weeks ?? null, description: r.description ?? "" }));
  workloadRows.value  = cfg.workload_options.map((r) => ({ key: r.key, label: r.label, complexity: r.complexity ?? "medium", description: r.description ?? "", price_hint: r.price_hint ?? "" }));
  taskRows.value      = cfg.task_options.map((r) => ({ key: r.key, label: r.label, description: r.description ?? "", required: Boolean(r.required) }));
  requiredFieldRows.value = cfg.required_fields.map((v) => ({ value: v }));
}

function cleanRows() {
  return {
    duration_options: durationRows.value.filter((r) => r.key.trim() && r.label.trim()).map((r) => ({
      key: r.key.trim(), label: r.label.trim(),
      ...(r.weeks ? { weeks: r.weeks } : {}),
      ...(r.description.trim() ? { description: r.description.trim() } : {}),
    })),
    workload_options: workloadRows.value.filter((r) => r.key.trim() && r.label.trim()).map((r) => ({
      key: r.key.trim(), label: r.label.trim(), complexity: r.complexity || "medium",
      ...(r.description.trim() ? { description: r.description.trim() } : {}),
      ...(r.price_hint.trim() ? { price_hint: r.price_hint.trim() } : {}),
    })),
    task_options: taskRows.value.filter((r) => r.key.trim() && r.label.trim()).map((r) => ({
      key: r.key.trim(), label: r.label.trim(), required: r.required,
      ...(r.description.trim() ? { description: r.description.trim() } : {}),
    })),
    required_fields: requiredFieldRows.value.map((r) => r.value.trim()).filter(Boolean),
  };
}

// ── Data operations ───────────────────────────────────────────────────────────
async function load() {
  isLoading.value = true;
  error.value = "";
  try {
    const { data } = await classesApi.configs(websiteParams.value);
    configs.value = data;
    const selected = data.find((c) => c.id === selectedId.value) ?? data[0];
    if (selected) editConfig(selected);
    else resetDraft();
  } catch {
    error.value = "Unable to load class configurations.";
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
    const payload = { ...draft, ...cleanRows() } as Record<string, unknown>;
    delete payload.id;
    const { data } = draft.id
      ? await classesApi.updateConfig(draft.id, payload as Partial<ClassServiceConfig>, websiteParams.value)
      : await classesApi.createConfig(payload as Partial<ClassServiceConfig>, websiteParams.value);
    notice.value = draft.id ? "Configuration updated." : "Configuration created.";
    await load();
    editConfig(data);
  } catch (caught) {
    error.value = caught instanceof Error ? caught.message : "Unable to save configuration.";
  } finally {
    isSaving.value = false;
  }
}

async function toggleActive(cfg: ClassServiceConfig) {
  try {
    await classesApi.updateConfig(cfg.id, { is_active: !cfg.is_active }, websiteParams.value);
    await load();
  } catch {
    error.value = "Unable to update status.";
  }
}

onMounted(async () => {
  await websites.ensure();
  selectedWebsiteId.value = portal.website?.id ?? websites.list[0]?.id ?? null;
  await load();
});

const draft = reactive<Draft>({
  id: null, name: "", slug: "", description: "",
  service_type: "full_class", pricing_mode: "quote",
  base_price: "0.00", currency: "USD", deposit_percentage: "50.00",
  quote_expiry_hours: 72, requires_portal_access: true,
  allow_installments: true, require_deposit_before_start: true,
  is_active: true, display_order: 0,
});
</script>

<template>
  <div class="min-h-full bg-slate-50">
    <!-- ── Page header ─────────────────────────────────────────────────────── -->
    <div class="border-b border-slate-200 bg-white px-6 py-5">
      <div class="mx-auto flex max-w-7xl items-start justify-between gap-4">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-signal/10">
            <Settings class="h-5 w-5 text-signal" />
          </div>
          <div>
            <h1 class="text-lg font-bold text-ink">Class Management</h1>
            <p class="text-sm text-graphite">Configure client-facing class services, scope options, and payment policy.</p>
          </div>
        </div>

        <div class="flex shrink-0 items-center gap-2">
          <!-- Superadmin website selector -->
          <div v-if="isSuperadmin" class="flex items-center gap-2">
            <span class="text-xs font-semibold text-graphite">Website</span>
            <select
              v-model.number="selectedWebsiteId"
              class="focus-ring h-9 rounded-md border border-slate-200 bg-white px-3 text-sm"
              @change="load"
            >
              <option v-for="site in websites.options" :key="site.value" :value="site.value">{{ site.label }}</option>
            </select>
          </div>
          <button
            class="focus-ring inline-flex h-9 items-center gap-1.5 rounded-md border border-slate-200 bg-white px-3 text-sm font-medium text-graphite hover:text-ink"
            @click="load"
          >
            <RefreshCw class="h-4 w-4" :class="{ 'animate-spin': isLoading }" />
            Refresh
          </button>
          <button
            class="focus-ring inline-flex h-9 items-center gap-1.5 rounded-md bg-signal px-4 text-sm font-semibold text-white hover:bg-emerald-600"
            @click="resetDraft"
          >
            <Plus class="h-4 w-4" />
            New config
          </button>
        </div>
      </div>
    </div>

    <div class="mx-auto max-w-7xl px-6 py-5 space-y-4">

      <!-- ── Status/error banners ──────────────────────────────────────────── -->
      <div v-if="error" class="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</div>
      <div v-if="notice" class="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ notice }}</div>

      <!-- ── Summary strip ─────────────────────────────────────────────────── -->
      <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <div class="rounded-xl border border-slate-200 bg-white px-4 py-3">
          <p class="text-xs font-semibold uppercase text-graphite">Active</p>
          <p class="mt-1 text-2xl font-bold text-ink">{{ activeConfigs.length }}</p>
        </div>
        <div class="rounded-xl border border-slate-200 bg-white px-4 py-3">
          <p class="text-xs font-semibold uppercase text-graphite">Total</p>
          <p class="mt-1 text-2xl font-bold text-ink">{{ configs.length }}</p>
        </div>
        <div class="rounded-xl border border-slate-200 bg-white px-4 py-3">
          <p class="text-xs font-semibold uppercase text-graphite">Durations</p>
          <p class="mt-1 text-2xl font-bold text-ink">{{ durationRows.length }}</p>
        </div>
        <div class="rounded-xl border border-slate-200 bg-white px-4 py-3">
          <p class="text-xs font-semibold uppercase text-graphite">Task types</p>
          <p class="mt-1 text-2xl font-bold text-ink">{{ taskRows.length }}</p>
        </div>
      </div>

      <!-- ── Main layout ───────────────────────────────────────────────────── -->
      <div class="grid gap-5 lg:grid-cols-[280px_1fr]">

        <!-- ── Left: preset list ─────────────────────────────────────────── -->
        <aside class="space-y-2">
          <div v-if="isLoading" class="rounded-xl border border-slate-200 bg-white py-12 text-center text-sm text-graphite">
            Loading…
          </div>
          <div v-else-if="!configs.length" class="rounded-xl border border-dashed border-slate-200 py-12 text-center">
            <BookOpen class="mx-auto mb-3 h-9 w-9 text-slate-300" />
            <p class="text-sm text-graphite">No configurations yet.</p>
            <button class="mt-3 text-sm font-semibold text-signal hover:underline" @click="resetDraft">Create the first one</button>
          </div>
          <button
            v-for="cfg in configs"
            v-else
            :key="cfg.id"
            class="group w-full rounded-xl border px-4 py-3 text-left transition-all"
            :class="selectedId === cfg.id
              ? 'border-signal bg-signal/5 shadow-sm'
              : 'border-slate-200 bg-white hover:border-slate-300 hover:shadow-sm'"
            @click="editConfig(cfg)"
          >
            <div class="flex items-start justify-between gap-2">
              <div class="min-w-0 flex-1">
                <div class="flex items-center gap-2">
                  <p class="truncate text-sm font-semibold text-ink">{{ cfg.name }}</p>
                  <span
                    class="shrink-0 rounded-full px-1.5 py-0.5 text-[10px] font-semibold"
                    :class="cfg.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'"
                  >{{ cfg.is_active ? "Active" : "Inactive" }}</span>
                </div>
                <p class="mt-0.5 text-xs text-graphite">{{ cfg.pricing_mode }} · {{ cfg.duration_options.length }}d · {{ cfg.task_options.length }}t</p>
                <p v-if="configWebsiteLabel(cfg)" class="mt-0.5 text-[10px] text-graphite/60">{{ configWebsiteLabel(cfg) }}</p>
              </div>
              <ChevronRight
                class="mt-0.5 h-4 w-4 shrink-0 transition-transform text-slate-300"
                :class="selectedId === cfg.id ? 'text-signal rotate-90' : 'group-hover:text-slate-400'"
              />
            </div>

            <!-- Quick-action buttons (show on hover) -->
            <div class="mt-2 hidden gap-1.5 group-hover:flex">
              <button
                class="rounded-md border border-slate-200 px-2 py-0.5 text-[10px] font-medium text-graphite hover:bg-slate-50"
                @click.stop="toggleActive(cfg)"
              >{{ cfg.is_active ? "Deactivate" : "Activate" }}</button>
            </div>
          </button>
        </aside>

        <!-- ── Right: edit form ──────────────────────────────────────────── -->
        <form class="space-y-5" @submit.prevent="save">

          <!-- Form header -->
          <div class="flex items-center justify-between rounded-xl border border-slate-200 bg-white px-5 py-4">
            <div>
              <h2 class="text-sm font-semibold text-ink">{{ draft.id ? "Edit configuration" : "New configuration" }}</h2>
              <p class="mt-0.5 text-xs text-graphite">{{ draft.id ? `ID ${draft.id} · ${draft.slug}` : "Fill in the details and save." }}</p>
            </div>
            <button
              type="submit"
              class="focus-ring inline-flex h-9 items-center gap-2 rounded-lg bg-signal px-4 text-sm font-semibold text-white hover:bg-emerald-600 disabled:opacity-60"
              :disabled="isSaving"
            >
              <Save class="h-4 w-4" />
              {{ isSaving ? "Saving…" : "Save" }}
            </button>
          </div>

          <!-- Section 1: Identity -->
          <div class="rounded-xl border border-slate-200 bg-white p-5">
            <h3 class="mb-4 text-xs font-bold uppercase tracking-wide text-graphite">Identity</h3>
            <div class="grid gap-4 sm:grid-cols-2">
              <label class="block">
                <span class="mb-1 block text-xs font-semibold text-graphite">Name <span class="text-rose-500">*</span></span>
                <input v-model="draft.name" placeholder="e.g. Standard Class Package" class="focus-ring w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" />
              </label>
              <label class="block">
                <span class="mb-1 block text-xs font-semibold text-graphite">Slug <span class="text-rose-500">*</span></span>
                <input v-model="draft.slug" placeholder="e.g. standard-class" class="focus-ring w-full rounded-lg border border-slate-200 px-3 py-2 text-sm font-mono" />
              </label>
              <label class="block">
                <span class="mb-1 block text-xs font-semibold text-graphite">Service type</span>
                <input v-model="draft.service_type" placeholder="full_class" class="focus-ring w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" />
              </label>
              <label class="block">
                <span class="mb-1 block text-xs font-semibold text-graphite">Display order</span>
                <input v-model.number="draft.display_order" type="number" class="focus-ring w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" />
              </label>
              <label class="block sm:col-span-2">
                <span class="mb-1 block text-xs font-semibold text-graphite">Description</span>
                <textarea v-model="draft.description" rows="2" placeholder="Brief description shown to clients" class="focus-ring w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" />
              </label>
            </div>
          </div>

          <!-- Section 2: Pricing -->
          <div class="rounded-xl border border-slate-200 bg-white p-5">
            <h3 class="mb-4 text-xs font-bold uppercase tracking-wide text-graphite">Pricing</h3>
            <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <label class="block">
                <span class="mb-1 block text-xs font-semibold text-graphite">Pricing mode</span>
                <select v-model="draft.pricing_mode" class="focus-ring w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm">
                  <option value="quote">Quote after review</option>
                  <option value="package">Package estimate</option>
                </select>
              </label>
              <label class="block">
                <span class="mb-1 block text-xs font-semibold text-graphite">Base price</span>
                <input v-model="draft.base_price" placeholder="0.00" class="focus-ring w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" />
              </label>
              <label class="block">
                <span class="mb-1 block text-xs font-semibold text-graphite">Currency</span>
                <input v-model="draft.currency" placeholder="USD" class="focus-ring w-full rounded-lg border border-slate-200 px-3 py-2 text-sm uppercase" />
              </label>
              <label class="block">
                <span class="mb-1 block text-xs font-semibold text-graphite">Deposit %</span>
                <input v-model="draft.deposit_percentage" placeholder="50.00" class="focus-ring w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" />
              </label>
              <label class="block">
                <span class="mb-1 block text-xs font-semibold text-graphite">Quote expiry (hours)</span>
                <input v-model.number="draft.quote_expiry_hours" type="number" min="1" class="focus-ring w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" />
              </label>
            </div>
          </div>

          <!-- Section 3: Policies -->
          <div class="rounded-xl border border-slate-200 bg-white p-5">
            <h3 class="mb-4 text-xs font-bold uppercase tracking-wide text-graphite">Policies</h3>
            <div class="grid gap-3 sm:grid-cols-2">
              <label class="flex cursor-pointer items-center gap-3 rounded-lg border border-slate-100 px-4 py-3 hover:bg-slate-50">
                <input v-model="draft.is_active" type="checkbox" class="h-4 w-4 rounded accent-signal" />
                <div>
                  <p class="text-sm font-medium text-ink">Active</p>
                  <p class="text-xs text-graphite">Visible to clients on the platform.</p>
                </div>
              </label>
              <label class="flex cursor-pointer items-center gap-3 rounded-lg border border-slate-100 px-4 py-3 hover:bg-slate-50">
                <input v-model="draft.requires_portal_access" type="checkbox" class="h-4 w-4 rounded accent-signal" />
                <div>
                  <p class="text-sm font-medium text-ink">Requires portal access</p>
                  <p class="text-xs text-graphite">Client must be invited before ordering.</p>
                </div>
              </label>
              <label class="flex cursor-pointer items-center gap-3 rounded-lg border border-slate-100 px-4 py-3 hover:bg-slate-50">
                <input v-model="draft.allow_installments" type="checkbox" class="h-4 w-4 rounded accent-signal" />
                <div>
                  <p class="text-sm font-medium text-ink">Allow installments</p>
                  <p class="text-xs text-graphite">Enable milestone-based payment.</p>
                </div>
              </label>
              <label class="flex cursor-pointer items-center gap-3 rounded-lg border border-slate-100 px-4 py-3 hover:bg-slate-50">
                <input v-model="draft.require_deposit_before_start" type="checkbox" class="h-4 w-4 rounded accent-signal" />
                <div>
                  <p class="text-sm font-medium text-ink">Require deposit before start</p>
                  <p class="text-xs text-graphite">Work does not begin until deposit is paid.</p>
                </div>
              </label>
            </div>
          </div>

          <!-- Section 4: Duration options -->
          <div class="rounded-xl border border-slate-200 bg-white p-5">
            <div class="mb-4 flex items-center justify-between">
              <div>
                <h3 class="text-xs font-bold uppercase tracking-wide text-graphite">Duration options</h3>
                <p class="mt-0.5 text-xs text-graphite">Time spans clients can choose from.</p>
              </div>
              <button type="button" class="focus-ring inline-flex h-8 items-center gap-1.5 rounded-lg border border-slate-200 px-3 text-xs font-semibold text-graphite hover:bg-slate-50" @click="durationRows.push({ key: '', label: '', weeks: null, description: '' })">
                <Plus class="h-3.5 w-3.5" /> Add
              </button>
            </div>
            <div v-if="durationRows.length" class="space-y-2">
              <!-- Header -->
              <div class="grid grid-cols-[1fr_1fr_80px_1.5fr_32px] gap-2 px-1 text-[10px] font-semibold uppercase text-graphite">
                <span>Key</span><span>Label</span><span>Weeks</span><span>Description</span><span />
              </div>
              <div v-for="(row, i) in durationRows" :key="i" class="grid grid-cols-[1fr_1fr_80px_1.5fr_32px] items-center gap-2">
                <input v-model="row.key" placeholder="4_weeks" class="focus-ring rounded-lg border border-slate-200 px-2 py-1.5 text-xs font-mono" />
                <input v-model="row.label" placeholder="4 weeks" class="focus-ring rounded-lg border border-slate-200 px-2 py-1.5 text-xs" />
                <input v-model.number="row.weeks" type="number" placeholder="4" class="focus-ring rounded-lg border border-slate-200 px-2 py-1.5 text-xs" />
                <input v-model="row.description" placeholder="Optional note" class="focus-ring rounded-lg border border-slate-200 px-2 py-1.5 text-xs" />
                <button type="button" class="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 text-graphite hover:border-rose-200 hover:bg-rose-50 hover:text-rose-500" @click="durationRows.splice(i, 1)">
                  <X class="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
            <p v-else class="text-sm text-graphite">No durations yet. Click Add to create one.</p>
          </div>

          <!-- Section 5: Workload options -->
          <div class="rounded-xl border border-slate-200 bg-white p-5">
            <div class="mb-4 flex items-center justify-between">
              <div>
                <h3 class="text-xs font-bold uppercase tracking-wide text-graphite">Workload options</h3>
                <p class="mt-0.5 text-xs text-graphite">Effort levels and price signals.</p>
              </div>
              <button type="button" class="focus-ring inline-flex h-8 items-center gap-1.5 rounded-lg border border-slate-200 px-3 text-xs font-semibold text-graphite hover:bg-slate-50" @click="workloadRows.push({ key: '', label: '', complexity: 'medium', description: '', price_hint: '' })">
                <Plus class="h-3.5 w-3.5" /> Add
              </button>
            </div>
            <div v-if="workloadRows.length" class="space-y-2">
              <div class="grid grid-cols-[1fr_1fr_120px_1.5fr_1fr_32px] gap-2 px-1 text-[10px] font-semibold uppercase text-graphite">
                <span>Key</span><span>Label</span><span>Complexity</span><span>Description</span><span>Price hint</span><span />
              </div>
              <div v-for="(row, i) in workloadRows" :key="i" class="grid grid-cols-[1fr_1fr_120px_1.5fr_1fr_32px] items-center gap-2">
                <input v-model="row.key" placeholder="standard" class="focus-ring rounded-lg border border-slate-200 px-2 py-1.5 text-xs font-mono" />
                <input v-model="row.label" placeholder="Standard" class="focus-ring rounded-lg border border-slate-200 px-2 py-1.5 text-xs" />
                <select v-model="row.complexity" class="focus-ring rounded-lg border border-slate-200 bg-white px-2 py-1.5 text-xs">
                  <option value="low">Low</option><option value="medium">Medium</option>
                  <option value="high">High</option><option value="very_high">Very high</option>
                </select>
                <input v-model="row.description" placeholder="Description" class="focus-ring rounded-lg border border-slate-200 px-2 py-1.5 text-xs" />
                <input v-model="row.price_hint" placeholder="$500–$800" class="focus-ring rounded-lg border border-slate-200 px-2 py-1.5 text-xs" />
                <button type="button" class="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 text-graphite hover:border-rose-200 hover:bg-rose-50 hover:text-rose-500" @click="workloadRows.splice(i, 1)">
                  <X class="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
            <p v-else class="text-sm text-graphite">No workload levels yet.</p>
          </div>

          <!-- Section 6: Task options -->
          <div class="rounded-xl border border-slate-200 bg-white p-5">
            <div class="mb-4 flex items-center justify-between">
              <div>
                <h3 class="text-xs font-bold uppercase tracking-wide text-graphite">Task options</h3>
                <p class="mt-0.5 text-xs text-graphite">Types of work included in the class.</p>
              </div>
              <button type="button" class="focus-ring inline-flex h-8 items-center gap-1.5 rounded-lg border border-slate-200 px-3 text-xs font-semibold text-graphite hover:bg-slate-50" @click="taskRows.push({ key: '', label: '', description: '', required: false })">
                <Plus class="h-3.5 w-3.5" /> Add
              </button>
            </div>
            <div v-if="taskRows.length" class="space-y-2">
              <div class="grid grid-cols-[1fr_1fr_1.5fr_100px_32px] gap-2 px-1 text-[10px] font-semibold uppercase text-graphite">
                <span>Key</span><span>Label</span><span>Description</span><span>Required</span><span />
              </div>
              <div v-for="(row, i) in taskRows" :key="i" class="grid grid-cols-[1fr_1fr_1.5fr_100px_32px] items-center gap-2">
                <input v-model="row.key" placeholder="assignments" class="focus-ring rounded-lg border border-slate-200 px-2 py-1.5 text-xs font-mono" />
                <input v-model="row.label" placeholder="Assignments" class="focus-ring rounded-lg border border-slate-200 px-2 py-1.5 text-xs" />
                <input v-model="row.description" placeholder="Optional note" class="focus-ring rounded-lg border border-slate-200 px-2 py-1.5 text-xs" />
                <label class="flex items-center gap-2 text-xs text-graphite cursor-pointer">
                  <input v-model="row.required" type="checkbox" class="h-4 w-4 rounded accent-signal" /> Required
                </label>
                <button type="button" class="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 text-graphite hover:border-rose-200 hover:bg-rose-50 hover:text-rose-500" @click="taskRows.splice(i, 1)">
                  <X class="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
            <p v-else class="text-sm text-graphite">No task types yet.</p>
          </div>

          <!-- Section 7: Required fields -->
          <div class="rounded-xl border border-slate-200 bg-white p-5">
            <div class="mb-4 flex items-center justify-between">
              <div>
                <h3 class="text-xs font-bold uppercase tracking-wide text-graphite">Required fields</h3>
                <p class="mt-0.5 text-xs text-graphite">Fields the client must complete when ordering.</p>
              </div>
              <button type="button" class="focus-ring inline-flex h-8 items-center gap-1.5 rounded-lg border border-slate-200 px-3 text-xs font-semibold text-graphite hover:bg-slate-50" @click="requiredFieldRows.push({ value: '' })">
                <Plus class="h-3.5 w-3.5" /> Add
              </button>
            </div>
            <div class="grid gap-2 sm:grid-cols-2">
              <div v-for="(row, i) in requiredFieldRows" :key="i" class="flex items-center gap-2">
                <input v-model="row.value" placeholder="field_name" class="focus-ring flex-1 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-mono" />
                <button type="button" class="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 text-graphite hover:border-rose-200 hover:bg-rose-50 hover:text-rose-500" @click="requiredFieldRows.splice(i, 1)">
                  <X class="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
            <p v-if="!requiredFieldRows.length" class="text-sm text-graphite">No required fields defined.</p>
          </div>

          <!-- Sticky footer save -->
          <div class="sticky bottom-4 flex justify-end">
            <button
              type="submit"
              class="focus-ring inline-flex h-10 items-center gap-2 rounded-lg bg-signal px-6 text-sm font-semibold text-white shadow-md hover:bg-emerald-600 disabled:opacity-60"
              :disabled="isSaving"
            >
              <Save class="h-4 w-4" />
              {{ isSaving ? "Saving…" : "Save configuration" }}
            </button>
          </div>

        </form>
      </div>
    </div>
  </div>
</template>
