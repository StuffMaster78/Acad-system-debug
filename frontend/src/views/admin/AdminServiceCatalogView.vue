<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { Plus, RefreshCw, Save, Trash2 } from "@lucide/vue";
import { api, apiPath } from "@/api/client";
import { useAuthStore } from "@/stores/auth";
import { usePortalContextStore } from "@/stores/portalContext";
import { useWebsitesStore } from "@/stores/websites";

const auth = useAuthStore();
const portal = usePortalContextStore();
const websites = useWebsitesStore();

const isSuperadmin = auth.role === "superadmin";
const selectedWebsiteId = ref<number | null>(null);
const loading = ref(false);
const saving = ref(false);
const error = ref("");
const notice = ref("");

// ── Data ──────────────────────────────────────────────────────────────────────
interface CatalogItem { id: number; service_code: string; name: string; description: string; service_family: string; is_active: boolean; sort_order: number }
interface Addon       { id: number; addon_code: string; name: string; description: string; flat_amount: string; is_public: boolean; is_active: boolean; sort_order: number }

const items  = ref<CatalogItem[]>([]);
const addons = ref<Addon[]>([]);
const activeTab = ref<"items" | "addons">("addons");

const itemDraft  = reactive({ service_code: "", name: "", description: "", service_family: "standard_paper", is_active: true, sort_order: 0 });
const addonDraft = reactive({ addon_code: "", name: "", description: "", flat_amount: "0.00", is_public: true, is_active: true, sort_order: 0 });
const editingItemId  = ref<number | null>(null);
const editingAddonId = ref<number | null>(null);

const websiteParams = () =>
  isSuperadmin && selectedWebsiteId.value ? `?website_id=${selectedWebsiteId.value}` : "";

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const [ir, ar] = await Promise.all([
      api.get<CatalogItem[]>(apiPath(`/pricing/admin/service-catalog/items/${websiteParams()}`)),
      api.get<Addon[]>(apiPath(`/pricing/admin/service-catalog/addons/${websiteParams()}`)),
    ]);
    items.value  = Array.isArray(ir.data) ? ir.data : (ir.data as any).results ?? [];
    addons.value = Array.isArray(ar.data) ? ar.data : (ar.data as any).results ?? [];
  } catch { error.value = "Failed to load catalog data."; }
  finally { loading.value = false; }
}

// ── Items ─────────────────────────────────────────────────────────────────────
function editItem(item: CatalogItem) {
  editingItemId.value = item.id;
  Object.assign(itemDraft, item);
}

function resetItem() {
  editingItemId.value = null;
  Object.assign(itemDraft, { service_code: "", name: "", description: "", service_family: "standard_paper", is_active: true, sort_order: 0 });
}

async function saveItem() {
  if (!itemDraft.service_code.trim() || !itemDraft.name.trim()) return;
  saving.value = true;
  try {
    const params = isSuperadmin && selectedWebsiteId.value ? { website_id: selectedWebsiteId.value } : undefined;
    if (editingItemId.value) {
      await api.patch(apiPath(`/pricing/admin/service-catalog/items/${editingItemId.value}/`), itemDraft, { params });
    } else {
      await api.post(apiPath("/pricing/admin/service-catalog/items/"), itemDraft, { params });
    }
    notice.value = "Catalog item saved.";
    resetItem();
    await load();
  } catch { error.value = "Failed to save item."; }
  finally { saving.value = false; }
}

async function deleteItem(id: number) {
  if (!confirm("Delete this catalog item?")) return;
  try { await api.delete(apiPath(`/pricing/admin/service-catalog/items/${id}/`)); await load(); } catch { error.value = "Failed to delete."; }
}

// ── Addons ────────────────────────────────────────────────────────────────────
function editAddon(addon: Addon) {
  editingAddonId.value = addon.id;
  Object.assign(addonDraft, addon);
}

function resetAddon() {
  editingAddonId.value = null;
  Object.assign(addonDraft, { addon_code: "", name: "", description: "", flat_amount: "0.00", is_public: true, is_active: true, sort_order: 0 });
}

async function saveAddon() {
  if (!addonDraft.addon_code.trim() || !addonDraft.name.trim()) return;
  saving.value = true;
  try {
    const params = isSuperadmin && selectedWebsiteId.value ? { website_id: selectedWebsiteId.value } : undefined;
    if (editingAddonId.value) {
      await api.patch(apiPath(`/pricing/admin/service-catalog/addons/${editingAddonId.value}/`), addonDraft, { params });
    } else {
      await api.post(apiPath("/pricing/admin/service-catalog/addons/"), addonDraft, { params });
    }
    notice.value = "Add-on saved.";
    resetAddon();
    await load();
  } catch { error.value = "Failed to save add-on."; }
  finally { saving.value = false; }
}

async function deleteAddon(id: number) {
  if (!confirm("Delete this add-on?")) return;
  try { await api.delete(apiPath(`/pricing/admin/service-catalog/addons/${id}/`)); await load(); } catch { error.value = "Failed to delete."; }
}

