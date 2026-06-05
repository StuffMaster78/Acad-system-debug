<script setup lang="ts">
import { computed, defineComponent, h, onMounted, reactive, ref, watch, type PropType, type Ref } from "vue";
import { Pencil, Plus, RefreshCw, Save, Trash2, X } from "@lucide/vue";
import { api, apiPath } from "@/api/client";
import { useAuthStore } from "@/stores/auth";
import { usePortalContextStore } from "@/stores/portalContext";
import { useWebsitesStore } from "@/stores/websites";

const auth = useAuthStore();
const portal = usePortalContextStore();
const websites = useWebsitesStore();
const isSuperadmin = auth.role === "superadmin";
const props = withDefaults(defineProps<{
  embedded?: boolean;
  sectionKey?: string;
}>(), {
  embedded: false,
  sectionKey: "base-rates",
});
const selectedWebsiteId = ref<number | null>(null);
const pricingReady = ref(false);
const loading = ref(false);
const saving  = ref(false);
const syncing = ref(false);
const error   = ref("");
const notice  = ref("");

type Tab = "profile" | "deadlines" | "academic-levels" | "paper-types" | "subject-categories" | "subject-rates" | "work-types" | "writer-levels" | "diagram-complexity" | "addons";
const SECTION_TAB_MAP: Record<string, Tab> = {
  "base-rates": "profile",
  "deadline-bands": "deadlines",
  "academic-level-rates": "academic-levels",
  "paper-type-rates": "paper-types",
  "subject-multipliers": "subject-categories",
  "subject-rates": "subject-rates",
  "work-type-rates": "work-types",
  "writer-level-rates": "writer-levels",
  "diagram-complexity": "diagram-complexity",
  "service-addons": "addons",
};
const activeTab = ref<Tab>(SECTION_TAB_MAP[props.sectionKey] ?? "profile");
const requestParams = computed(() =>
  isSuperadmin && selectedWebsiteId.value ? { website_id: selectedWebsiteId.value } : undefined,
);

const TABS: { key: Tab; label: string }[] = [
  { key: "profile",            label: "Base Rates" },
  { key: "deadlines",          label: "Deadlines" },
  { key: "academic-levels",    label: "Academic Levels" },
  { key: "paper-types",        label: "Paper Types" },
  { key: "subject-categories", label: "Subject Categories" },
  { key: "subject-rates",      label: "Subject Rates" },
  { key: "work-types",         label: "Work Types" },
  { key: "writer-levels",      label: "Writer Levels" },
  { key: "diagram-complexity", label: "Diagram Complexity" },
  { key: "addons",             label: "Add-ons" },
];

// ── Helpers ────────────────────────────────────────────────────────────────
function ok(msg: string)   { notice.value = msg; error.value = ""; setTimeout(() => { notice.value = ""; }, 3000); }
function fail(msg: string) { error.value = msg; }
function pp(sub: string)   { return apiPath(`/pricing/${sub}`); }

// ══════════════════════════════════════════════════════════════════════════
// Pricing Profile
// ══════════════════════════════════════════════════════════════════════════
interface PricingProfile {
  id: number; profile_name: string; currency: string;
  base_price_per_page: string; base_price_per_slide: string; base_price_per_diagram: string;
  double_spacing_multiplier: string; single_spacing_multiplier: string;
  preferred_writer_fee: string;
  minimum_paper_order_charge: string; minimum_design_order_charge: string; minimum_diagram_order_charge: string;
  max_pages_per_hour: number; extra_hour_per_extra_page: number; rush_recommendation_only: boolean;
}
const profile = reactive<Partial<PricingProfile>>({});

async function loadProfile() {
  const { data } = await api.get<PricingProfile>(pp("admin/profile/"), { params: requestParams.value });
  Object.assign(profile, data);
}

async function saveProfile() {
  saving.value = true;
  try {
    await api.patch(pp("admin/profile/"), profile, { params: requestParams.value });
    ok("Pricing profile saved.");
  } catch { fail("Failed to save."); }
  finally { saving.value = false; }
}

