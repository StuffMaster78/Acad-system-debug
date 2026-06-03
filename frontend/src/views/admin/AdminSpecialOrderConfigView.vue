<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { Plus, RefreshCw, Save, Sparkles, Trash2 } from "@lucide/vue";
import { specialOrdersApi, type MilestoneTemplate, type RushRule, type WriterLevelRule, type ClientTierRule } from "@/api/specialOrders";
import { useAuthStore } from "@/stores/auth";
import { usePortalContextStore } from "@/stores/portalContext";
import { useWebsitesStore } from "@/stores/websites";
import type { PredefinedConfig, SpecialOrderQuoteConfig } from "@/types/specialOrders";

type ServiceDraft = {
  id: number | null;
  name: string;
  slug: string;
  description: string;
  is_active: boolean;
  requires_full_payment: boolean;
  allow_wallet_payment: boolean;
  allow_external_payment: boolean;
  allow_discounts: boolean;
};

type DurationRow = { id?: number; duration_days: number | null; price: string; is_active: boolean };

const predefined = ref<PredefinedConfig[]>([]);
const durationRows = ref<DurationRow[]>([]);
const quoteConfig = ref<SpecialOrderQuoteConfig | null>(null);
const selectedId = ref<number | null>(null);
const isLoading = ref(false);
const isSavingPolicy = ref(false);
const isSavingService = ref(false);
const error = ref("");
const notice = ref("");
const selectedWebsiteId = ref<number | null>(null);

const auth = useAuthStore();
const portal = usePortalContextStore();
const websites = useWebsitesStore();

const serviceDraft = reactive<ServiceDraft>({
  id: null,
  name: "",
  slug: "",
  description: "",
  is_active: true,
  requires_full_payment: true,
  allow_wallet_payment: true,
  allow_external_payment: true,
  allow_discounts: true,
});

const policyDraft = reactive({
  default_deposit_percentage: "50.00",
  minimum_deposit_amount: "0.00",
  allow_installments: true,
  require_deposit_before_staffing: true,
  require_full_payment_before_delivery: true,
  quote_expiry_hours: 72,
  allow_wallet_payment: true,
  allow_external_payment: true,
  allow_discounts: true,
});

const activePredefined = computed(() => predefined.value.filter((cfg) => cfg.is_active));
const durationCount = computed(() => predefined.value.reduce((sum, cfg) => sum + cfg.durations.length, 0));
const isSuperadmin = computed(() => auth.role === "superadmin");
const websiteParams = computed(() =>
  isSuperadmin.value && selectedWebsiteId.value ? { website_id: selectedWebsiteId.value } : undefined,
);
const selectedWebsiteLabel = computed(() => {
  if (selectedWebsiteId.value) return websites.labelById(selectedWebsiteId.value);
  if (portal.website) return `${portal.website.name} (${portal.website.domain})`;
  const config = predefined.value[0];
  if (config?.website_name || config?.website_domain) {
    return config.website_domain ? `${config.website_name || config.website_domain} (${config.website_domain})` : config.website_name || "Current website";
  }
  return "Current website";
});

function configWebsiteLabel(cfg: PredefinedConfig): string {
  if (cfg.website) return websites.labelById(cfg.website);
  if (cfg.website_name || cfg.website_domain) {
    return cfg.website_domain ? `${cfg.website_name || cfg.website_domain} (${cfg.website_domain})` : cfg.website_name || "Current website";
  }
  return selectedWebsiteLabel.value;
}

function defaultDurations(): DurationRow[] {
  return [
    { duration_days: 1, price: "75.00", is_active: true },
    { duration_days: 3, price: "55.00", is_active: true },
    { duration_days: 7, price: "40.00", is_active: true },
  ];
}

function addDuration() {
  durationRows.value.push({ duration_days: null, price: "0.00", is_active: true });
}

function syncPolicy() {
  const settings = quoteConfig.value?.settings;
  if (!settings) return;
  Object.assign(policyDraft, {
    default_deposit_percentage: settings.default_deposit_percentage,
    minimum_deposit_amount: settings.minimum_deposit_amount,
    allow_installments: settings.allow_installments,
    require_deposit_before_staffing: settings.require_deposit_before_staffing,
    require_full_payment_before_delivery: settings.require_full_payment_before_delivery,
    quote_expiry_hours: settings.quote_expiry_hours,
    allow_wallet_payment: settings.allow_wallet_payment,
    allow_external_payment: settings.allow_external_payment,
    allow_discounts: settings.allow_discounts,
  });
}

