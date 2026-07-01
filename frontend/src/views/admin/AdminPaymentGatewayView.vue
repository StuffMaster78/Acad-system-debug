<script setup lang="ts">
import { onMounted, ref, computed } from "vue";
import {
  Globe, Plus, Pencil, Trash2, X, Loader2, CheckCircle2,
  AlertTriangle, Shield, RefreshCw, Search,
} from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { adminGatewayApi, type GatewayConfig, type NotificationEmail } from "@/api/adminGateway";
import { websitesApi, type Website } from "@/api/websites";

const activeTab = ref<"gateways" | "notification-emails">("gateways");

// ── Websites list (for dropdowns) ────────────────────────────────────────────
const websites = ref<Website[]>([]);
async function fetchWebsites() {
  try {
    const { data } = await websitesApi.list({ page_size: 100 });
    websites.value = Array.isArray(data) ? data : (data as any).results ?? [];
  } catch { /* non-critical */ }
}

// ── Gateway configs ───────────────────────────────────────────────────────────
const configs = ref<GatewayConfig[]>([]);
const configsLoading = ref(false);
const configsError = ref("");
const gatewaySearch = ref("");

const filteredConfigs = computed(() => {
  const q = gatewaySearch.value.toLowerCase();
  if (!q) return configs.value;
  return configs.value.filter(c =>
    c.website_domain.toLowerCase().includes(q) ||
    c.gateway.toLowerCase().includes(q) ||
    c.mode.toLowerCase().includes(q)
  );
});

async function fetchConfigs() {
  configsLoading.value = true;
  configsError.value = "";
  try {
    const { data } = await adminGatewayApi.listConfigs();
    configs.value = Array.isArray(data) ? data : [];
  } catch (err: unknown) {
    configsError.value = (err as any)?.response?.data?.detail ?? "Could not load gateway configs.";
  } finally {
    configsLoading.value = false;
  }
}

// Edit gateway config
const editingConfig = ref<GatewayConfig | null>(null);
const editForm = ref({ gateway: "", webhook_endpoint: "", callback_base_url: "", mode: "live" as "live"|"test", is_active: true, statement_descriptor: "", secret_key_env_var: "", webhook_secret_env_var: "" });
const editSaving = ref(false);
const editError = ref("");

function openEdit(cfg: GatewayConfig) {
  editingConfig.value = cfg;
  editForm.value = {
    gateway: cfg.gateway,
    webhook_endpoint: cfg.webhook_endpoint,
    callback_base_url: cfg.callback_base_url,
    mode: cfg.mode,
    is_active: cfg.is_active,
    statement_descriptor: cfg.statement_descriptor || "",
    secret_key_env_var: cfg.secret_key_env_var || "",
    webhook_secret_env_var: cfg.webhook_secret_env_var || "",
  };
  editError.value = "";
}

function closeEdit() {
  editingConfig.value = null;
}

async function saveConfig() {
  if (!editingConfig.value) return;
  editSaving.value = true;
  editError.value = "";
  try {
    const { data } = await adminGatewayApi.updateConfig(editingConfig.value.id, editForm.value);
    const idx = configs.value.findIndex(c => c.id === data.id);
    if (idx !== -1) configs.value[idx] = data;
    closeEdit();
  } catch (err: unknown) {
    editError.value = (err as any)?.response?.data?.detail ?? "Failed to save.";
  } finally {
    editSaving.value = false;
  }
}

// Create new config
const showCreate = ref(false);
const createForm = ref({ website: 0, gateway: "stripe", webhook_endpoint: "/api/payments/webhooks/stripe/", callback_base_url: "", mode: "live" as "live"|"test" });
const createSaving = ref(false);
const createError = ref("");

async function saveNewConfig() {
  createSaving.value = true;
  createError.value = "";
  try {
    const { data } = await adminGatewayApi.createConfig(createForm.value);
    configs.value.push(data);
    showCreate.value = false;
  } catch (err: unknown) {
    createError.value = (err as any)?.response?.data?.detail ?? "Failed to create.";
  } finally {
    createSaving.value = false;
  }
}

// ── Notification emails ───────────────────────────────────────────────────────
const notifEmails = ref<NotificationEmail[]>([]);
const notifLoading = ref(false);
const notifError = ref("");
const emailSearch = ref("");