async function syncOrderConfigRates() {
  syncing.value = true;
  error.value = "";
  try {
    const { data } = await api.post<{
      paper_type_rates: { created: number; updated: number };
      subject_rates: { created: number; updated: number };
    }>(pp("admin/sync-order-config-rates/"), {}, { params: requestParams.value });
    await Promise.all([
      paperTypes.load(),
      subjectCategories.load(),
      subjectRates.load(),
    ]);
    ok(
      `Synced ${data.paper_type_rates.created + data.paper_type_rates.updated} paper type rates and ${data.subject_rates.created + data.subject_rates.updated} subject rates.`,
    );
  } catch {
    fail("Failed to sync rates from order configs.");
  } finally {
    syncing.value = false;
  }
}

// ══════════════════════════════════════════════════════════════════════════
// Generic dimension CRUD factory
// ══════════════════════════════════════════════════════════════════════════
interface DimRow { id: number; [k: string]: unknown }

interface DimensionTableModel {
  rows: Ref<DimRow[]>;
  draft: DimRow;
  editingId: Ref<number | null>;
  dim_saving: Ref<boolean>;
  load: () => Promise<void>;
  save: () => Promise<void>;
  remove: (id: number) => Promise<void>;
  startEdit: (row: DimRow) => void;
  cancelEdit: () => void;
}

function useDimension<T extends DimRow>(endpoint: string, blank: Omit<T, "id">): DimensionTableModel {
  const rows       = ref<DimRow[]>([]);
  const draft      = reactive({ ...blank }) as unknown as DimRow;
  const editingId  = ref<number | null>(null);
  const dim_saving = ref(false);
  const fieldKeys = Object.keys(blank);

  function resetDraft() {
    (fieldKeys as (keyof typeof blank)[]).forEach((k) => {
      (draft as Record<string, unknown>)[k as string] = blank[k];
    });
  }
  function startEdit(row: DimRow) {
    editingId.value = row.id;
    fieldKeys.forEach((key) => {
      draft[key] = row[key];
    });
  }
  function cancelEdit() { editingId.value = null; resetDraft(); }
  function payload() {
    return fieldKeys.reduce<Record<string, unknown>>((acc, key) => {
      acc[key] = key === "custom_multiplier" && draft[key] === "" ? null : draft[key];
      return acc;
    }, {});
  }

  async function load() {
    loading.value = true;
    try {
      const { data } = await api.get<DimRow[] | { results: DimRow[] }>(pp(endpoint), { params: requestParams.value });
      rows.value = Array.isArray(data) ? data : data.results ?? [];
    } catch { fail(`Failed to load.`); }
    finally { loading.value = false; }
  }

  async function save() {
    dim_saving.value = true;
    try {
      if (editingId.value) {
        await api.patch(pp(`${endpoint}${editingId.value}/`), payload(), { params: requestParams.value });
      } else {
        await api.post(pp(endpoint), payload(), { params: requestParams.value });
      }
      ok("Saved.");
      cancelEdit();
      await load();
    } catch { fail("Save failed."); }
    finally { dim_saving.value = false; }
  }

  async function remove(id: number) {
    if (!confirm("Delete this item?")) return;
    try {
      await api.delete(pp(`${endpoint}${id}/`), { params: requestParams.value });
      ok("Deleted.");
      await load();
    } catch { fail("Delete failed."); }
  }

  return { rows, draft, editingId, dim_saving, load, save, remove, startEdit, cancelEdit };
}