function resetServiceDraft() {
  selectedId.value = null;
  Object.assign(serviceDraft, {
    id: null,
    name: "",
    slug: "",
    description: "",
    is_active: true,
    requires_full_payment: true,
    allow_wallet_payment: true,
    allow_external_payment: true,
    allow_discounts: true,
  });
  durationRows.value = defaultDurations();
}

function editService(cfg: PredefinedConfig) {
  selectedId.value = cfg.id;
  Object.assign(serviceDraft, {
    id: cfg.id,
    name: cfg.name,
    slug: cfg.slug,
    description: cfg.description,
    is_active: cfg.is_active,
    requires_full_payment: cfg.requires_full_payment,
    allow_wallet_payment: cfg.allow_wallet_payment,
    allow_external_payment: cfg.allow_external_payment,
    allow_discounts: cfg.allow_discounts,
  });
  durationRows.value = cfg.durations.map((row) => ({
    id: row.id,
    duration_days: row.duration_days,
    price: row.price,
    is_active: row.is_active,
  }));
}

async function load() {
  isLoading.value = true;
  error.value = "";
  try {
    const [predefinedRes, quoteRes] = await Promise.all([
      specialOrdersApi.listPredefinedConfigs(websiteParams.value),
      specialOrdersApi.quoteConfig(websiteParams.value),
    ]);
    predefined.value = predefinedRes.data;
    quoteConfig.value = quoteRes.data;
    syncPolicy();
    const selected = predefinedRes.data.find((cfg) => cfg.id === selectedId.value) ?? predefinedRes.data[0];
    if (selected) editService(selected);
    else resetServiceDraft();
  } catch {
    error.value = "Unable to load special order configs.";
    predefined.value = [];
    quoteConfig.value = null;
  } finally {
    isLoading.value = false;
  }
}

async function savePolicy() {
  isSavingPolicy.value = true;
  error.value = "";
  notice.value = "";
  try {
    const { data } = await specialOrdersApi.updateQuoteConfig({ ...policyDraft }, websiteParams.value);
    quoteConfig.value = data;
    syncPolicy();
    notice.value = "Quote policy saved.";
  } catch {
    error.value = "Unable to save quote policy.";
  } finally {
    isSavingPolicy.value = false;
  }
}

async function saveService() {
  if (!serviceDraft.name.trim() || !serviceDraft.slug.trim()) {
    error.value = "Service name and slug are required.";
    return;
  }
  isSavingService.value = true;
  error.value = "";
  notice.value = "";
  try {
    const payload = {
      name: serviceDraft.name,
      slug: serviceDraft.slug,
      description: serviceDraft.description,
      is_active: serviceDraft.is_active,
      requires_full_payment: serviceDraft.requires_full_payment,
      allow_wallet_payment: serviceDraft.allow_wallet_payment,
      allow_external_payment: serviceDraft.allow_external_payment,
      allow_discounts: serviceDraft.allow_discounts,
      durations: durationRows.value
        .filter((row) => row.duration_days && Number(row.duration_days) > 0)
        .map((row) => ({
          ...(row.id ? { id: row.id } : {}),
          duration_days: Number(row.duration_days),
          price: row.price || "0.00",
          is_active: row.is_active,
        })),
    };
    const { data } = serviceDraft.id
      ? await specialOrdersApi.updatePredefinedConfig(serviceDraft.id, payload, websiteParams.value)
      : await specialOrdersApi.createPredefinedConfig(payload, websiteParams.value);
    notice.value = "Express service preset saved.";
    await load();
    editService(data);
  } catch (caught) {
    error.value = caught instanceof Error ? caught.message : "Unable to save express service preset.";
  } finally {
    isSavingService.value = false;
  }
}

async function switchWebsite() {
  resetServiceDraft();
  await load();
  await loadTemplates();
  if (selectedId.value) await loadRules(selectedId.value);
}

// ── Milestone templates ───────────────────────────────────────────────────────
const templates = ref<MilestoneTemplate[]>([]);
const templateDraft = reactive({ name: "", description: "", is_active: true });
const itemDraft = reactive({ sequence: 1, label: "", percentage: "25.00", required_before_staffing: false, required_before_delivery: false });
const expandedTemplateId = ref<number | null>(null);

