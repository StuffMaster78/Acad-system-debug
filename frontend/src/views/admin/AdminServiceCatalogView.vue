<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { Plus, RefreshCw, Save, Trash2 } from "@lucide/vue";
import { api, apiPath } from "@/api/client";
import { useAuthStore } from "@/stores/auth";
import { usePortalContextStore } from "@/stores/portalContext";
import { useWebsitesStore } from "@/stores/websites";

const auth = useAuthStore();
const portal = usePortalContextStore();
const websites = useWebsitesStore();

const isSuperadmin = auth.role === "superadmin";
type CatalogTab = "items" | "addons";
const props = withDefaults(defineProps<{
  embedded?: boolean;
  tab?: CatalogTab;
}>(), {
  embedded: false,
  tab: "items",
});
const selectedWebsiteId = ref<number | null>(null);
const loading = ref(false);
const saving = ref(false);
const error = ref("");
const notice = ref("");

type ServiceFamily = "paper_order" | "design_order" | "diagram_order";
type PricingStrategy = "formula" | "fixed" | "hybrid";
type PricingUnit = "page" | "slide" | "item" | "quantity" | "order" | "diagram";

interface DesignConfig {
  design_product_type: string;
  default_package_type: string;
  supports_quantity: boolean;
  supports_slides: boolean;
  supports_deadline: boolean;
  supports_files: boolean;
  supports_topic: boolean;
  supports_instructions: boolean;
}

interface DiagramConfig {
  diagram_type: string;
  supports_quantity: boolean;
  supports_complexity: boolean;
  supports_deadline: boolean;
  supports_files: boolean;
  supports_topic: boolean;
  supports_instructions: boolean;
}

interface CatalogItem {
  id: number;
  service_code: string;
  name: string;
  description: string;
  service_family: ServiceFamily;
  pricing_strategy: PricingStrategy;
  pricing_unit: PricingUnit;
  base_amount: string;
  minimum_charge: string;
  is_public: boolean;
  is_active: boolean;
  sort_order: number;
  design_order_config?: DesignConfig;
  diagram_order_config?: DiagramConfig;
}

interface Addon {
  id: number;
  addon_code: string;
  name: string;
  description: string;
  flat_amount: string;
  is_public: boolean;
  is_active: boolean;
  sort_order: number;
}

const items = ref<CatalogItem[]>([]);
const addons = ref<Addon[]>([]);
const activeTab = ref<CatalogTab>(props.tab);
const PAGE_SIZE = 10;
const serviceSearch = ref("");
const addonSearch = ref("");
const servicePage = ref(1);
const addonPage = ref(1);

const serviceFamilyOptions = [
  { value: "paper_order", label: "Paper order" },
  { value: "design_order", label: "Design order" },
  { value: "diagram_order", label: "Diagram order" },
] as const;
const pricingStrategyOptions = [
  { value: "formula", label: "Formula" },
  { value: "fixed", label: "Fixed" },
  { value: "hybrid", label: "Hybrid" },
] as const;
const pricingUnitOptions = [
  { value: "page", label: "Page" },
  { value: "slide", label: "Slide" },
  { value: "item", label: "Item" },
  { value: "quantity", label: "Quantity" },
  { value: "order", label: "Order" },
  { value: "diagram", label: "Diagram" },
] as const;
const designProductOptions = [
  { value: "", label: "Unspecified" },
  { value: "presentation", label: "Presentation" },
  { value: "brochure", label: "Brochure" },
  { value: "catalogue", label: "Catalogue" },
  { value: "poster", label: "Poster" },
  { value: "flyer", label: "Flyer" },
  { value: "infographic", label: "Infographic" },
] as const;
const designPackageOptions = [
  { value: "", label: "Unspecified" },
  { value: "standard", label: "Standard" },
  { value: "premium", label: "Premium" },
  { value: "custom", label: "Custom" },
] as const;
const diagramTypeOptions = [
  { value: "", label: "Unspecified" },
  { value: "flowchart", label: "Flowchart" },
  { value: "erd", label: "ERD" },
  { value: "uml", label: "UML diagram" },
  { value: "process_diagram", label: "Process diagram" },
  { value: "system_diagram", label: "System diagram" },
] as const;