// ── Dimension instances ────────────────────────────────────────────────────
const deadlines = useDimension<{ id: number; label: string; max_hours: number; multiplier: string; sort_order: number; is_active: boolean }>(
  "admin/dimensions/deadline-rates/",
  { label: "", max_hours: 48, multiplier: "1.0000", sort_order: 0, is_active: true },
);
const academicLevels = useDimension<{ id: number; code: string; label: string; multiplier: string; sort_order: number; is_active: boolean }>(
  "admin/dimensions/academic-levels/",
  { code: "", label: "", multiplier: "1.0000", sort_order: 0, is_active: true },
);
const paperTypes = useDimension<{ id: number; code: string; label: string; multiplier: string; sort_order: number; is_active: boolean }>(
  "admin/dimensions/paper-types/",
  { code: "", label: "", multiplier: "1.0000", sort_order: 0, is_active: true },
);
const subjectCategories = useDimension<{ id: number; code: string; label: string; multiplier: string; sort_order: number; is_active: boolean }>(
  "admin/dimensions/subject-categories/",
  { code: "", label: "", multiplier: "1.0000", sort_order: 0, is_active: true },
);
const subjectRates = useDimension<{ id: number; code: string; label: string; category_id: number; custom_multiplier: string | null; sort_order: number; is_active: boolean }>(
  "admin/dimensions/subject-rates/",
  { code: "", label: "", category_id: 0, custom_multiplier: null, sort_order: 0, is_active: true },
);
const subjectCategoryOptions = computed(() =>
  subjectCategories.rows.value.map((item) => ({ value: item.id, label: String(item.label ?? item.code) })),
);
const workTypes = useDimension<{ id: number; code: string; label: string; multiplier: string; sort_order: number; is_active: boolean }>(
  "admin/dimensions/work-types/",
  { code: "", label: "", multiplier: "1.0000", sort_order: 0, is_active: true },
);
const writerLevels = useDimension<{ id: number; code: string; label: string; amount: string; is_flat_fee: boolean; sort_order: number; is_active: boolean }>(
  "admin/dimensions/writer-levels/",
  { code: "", label: "", amount: "0.00", is_flat_fee: true, sort_order: 0, is_active: true },
);
const diagramComplexity = useDimension<{ id: number; complexity: string; multiplier: string; is_active: boolean }>(
  "admin/dimensions/diagram-complexity/",
  { complexity: "simple", multiplier: "1.0000", is_active: true },
);
const addons = useDimension<{ id: number; addon_code: string; name: string; description: string; flat_amount: string; is_public: boolean; is_active: boolean; sort_order: number }>(
  "admin/service-catalog/addons/",
  { addon_code: "", name: "", description: "", flat_amount: "0.00", is_public: true, is_active: true, sort_order: 0 },
);

// ── Init ───────────────────────────────────────────────────────────────────
async function loadAll() {
  loading.value = true;
  error.value = "";
  try {
    await Promise.all([
      loadProfile(),
      deadlines.load(),
      academicLevels.load(),
      paperTypes.load(),
      subjectCategories.load(),
      subjectRates.load(),
      workTypes.load(),
      writerLevels.load(),
      diagramComplexity.load(),
      addons.load(),
    ]);
  } catch { fail("Failed to load configuration."); }
  finally { loading.value = false; }
}
onMounted(async () => {
  await websites.ensure();
  selectedWebsiteId.value = portal.website?.id ?? websites.list[0]?.id ?? null;
  await loadAll();
  pricingReady.value = true;
});

watch(selectedWebsiteId, () => {
  if (!pricingReady.value) return;
  loadAll();
});

watch(
  () => props.sectionKey,
  (sectionKey) => {
    activeTab.value = SECTION_TAB_MAP[sectionKey] ?? "profile";
  },
);

// ══════════════════════════════════════════════════════════════════════════
// DimTable — inline sub-component (avoids separate file)
// ══════════════════════════════════════════════════════════════════════════
type ColType = "text" | "decimal" | "number" | "bool" | "complexity" | "select";
interface Col { key: string; label: string; type: ColType; options?: { value: string | number; label: string }[] }

