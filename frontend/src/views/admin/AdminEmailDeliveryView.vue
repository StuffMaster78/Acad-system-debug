<template>
  <div class="p-6 space-y-4">
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Email Delivery</h1>
      <p class="text-sm text-gray-500 mt-0.5">Provider configuration, campaign delivery tracking, and per-user history</p>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex gap-6">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key"
          :class="[
            'pb-3 text-sm font-medium border-b-2 transition-colors',
            activeTab === tab.key
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-gray-500 hover:text-gray-700',
          ]"
        >{{ tab.label }}</button>
      </nav>
    </div>

    <!-- ── Providers ──────────────────────────────────────────────────────── -->
    <div v-if="activeTab === 'providers'" class="space-y-4">
      <div class="flex items-center justify-between">
        <p class="text-sm text-gray-500">
          One email service integration per website. Used by the mass-email campaign engine.
        </p>
        <button @click="showProviderForm = true" class="btn-primary text-sm">+ Add Provider</button>
      </div>

      <div v-if="loadingProviders" class="text-center py-10 text-gray-400">Loading…</div>
      <div v-else-if="!providers.length" class="text-center py-10 text-gray-400 text-sm">No providers configured.</div>
      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          v-for="prov in providers"
          :key="prov.id"
          class="bg-white rounded-lg border border-gray-200 p-5 space-y-3"
        >
          <div class="flex items-start justify-between">
            <div>
              <span class="inline-block text-xs font-mono font-semibold uppercase px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 mb-1">
                {{ prov.provider_name }}
              </span>
              <p class="font-semibold text-gray-800 text-sm">{{ prov.sender_name }}</p>
              <p class="text-xs text-gray-400">{{ prov.sender_email }}</p>
            </div>
            <span
              :class="prov.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'"
              class="text-xs font-medium px-2 py-0.5 rounded-full"
            >{{ prov.is_active ? 'Active' : 'Inactive' }}</span>
          </div>

          <p class="text-xs text-gray-400 font-mono">
            API Key: <span class="bg-gray-100 px-1.5 py-0.5 rounded">••••••••{{ prov.api_key.slice(-4) }}</span>
          </p>

          <div class="flex gap-2 pt-1">
            <button @click="openEditProvider(prov)" class="text-xs px-3 py-1.5 rounded border border-gray-200 hover:bg-gray-50">Edit</button>
            <button
              @click="toggleProvider(prov)"
              :disabled="actioning"
              class="text-xs px-3 py-1.5 rounded border hover:bg-gray-50 disabled:opacity-50"
              :class="prov.is_active ? 'border-amber-200 text-amber-600' : 'border-green-200 text-green-600'"
            >{{ prov.is_active ? 'Disable' : 'Enable' }}</button>
            <button @click="confirmDeleteProvider(prov.id)" class="text-xs px-3 py-1.5 rounded border border-red-200 text-red-500 hover:bg-red-50">Remove</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Recipients ─────────────────────────────────────────────────────── -->
    <div v-if="activeTab === 'recipients'" class="space-y-4">
      <!-- Filters -->
      <div class="flex flex-wrap gap-3 items-end">
        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Status</label>
          <select v-model="recipientFilter.status" @change="loadRecipients" class="input text-sm w-36">
            <option value="">All</option>
            <option value="sent">Sent</option>
            <option value="opened">Opened</option>
            <option value="failed">Failed</option>
            <option value="pending">Pending</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Search email</label>
          <input v-model="recipientSearch" @keydown.enter="loadRecipients" class="input text-sm w-52" placeholder="user@example.com" />
        </div>
        <button @click="loadRecipients" class="text-sm px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-50">Search</button>
      </div>

      <div v-if="loadingRecipients" class="text-center py-10 text-gray-400">Loading…</div>
      <div v-else-if="!recipients.length" class="text-center py-10 text-gray-400 text-sm">No recipients found.</div>
      <div v-else class="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="bg-gray-50 text-xs text-gray-500 uppercase">
            <tr>
              <th class="px-3 py-2 text-left">Email</th>
              <th class="px-3 py-2 text-left">Campaign</th>
              <th class="px-3 py-2 text-left">Status</th>
              <th class="px-3 py-2 text-left">Sent</th>
              <th class="px-3 py-2 text-left">Opened</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="rec in recipients" :key="rec.id" class="hover:bg-gray-50">
              <td class="px-3 py-2 text-gray-700 font-mono text-xs">{{ rec.email }}</td>
              <td class="px-3 py-2">
                <p v-if="rec.campaign" class="text-gray-800 font-medium text-xs">{{ rec.campaign.title }}</p>
                <p v-if="rec.campaign" class="text-gray-400 text-xs">{{ rec.campaign.email_type }}</p>
                <span v-else class="text-gray-400 text-xs">—</span>
              </td>
              <td class="px-3 py-2">
                <span :class="recipientStatusClass(rec.status)" class="text-xs px-2 py-0.5 rounded-full font-medium">{{ rec.status }}</span>
                <p v-if="rec.error_message" class="text-xs text-red-500 mt-0.5 max-w-xs truncate">{{ rec.error_message }}</p>
              </td>
              <td class="px-3 py-2 text-gray-400 text-xs">{{ rec.sent_at ? fmtTime(rec.sent_at) : '—' }}</td>
              <td class="px-3 py-2 text-gray-400 text-xs">{{ rec.opened_at ? fmtTime(rec.opened_at) : '—' }}</td>
            </tr>
          </tbody>
        </table>
        </div>
      </div>
    </div>

    <!-- ── History ─────────────────────────────────────────────────────────── -->
    <div v-if="activeTab === 'history'" class="space-y-4">
      <p class="text-sm text-gray-500">Look up the full email history for any platform user.</p>

      <!-- User lookup -->
      <div class="bg-white rounded-lg border border-gray-200 p-5 space-y-4">
        <h2 class="font-semibold text-gray-800 text-sm">User Email History</h2>
        <div class="flex flex-wrap gap-3 items-end">
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">User ID</label>
            <input v-model.number="historyUserId" type="number" class="input text-sm w-36" placeholder="e.g. 42" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Status</label>
            <select v-model="historyFilter.status" class="input text-sm w-36">
              <option value="">All</option>
              <option value="sent">Sent</option>
              <option value="opened">Opened</option>
              <option value="failed">Failed</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Email type</label>
            <select v-model="historyFilter.email_type" class="input text-sm w-40">
              <option value="">All types</option>
              <option value="marketing">Marketing</option>
              <option value="transactional">Transactional</option>
              <option value="notification">Notification</option>
            </select>
          </div>
          <button @click="loadHistory" :disabled="!historyUserId || loadingHistory" class="text-sm px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50">
            {{ loadingHistory ? 'Loading…' : 'Look Up' }}
          </button>
        </div>
      </div>

      <div v-if="historySearched && !historyRecords.length && !loadingHistory" class="text-center py-10 text-gray-400 text-sm">
        No email history found for user #{{ historyUserId }}.
      </div>
      <div v-else-if="historyRecords.length" class="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div class="px-5 py-3 border-b border-gray-100 flex items-center justify-between">
          <p class="text-sm font-semibold text-gray-700">User #{{ historyUserId }} — {{ historyRecords.length }} emails</p>
          <div class="flex gap-4 text-xs text-gray-500">
            <span>Opened: {{ historyRecords.filter(r => r.opened_at).length }}</span>
            <span>Failed: {{ historyRecords.filter(r => r.status === 'failed').length }}</span>
          </div>
        </div>
        <div class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="bg-gray-50 text-xs text-gray-500 uppercase">
            <tr>
              <th class="px-3 py-2 text-left">Campaign</th>
              <th class="px-3 py-2 text-left">Type</th>
              <th class="px-3 py-2 text-left">Status</th>
              <th class="px-3 py-2 text-left">Sent</th>
              <th class="px-3 py-2 text-left">Opened</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="rec in historyRecords" :key="rec.id" class="hover:bg-gray-50">
              <td class="px-3 py-2">
                <p v-if="rec.campaign" class="font-medium text-gray-800">{{ rec.campaign.title }}</p>
                <p v-if="rec.campaign" class="text-xs text-gray-400 mt-0.5">{{ rec.campaign.subject }}</p>
                <span v-else class="text-gray-400">—</span>
              </td>
              <td class="px-3 py-2 text-xs text-gray-500 font-mono">{{ rec.campaign?.email_type ?? '—' }}</td>
              <td class="px-3 py-2">
                <span :class="recipientStatusClass(rec.status)" class="text-xs px-2 py-0.5 rounded-full font-medium">{{ rec.status }}</span>
              </td>
              <td class="px-3 py-2 text-xs text-gray-400">{{ rec.sent_at ? fmtTime(rec.sent_at) : '—' }}</td>
              <td class="px-3 py-2 text-xs text-gray-400">{{ rec.opened_at ? fmtTime(rec.opened_at) : '—' }}</td>
            </tr>
          </tbody>
        </table>
        </div>
      </div>
    </div>

    <!-- ── Provider form dialog ───────────────────────────────────────────── -->
    <div v-if="showProviderForm" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-6 space-y-4">
        <h3 class="font-semibold text-gray-800">{{ editingProvider ? 'Edit Provider' : 'Add Email Provider' }}</h3>
        <div class="space-y-3">
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Provider</label>
            <select v-model="providerForm.provider_name" class="input">
              <option value="sendgrid">SendGrid</option>
              <option value="mailgun">Mailgun</option>
              <option value="smtp">SMTP</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">API Key</label>
            <input v-model="providerForm.api_key" type="password" autocomplete="off" class="input" placeholder="Leave blank to keep existing" />
            <p v-if="providerForm.provider_name === 'mailgun'" class="mt-1 text-xs text-amber-700">
              Mailgun: store as <code class="rounded bg-amber-50 px-1">key:mg.yourdomain.com</code> (key and sending domain separated by colon).
            </p>
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Sender Name</label>
            <input v-model="providerForm.sender_name" class="input" placeholder="My Company" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Sender Email</label>
            <input v-model="providerForm.sender_email" type="email" class="input" placeholder="noreply@company.com" />
          </div>
          <label class="flex items-center gap-3 cursor-pointer">
            <input v-model="providerForm.is_active" type="checkbox" class="rounded" />
            <span class="text-sm text-gray-700">Active</span>
          </label>
        </div>
        <div class="flex justify-end gap-3 pt-2">
          <button @click="closeProviderForm" class="text-sm text-gray-500 hover:text-gray-700">Cancel</button>
          <button @click="saveProvider" :disabled="actioning || !providerForm.sender_email || !providerForm.sender_name" class="btn-primary text-sm">
            {{ actioning ? 'Saving…' : (editingProvider ? 'Update' : 'Add') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete provider confirm -->
    <div v-if="deleteProviderId !== null" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 space-y-4">
        <h3 class="font-semibold text-gray-800">Remove Email Provider?</h3>
        <p class="text-sm text-gray-500">This will delete the provider configuration. Campaigns using it may stop sending.</p>
        <div class="flex justify-end gap-3">
          <button @click="deleteProviderId = null" class="text-sm text-gray-500 hover:text-gray-700">Cancel</button>
          <button @click="doDeleteProvider" :disabled="actioning" class="text-sm px-4 py-2 rounded-lg bg-red-600 text-white hover:bg-red-700 disabled:opacity-50">
            {{ actioning ? 'Removing…' : 'Remove' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <div
      v-if="toast"
      class="fixed bottom-6 right-6 z-50 px-4 py-3 rounded-xl shadow-lg text-sm text-white"
      :class="toast.type === 'error' ? 'bg-red-600' : 'bg-green-600'"
    >{{ toast.message }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from "vue";
import { adminCommsApi } from "@/api/adminComms";
import type { EmailProvider, CampaignRecipient } from "@/api/adminComms";
import { useWebsitesStore } from "@/stores/websites";
import { usePortalContextStore } from "@/stores/portalContext";

const tabs = [
  { key: "providers", label: "Providers" },
  { key: "recipients", label: "Recipients" },
  { key: "history", label: "Email History" },
] as const;

const activeTab = ref("providers");

// ── Providers ──────────────────────────────────────────────────────────────
const websites = useWebsitesStore();
const portalCtx = usePortalContextStore();
const defaultWebsiteId = computed(() => portalCtx.website?.id ?? websites.list[0]?.id ?? null);

const providers = ref<EmailProvider[]>([]);
const loadingProviders = ref(false);
const showProviderForm = ref(false);
const editingProvider = ref<EmailProvider | null>(null);
const deleteProviderId = ref<number | null>(null);
const actioning = ref(false);

const providerForm = reactive({
  provider_name: "sendgrid" as "smtp" | "sendgrid" | "mailgun",
  api_key: "",
  sender_name: "",
  sender_email: "",
  is_active: true,
  website: defaultWebsiteId.value,
});

function openEditProvider(prov: EmailProvider) {
  editingProvider.value = prov;
  Object.assign(providerForm, {
    provider_name: prov.provider_name,
    api_key: "",
    sender_name: prov.sender_name,
    sender_email: prov.sender_email,
    is_active: prov.is_active,
    website: prov.website,
  });
  showProviderForm.value = true;
}

function closeProviderForm() {
  showProviderForm.value = false;
  editingProvider.value = null;
  Object.assign(providerForm, { provider_name: "sendgrid", api_key: "", sender_name: "", sender_email: "", is_active: true, website: defaultWebsiteId.value });
}

function confirmDeleteProvider(id: number) {
  deleteProviderId.value = id;
}

async function loadProviders() {
  loadingProviders.value = true;
  try {
    const resp = await adminCommsApi.providers();
    const data = resp.data;
    providers.value = Array.isArray(data) ? data : data.results;
  } catch {
    showToast("Failed to load providers", "error");
  } finally {
    loadingProviders.value = false;
  }
}

async function saveProvider() {
  actioning.value = true;
  try {
    if (editingProvider.value) {
      const payload: Partial<typeof providerForm> = {
        provider_name: providerForm.provider_name,
        sender_name: providerForm.sender_name,
        sender_email: providerForm.sender_email,
        is_active: providerForm.is_active,
      };
      if (providerForm.api_key) payload.api_key = providerForm.api_key;
      const resp = await adminCommsApi.updateProvider(editingProvider.value.id, payload);
      const idx = providers.value.findIndex((p) => p.id === editingProvider.value!.id);
      if (idx !== -1) providers.value[idx] = resp.data;
    } else {
      const resp = await adminCommsApi.createProvider({
        website: providerForm.website,
        provider_name: providerForm.provider_name,
        api_key: providerForm.api_key,
        sender_name: providerForm.sender_name,
        sender_email: providerForm.sender_email,
        is_active: providerForm.is_active,
      });
      providers.value.unshift(resp.data);
    }
    closeProviderForm();
    showToast(editingProvider.value ? "Provider updated" : "Provider added");
  } catch {
    showToast("Failed to save provider", "error");
  } finally {
    actioning.value = false;
  }
}

async function toggleProvider(prov: EmailProvider) {
  actioning.value = true;
  try {
    const resp = await adminCommsApi.updateProvider(prov.id, { is_active: !prov.is_active });
    const idx = providers.value.findIndex((p) => p.id === prov.id);
    if (idx !== -1) providers.value[idx] = resp.data;
    showToast(`Provider ${resp.data.is_active ? "enabled" : "disabled"}`);
  } catch {
    showToast("Failed to update provider", "error");
  } finally {
    actioning.value = false;
  }
}

async function doDeleteProvider() {
  if (deleteProviderId.value === null) return;
  actioning.value = true;
  try {
    await adminCommsApi.deleteProvider(deleteProviderId.value);
    providers.value = providers.value.filter((p) => p.id !== deleteProviderId.value);
    deleteProviderId.value = null;
    showToast("Provider removed");
  } catch {
    showToast("Failed to remove provider", "error");
  } finally {
    actioning.value = false;
  }
}

// ── Recipients ─────────────────────────────────────────────────────────────
const recipients = ref<CampaignRecipient[]>([]);
const loadingRecipients = ref(false);
const recipientFilter = reactive({ status: "" });
const recipientSearch = ref("");

async function loadRecipients() {
  loadingRecipients.value = true;
  try {
    const params: Record<string, unknown> = {};
    if (recipientFilter.status) params.status = recipientFilter.status;
    if (recipientSearch.value.trim()) params.search = recipientSearch.value.trim();
    const resp = await adminCommsApi.recipients(params);
    const data = resp.data;
    recipients.value = Array.isArray(data) ? data : data.results;
  } catch {
    showToast("Failed to load recipients", "error");
  } finally {
    loadingRecipients.value = false;
  }
}

// ── History ────────────────────────────────────────────────────────────────
const historyRecords = ref<CampaignRecipient[]>([]);
const loadingHistory = ref(false);
const historyUserId = ref<number | null>(null);
const historySearched = ref(false);
const historyFilter = reactive({ status: "", email_type: "" });

async function loadHistory() {
  if (!historyUserId.value) return;
  loadingHistory.value = true;
  historySearched.value = true;
  try {
    const params: Record<string, string> = {};
    if (historyFilter.status) params.status = historyFilter.status;
    if (historyFilter.email_type) params.email_type = historyFilter.email_type;
    const resp = await adminCommsApi.adminEmailHistory(historyUserId.value, params);
    const data = resp.data;
    historyRecords.value = Array.isArray(data) ? data : data.results;
  } catch {
    showToast("Failed to load history", "error");
  } finally {
    loadingHistory.value = false;
  }
}

// ── Helpers ────────────────────────────────────────────────────────────────
const toast = ref<{ message: string; type: "success" | "error" } | null>(null);

function showToast(message: string, type: "success" | "error" = "success") {
  toast.value = { message, type };
  setTimeout(() => (toast.value = null), 3500);
}

function fmtTime(ts: string) {
  return new Date(ts).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

function recipientStatusClass(status: string) {
  const map: Record<string, string> = {
    sent: "bg-blue-100 text-blue-700",
    opened: "bg-green-100 text-green-700",
    failed: "bg-red-100 text-red-700",
    pending: "bg-amber-100 text-amber-700",
  };
  return map[status] ?? "bg-gray-100 text-gray-600";
}

onMounted(() => {
  websites.ensure();
  loadProviders();
  loadRecipients();
});
</script>

<style scoped>
.input {
  @apply w-full border border-gray-300 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent;
}
.btn-primary {
  @apply px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 transition;
}
</style>