function defaultDesignConfig(): DesignConfig {
  return {
    design_product_type: "",
    default_package_type: "",
    supports_quantity: false,
    supports_slides: false,
    supports_deadline: true,
    supports_files: true,
    supports_topic: true,
    supports_instructions: true,
  };
}

function defaultDiagramConfig(): DiagramConfig {
  return {
    diagram_type: "",
    supports_quantity: true,
    supports_complexity: true,
    supports_deadline: true,
    supports_files: true,
    supports_topic: true,
    supports_instructions: true,
  };
}

const itemDraft = reactive({
  service_code: "",
  name: "",
  description: "",
  service_family: "paper_order" as ServiceFamily,
  pricing_strategy: "formula" as PricingStrategy,
  pricing_unit: "page" as PricingUnit,
  base_amount: "0.00",
  minimum_charge: "0.00",
  is_public: true,
  is_active: true,
  sort_order: 0,
  design_order_config: defaultDesignConfig(),
  diagram_order_config: defaultDiagramConfig(),
});
const addonDraft = reactive({
  addon_code: "",
  name: "",
  description: "",
  flat_amount: "0.00",
  is_public: true,
  is_active: true,
  sort_order: 0,
});
const editingItemId = ref<number | null>(null);
const editingAddonId = ref<number | null>(null);

const websiteParams = () =>
  isSuperadmin && selectedWebsiteId.value ? `?website_id=${selectedWebsiteId.value}` : "";
const requestParams = computed(() =>
  isSuperadmin && selectedWebsiteId.value ? { website_id: selectedWebsiteId.value } : undefined,
);

function serviceFamilyLabel(value: string) {
  return serviceFamilyOptions.find((option) => option.value === value)?.label ?? value.replace(/_/g, " ");
}

function itemConfigSummary(item: CatalogItem) {
  if (item.service_family === "design_order") {
    const config = item.design_order_config;
    if (!config) return "Design settings not configured";
    const pieces = [
      config.design_product_type || "any product",
      config.default_package_type || "any package",
      config.supports_slides ? "slides" : null,
      config.supports_quantity ? "quantity" : null,
    ].filter(Boolean);
    return pieces.join(" · ");
  }
  if (item.service_family === "diagram_order") {
    const config = item.diagram_order_config;
    if (!config) return "Diagram settings not configured";
    const pieces = [
      config.diagram_type || "any diagram",
      config.supports_complexity ? "complexity" : null,
      config.supports_quantity ? "quantity" : null,
    ].filter(Boolean);
    return pieces.join(" · ");
  }
  return `${item.pricing_unit} · ${item.pricing_strategy}`;
}

function includesQuery(values: unknown[], query: string) {
  const needle = query.trim().toLowerCase();
  if (!needle) return true;
  return values.some((value) => String(value ?? "").toLowerCase().includes(needle));
}

const filteredItems = computed(() =>
  items.value.filter((item) =>
    includesQuery([
      item.name,
      item.service_code,
      item.description,
      item.service_family,
      item.pricing_strategy,
      item.pricing_unit,
      itemConfigSummary(item),
    ], serviceSearch.value),
  ),
);
const filteredAddons = computed(() =>
  addons.value.filter((addon) =>
    includesQuery([
      addon.name,
      addon.addon_code,
      addon.description,
      addon.flat_amount,
      addon.is_public ? "public" : "private",
      addon.is_active ? "active" : "inactive",
    ], addonSearch.value),
  ),
);
const serviceTotalPages = computed(() => Math.max(1, Math.ceil(filteredItems.value.length / PAGE_SIZE)));
const addonTotalPages = computed(() => Math.max(1, Math.ceil(filteredAddons.value.length / PAGE_SIZE)));
const visibleItems = computed(() => {
  const start = (servicePage.value - 1) * PAGE_SIZE;
  return filteredItems.value.slice(start, start + PAGE_SIZE);
});
const visibleAddons = computed(() => {
  const start = (addonPage.value - 1) * PAGE_SIZE;
  return filteredAddons.value.slice(start, start + PAGE_SIZE);
});
const serviceShowingFrom = computed(() => filteredItems.value.length ? (servicePage.value - 1) * PAGE_SIZE + 1 : 0);
const serviceShowingTo = computed(() => Math.min(servicePage.value * PAGE_SIZE, filteredItems.value.length));
const addonShowingFrom = computed(() => filteredAddons.value.length ? (addonPage.value - 1) * PAGE_SIZE + 1 : 0);
const addonShowingTo = computed(() => Math.min(addonPage.value * PAGE_SIZE, filteredAddons.value.length));

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const [ir, ar] = await Promise.all([
      api.get<CatalogItem[]>(apiPath(`/pricing/admin/service-catalog/items/${websiteParams()}`)),
      api.get<Addon[]>(apiPath(`/pricing/admin/service-catalog/addons/${websiteParams()}`)),
    ]);
    items.value = Array.isArray(ir.data) ? ir.data : (ir.data as { results?: CatalogItem[] }).results ?? [];
    addons.value = Array.isArray(ar.data) ? ar.data : (ar.data as { results?: Addon[] }).results ?? [];
  } catch {
    error.value = "Failed to load catalog data.";
  } finally {
    loading.value = false;
  }
}