onMounted(async () => {
  await websites.ensure();
  selectedWebsiteId.value = portal.website?.id ?? websites.list[0]?.id ?? null;
  await load();
});
</script>

<template>
  <div class="min-h-screen bg-slate-50 p-6 space-y-5">

    <!-- Header -->
    <div class="flex items-center justify-between flex-wrap gap-3">
      <div>
        <h1 class="text-xl font-bold text-ink">Service Catalog &amp; Add-ons</h1>
        <p class="text-sm text-graphite mt-0.5">Manage orderable services and optional add-ons available to clients.</p>
      </div>
      <div class="flex gap-2 items-center flex-wrap">
        <select
          v-if="isSuperadmin"
          v-model.number="selectedWebsiteId"
          class="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus-ring"
          @change="load"
        >
          <option v-for="s in websites.options" :key="s.value" :value="s.value">{{ s.label }}</option>
        </select>
        <button class="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm" @click="load">
          <RefreshCw class="size-4" :class="loading ? 'animate-spin' : ''" /> Refresh
        </button>
      </div>
    </div>

    <!-- Notices -->
    <div v-if="error"  class="rounded-lg border border-rose-200    bg-rose-50    px-4 py-3 text-sm text-rose-700">{{ error }}</div>
    <div v-if="notice" class="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ notice }}</div>

    <!-- Tabs -->
    <div class="flex gap-2 border-b border-slate-200">
      <button
        v-for="t in [{ key: 'addons', label: 'Add-ons / Upsells' }, { key: 'items', label: 'Service Catalog Items' }]"
        :key="t.key"
        class="pb-3 text-sm font-medium border-b-2 transition-colors -mb-px px-1"
        :class="activeTab === t.key ? 'border-ink text-ink' : 'border-transparent text-graphite hover:text-ink'"
        @click="activeTab = t.key as typeof activeTab"
      >{{ t.label }}</button>
    </div>

    <!-- ── ADD-ONS TAB ─────────────────────────────────────────────────────── -->
    <template v-if="activeTab === 'addons'">
      <div class="grid gap-5 lg:grid-cols-[1fr_22rem]">

        <!-- Add-on list -->
        <div class="rounded-xl border border-slate-200 bg-white overflow-hidden">
          <div class="border-b border-slate-100 px-5 py-4 flex items-center justify-between">
            <h2 class="text-sm font-semibold text-ink">Add-ons ({{ addons.length }})</h2>
            <button class="text-xs text-berry hover:underline" @click="resetAddon"><Plus class="inline size-3.5 mr-1" />New</button>
          </div>
          <div v-if="loading" class="py-10 text-center text-sm text-graphite">Loading…</div>
          <div v-else-if="!addons.length" class="py-10 text-center text-sm text-graphite">No add-ons yet.</div>
          <table v-else class="min-w-full text-sm">
            <thead class="bg-slate-50 border-b border-slate-100 text-xs text-graphite uppercase tracking-wide">
              <tr>
                <th class="px-4 py-3 text-left">Name</th>
                <th class="px-4 py-3 text-left">Code</th>
                <th class="px-4 py-3 text-right">Price</th>
                <th class="px-4 py-3 text-left">Status</th>
                <th class="px-4 py-3" />
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-50">
              <tr v-for="a in addons" :key="a.id" class="hover:bg-slate-50">
                <td class="px-4 py-3">
                  <p class="font-medium text-ink">{{ a.name }}</p>
                  <p class="text-xs text-graphite truncate max-w-[200px]">{{ a.description }}</p>
                </td>
                <td class="px-4 py-3 font-mono text-xs text-graphite">{{ a.addon_code }}</td>
                <td class="px-4 py-3 text-right font-semibold text-ink">${{ a.flat_amount }}</td>
                <td class="px-4 py-3">
                  <span class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold"
                    :class="a.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-graphite'">
                    {{ a.is_active ? "Active" : "Inactive" }}
                  </span>
                </td>
                <td class="px-4 py-3">
                  <div class="flex gap-1 justify-end">
                    <button class="rounded border border-slate-200 px-2 py-1 text-xs hover:bg-slate-50" @click="editAddon(a)">Edit</button>
                    <button class="rounded border border-rose-200 px-2 py-1 text-xs text-rose-600 hover:bg-rose-50" @click="deleteAddon(a.id)"><Trash2 class="size-3" /></button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Add-on form -->
        <div class="rounded-xl border border-slate-200 bg-white p-5 space-y-4">
          <h3 class="text-sm font-semibold text-ink">{{ editingAddonId ? "Edit add-on" : "New add-on" }}</h3>
          <label class="block space-y-1">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Code *</span>
            <input v-model="addonDraft.addon_code" placeholder="e.g. plagiarism_check" class="focus-ring mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" />
          </label>
          <label class="block space-y-1">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Name *</span>
            <input v-model="addonDraft.name" placeholder="Plagiarism Report" class="focus-ring mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" />
          </label>
          <label class="block space-y-1">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Description</span>
            <textarea v-model="addonDraft.description" rows="2" class="focus-ring mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm resize-none" />
          </label>
          <label class="block space-y-1">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Price (flat, USD)</span>
            <input v-model="addonDraft.flat_amount" type="number" min="0" step="0.01" class="focus-ring mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" />
          </label>
          <div class="flex gap-4 text-sm text-graphite">
            <label class="flex items-center gap-2"><input v-model="addonDraft.is_active" type="checkbox" class="rounded accent-berry" /> Active</label>
            <label class="flex items-center gap-2"><input v-model="addonDraft.is_public" type="checkbox" class="rounded accent-berry" /> Visible to clients</label>
          </div>
          <div class="flex gap-2">
            <button class="flex-1 inline-flex items-center justify-center gap-2 rounded-lg bg-berry px-4 py-2 text-sm font-semibold text-white hover:bg-berry/90 disabled:opacity-60"
              :disabled="saving || !addonDraft.addon_code.trim() || !addonDraft.name.trim()"
              @click="saveAddon">
              <Save class="size-4" /> {{ saving ? "Saving…" : editingAddonId ? "Save changes" : "Create add-on" }}
            </button>
            <button v-if="editingAddonId" class="rounded-lg border border-slate-200 px-4 py-2 text-sm text-graphite hover:bg-slate-50" @click="resetAddon">Cancel</button>
          </div>
        </div>
      </div>
    </template>

    <!-- ── CATALOG ITEMS TAB ──────────────────────────────────────────────── -->
    <template v-else>
      <div class="grid gap-5 lg:grid-cols-[1fr_22rem]">

        <!-- Items list -->
        <div class="rounded-xl border border-slate-200 bg-white overflow-hidden">
          <div class="border-b border-slate-100 px-5 py-4 flex items-center justify-between">
            <h2 class="text-sm font-semibold text-ink">Catalog items ({{ items.length }})</h2>
            <button class="text-xs text-berry hover:underline" @click="resetItem"><Plus class="inline size-3.5 mr-1" />New</button>
          </div>
          <div v-if="loading" class="py-10 text-center text-sm text-graphite">Loading…</div>
          <div v-else-if="!items.length" class="py-10 text-center text-sm text-graphite">No catalog items yet.</div>
          <table v-else class="min-w-full text-sm">
            <thead class="bg-slate-50 border-b border-slate-100 text-xs text-graphite uppercase tracking-wide">
              <tr>
                <th class="px-4 py-3 text-left">Name</th>
                <th class="px-4 py-3 text-left">Code</th>
                <th class="px-4 py-3 text-left">Family</th>
                <th class="px-4 py-3 text-left">Status</th>
                <th class="px-4 py-3" />
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-50">
              <tr v-for="item in items" :key="item.id" class="hover:bg-slate-50">
                <td class="px-4 py-3 font-medium text-ink">{{ item.name }}</td>
                <td class="px-4 py-3 font-mono text-xs text-graphite">{{ item.service_code }}</td>
                <td class="px-4 py-3 text-graphite capitalize">{{ item.service_family.replace(/_/g, ' ') }}</td>
                <td class="px-4 py-3">
                  <span class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold"
                    :class="item.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-graphite'">
                    {{ item.is_active ? "Active" : "Inactive" }}
                  </span>
                </td>
                <td class="px-4 py-3">
                  <div class="flex gap-1 justify-end">
                    <button class="rounded border border-slate-200 px-2 py-1 text-xs hover:bg-slate-50" @click="editItem(item)">Edit</button>
                    <button class="rounded border border-rose-200 px-2 py-1 text-xs text-rose-600 hover:bg-rose-50" @click="deleteItem(item.id)"><Trash2 class="size-3" /></button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Item form -->
        <div class="rounded-xl border border-slate-200 bg-white p-5 space-y-4">
          <h3 class="text-sm font-semibold text-ink">{{ editingItemId ? "Edit item" : "New item" }}</h3>
          <label class="block space-y-1">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Service code *</span>
            <input v-model="itemDraft.service_code" placeholder="e.g. standard_paper" class="focus-ring mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" />
          </label>
          <label class="block space-y-1">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Name *</span>
            <input v-model="itemDraft.name" class="focus-ring mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" />
          </label>
          <label class="block space-y-1">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Service family</span>
            <input v-model="itemDraft.service_family" class="focus-ring mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" placeholder="standard_paper" />
          </label>
          <div class="flex gap-4 text-sm text-graphite">
            <label class="flex items-center gap-2"><input v-model="itemDraft.is_active" type="checkbox" class="rounded accent-berry" /> Active</label>
          </div>
          <div class="flex gap-2">
            <button class="flex-1 inline-flex items-center justify-center gap-2 rounded-lg bg-berry px-4 py-2 text-sm font-semibold text-white hover:bg-berry/90 disabled:opacity-60"
              :disabled="saving"
              @click="saveItem">
              <Save class="size-4" /> {{ saving ? "Saving…" : editingItemId ? "Save changes" : "Create item" }}
            </button>
            <button v-if="editingItemId" class="rounded-lg border border-slate-200 px-4 py-2 text-sm text-graphite hover:bg-slate-50" @click="resetItem">Cancel</button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