async function loadTemplates() {
  try {
    const { data } = await specialOrdersApi.milestoneTemplates(websiteParams.value);
    templates.value = data;
  } catch { /* non-fatal */ }
}

async function saveTemplate() {
  if (!templateDraft.name.trim()) return;
  try {
    await specialOrdersApi.createMilestoneTemplate({ ...templateDraft });
    Object.assign(templateDraft, { name: "", description: "", is_active: true });
    await loadTemplates();
    notice.value = "Milestone template created.";
  } catch { error.value = "Failed to create template."; }
}

async function deleteTemplate(id: number) {
  try {
    await specialOrdersApi.deleteMilestoneTemplate(id);
    await loadTemplates();
  } catch { error.value = "Failed to delete template."; }
}

async function addItem(templateId: number) {
  if (!itemDraft.label.trim()) return;
  try {
    await specialOrdersApi.addMilestoneTemplateItem(templateId, { ...itemDraft });
    Object.assign(itemDraft, { sequence: itemDraft.sequence + 1, label: "", percentage: "25.00", required_before_staffing: false, required_before_delivery: false });
    await loadTemplates();
  } catch { error.value = "Failed to add item."; }
}

async function deleteItem(itemId: number) {
  try {
    await specialOrdersApi.deleteMilestoneTemplateItem(itemId);
    await loadTemplates();
  } catch { error.value = "Failed to delete item."; }
}

// ── Pricing rules ─────────────────────────────────────────────────────────────
const rushRules        = ref<RushRule[]>([]);
const writerLevelRules = ref<WriterLevelRule[]>([]);
const clientTierRules  = ref<ClientTierRule[]>([]);
const rushDraft        = reactive({ max_duration_days: 3, surcharge_percentage: "20.00", is_active: true });
const levelDraft       = reactive({ writer_level: "expert", surcharge_percentage: "15.00", is_active: true });
const tierDraft        = reactive({ client_tier: "gold", discount_percentage: "5.00", is_active: true });

async function loadRules(configId: number) {
  try {
    const [r, l, t] = await Promise.allSettled([
      specialOrdersApi.rushRules(configId),
      specialOrdersApi.writerLevelRules(configId),
      specialOrdersApi.clientTierRules(configId),
    ]);
    if (r.status === "fulfilled") rushRules.value = r.value.data;
    if (l.status === "fulfilled") writerLevelRules.value = l.value.data;
    if (t.status === "fulfilled") clientTierRules.value = t.value.data;
  } catch { /* non-fatal */ }
}

async function addRushRule(configId: number) {
  try { await specialOrdersApi.createRushRule(configId, { ...rushDraft }); await loadRules(configId); } catch { error.value = "Failed to add rush rule."; }
}
async function addLevelRule(configId: number) {
  try { await specialOrdersApi.createWriterLevelRule(configId, { ...levelDraft }); await loadRules(configId); } catch { error.value = "Failed to add level rule."; }
}
async function addTierRule(configId: number) {
  try { await specialOrdersApi.createClientTierRule(configId, { ...tierDraft }); await loadRules(configId); } catch { error.value = "Failed to add tier rule."; }
}
async function delRule(type: "rush" | "level" | "tier", id: number) {
  try {
    if (type === "rush")  await specialOrdersApi.deleteRushRule(id);
    if (type === "level") await specialOrdersApi.deleteWriterLevelRule(id);
    if (type === "tier")  await specialOrdersApi.deleteClientTierRule(id);
    if (selectedId.value) await loadRules(selectedId.value);
  } catch { error.value = "Failed to delete rule."; }
}

// override editService to also load rules
const _origEditService = editService;
function editServiceWithRules(cfg: PredefinedConfig) {
  _origEditService(cfg);
  if (cfg.id) loadRules(cfg.id);
}

onMounted(async () => {
  await websites.ensure();
  selectedWebsiteId.value = portal.website?.id ?? websites.list[0]?.id ?? null;
  await load();
  await loadTemplates();
});
</script>