const DimTable = defineComponent({
  props: {
    title:       { type: String, required: true },
    description: { type: String, default: "" },
    dim:         { type: Object as PropType<DimensionTableModel>, required: true },
    columns:     { type: Array as PropType<Col[]>, required: true },
  },
  setup(props) {
    const inp = "focus-ring h-8 w-full rounded-md border border-slate-200 px-2 text-sm";
    const PAGE_SIZE = 10;
    const query = ref("");
    const page = ref(1);
    const filteredRows = computed(() => {
      const q = query.value.trim().toLowerCase();
      if (!q) return props.dim.rows.value;
      return props.dim.rows.value.filter((row) => {
        const raw = row as Record<string, unknown>;
        return [
          ...props.columns.map((col) => raw[col.key]),
          raw.category_label,
        ].some((value) => String(value ?? "").toLowerCase().includes(q));
      });
    });
    const totalPages = computed(() => Math.max(1, Math.ceil(filteredRows.value.length / PAGE_SIZE)));
    const pageRows = computed(() => {
      const start = (page.value - 1) * PAGE_SIZE;
      return filteredRows.value.slice(start, start + PAGE_SIZE);
    });
    const showingFrom = computed(() => filteredRows.value.length ? (page.value - 1) * PAGE_SIZE + 1 : 0);
    const showingTo = computed(() => Math.min(page.value * PAGE_SIZE, filteredRows.value.length));

    watch(query, () => { page.value = 1; });
    watch(totalPages, (next) => {
      if (page.value > next) page.value = next;
    });

    function cell(col: Col, row: Record<string, unknown>) {
      if (col.type === "bool") return h("span", { class: row[col.key] ? "text-emerald-600 font-semibold text-xs" : "text-slate-400 text-xs" }, row[col.key] ? "Yes" : "No");
      if (col.type === "complexity") return h("span", { class: "capitalize" }, String(row[col.key] ?? ""));
      if (col.type === "select") {
        const match = col.options?.find((option) => String(option.value) === String(row[col.key]));
        return h("span", {}, match?.label ?? String(row.category_label ?? row[col.key] ?? ""));
      }
      return h("span", {}, String(row[col.key] ?? ""));
    }

    function input(col: Col, draft: Record<string, unknown>) {
      if (col.type === "bool")
        return h("input", { type: "checkbox", class: "h-4 w-4 rounded border-slate-300 text-signal", checked: draft[col.key],
          onChange: (e: Event) => { draft[col.key] = (e.target as HTMLInputElement).checked; } });
      if (col.type === "complexity")
        return h("select", { class: inp, value: draft[col.key],
          onChange: (e: Event) => { draft[col.key] = (e.target as HTMLSelectElement).value; } },
          ["simple", "moderate", "complex"].map((v) => h("option", { value: v }, v.charAt(0).toUpperCase() + v.slice(1))));
      if (col.type === "select")
        return h("select", { class: inp, value: draft[col.key],
          onChange: (e: Event) => { draft[col.key] = Number((e.target as HTMLSelectElement).value); } },
          [
            h("option", { value: 0, disabled: true }, "Select category"),
            ...(col.options ?? []).map((opt) => h("option", { value: opt.value }, opt.label)),
          ]);
      return h("input", { type: col.type === "text" ? "text" : "number", step: col.type === "decimal" ? "0.0001" : undefined,
        class: inp, value: draft[col.key], onInput: (e: Event) => { draft[col.key] = (e.target as HTMLInputElement).value; } });
    }

    return () => {
      const { dim } = props;
      const draft = dim.draft as Record<string, unknown>;
      const isSaving = dim.dim_saving.value;

      return h("div", { class: "rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden" }, [
        h("div", { class: "flex flex-wrap items-start justify-between gap-3 border-b border-slate-100 px-5 py-4" }, [
          h("div", {}, [
            h("h2", { class: "text-sm font-semibold text-ink" }, props.title),
            props.description ? h("p", { class: "mt-0.5 text-xs text-graphite" }, props.description) : null,
          ]),
          h("input", {
            type: "search",
            class: "focus-ring h-8 min-w-[14rem] rounded-lg border border-slate-200 bg-white px-2 text-xs text-graphite",
            placeholder: `Search ${props.title.toLowerCase()}...`,
            value: query.value,
            onInput: (e: Event) => { query.value = (e.target as HTMLInputElement).value; },
          }),
        ]),
        h("div", { class: "overflow-x-auto" },
          h("table", { class: "min-w-[920px] text-sm" }, [
            h("thead", { class: "bg-slate-50 text-xs font-semibold uppercase text-graphite" },
              h("tr", {}, [
                ...props.columns.map((c) => h("th", { class: "px-3 py-2 text-left whitespace-nowrap" }, c.label)),
                h("th", { class: "px-3 py-2 text-right" }, ""),
              ])),
            h("tbody", { class: "divide-y divide-slate-100" }, [
              ...pageRows.value.map((row) => {
                const editing = dim.editingId.value === row.id;
                return h("tr", { key: row.id, class: editing ? "bg-signal/5" : "hover:bg-slate-50" }, [
                  ...props.columns.map((c) => h("td", { class: "px-3 py-2" }, editing ? input(c, draft) : cell(c, row as Record<string, unknown>))),
                  h("td", { class: "px-3 py-2 text-right" }, editing
                    ? h("span", { class: "inline-flex gap-1" }, [
                        h("button", { class: "focus-ring inline-flex items-center gap-1 rounded-md bg-signal px-3 py-1 text-xs font-semibold text-white disabled:opacity-60",
                          disabled: isSaving, onClick: () => dim.save() }, [h(Save, { class: "h-3 w-3" }), isSaving ? "…" : "Save"]),
                        h("button", { class: "focus-ring rounded-md border border-slate-200 px-2 py-1 text-xs text-graphite hover:bg-slate-50", onClick: () => dim.cancelEdit() }, h(X, { class: "h-3 w-3" })),
                      ])
                    : h("span", { class: "inline-flex gap-1" }, [
                        h("button", { class: "focus-ring rounded-md border border-slate-200 p-1.5 text-graphite hover:text-ink", onClick: () => dim.startEdit(row) }, h(Pencil, { class: "h-3.5 w-3.5" })),
                        h("button", { class: "focus-ring rounded-md border border-rose-200 p-1.5 text-rose-400 hover:text-rose-600", onClick: () => dim.remove(row.id) }, h(Trash2, { class: "h-3.5 w-3.5" })),
                      ])),
                ]);
              }),
              // Add-new row (only when not editing an existing row)
              dim.editingId.value === null
                ? h("tr", { class: "bg-slate-50/50" }, [
                    ...props.columns.map((c) => h("td", { class: "px-3 py-2" }, input(c, draft))),
                    h("td", { class: "px-3 py-2 text-right" },
                      h("button", { class: "focus-ring inline-flex items-center gap-1 rounded-md bg-signal px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-60",
                        disabled: isSaving, onClick: () => dim.save() }, [h(Plus, { class: "h-3 w-3" }), "Add"])),
                  ])
                : null,
            ]),
          ])),
        h("div", { class: "flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 px-5 py-2 text-xs text-graphite" }, [
          h("span", {}, `Showing ${showingFrom.value}-${showingTo.value} of ${filteredRows.value.length} item${filteredRows.value.length === 1 ? "" : "s"}`),
          h("span", { class: "inline-flex items-center gap-2" }, [
            h("button", {
              class: "rounded border border-slate-200 px-2 py-1 disabled:opacity-40",
              disabled: page.value <= 1,
              onClick: () => { page.value -= 1; },
            }, "Prev"),
            h("span", {}, `Page ${page.value} / ${totalPages.value}`),
            h("button", {
              class: "rounded border border-slate-200 px-2 py-1 disabled:opacity-40",
              disabled: page.value >= totalPages.value,
              onClick: () => { page.value += 1; },
            }, "Next"),
          ]),
        ]),
      ]);
    };
  },
});
</script>