function resetItem() {
  editingItemId.value = null;
  Object.assign(itemDraft, {
    service_code: "",
    name: "",
    description: "",
    service_family: "paper_order",
    pricing_strategy: "formula",
    pricing_unit: "page",
    base_amount: "0.00",
    minimum_charge: "0.00",
    is_public: true,
    is_active: true,
    sort_order: 0,
    design_order_config: defaultDesignConfig(),
    diagram_order_config: defaultDiagramConfig(),
  });
}

function editItem(item: CatalogItem) {
  editingItemId.value = item.id;
  Object.assign(itemDraft, {
    service_code: item.service_code,
    name: item.name,
    description: item.description ?? "",
    service_family: item.service_family,
    pricing_strategy: item.pricing_strategy,
    pricing_unit: item.pricing_unit,
    base_amount: item.base_amount,
    minimum_charge: item.minimum_charge,
    is_public: item.is_public,
    is_active: item.is_active,
    sort_order: item.sort_order,
    design_order_config: { ...defaultDesignConfig(), ...(item.design_order_config ?? {}) },
    diagram_order_config: { ...defaultDiagramConfig(), ...(item.diagram_order_config ?? {}) },
  });
}

function itemPayload() {
  const payload: Record<string, unknown> = {
    service_code: itemDraft.service_code,
    name: itemDraft.name,
    description: itemDraft.description,
    service_family: itemDraft.service_family,
    pricing_strategy: itemDraft.pricing_strategy,
    pricing_unit: itemDraft.pricing_unit,
    base_amount: itemDraft.base_amount,
    minimum_charge: itemDraft.minimum_charge,
    is_public: itemDraft.is_public,
    is_active: itemDraft.is_active,
    sort_order: itemDraft.sort_order,
  };
  if (itemDraft.service_family === "design_order") {
    payload.design_order_config = itemDraft.design_order_config;
  }
  if (itemDraft.service_family === "diagram_order") {
    payload.diagram_order_config = itemDraft.diagram_order_config;
  }
  return payload;
}

async function saveItem() {
  if (!itemDraft.service_code.trim() || !itemDraft.name.trim()) return;
  saving.value = true;
  error.value = "";
  try {
    if (editingItemId.value) {
      await api.patch(
        apiPath(`/pricing/admin/service-catalog/items/${editingItemId.value}/`),
        itemPayload(),
        { params: requestParams.value },
      );
    } else {
      await api.post(apiPath("/pricing/admin/service-catalog/items/"), itemPayload(), {
        params: requestParams.value,
      });
    }
    notice.value = "Catalog item saved.";
    resetItem();
    await load();
  } catch {
    error.value = "Failed to save item.";
  } finally {
    saving.value = false;
  }
}

async function deleteItem(id: number) {
  if (!confirm("Delete this catalog item?")) return;
  try {
    await api.delete(apiPath(`/pricing/admin/service-catalog/items/${id}/`), {
      params: requestParams.value,
    });
    await load();
  } catch {
    error.value = "Failed to delete.";
  }
}

function resetAddon() {
  editingAddonId.value = null;
  Object.assign(addonDraft, {
    addon_code: "",
    name: "",
    description: "",
    flat_amount: "0.00",
    is_public: true,
    is_active: true,
    sort_order: 0,
  });
}