<template>
  <div class="min-h-full bg-slate-50 p-6">
    <div class="mx-auto max-w-7xl space-y-5">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-xl font-bold text-ink">Special Order Management</h1>
          <p class="text-sm text-graphite">Preset express services, duration prices, custom quote policy, and milestone behavior.</p>
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
          <button class="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-graphite hover:text-ink" @click="load">
            <RefreshCw class="size-4" :class="{ 'animate-spin': isLoading }" />
            Refresh
          </button>
        </div>
      </div>

      <div class="grid gap-3 sm:grid-cols-4">
        <div class="rounded-lg border border-slate-200 bg-white p-4">
          <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Express presets</p>
          <p class="mt-1 text-2xl font-bold text-ink">{{ activePredefined.length }}</p>
        </div>
        <div class="rounded-lg border border-slate-200 bg-white p-4">
          <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Duration prices</p>
          <p class="mt-1 text-2xl font-bold text-ink">{{ durationCount }}</p>
        </div>
        <div class="rounded-lg border border-slate-200 bg-white p-4">
          <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Default deposit</p>
          <p class="mt-1 text-2xl font-bold text-ink">{{ policyDraft.default_deposit_percentage }}%</p>
        </div>
        <div class="rounded-lg border border-slate-200 bg-white p-4">
          <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Milestone templates</p>
          <p class="mt-1 text-2xl font-bold text-ink">{{ quoteConfig?.milestone_templates.length ?? 0 }}</p>
        </div>
      </div>

      <div v-if="error" class="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</div>
      <div v-if="notice" class="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ notice }}</div>

      <section class="rounded-lg border border-slate-200 bg-white p-5">
        <div class="mb-4 flex items-center justify-between">
          <div>
            <h2 class="text-sm font-semibold text-ink">Custom quote policy</h2>
            <p class="mt-0.5 text-xs text-graphite">{{ selectedWebsiteLabel }}</p>
          </div>
          <button class="inline-flex items-center gap-2 rounded-lg bg-berry px-4 py-2 text-sm font-semibold text-white hover:bg-berry/90 disabled:opacity-60" :disabled="isSavingPolicy" @click="savePolicy">
            <Save class="size-4" /> {{ isSavingPolicy ? "Saving…" : "Save policy" }}
          </button>
        </div>
        <div class="grid gap-4 sm:grid-cols-3">
          <label class="text-sm">
            <span class="mb-1 block font-medium text-ink">Default deposit %</span>
            <input v-model="policyDraft.default_deposit_percentage" class="w-full rounded-lg border border-slate-200 px-3 py-2 focus-ring" />
          </label>
          <label class="text-sm">
            <span class="mb-1 block font-medium text-ink">Minimum deposit</span>
            <input v-model="policyDraft.minimum_deposit_amount" class="w-full rounded-lg border border-slate-200 px-3 py-2 focus-ring" />
          </label>
          <label class="text-sm">
            <span class="mb-1 block font-medium text-ink">Quote expiry hours</span>
            <input v-model.number="policyDraft.quote_expiry_hours" type="number" class="w-full rounded-lg border border-slate-200 px-3 py-2 focus-ring" />
          </label>
        </div>
        <div class="mt-4 grid gap-3 sm:grid-cols-3">
          <label class="flex items-center gap-2 text-sm text-graphite"><input v-model="policyDraft.allow_installments" type="checkbox" class="rounded accent-berry" /> Allow installments</label>
          <label class="flex items-center gap-2 text-sm text-graphite"><input v-model="policyDraft.require_deposit_before_staffing" type="checkbox" class="rounded accent-berry" /> Deposit before staffing</label>
          <label class="flex items-center gap-2 text-sm text-graphite"><input v-model="policyDraft.require_full_payment_before_delivery" type="checkbox" class="rounded accent-berry" /> Full payment before delivery</label>
          <label class="flex items-center gap-2 text-sm text-graphite"><input v-model="policyDraft.allow_wallet_payment" type="checkbox" class="rounded accent-berry" /> Wallet payment</label>
          <label class="flex items-center gap-2 text-sm text-graphite"><input v-model="policyDraft.allow_external_payment" type="checkbox" class="rounded accent-berry" /> External payment</label>
          <label class="flex items-center gap-2 text-sm text-graphite"><input v-model="policyDraft.allow_discounts" type="checkbox" class="rounded accent-berry" /> Discounts</label>
        </div>
      </section>

      <!-- ── Pricing Rules (per preset) ─────────────────────────────────── -->
      <section v-if="selectedId" class="rounded-lg border border-slate-200 bg-white p-5 space-y-4">
        <h2 class="text-sm font-semibold text-ink">Pricing Rules — <span class="font-normal text-graphite">{{ predefined.find(p => p.id === selectedId)?.name }}</span></h2>

        <!-- Rush surcharges -->
        <div>
          <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-2">Rush surcharges</p>
          <div class="space-y-1 mb-2">
            <div v-for="r in rushRules" :key="r.id" class="flex items-center gap-3 rounded-lg border border-slate-100 bg-slate-50 px-3 py-2 text-sm">
              <span class="text-ink font-medium">≤ {{ r.max_duration_days }}d</span>
              <span class="text-graphite">+{{ r.surcharge_percentage }}%</span>
              <button class="ml-auto text-rose-400 hover:text-rose-600" @click="delRule('rush', r.id!)"><Trash2 class="size-3.5" /></button>
            </div>
          </div>
          <div class="flex gap-2">
            <input v-model.number="rushDraft.max_duration_days" type="number" min="1" placeholder="Max days" class="w-24 rounded-lg border border-slate-200 px-2 py-1.5 text-sm focus-ring" />
            <input v-model="rushDraft.surcharge_percentage" placeholder="Surcharge %" class="w-28 rounded-lg border border-slate-200 px-2 py-1.5 text-sm focus-ring" />
            <button class="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm hover:bg-slate-50" @click="addRushRule(selectedId!)"><Plus class="size-3.5" /></button>
          </div>
        </div>

        <!-- Writer level surcharges -->
        <div>
          <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-2">Writer level surcharges</p>
          <div class="space-y-1 mb-2">
            <div v-for="r in writerLevelRules" :key="r.id" class="flex items-center gap-3 rounded-lg border border-slate-100 bg-slate-50 px-3 py-2 text-sm">
              <span class="capitalize text-ink font-medium">{{ r.writer_level }}</span>
              <span class="text-graphite">+{{ r.surcharge_percentage }}%</span>
              <button class="ml-auto text-rose-400 hover:text-rose-600" @click="delRule('level', r.id!)"><Trash2 class="size-3.5" /></button>
            </div>
          </div>
          <div class="flex gap-2">
            <input v-model="levelDraft.writer_level" placeholder="Level" class="w-28 rounded-lg border border-slate-200 px-2 py-1.5 text-sm focus-ring" />
            <input v-model="levelDraft.surcharge_percentage" placeholder="Surcharge %" class="w-28 rounded-lg border border-slate-200 px-2 py-1.5 text-sm focus-ring" />
            <button class="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm hover:bg-slate-50" @click="addLevelRule(selectedId!)"><Plus class="size-3.5" /></button>
          </div>
        </div>

        <!-- Client tier discounts -->
        <div>
          <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-2">Client tier discounts</p>
          <div class="space-y-1 mb-2">
            <div v-for="r in clientTierRules" :key="r.id" class="flex items-center gap-3 rounded-lg border border-slate-100 bg-slate-50 px-3 py-2 text-sm">
              <span class="capitalize text-ink font-medium">{{ r.client_tier }}</span>
              <span class="text-graphite">−{{ r.discount_percentage }}%</span>
              <button class="ml-auto text-rose-400 hover:text-rose-600" @click="delRule('tier', r.id!)"><Trash2 class="size-3.5" /></button>
            </div>
          </div>
          <div class="flex gap-2">
            <input v-model="tierDraft.client_tier" placeholder="Tier" class="w-28 rounded-lg border border-slate-200 px-2 py-1.5 text-sm focus-ring" />
            <input v-model="tierDraft.discount_percentage" placeholder="Discount %" class="w-28 rounded-lg border border-slate-200 px-2 py-1.5 text-sm focus-ring" />
            <button class="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm hover:bg-slate-50" @click="addTierRule(selectedId!)"><Plus class="size-3.5" /></button>
          </div>
        </div>
      </section>

      <!-- ── Milestone Templates ─────────────────────────────────────────── -->
      <section class="rounded-lg border border-slate-200 bg-white p-5 space-y-4">
        <div class="flex items-center justify-between">
          <h2 class="text-sm font-semibold text-ink">Milestone Payment Templates</h2>
          <span class="text-xs text-graphite">{{ templates.length }} template{{ templates.length !== 1 ? 's' : '' }}</span>
        </div>

        <!-- Create new template -->
        <div class="grid gap-3 sm:grid-cols-[1fr_1fr_auto]">
          <input v-model="templateDraft.name" placeholder="Template name" class="rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring" />
          <input v-model="templateDraft.description" placeholder="Description (optional)" class="rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring" />
          <button class="inline-flex items-center gap-2 rounded-lg bg-berry px-4 py-2 text-sm font-semibold text-white hover:bg-berry/90" @click="saveTemplate">
            <Plus class="size-4" /> Create
          </button>
        </div>

        <!-- Template list -->
        <div class="space-y-3">
          <div v-if="!templates.length" class="py-6 text-center text-sm text-graphite">No templates yet.</div>

          <div
            v-for="t in templates"
            :key="t.id"
            class="rounded-lg border border-slate-200 overflow-hidden"
          >
            <!-- Template header -->
            <div
              class="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-slate-50"
              @click="expandedTemplateId = expandedTemplateId === t.id ? null : t.id"
            >
              <div>
                <p class="text-sm font-semibold text-ink">{{ t.name }}</p>
                <p class="text-xs text-graphite">
                  {{ t.items.length }} item{{ t.items.length !== 1 ? 's' : '' }} ·
                  Total: {{ t.items.reduce((s, i) => s + Number(i.percentage), 0).toFixed(1) }}%
                  <span :class="t.items.reduce((s, i) => s + Number(i.percentage), 0) === 100 ? 'text-signal-600' : 'text-rose-500'">
                    {{ t.items.reduce((s, i) => s + Number(i.percentage), 0) === 100 ? '✓' : '≠ 100%' }}
                  </span>
                </p>
              </div>
              <button class="text-rose-400 hover:text-rose-600 ml-2" @click.stop="deleteTemplate(t.id)"><Trash2 class="size-4" /></button>
            </div>

            <!-- Expanded items -->
            <div v-if="expandedTemplateId === t.id" class="border-t border-slate-100 px-4 py-3 space-y-2 bg-slate-50">
              <div
                v-for="item in t.items"
                :key="item.id"
                class="flex items-center gap-3 text-sm"
              >
                <span class="w-7 text-xs font-bold text-graphite">{{ item.sequence }}.</span>
                <span class="flex-1 text-ink">{{ item.label }}</span>
                <span class="font-semibold text-berry w-14 text-right">{{ item.percentage }}%</span>
                <span v-if="item.required_before_staffing" class="text-xs text-amber-600">staffing</span>
                <span v-if="item.required_before_delivery" class="text-xs text-signal-600">delivery</span>
                <button class="text-rose-300 hover:text-rose-500" @click="deleteItem(item.id!)"><Trash2 class="size-3.5" /></button>
              </div>

              <!-- Add item form -->
              <div class="grid gap-2 pt-2 sm:grid-cols-[3rem_1fr_6rem_auto]">
                <input v-model.number="itemDraft.sequence" type="number" min="1" placeholder="#" class="rounded border border-slate-200 px-2 py-1.5 text-sm focus-ring" />
                <input v-model="itemDraft.label" placeholder="Label (e.g. Deposit)" class="rounded border border-slate-200 px-2 py-1.5 text-sm focus-ring" />
                <input v-model="itemDraft.percentage" placeholder="%" class="rounded border border-slate-200 px-2 py-1.5 text-sm focus-ring" />
                <button class="rounded border border-slate-200 bg-white px-3 py-1.5 text-sm hover:bg-slate-50" @click="addItem(t.id)"><Plus class="size-3.5" /></button>
              </div>
              <div class="flex gap-4 text-xs text-graphite">
                <label class="flex items-center gap-1.5"><input v-model="itemDraft.required_before_staffing" type="checkbox" class="rounded accent-berry" /> Required before staffing</label>
                <label class="flex items-center gap-1.5"><input v-model="itemDraft.required_before_delivery" type="checkbox" class="rounded accent-berry" /> Required before delivery</label>
              </div>
            </div>
          </div>
        </div>
      </section>

      <div class="grid gap-5 lg:grid-cols-[22rem_1fr]">
        <section class="overflow-hidden rounded-lg border border-slate-200 bg-white">
          <div class="flex items-center justify-between border-b border-slate-100 px-4 py-3">
            <h2 class="text-sm font-semibold text-ink">Express presets</h2>
            <button class="text-xs font-medium text-berry hover:underline" @click="resetServiceDraft">
              <Plus class="mr-1 inline size-3.5" /> New
            </button>
          </div>
          <div v-if="isLoading" class="py-12 text-center text-graphite">Loading…</div>
          <div v-else-if="!predefined.length" class="py-12 text-center">
            <Sparkles class="mx-auto mb-3 size-9 text-slate-300" />
            <p class="text-sm text-graphite">No express presets yet.</p>
          </div>
          <button
            v-for="cfg in predefined"
            v-else
            :key="cfg.id"
            class="block w-full border-b border-slate-50 px-4 py-3 text-left hover:bg-slate-50"
            :class="{ 'bg-berry/5': selectedId === cfg.id }"
            @click="editServiceWithRules(cfg)"
          >
            <p class="font-medium text-ink">{{ cfg.name }}</p>
            <p class="mt-0.5 text-xs text-graphite">{{ cfg.durations.length }} duration prices · {{ cfg.requires_full_payment ? "full payment" : "flexible" }}</p>
            <p class="mt-1 text-xs text-slate-400">{{ configWebsiteLabel(cfg) }}</p>
          </button>
        </section>

        <section class="rounded-lg border border-slate-200 bg-white p-5">
          <div class="mb-4 flex items-center justify-between">
            <div>
              <h2 class="text-sm font-semibold text-ink">{{ serviceDraft.id ? "Edit express preset" : "Create express preset" }}</h2>
              <p class="mt-0.5 text-xs text-graphite">{{ selectedWebsiteLabel }}</p>
            </div>
            <button class="inline-flex items-center gap-2 rounded-lg bg-berry px-4 py-2 text-sm font-semibold text-white hover:bg-berry/90 disabled:opacity-60" :disabled="isSavingService" @click="saveService">
              <Save class="size-4" /> {{ isSavingService ? "Saving…" : "Save preset" }}
            </button>
          </div>

          <div class="grid gap-4 sm:grid-cols-2">
            <label class="text-sm">
              <span class="mb-1 block font-medium text-ink">Service name</span>
              <input v-model="serviceDraft.name" class="w-full rounded-lg border border-slate-200 px-3 py-2 focus-ring" />
            </label>
            <label class="text-sm">
              <span class="mb-1 block font-medium text-ink">Slug</span>
              <input v-model="serviceDraft.slug" class="w-full rounded-lg border border-slate-200 px-3 py-2 focus-ring" />
            </label>
            <label class="text-sm sm:col-span-2">
              <span class="mb-1 block font-medium text-ink">Description</span>
              <textarea v-model="serviceDraft.description" rows="3" class="w-full rounded-lg border border-slate-200 px-3 py-2 focus-ring" />
            </label>
          </div>

          <div class="mt-4 grid gap-3 sm:grid-cols-3">
            <label class="flex items-center gap-2 text-sm text-graphite"><input v-model="serviceDraft.is_active" type="checkbox" class="rounded accent-berry" /> Active</label>
            <label class="flex items-center gap-2 text-sm text-graphite"><input v-model="serviceDraft.requires_full_payment" type="checkbox" class="rounded accent-berry" /> Full payment</label>
            <label class="flex items-center gap-2 text-sm text-graphite"><input v-model="serviceDraft.allow_wallet_payment" type="checkbox" class="rounded accent-berry" /> Wallet payment</label>
            <label class="flex items-center gap-2 text-sm text-graphite"><input v-model="serviceDraft.allow_external_payment" type="checkbox" class="rounded accent-berry" /> External payment</label>
            <label class="flex items-center gap-2 text-sm text-graphite"><input v-model="serviceDraft.allow_discounts" type="checkbox" class="rounded accent-berry" /> Discounts</label>
          </div>

          <div class="mt-5 rounded-lg border border-slate-200 p-4">
            <div class="mb-3 flex items-center justify-between">
              <h3 class="text-sm font-semibold text-ink">Duration Prices</h3>
              <button class="text-xs font-medium text-berry hover:underline" @click="addDuration">Add duration</button>
            </div>
            <div class="space-y-2">
              <div
                v-for="(row, index) in durationRows"
                :key="row.id ?? index"
                class="grid gap-2 sm:grid-cols-[8rem_1fr_7rem_2.5rem]"
              >
                <input
                  v-model.number="row.duration_days"
                  type="number"
                  min="1"
                  placeholder="Days"
                  class="rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring"
                />
                <input
                  v-model="row.price"
                  placeholder="Price"
                  class="rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring"
                />
                <label class="flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm text-graphite">
                  <input v-model="row.is_active" type="checkbox" class="rounded accent-berry" />
                  Active
                </label>
                <button
                  class="rounded-lg border border-slate-200 px-3 py-2 text-sm text-graphite hover:bg-slate-50"
                  title="Remove duration"
                  @click="durationRows.splice(index, 1)"
                >
                  x
                </button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>