const filteredEmails = computed(() => {
  const q = emailSearch.value.toLowerCase();
  if (!q) return notifEmails.value;
  return notifEmails.value.filter(e =>
    e.email.toLowerCase().includes(q) ||
    e.website_domain.toLowerCase().includes(q) ||
    (e.label || "").toLowerCase().includes(q)
  );
});

async function fetchNotifEmails() {
  notifLoading.value = true;
  notifError.value = "";
  try {
    const { data } = await adminGatewayApi.listNotificationEmails();
    notifEmails.value = Array.isArray(data) ? data : [];
  } catch (err: unknown) {
    notifError.value = (err as any)?.response?.data?.detail ?? "Could not load notification emails.";
  } finally {
    notifLoading.value = false;
  }
}

const showAddEmail = ref(false);
const addEmailForm = ref({ website: 0, email: "", label: "" });
const addEmailSaving = ref(false);
const addEmailError = ref("");

async function saveNewEmail() {
  addEmailSaving.value = true;
  addEmailError.value = "";
  try {
    const { data } = await adminGatewayApi.createNotificationEmail(addEmailForm.value);
    notifEmails.value.push(data);
    showAddEmail.value = false;
    addEmailForm.value = { website: 0, email: "", label: "" };
  } catch (err: unknown) {
    addEmailError.value = (err as any)?.response?.data?.detail ?? "Failed to add.";
  } finally {
    addEmailSaving.value = false;
  }
}

const deletingEmailId = ref<number | null>(null);
async function deleteEmail(id: number) {
  if (!confirm("Remove this notification email?")) return;
  deletingEmailId.value = id;
  try {
    await adminGatewayApi.deleteNotificationEmail(id);
    notifEmails.value = notifEmails.value.filter(e => e.id !== id);
  } finally {
    deletingEmailId.value = null;
  }
}

const togglingEmailId = ref<number | null>(null);
async function toggleEmail(entry: NotificationEmail) {
  togglingEmailId.value = entry.id;
  try {
    const { data } = await adminGatewayApi.updateNotificationEmail(entry.id, { is_active: !entry.is_active });
    const idx = notifEmails.value.findIndex(e => e.id === data.id);
    if (idx !== -1) notifEmails.value[idx] = data;
  } finally {
    togglingEmailId.value = null;
  }
}