function editAddon(addon: Addon) {
  editingAddonId.value = addon.id;
  Object.assign(addonDraft, addon);
}

async function saveAddon() {
  if (!addonDraft.addon_code.trim() || !addonDraft.name.trim()) return;
  saving.value = true;
  error.value = "";
  try {
    if (editingAddonId.value) {
      await api.patch(
        apiPath(`/pricing/admin/service-catalog/addons/${editingAddonId.value}/`),
        addonDraft,
        { params: requestParams.value },
      );
    } else {
      await api.post(apiPath("/pricing/admin/service-catalog/addons/"), addonDraft, {
        params: requestParams.value,
      });
    }
    notice.value = "Add-on saved.";
    resetAddon();
    await load();
  } catch {
    error.value = "Failed to save add-on.";
  } finally {
    saving.value = false;
  }
}

async function deleteAddon(id: number) {
  if (!confirm("Delete this add-on?")) return;
  try {
    await api.delete(apiPath(`/pricing/admin/service-catalog/addons/${id}/`), {
      params: requestParams.value,
    });
    await load();
  } catch {
    error.value = "Failed to delete.";
  }
}

onMounted(async () => {
  await websites.ensure();
  selectedWebsiteId.value = portal.website?.id ?? websites.list[0]?.id ?? null;
  await load();
});

watch(
  () => props.tab,
  (tab) => {
    activeTab.value = tab;
  },
);

watch(serviceSearch, () => {
  servicePage.value = 1;
});

watch(addonSearch, () => {
  addonPage.value = 1;
});

watch(serviceTotalPages, (next) => {
  if (servicePage.value > next) servicePage.value = next;
});

watch(addonTotalPages, (next) => {
  if (addonPage.value > next) addonPage.value = next;
});
</script>