<template>
  <div class="space-y-4">

    <!-- Header -->
    <div
      v-if="props.embedded"
      class="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm"
    >
      <div>
        <p class="text-sm font-semibold text-ink">{{ TABS.find((tab) => tab.key === activeTab)?.label }}</p>
        <p class="text-xs text-graphite">Connected pricing rules used by calculators and order quoting.</p>
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <select
          v-if="isSuperadmin"
          v-model.number="selectedWebsiteId"
          class="focus-ring rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm"
        >
          <option v-for="site in websites.options" :key="site.value" :value="site.value">{{ site.label }}</option>
        </select>
        <button class="focus-ring inline-flex h-9 items-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
          :disabled="loading" @click="loadAll">
          <RefreshCw class="h-4 w-4" :class="loading ? 'animate-spin' : ''" /> Refresh
        </button>
        <button class="focus-ring inline-flex h-9 items-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
          :disabled="syncing" @click="syncOrderConfigRates">
          <RefreshCw class="h-4 w-4" :class="syncing ? 'animate-spin' : ''" /> Sync rates
        </button>
      </div>
    </div>
    <div v-else class="flex flex-col gap-3 border-b border-slate-200 pb-6 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Pricing</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Calculator Configuration</h1>
        <p class="mt-2 text-sm text-graphite">
          Base rates and multipliers for the Paper, Design, and Diagram calculators.
        </p>
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <select
          v-if="isSuperadmin"
          v-model.number="selectedWebsiteId"
          class="focus-ring rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm"
        >
          <option v-for="site in websites.options" :key="site.value" :value="site.value">{{ site.label }}</option>
        </select>
        <button class="focus-ring inline-flex h-9 items-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
          :disabled="loading" @click="loadAll">
          <RefreshCw class="h-4 w-4" :class="loading ? 'animate-spin' : ''" /> Refresh
        </button>
        <button class="focus-ring inline-flex h-9 items-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
          :disabled="syncing" @click="syncOrderConfigRates">
          <RefreshCw class="h-4 w-4" :class="syncing ? 'animate-spin' : ''" /> Sync rates
        </button>
      </div>
    </div>

    <!-- Feedback -->
    <div v-if="error"  class="rounded-md border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">{{ error }}</div>
    <div v-if="notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">{{ notice }}</div>

    <!-- Tab nav -->
    <div v-if="!props.embedded" class="flex flex-wrap gap-1 border-b border-slate-200">
      <button v-for="t in TABS" :key="t.key"
        class="whitespace-nowrap px-4 py-2.5 text-sm font-medium transition-colors"
        :class="activeTab === t.key ? 'border-b-2 border-signal text-signal' : 'text-graphite hover:text-ink'"
        @click="activeTab = t.key">{{ t.label }}</button>
    </div>

    <!-- ── Base Rates ──────────────────────────────────────────────────── -->
    <template v-if="activeTab === 'profile'">
      <div class="grid gap-5 sm:grid-cols-3">
        <!-- per-unit card -->
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:col-span-3">
          <p class="mb-3 text-xs font-semibold uppercase tracking-wide text-graphite">Base price per unit</p>
          <div class="grid gap-4 sm:grid-cols-3">
            <label class="block"><span class="text-xs font-semibold uppercase text-graphite">Per page (paper)</span>
              <input v-model="profile.base_price_per_page" type="number" step="0.01" min="0" class="focus-ring mt-1 h-9 w-full rounded-md border border-slate-200 px-3 text-sm" /></label>
            <label class="block"><span class="text-xs font-semibold uppercase text-graphite">Per slide (design)</span>
              <input v-model="profile.base_price_per_slide" type="number" step="0.01" min="0" class="focus-ring mt-1 h-9 w-full rounded-md border border-slate-200 px-3 text-sm" /></label>
            <label class="block"><span class="text-xs font-semibold uppercase text-graphite">Per diagram</span>
              <input v-model="profile.base_price_per_diagram" type="number" step="0.01" min="0" class="focus-ring mt-1 h-9 w-full rounded-md border border-slate-200 px-3 text-sm" /></label>
          </div>
        </div>
        <!-- minimums -->
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:col-span-3">
          <p class="mb-3 text-xs font-semibold uppercase tracking-wide text-graphite">Minimum order charges</p>
          <div class="grid gap-4 sm:grid-cols-3">
            <label class="block"><span class="text-xs font-semibold uppercase text-graphite">Paper minimum</span>
              <input v-model="profile.minimum_paper_order_charge" type="number" step="0.01" min="0" class="focus-ring mt-1 h-9 w-full rounded-md border border-slate-200 px-3 text-sm" /></label>
            <label class="block"><span class="text-xs font-semibold uppercase text-graphite">Design minimum</span>
              <input v-model="profile.minimum_design_order_charge" type="number" step="0.01" min="0" class="focus-ring mt-1 h-9 w-full rounded-md border border-slate-200 px-3 text-sm" /></label>
            <label class="block"><span class="text-xs font-semibold uppercase text-graphite">Diagram minimum</span>
              <input v-model="profile.minimum_diagram_order_charge" type="number" step="0.01" min="0" class="focus-ring mt-1 h-9 w-full rounded-md border border-slate-200 px-3 text-sm" /></label>
          </div>
        </div>
        <!-- spacing + fees -->
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:col-span-3">
          <p class="mb-3 text-xs font-semibold uppercase tracking-wide text-graphite">Spacing &amp; fees</p>
          <div class="grid gap-4 sm:grid-cols-4">
            <label class="block"><span class="text-xs font-semibold uppercase text-graphite">Double spacing ×</span>
              <input v-model="profile.double_spacing_multiplier" type="number" step="0.0001" min="0.1" class="focus-ring mt-1 h-9 w-full rounded-md border border-slate-200 px-3 text-sm" /></label>
            <label class="block"><span class="text-xs font-semibold uppercase text-graphite">Single spacing ×</span>
              <input v-model="profile.single_spacing_multiplier" type="number" step="0.0001" min="0.1" class="focus-ring mt-1 h-9 w-full rounded-md border border-slate-200 px-3 text-sm" /></label>
            <label class="block"><span class="text-xs font-semibold uppercase text-graphite">Preferred writer fee</span>
              <input v-model="profile.preferred_writer_fee" type="number" step="0.01" min="0" class="focus-ring mt-1 h-9 w-full rounded-md border border-slate-200 px-3 text-sm" /></label>
            <label class="block"><span class="text-xs font-semibold uppercase text-graphite">Currency code</span>
              <input v-model="profile.currency" type="text" maxlength="3" placeholder="USD" class="focus-ring mt-1 h-9 w-full rounded-md border border-slate-200 px-3 text-sm uppercase" /></label>
          </div>
        </div>
        <!-- deadline safety -->
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:col-span-3">
          <p class="mb-3 text-xs font-semibold uppercase tracking-wide text-graphite">Deadline safety thresholds</p>
          <div class="grid gap-4 sm:grid-cols-3">
            <label class="block"><span class="text-xs font-semibold uppercase text-graphite">Max pages per hour</span>
              <input v-model.number="profile.max_pages_per_hour" type="number" min="1" class="focus-ring mt-1 h-9 w-full rounded-md border border-slate-200 px-3 text-sm" />
              <p class="mt-1 text-xs text-graphite">Used to flag tight deadlines in the calculator.</p></label>
            <label class="flex items-center gap-2 pt-5">
              <input v-model="profile.rush_recommendation_only" type="checkbox" class="h-4 w-4 rounded border-slate-300 text-signal" />
              <span class="text-sm text-ink">Recommendation only — no hard block on rush orders</span>
            </label>
          </div>
        </div>
      </div>
      <div class="flex justify-end pt-2">
        <button class="focus-ring inline-flex h-10 items-center gap-2 rounded-lg bg-signal px-5 text-sm font-semibold text-white disabled:opacity-60"
          :disabled="saving" @click="saveProfile">
          <Save class="h-4 w-4" />{{ saving ? "Saving…" : "Save base rates" }}
        </button>
      </div>
    </template>

    <!-- ── Dimension tables ────────────────────────────────────────────── -->
    <DimTable v-if="activeTab === 'deadlines'" title="Deadline Bands"
      description="Each band applies a rush multiplier to orders within max_hours. Sorted by max_hours ascending — the first matching band wins."
      :dim="deadlines"
      :columns="[{ key:'label',label:'Label',type:'text' },{ key:'max_hours',label:'Max hours',type:'number' },{ key:'multiplier',label:'Multiplier ×',type:'decimal' },{ key:'sort_order',label:'Order',type:'number' },{ key:'is_active',label:'Active',type:'bool' }]"
    />
    <DimTable v-if="activeTab === 'academic-levels'" title="Academic Level Rates"
      description="Multiplier applied for each academic level. 1.0 = no surcharge. PhD level is typically 1.4–1.6×."
      :dim="academicLevels"
      :columns="[{ key:'code',label:'Code',type:'text' },{ key:'label',label:'Label',type:'text' },{ key:'multiplier',label:'Multiplier ×',type:'decimal' },{ key:'sort_order',label:'Order',type:'number' },{ key:'is_active',label:'Active',type:'bool' }]"
    />
    <DimTable v-if="activeTab === 'paper-types'" title="Paper Type Rates"
      description="Multiplier per paper type. Dissertations and theses carry a higher multiplier than standard essays."
      :dim="paperTypes"
      :columns="[{ key:'code',label:'Code',type:'text' },{ key:'label',label:'Label',type:'text' },{ key:'multiplier',label:'Multiplier ×',type:'decimal' },{ key:'sort_order',label:'Order',type:'number' },{ key:'is_active',label:'Active',type:'bool' }]"
    />
    <DimTable v-if="activeTab === 'subject-categories'" title="Subject Categories"
      description="Category multipliers used to group subjects, such as nursing, technology, STEM, law, and business."
      :dim="subjectCategories"
      :columns="[{ key:'code',label:'Code',type:'text' },{ key:'label',label:'Label',type:'text' },{ key:'multiplier',label:'Multiplier ×',type:'decimal' },{ key:'sort_order',label:'Order',type:'number' },{ key:'is_active',label:'Active',type:'bool' }]"
    />
    <DimTable v-if="activeTab === 'subject-rates'" title="Subject Rates"
      description="Website subjects mapped to a pricing category, with optional custom multiplier override for a specific subject."
      :dim="subjectRates"
      :columns="[{ key:'code',label:'Code',type:'text' },{ key:'label',label:'Subject',type:'text' },{ key:'category_id',label:'Category',type:'select',options:subjectCategoryOptions },{ key:'custom_multiplier',label:'Custom multiplier ×',type:'decimal' },{ key:'sort_order',label:'Order',type:'number' },{ key:'is_active',label:'Active',type:'bool' }]"
    />
    <DimTable v-if="activeTab === 'work-types'" title="Work Type Rates"
      description="Multiplier per work type (e.g. writing, editing, proofreading). Most are 1.0."
      :dim="workTypes"
      :columns="[{ key:'code',label:'Code',type:'text' },{ key:'label',label:'Label',type:'text' },{ key:'multiplier',label:'Multiplier ×',type:'decimal' },{ key:'sort_order',label:'Order',type:'number' },{ key:'is_active',label:'Active',type:'bool' }]"
    />
    <DimTable v-if="activeTab === 'writer-levels'" title="Writer Level Rates"
      description="Premium for selecting a specific writer level. is_flat_fee = fixed dollar amount added. Otherwise treated as a multiplier."
      :dim="writerLevels"
      :columns="[{ key:'code',label:'Code',type:'text' },{ key:'label',label:'Label',type:'text' },{ key:'amount',label:'Amount',type:'decimal' },{ key:'is_flat_fee',label:'Flat fee',type:'bool' },{ key:'sort_order',label:'Order',type:'number' },{ key:'is_active',label:'Active',type:'bool' }]"
    />
    <DimTable v-if="activeTab === 'diagram-complexity'" title="Diagram Complexity Rates"
      description="Multiplier per complexity level for the Diagram calculator. Three fixed levels — use update_or_create semantics."
      :dim="diagramComplexity"
      :columns="[{ key:'complexity',label:'Complexity',type:'complexity' },{ key:'multiplier',label:'Multiplier ×',type:'decimal' },{ key:'is_active',label:'Active',type:'bool' }]"
    />
    <DimTable v-if="activeTab === 'addons'" title="Add-ons"
      description="Optional flat-fee extras shown across all calculators. is_public = visible to clients on the public calculator."
      :dim="addons"
      :columns="[{ key:'addon_code',label:'Code',type:'text' },{ key:'name',label:'Name',type:'text' },{ key:'description',label:'Description',type:'text' },{ key:'flat_amount',label:'Amount $',type:'decimal' },{ key:'is_public',label:'Public',type:'bool' },{ key:'is_active',label:'Active',type:'bool' },{ key:'sort_order',label:'Order',type:'number' }]"
    />

  </div>
</template>