onMounted(() => {
  fetchWebsites();
  fetchConfigs();
  fetchNotifEmails();
});
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Settings</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Payment Gateway</h1>
        <p class="mt-2 max-w-2xl text-sm text-graphite">
          Manage per-website payment gateway configuration and notification email forwarding.
        </p>
      </div>
      <button
        class="focus-ring inline-flex items-center gap-2 rounded-md border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold disabled:opacity-60"
        type="button"
        :disabled="configsLoading || notifLoading"
        @click="fetchConfigs(); fetchNotifEmails()"
      >
        <Loader2 v-if="configsLoading || notifLoading" class="h-4 w-4 animate-spin" />
        <RefreshCw v-else class="h-4 w-4" />
        Refresh
      </button>
    </section>

    <!-- Tabs -->
    <div class="flex items-center gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1 w-fit">
      <button
        class="focus-ring rounded-md px-4 py-2 text-sm font-semibold transition-colors"
        :class="activeTab === 'gateways' ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
        @click="activeTab = 'gateways'"
      >
        <span class="flex items-center gap-2">
          <Shield class="h-4 w-4" />
          Gateways
          <span v-if="configs.length" class="ml-0.5 rounded-full bg-slate-200 px-1.5 py-0.5 text-xs">{{ configs.length }}</span>
        </span>
      </button>
      <button
        class="focus-ring rounded-md px-4 py-2 text-sm font-semibold transition-colors"
        :class="activeTab === 'notification-emails' ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
        @click="activeTab = 'notification-emails'"
      >
        <span class="flex items-center gap-2">
          Payment Notification Emails
          <span v-if="notifEmails.length" class="ml-0.5 rounded-full bg-slate-200 px-1.5 py-0.5 text-xs">{{ notifEmails.length }}</span>
        </span>
      </button>
    </div>

    <!-- ── GATEWAYS TAB ─────────────────────────────────────────────────────── -->
    <template v-if="activeTab === 'gateways'">
      <p v-if="configsError" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">{{ configsError }}</p>

      <!-- Toolbar -->
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div class="relative w-full max-w-xs">
          <Search class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            v-model="gatewaySearch"
            type="text"
            placeholder="Search…"
            class="focus-ring w-full rounded-md border border-slate-200 bg-white py-2 pl-9 pr-3 text-sm"
          />
        </div>
        <button
          class="focus-ring inline-flex items-center gap-2 rounded-md bg-signal px-4 py-2 text-sm font-semibold text-white hover:bg-signal/90 transition-colors"
          @click="showCreate = true"
        >
          <Plus class="h-4 w-4" /> Add Gateway
        </button>
      </div>

      <!-- Table -->
      <div class="rounded-lg border border-slate-200 bg-white overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-200 text-sm">
          <thead class="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-graphite">
            <tr>
              <th class="px-4 py-3">Website</th>
              <th class="px-4 py-3">Gateway</th>
              <th class="px-4 py-3">Endpoint</th>
              <th class="px-4 py-3">Callback</th>
              <th class="px-4 py-3">Mode</th>
              <th class="px-4 py-3">Status</th>
              <th class="px-4 py-3">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-if="configsLoading && !filteredConfigs.length">
              <td colspan="7" class="px-4 py-8 text-center text-sm text-graphite">
                <Loader2 class="mx-auto h-5 w-5 animate-spin text-slate-400" />
              </td>
            </tr>
            <tr v-else-if="!filteredConfigs.length">
              <td colspan="7" class="px-4 py-10 text-center text-sm text-graphite">
                No gateway configs yet.
              </td>
            </tr>
            <tr v-for="cfg in filteredConfigs" :key="cfg.id" class="hover:bg-slate-50 transition-colors">
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <Globe class="h-4 w-4 shrink-0 text-slate-400" />
                  <div>
                    <p class="font-medium text-ink">{{ cfg.website_name }}</p>
                    <p class="text-xs text-graphite">{{ cfg.website_domain }}</p>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3">
                <span class="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-slate-50 px-2.5 py-0.5 text-xs font-semibold capitalize text-slate-700">
                  {{ cfg.gateway }}
                </span>
              </td>
              <td class="px-4 py-3 font-mono text-xs text-graphite">{{ cfg.webhook_endpoint }}</td>
              <td class="px-4 py-3 text-xs text-graphite max-w-[200px] truncate">
                {{ cfg.effective_callback_base_url || '—' }}
              </td>
              <td class="px-4 py-3">
                <span
                  class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold"
                  :class="cfg.mode === 'live' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'"
                >
                  {{ cfg.mode }}
                </span>
              </td>
              <td class="px-4 py-3">
                <StatusPill
                  :label="cfg.is_active ? 'Active' : 'Inactive'"
                  :tone="cfg.is_active ? 'success' : 'neutral'"
                />
              </td>
              <td class="px-4 py-3">
                <button
                  class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-slate-200 px-3 py-1.5 text-xs font-semibold text-graphite hover:bg-slate-50 transition-colors"
                  @click="openEdit(cfg)"
                >
                  <Pencil class="h-3.5 w-3.5" /> Edit
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <!-- ── NOTIFICATION EMAILS TAB ─────────────────────────────────────────── -->
    <template v-else-if="activeTab === 'notification-emails'">
      <p v-if="notifError" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">{{ notifError }}</p>

      <!-- Toolbar -->
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div class="relative w-full max-w-xs">
          <Search class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            v-model="emailSearch"
            type="text"
            placeholder="Search email or website…"
            class="focus-ring w-full rounded-md border border-slate-200 bg-white py-2 pl-9 pr-3 text-sm"
          />
        </div>
        <button
          class="focus-ring inline-flex items-center gap-2 rounded-md bg-signal px-4 py-2 text-sm font-semibold text-white hover:bg-signal/90 transition-colors"
          @click="showAddEmail = true"
        >
          <Plus class="h-4 w-4" /> Add Email
        </button>
      </div>

      <!-- Table -->
      <div class="rounded-lg border border-slate-200 bg-white overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-200 text-sm">
          <thead class="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-graphite">
            <tr>
              <th class="px-4 py-3 w-10">#</th>
              <th class="px-4 py-3">Email</th>
              <th class="px-4 py-3">Label</th>
              <th class="px-4 py-3">Website</th>
              <th class="px-4 py-3">Status</th>
              <th class="px-4 py-3">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-if="notifLoading && !filteredEmails.length">
              <td colspan="6" class="px-4 py-8 text-center">
                <Loader2 class="mx-auto h-5 w-5 animate-spin text-slate-400" />
              </td>
            </tr>
            <tr v-else-if="!filteredEmails.length">
              <td colspan="6" class="px-4 py-10 text-center text-sm text-graphite">
                No notification emails configured.
              </td>
            </tr>
            <tr v-for="(entry, i) in filteredEmails" :key="entry.id" class="hover:bg-slate-50 transition-colors">
              <td class="px-4 py-3 text-graphite">{{ i + 1 }}</td>
              <td class="px-4 py-3 font-medium text-ink">{{ entry.email }}</td>
              <td class="px-4 py-3 text-graphite text-xs">{{ entry.label || '—' }}</td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-1.5">
                  <Globe class="h-3.5 w-3.5 text-slate-400 shrink-0" />
                  <span class="text-xs text-graphite">{{ entry.website_domain }}</span>
                </div>
              </td>
              <td class="px-4 py-3">
                <StatusPill
                  :label="entry.is_active ? 'Active' : 'Paused'"
                  :tone="entry.is_active ? 'success' : 'neutral'"
                />
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <button
                    class="focus-ring rounded-md border border-slate-200 px-2.5 py-1 text-xs font-semibold text-graphite hover:bg-slate-50 disabled:opacity-50 transition-colors"
                    :disabled="togglingEmailId === entry.id"
                    @click="toggleEmail(entry)"
                  >
                    {{ entry.is_active ? 'Pause' : 'Resume' }}
                  </button>
                  <button
                    class="focus-ring rounded-md border border-rose-200 bg-rose-50 px-2.5 py-1 text-xs font-semibold text-rose-700 hover:bg-rose-100 disabled:opacity-50 transition-colors"
                    :disabled="deletingEmailId === entry.id"
                    @click="deleteEmail(entry.id)"
                  >
                    <Loader2 v-if="deletingEmailId === entry.id" class="h-3.5 w-3.5 animate-spin" />
                    <Trash2 v-else class="h-3.5 w-3.5" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>

  <!-- ── EDIT GATEWAY DIALOG ────────────────────────────────────────────────── -->
  <Teleport to="body">
    <div v-if="editingConfig" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" @click.self="closeEdit">
      <div class="w-full max-w-lg rounded-2xl border border-slate-200 bg-white shadow-2xl">
        <div class="flex items-center justify-between border-b border-slate-100 px-6 py-4">
          <div>
            <p class="font-semibold text-ink">Edit Gateway Config</p>
            <p class="text-xs text-graphite mt-0.5">{{ editingConfig.website_domain }}</p>
          </div>
          <button class="focus-ring rounded-md p-1.5 hover:bg-slate-100" @click="closeEdit"><X class="h-4 w-4" /></button>
        </div>
        <div class="space-y-4 px-6 py-5">
          <div>
            <label class="block text-xs font-semibold text-graphite mb-1">Gateway provider</label>
            <input v-model="editForm.gateway" class="focus-ring w-full rounded-md border border-slate-200 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-graphite mb-1">Webhook endpoint <span class="font-normal text-slate-400">(path Stripe POSTs to)</span></label>
            <input v-model="editForm.webhook_endpoint" class="focus-ring w-full rounded-md border border-slate-200 px-3 py-2 text-sm font-mono" placeholder="/api/payments/webhooks/stripe/" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-graphite mb-1">Callback base URL <span class="font-normal text-slate-400">(where Stripe returns clients — blank = Website.root_url)</span></label>
            <input v-model="editForm.callback_base_url" class="focus-ring w-full rounded-md border border-slate-200 px-3 py-2 text-sm" placeholder="https://app.gradecrest.com" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-graphite mb-1">Mode</label>
            <div class="flex gap-3">
              <label class="flex items-center gap-2 cursor-pointer">
                <input v-model="editForm.mode" type="radio" value="live" class="accent-signal" />
                <span class="text-sm font-medium text-emerald-700">Live</span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer">
                <input v-model="editForm.mode" type="radio" value="test" class="accent-amber-500" />
                <span class="text-sm font-medium text-amber-700">Test</span>
              </label>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <input v-model="editForm.is_active" type="checkbox" id="cfg-active" class="accent-signal" />
            <label for="cfg-active" class="text-sm text-ink cursor-pointer">Gateway active</label>
          </div>

          <!-- Per-site credentials -->
          <div class="rounded-lg border border-slate-200 bg-slate-50 p-4 space-y-3">
            <p class="text-xs font-semibold text-ink">Per-site Stripe credentials</p>
            <p class="text-xs text-graphite leading-5">
              Store the Stripe secret key and webhook secret in environment variables on the server,
              then enter the <em>variable name</em> here (never the value itself).
              Leave blank to inherit the platform default.
            </p>
            <div>
              <label class="block text-xs font-semibold text-graphite mb-1">
                Secret key env var
                <span class="font-normal text-slate-400">e.g. STRIPE_SECRET_KEY_NURSEMYGRADE</span>
              </label>
              <div class="flex items-center gap-2">
                <input
                  v-model="editForm.secret_key_env_var"
                  class="focus-ring flex-1 rounded-md border border-slate-200 px-3 py-2 text-sm font-mono"
                  placeholder="STRIPE_SECRET_KEY_SITENAME"
                />
                <span
                  :class="editingConfig?.secret_key_configured ? 'text-emerald-600' : 'text-slate-400'"
                  class="text-xs font-semibold whitespace-nowrap"
                >
                  {{ editingConfig?.secret_key_configured ? '✓ Configured' : 'Not set' }}
                </span>
              </div>
            </div>
            <div>
              <label class="block text-xs font-semibold text-graphite mb-1">
                Webhook secret env var
                <span class="font-normal text-slate-400">e.g. STRIPE_WEBHOOK_SECRET_NURSEMYGRADE</span>
              </label>
              <div class="flex items-center gap-2">
                <input
                  v-model="editForm.webhook_secret_env_var"
                  class="focus-ring flex-1 rounded-md border border-slate-200 px-3 py-2 text-sm font-mono"
                  placeholder="STRIPE_WEBHOOK_SECRET_SITENAME"
                />
                <span
                  :class="editingConfig?.webhook_secret_configured ? 'text-emerald-600' : 'text-slate-400'"
                  class="text-xs font-semibold whitespace-nowrap"
                >
                  {{ editingConfig?.webhook_secret_configured ? '✓ Configured' : 'Not set' }}
                </span>
              </div>
            </div>
            <div>
              <label class="block text-xs font-semibold text-graphite mb-1">
                Statement descriptor
                <span class="font-normal text-slate-400">max 22 chars — appears on the cardholder's bank statement</span>
              </label>
              <input
                v-model="editForm.statement_descriptor"
                class="focus-ring w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                maxlength="22"
                placeholder="YOURSITE"
              />
              <p class="mt-1 text-xs text-graphite">{{ editForm.statement_descriptor.length }}/22 · Latin chars only, no &lt; &gt; \ ' " *</p>
            </div>
            <div v-if="editingConfig?.website_slug" class="rounded-md border border-slate-200 bg-white px-3 py-2">
              <p class="text-xs font-semibold text-graphite">Per-site webhook URL</p>
              <p class="mt-0.5 font-mono text-xs text-ink break-all">
                /api/payments/webhooks/{{ editForm.gateway || 'stripe' }}/{{ editingConfig.website_slug }}/
              </p>
              <p class="mt-1 text-xs text-slate-400">Register this path in your Stripe dashboard for this site's account.</p>
            </div>
          </div>

          <p v-if="editError" class="text-xs text-rose-600">{{ editError }}</p>
        </div>
        <div class="flex justify-end gap-3 border-t border-slate-100 px-6 py-4">
          <button class="focus-ring rounded-md border border-slate-200 px-4 py-2 text-sm font-semibold text-graphite hover:bg-slate-50" @click="closeEdit">Cancel</button>
          <button
            class="focus-ring inline-flex items-center gap-2 rounded-md bg-signal px-5 py-2 text-sm font-semibold text-white hover:bg-signal/90 disabled:opacity-60"
            :disabled="editSaving"
            @click="saveConfig"
          >
            <Loader2 v-if="editSaving" class="h-4 w-4 animate-spin" />
            Save changes
          </button>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- ── CREATE GATEWAY DIALOG ──────────────────────────────────────────────── -->
  <Teleport to="body">
    <div v-if="showCreate" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" @click.self="showCreate = false">
      <div class="w-full max-w-lg rounded-2xl border border-slate-200 bg-white shadow-2xl">
        <div class="flex items-center justify-between border-b border-slate-100 px-6 py-4">
          <p class="font-semibold text-ink">Add Gateway Config</p>
          <button class="focus-ring rounded-md p-1.5 hover:bg-slate-100" @click="showCreate = false"><X class="h-4 w-4" /></button>
        </div>
        <div class="space-y-4 px-6 py-5">
          <div>
            <label class="block text-xs font-semibold text-graphite mb-1">Website</label>
            <select v-model="createForm.website" class="focus-ring w-full rounded-md border border-slate-200 px-3 py-2 text-sm">
              <option :value="0" disabled>Select a website…</option>
              <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }} — {{ site.domain }}</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-semibold text-graphite mb-1">Gateway provider</label>
            <input v-model="createForm.gateway" class="focus-ring w-full rounded-md border border-slate-200 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-graphite mb-1">Webhook endpoint</label>
            <input v-model="createForm.webhook_endpoint" class="focus-ring w-full rounded-md border border-slate-200 px-3 py-2 text-sm font-mono" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-graphite mb-1">Callback base URL <span class="font-normal text-slate-400">(optional)</span></label>
            <input v-model="createForm.callback_base_url" class="focus-ring w-full rounded-md border border-slate-200 px-3 py-2 text-sm" placeholder="https://app.example.com" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-graphite mb-1">Mode</label>
            <div class="flex gap-3">
              <label class="flex items-center gap-2 cursor-pointer">
                <input v-model="createForm.mode" type="radio" value="live" class="accent-signal" />
                <span class="text-sm font-medium text-emerald-700">Live</span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer">
                <input v-model="createForm.mode" type="radio" value="test" class="accent-amber-500" />
                <span class="text-sm font-medium text-amber-700">Test</span>
              </label>
            </div>
          </div>
          <p v-if="createError" class="text-xs text-rose-600">{{ createError }}</p>
        </div>
        <div class="flex justify-end gap-3 border-t border-slate-100 px-6 py-4">
          <button class="focus-ring rounded-md border border-slate-200 px-4 py-2 text-sm font-semibold text-graphite hover:bg-slate-50" @click="showCreate = false">Cancel</button>
          <button
            class="focus-ring inline-flex items-center gap-2 rounded-md bg-signal px-5 py-2 text-sm font-semibold text-white hover:bg-signal/90 disabled:opacity-60"
            :disabled="createSaving || !createForm.website"
            @click="saveNewConfig"
          >
            <Loader2 v-if="createSaving" class="h-4 w-4 animate-spin" />
            Add gateway
          </button>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- ── ADD NOTIFICATION EMAIL DIALOG ─────────────────────────────────────── -->
  <Teleport to="body">
    <div v-if="showAddEmail" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" @click.self="showAddEmail = false">
      <div class="w-full max-w-md rounded-2xl border border-slate-200 bg-white shadow-2xl">
        <div class="flex items-center justify-between border-b border-slate-100 px-6 py-4">
          <p class="font-semibold text-ink">Add Payment Notification Email</p>
          <button class="focus-ring rounded-md p-1.5 hover:bg-slate-100" @click="showAddEmail = false"><X class="h-4 w-4" /></button>
        </div>
        <div class="space-y-4 px-6 py-5">
          <div>
            <label class="block text-xs font-semibold text-graphite mb-1">Website</label>
            <select v-model="addEmailForm.website" class="focus-ring w-full rounded-md border border-slate-200 px-3 py-2 text-sm">
              <option :value="0" disabled>Select a website…</option>
              <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }} — {{ site.domain }}</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-semibold text-graphite mb-1">Email address</label>
            <input v-model="addEmailForm.email" type="email" class="focus-ring w-full rounded-md border border-slate-200 px-3 py-2 text-sm" placeholder="payments@example.com" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-graphite mb-1">Label <span class="font-normal text-slate-400">(optional)</span></label>
            <input v-model="addEmailForm.label" class="focus-ring w-full rounded-md border border-slate-200 px-3 py-2 text-sm" placeholder="Finance team" />
          </div>
          <p v-if="addEmailError" class="text-xs text-rose-600">{{ addEmailError }}</p>
        </div>
        <div class="flex justify-end gap-3 border-t border-slate-100 px-6 py-4">
          <button class="focus-ring rounded-md border border-slate-200 px-4 py-2 text-sm font-semibold text-graphite hover:bg-slate-50" @click="showAddEmail = false">Cancel</button>
          <button
            class="focus-ring inline-flex items-center gap-2 rounded-md bg-signal px-5 py-2 text-sm font-semibold text-white hover:bg-signal/90 disabled:opacity-60"
            :disabled="addEmailSaving || !addEmailForm.website || !addEmailForm.email"
            @click="saveNewEmail"
          >
            <Loader2 v-if="addEmailSaving" class="h-4 w-4 animate-spin" />
            Add email
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