<template>
  <div class="space-y-5">
    <div
      v-if="props.embedded"
      class="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm"
    >
      <div>
        <p class="text-sm font-semibold text-ink">{{ activeTab === "items" ? "Service Catalog" : "Add-ons & Upsells" }}</p>
        <p class="text-xs text-graphite">
          {{ activeTab === "items" ? "Orderable paper, design, and diagram services." : "Optional client-facing extras and upsells." }}
        </p>
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <select
          v-if="isSuperadmin"
          v-model.number="selectedWebsiteId"
          class="focus-ring rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm"
          @change="load"
        >
          <option v-for="site in websites.options" :key="site.value" :value="site.value">{{ site.label }}</option>
        </select>
        <button class="focus-ring inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-semibold" @click="load">
          <RefreshCw class="size-4" :class="loading ? 'animate-spin' : ''" /> Refresh
        </button>
      </div>
    </div>
    <div v-else class="flex flex-wrap items-end justify-between gap-3 border-b border-slate-200 pb-5">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Catalog</p>
        <h1 class="mt-2 text-2xl font-semibold text-ink">Service Catalog &amp; Add-ons</h1>
        <p class="mt-1 text-sm text-graphite">Manage orderable paper, design, and diagram services plus client-facing extras.</p>
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <select
          v-if="isSuperadmin"
          v-model.number="selectedWebsiteId"
          class="focus-ring rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm"
          @change="load"
        >
          <option v-for="site in websites.options" :key="site.value" :value="site.value">{{ site.label }}</option>
        </select>
        <button class="focus-ring inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-semibold" @click="load">
          <RefreshCw class="size-4" :class="loading ? 'animate-spin' : ''" /> Refresh
        </button>
      </div>
    </div>

    <div v-if="error" class="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</div>
    <div v-if="notice" class="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ notice }}</div>

    <div v-if="!props.embedded" class="flex gap-2 border-b border-slate-200">
      <button
        v-for="tab in [{ key: 'items', label: 'Services' }, { key: 'addons', label: 'Add-ons / Upsells' }]"
        :key="tab.key"
        class="-mb-px border-b-2 px-1 pb-3 text-sm font-medium transition-colors"
        :class="activeTab === tab.key ? 'border-ink text-ink' : 'border-transparent text-graphite hover:text-ink'"
        @click="activeTab = tab.key as typeof activeTab"
      >
        {{ tab.label }}
      </button>
    </div>

    <template v-if="activeTab === 'items'">
      <div class="grid gap-5 2xl:grid-cols-[minmax(0,1fr)_28rem]">
        <div class="overflow-hidden rounded-xl border border-slate-200 bg-white">
          <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 px-5 py-4">
            <div>
              <h2 class="text-sm font-semibold text-ink">Services ({{ filteredItems.length }} / {{ items.length }})</h2>
              <p class="text-xs text-graphite">Landscape view of service family, pricing, rules, and visibility.</p>
            </div>
            <input
              v-model="serviceSearch"
              type="search"
              placeholder="Search services..."
              class="focus-ring h-9 min-w-[16rem] rounded-lg border border-slate-200 bg-white px-3 text-sm"
            />
            <button class="text-xs font-semibold text-signal hover:underline" @click="resetItem">
              <Plus class="mr-1 inline size-3.5" />New
            </button>
          </div>
          <div v-if="loading" class="py-10 text-center text-sm text-graphite">Loading...</div>
          <div v-else-if="!visibleItems.length" class="py-10 text-center text-sm text-graphite">
            {{ items.length ? "No services match your search." : "No catalog items yet." }}
          </div>
          <div v-else class="overflow-x-auto">
          <table class="min-w-[1080px] text-sm">
            <thead class="border-b border-slate-100 bg-slate-50 text-xs uppercase tracking-wide text-graphite">
              <tr>
                <th class="px-4 py-3 text-left">Name</th>
                <th class="px-4 py-3 text-left">Family</th>
                <th class="px-4 py-3 text-left">Pricing</th>
                <th class="px-4 py-3 text-left">Rules</th>
                <th class="px-4 py-3 text-center">Public</th>
                <th class="px-4 py-3 text-right">Sort</th>
                <th class="px-4 py-3 text-left">Status</th>
                <th class="px-4 py-3" />
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-50">
              <tr v-for="item in visibleItems" :key="item.id" class="hover:bg-slate-50">
                <td class="px-4 py-3 min-w-[220px]">
                  <p class="font-medium text-ink">{{ item.name }}</p>
                  <p class="font-mono text-xs text-graphite">{{ item.service_code }}</p>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-graphite">{{ serviceFamilyLabel(item.service_family) }}</td>
                <td class="px-4 py-3 whitespace-nowrap text-graphite">
                  <p class="capitalize">{{ item.pricing_strategy }} / {{ item.pricing_unit }}</p>
                  <p class="text-xs">Base ${{ item.base_amount }} · Min ${{ item.minimum_charge }}</p>
                </td>
                <td class="px-4 py-3 min-w-[220px] text-xs text-graphite">{{ itemConfigSummary(item) }}</td>
                <td class="px-4 py-3 text-center">
                  <span
                    class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold"
                    :class="item.is_public ? 'bg-sky-50 text-sky-700' : 'bg-slate-100 text-graphite'"
                  >
                    {{ item.is_public ? "Public" : "Hidden" }}
                  </span>
                </td>
                <td class="px-4 py-3 text-right text-graphite">{{ item.sort_order }}</td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <span
                    class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold"
                    :class="item.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-graphite'"
                  >
                    {{ item.is_active ? "Active" : "Inactive" }}
                  </span>
                </td>
                <td class="px-4 py-3">
                  <div class="flex justify-end gap-1">
                    <button class="rounded border border-slate-200 px-2 py-1 text-xs hover:bg-slate-50" @click="editItem(item)">Edit</button>
                    <button class="rounded border border-rose-200 px-2 py-1 text-xs text-rose-600 hover:bg-rose-50" @click="deleteItem(item.id)">
                      <Trash2 class="size-3" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          </div>
          <div v-if="items.length" class="flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 px-5 py-2 text-xs text-graphite">
            <span>Showing {{ serviceShowingFrom }}-{{ serviceShowingTo }} of {{ filteredItems.length }} services</span>
            <div class="flex items-center gap-2">
              <button class="rounded border border-slate-200 px-2 py-1 disabled:opacity-40" :disabled="servicePage <= 1" @click="servicePage -= 1">Prev</button>
              <span>Page {{ servicePage }} / {{ serviceTotalPages }}</span>
              <button class="rounded border border-slate-200 px-2 py-1 disabled:opacity-40" :disabled="servicePage >= serviceTotalPages" @click="servicePage += 1">Next</button>
            </div>
          </div>
        </div>

        <form class="space-y-4 rounded-xl border border-slate-200 bg-white p-5" @submit.prevent="saveItem">
          <h3 class="text-sm font-semibold text-ink">{{ editingItemId ? "Edit service" : "New service" }}</h3>
          <div class="grid gap-3 sm:grid-cols-2">
            <label class="block sm:col-span-2">
              <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Name *</span>
              <input v-model.trim="itemDraft.name" class="focus-ring mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" />
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Service code *</span>
              <input v-model.trim="itemDraft.service_code" placeholder="e.g. presentation_design" class="focus-ring mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" />
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Family</span>
              <select v-model="itemDraft.service_family" class="focus-ring mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm">
                <option v-for="option in serviceFamilyOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
              </select>
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Pricing strategy</span>
              <select v-model="itemDraft.pricing_strategy" class="focus-ring mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm">
                <option v-for="option in pricingStrategyOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
              </select>
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Pricing unit</span>
              <select v-model="itemDraft.pricing_unit" class="focus-ring mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm">
                <option v-for="option in pricingUnitOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
              </select>
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Base amount</span>
              <input v-model="itemDraft.base_amount" type="number" min="0" step="0.01" class="focus-ring mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" />
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Minimum charge</span>
              <input v-model="itemDraft.minimum_charge" type="number" min="0" step="0.01" class="focus-ring mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" />
            </label>
            <label class="block sm:col-span-2">
              <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Description</span>
              <textarea v-model.trim="itemDraft.description" rows="2" class="focus-ring mt-1 w-full resize-none rounded-lg border border-slate-200 px-3 py-2 text-sm" />
            </label>
          </div>

          <div v-if="itemDraft.service_family === 'design_order'" class="rounded-lg border border-blue-100 bg-blue-50/40 p-3">
            <p class="mb-3 text-xs font-semibold uppercase tracking-wide text-blue-700">Design settings</p>
            <div class="grid gap-3 sm:grid-cols-2">
              <label class="block">
                <span class="text-xs font-semibold text-graphite">Product type</span>
                <select v-model="itemDraft.design_order_config.design_product_type" class="focus-ring mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm">
                  <option v-for="option in designProductOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
                </select>
              </label>
              <label class="block">
                <span class="text-xs font-semibold text-graphite">Default package</span>
                <select v-model="itemDraft.design_order_config.default_package_type" class="focus-ring mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm">
                  <option v-for="option in designPackageOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
                </select>
              </label>
            </div>
            <div class="mt-3 grid gap-2 text-sm text-graphite sm:grid-cols-2">
              <label class="flex items-center gap-2"><input v-model="itemDraft.design_order_config.supports_quantity" type="checkbox" class="rounded accent-signal" /> Quantity</label>
              <label class="flex items-center gap-2"><input v-model="itemDraft.design_order_config.supports_slides" type="checkbox" class="rounded accent-signal" /> Slides</label>
              <label class="flex items-center gap-2"><input v-model="itemDraft.design_order_config.supports_deadline" type="checkbox" class="rounded accent-signal" /> Deadline</label>
              <label class="flex items-center gap-2"><input v-model="itemDraft.design_order_config.supports_files" type="checkbox" class="rounded accent-signal" /> Files</label>
              <label class="flex items-center gap-2"><input v-model="itemDraft.design_order_config.supports_topic" type="checkbox" class="rounded accent-signal" /> Topic</label>
              <label class="flex items-center gap-2"><input v-model="itemDraft.design_order_config.supports_instructions" type="checkbox" class="rounded accent-signal" /> Instructions</label>
            </div>
          </div>

          <div v-if="itemDraft.service_family === 'diagram_order'" class="rounded-lg border border-violet-100 bg-violet-50/40 p-3">
            <p class="mb-3 text-xs font-semibold uppercase tracking-wide text-violet-700">Diagram settings</p>
            <label class="block">
              <span class="text-xs font-semibold text-graphite">Diagram type</span>
              <select v-model="itemDraft.diagram_order_config.diagram_type" class="focus-ring mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm">
                <option v-for="option in diagramTypeOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
              </select>
            </label>
            <div class="mt-3 grid gap-2 text-sm text-graphite sm:grid-cols-2">
              <label class="flex items-center gap-2"><input v-model="itemDraft.diagram_order_config.supports_quantity" type="checkbox" class="rounded accent-signal" /> Quantity</label>
              <label class="flex items-center gap-2"><input v-model="itemDraft.diagram_order_config.supports_complexity" type="checkbox" class="rounded accent-signal" /> Complexity</label>
              <label class="flex items-center gap-2"><input v-model="itemDraft.diagram_order_config.supports_deadline" type="checkbox" class="rounded accent-signal" /> Deadline</label>
              <label class="flex items-center gap-2"><input v-model="itemDraft.diagram_order_config.supports_files" type="checkbox" class="rounded accent-signal" /> Files</label>
              <label class="flex items-center gap-2"><input v-model="itemDraft.diagram_order_config.supports_topic" type="checkbox" class="rounded accent-signal" /> Topic</label>
              <label class="flex items-center gap-2"><input v-model="itemDraft.diagram_order_config.supports_instructions" type="checkbox" class="rounded accent-signal" /> Instructions</label>
            </div>
          </div>

          <div class="flex flex-wrap gap-4 text-sm text-graphite">
            <label class="flex items-center gap-2"><input v-model="itemDraft.is_active" type="checkbox" class="rounded accent-signal" /> Active</label>
            <label class="flex items-center gap-2"><input v-model="itemDraft.is_public" type="checkbox" class="rounded accent-signal" /> Visible to clients</label>
          </div>
          <div class="flex gap-2">
            <button
              class="focus-ring inline-flex flex-1 items-center justify-center gap-2 rounded-lg bg-signal px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
              :disabled="saving || !itemDraft.service_code.trim() || !itemDraft.name.trim()"
              type="submit"
            >
              <Save class="size-4" /> {{ saving ? "Saving..." : editingItemId ? "Save changes" : "Create service" }}
            </button>
            <button v-if="editingItemId" class="rounded-lg border border-slate-200 px-4 py-2 text-sm text-graphite hover:bg-slate-50" type="button" @click="resetItem">Cancel</button>
          </div>
        </form>
      </div>
    </template>

    <template v-else>
      <div class="grid gap-5 2xl:grid-cols-[minmax(0,1fr)_24rem]">
        <div class="overflow-hidden rounded-xl border border-slate-200 bg-white">
          <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 px-5 py-4">
            <div>
              <h2 class="text-sm font-semibold text-ink">Add-ons ({{ filteredAddons.length }} / {{ addons.length }})</h2>
              <p class="text-xs text-graphite">Landscape view of code, price, visibility, and status.</p>
            </div>
            <input
              v-model="addonSearch"
              type="search"
              placeholder="Search add-ons..."
              class="focus-ring h-9 min-w-[16rem] rounded-lg border border-slate-200 bg-white px-3 text-sm"
            />
            <button class="text-xs font-semibold text-signal hover:underline" @click="resetAddon">
              <Plus class="mr-1 inline size-3.5" />New
            </button>
          </div>
          <div v-if="loading" class="py-10 text-center text-sm text-graphite">Loading...</div>
          <div v-else-if="!visibleAddons.length" class="py-10 text-center text-sm text-graphite">
            {{ addons.length ? "No add-ons match your search." : "No add-ons yet." }}
          </div>
          <div v-else class="overflow-x-auto">
          <table class="min-w-[860px] text-sm">
            <thead class="border-b border-slate-100 bg-slate-50 text-xs uppercase tracking-wide text-graphite">
              <tr>
                <th class="px-4 py-3 text-left">Name</th>
                <th class="px-4 py-3 text-left">Code</th>
                <th class="px-4 py-3 text-right">Price</th>
                <th class="px-4 py-3 text-center">Public</th>
                <th class="px-4 py-3 text-right">Sort</th>
                <th class="px-4 py-3 text-left">Status</th>
                <th class="px-4 py-3" />
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-50">
              <tr v-for="addon in visibleAddons" :key="addon.id" class="hover:bg-slate-50">
                <td class="px-4 py-3 min-w-[240px]">
                  <p class="font-medium text-ink">{{ addon.name }}</p>
                  <p class="max-w-[340px] text-xs text-graphite">{{ addon.description }}</p>
                </td>
                <td class="px-4 py-3 whitespace-nowrap font-mono text-xs text-graphite">{{ addon.addon_code }}</td>
                <td class="px-4 py-3 whitespace-nowrap text-right font-semibold text-ink">${{ addon.flat_amount }}</td>
                <td class="px-4 py-3 text-center">
                  <span
                    class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold"
                    :class="addon.is_public ? 'bg-sky-50 text-sky-700' : 'bg-slate-100 text-graphite'"
                  >
                    {{ addon.is_public ? "Public" : "Hidden" }}
                  </span>
                </td>
                <td class="px-4 py-3 text-right text-graphite">{{ addon.sort_order }}</td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <span
                    class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold"
                    :class="addon.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-graphite'"
                  >
                    {{ addon.is_active ? "Active" : "Inactive" }}
                  </span>
                </td>
                <td class="px-4 py-3">
                  <div class="flex justify-end gap-1">
                    <button class="rounded border border-slate-200 px-2 py-1 text-xs hover:bg-slate-50" @click="editAddon(addon)">Edit</button>
                    <button class="rounded border border-rose-200 px-2 py-1 text-xs text-rose-600 hover:bg-rose-50" @click="deleteAddon(addon.id)">
                      <Trash2 class="size-3" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          </div>
          <div v-if="addons.length" class="flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 px-5 py-2 text-xs text-graphite">
            <span>Showing {{ addonShowingFrom }}-{{ addonShowingTo }} of {{ filteredAddons.length }} add-ons</span>
            <div class="flex items-center gap-2">
              <button class="rounded border border-slate-200 px-2 py-1 disabled:opacity-40" :disabled="addonPage <= 1" @click="addonPage -= 1">Prev</button>
              <span>Page {{ addonPage }} / {{ addonTotalPages }}</span>
              <button class="rounded border border-slate-200 px-2 py-1 disabled:opacity-40" :disabled="addonPage >= addonTotalPages" @click="addonPage += 1">Next</button>
            </div>
          </div>
        </div>

        <form class="space-y-4 rounded-xl border border-slate-200 bg-white p-5" @submit.prevent="saveAddon">
          <h3 class="text-sm font-semibold text-ink">{{ editingAddonId ? "Edit add-on" : "New add-on" }}</h3>
          <label class="block">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Code *</span>
            <input v-model.trim="addonDraft.addon_code" placeholder="e.g. plagiarism_check" class="focus-ring mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" />
          </label>
          <label class="block">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Name *</span>
            <input v-model.trim="addonDraft.name" placeholder="Plagiarism Report" class="focus-ring mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" />
          </label>
          <label class="block">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Description</span>
            <textarea v-model.trim="addonDraft.description" rows="2" class="focus-ring mt-1 w-full resize-none rounded-lg border border-slate-200 px-3 py-2 text-sm" />
          </label>
          <label class="block">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Price</span>
            <input v-model="addonDraft.flat_amount" type="number" min="0" step="0.01" class="focus-ring mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" />
          </label>
          <div class="flex flex-wrap gap-4 text-sm text-graphite">
            <label class="flex items-center gap-2"><input v-model="addonDraft.is_active" type="checkbox" class="rounded accent-signal" /> Active</label>
            <label class="flex items-center gap-2"><input v-model="addonDraft.is_public" type="checkbox" class="rounded accent-signal" /> Visible to clients</label>
          </div>
          <div class="flex gap-2">
            <button
              class="focus-ring inline-flex flex-1 items-center justify-center gap-2 rounded-lg bg-signal px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
              :disabled="saving || !addonDraft.addon_code.trim() || !addonDraft.name.trim()"
              type="submit"
            >
              <Save class="size-4" /> {{ saving ? "Saving..." : editingAddonId ? "Save changes" : "Create add-on" }}
            </button>
            <button v-if="editingAddonId" class="rounded-lg border border-slate-200 px-4 py-2 text-sm text-graphite hover:bg-slate-50" type="button" @click="resetAddon">Cancel</button>
          </div>
        </form>
      </div>
    </template>
  </div>
</template>
