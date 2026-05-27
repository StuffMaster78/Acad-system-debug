<template>
  <div class="p-6 space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Website & Tenant</h1>
        <p v-if="website" class="text-sm text-gray-500 mt-0.5">{{ website.domain }}</p>
      </div>
      <span
        v-if="website"
        :class="website.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'"
        class="text-xs font-semibold px-2.5 py-1 rounded-full"
      >{{ website.is_active ? 'Active' : 'Inactive' }}</span>
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

    <!-- ── Site Settings ─────────────────────────────────────────────────── -->
    <div v-if="activeTab === 'settings'" class="space-y-6">
      <div v-if="loadingWebsite" class="text-center py-10 text-gray-400">Loading…</div>
      <template v-else-if="website">
        <!-- Basic info -->
        <section class="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
          <h2 class="font-semibold text-gray-800">Basic Information</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Site Name</label>
              <input v-model="settingsDraft.name" class="input" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Domain</label>
              <input v-model="settingsDraft.domain" class="input" disabled />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Contact Email</label>
              <input v-model="settingsDraft.contact_email" class="input" type="email" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Contact Phone</label>
              <input v-model="settingsDraft.contact_phone" class="input" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Admin Notifications Email</label>
              <input v-model="settingsDraft.admin_notifications_email" class="input" type="email" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Theme Color</label>
              <input v-model="settingsDraft.theme_color" class="input" type="color" />
            </div>
          </div>
        </section>

        <!-- Registration & guest -->
        <section class="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
          <h2 class="font-semibold text-gray-800">Registration & Guest Access</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <label class="flex items-center gap-3 cursor-pointer">
              <input v-model="settingsDraft.allow_registration" type="checkbox" class="rounded" />
              <span class="text-sm text-gray-700">Allow Registration</span>
            </label>
            <label class="flex items-center gap-3 cursor-pointer">
              <input v-model="settingsDraft.allow_guest_checkout" type="checkbox" class="rounded" />
              <span class="text-sm text-gray-700">Allow Guest Checkout</span>
            </label>
            <label class="flex items-center gap-3 cursor-pointer">
              <input v-model="settingsDraft.guest_requires_email_verification" type="checkbox" class="rounded" />
              <span class="text-sm text-gray-700">Guest Requires Email Verification</span>
            </label>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Guest Max Order Amount</label>
              <input v-model="settingsDraft.guest_max_order_amount" class="input" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Guest Block Urgent Before (hours)</label>
              <input v-model.number="settingsDraft.guest_block_urgent_before_hours" class="input" type="number" min="0" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Guest Magic Link TTL (hours)</label>
              <input v-model.number="settingsDraft.guest_magic_link_ttl_hours" class="input" type="number" min="1" />
            </div>
          </div>
        </section>

        <!-- SEO -->
        <section class="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
          <h2 class="font-semibold text-gray-800">SEO & Analytics</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="md:col-span-2">
              <label class="block text-xs font-medium text-gray-600 mb-1">Meta Title</label>
              <input v-model="settingsDraft.meta_title" class="input" />
            </div>
            <div class="md:col-span-2">
              <label class="block text-xs font-medium text-gray-600 mb-1">Meta Description</label>
              <textarea v-model="settingsDraft.meta_description" class="input h-20 resize-none" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Google Analytics ID</label>
              <input v-model="settingsDraft.google_analytics_id" class="input" placeholder="G-XXXXXXXXXX" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Google Search Console ID</label>
              <input v-model="settingsDraft.google_search_console_id" class="input" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Bing Webmaster ID</label>
              <input v-model="settingsDraft.bing_webmaster_id" class="input" />
            </div>
          </div>
          <div class="flex justify-end">
            <button @click="saveSeoSettings" :disabled="savingSeo" class="btn-primary text-sm">
              {{ savingSeo ? 'Saving…' : 'Save SEO Settings' }}
            </button>
          </div>
        </section>

        <!-- Live chat -->
        <section class="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
          <h2 class="font-semibold text-gray-800">Live Chat</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <label class="flex items-center gap-3 cursor-pointer md:col-span-2">
              <input v-model="settingsDraft.enable_live_chat" type="checkbox" class="rounded" />
              <span class="text-sm text-gray-700">Enable Live Chat</span>
            </label>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Tawk.to Property ID</label>
              <input v-model="settingsDraft.tawkto_property_id" class="input" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Tawk.to Widget ID</label>
              <input v-model="settingsDraft.tawkto_widget_id" class="input" />
            </div>
          </div>
        </section>

        <!-- Save / danger zone -->
        <div class="flex items-center justify-between">
          <div class="flex gap-3">
            <button
              v-if="!website.is_deleted"
              @click="confirmSoftDelete"
              class="text-sm px-4 py-2 rounded-lg border border-red-300 text-red-600 hover:bg-red-50 transition"
            >Soft-delete Site</button>
            <button
              v-else
              @click="doRestore"
              :disabled="actioning"
              class="text-sm px-4 py-2 rounded-lg border border-green-300 text-green-600 hover:bg-green-50 transition"
            >{{ actioning ? 'Restoring…' : 'Restore Site' }}</button>
          </div>
          <button @click="saveSettings" :disabled="savingSettings" class="btn-primary text-sm">
            {{ savingSettings ? 'Saving…' : 'Save Settings' }}
          </button>
        </div>

        <!-- Action logs -->
        <section class="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
            <h2 class="font-semibold text-gray-800">Action Log</h2>
            <span class="text-xs text-gray-400">Recent site-level events</span>
          </div>
          <div v-if="loadingLogs" class="p-6 text-center text-gray-400 text-sm">Loading…</div>
          <div v-else-if="!actionLogs.length" class="p-6 text-center text-gray-400 text-sm">No events recorded.</div>
          <table v-else class="w-full text-sm">
            <thead class="bg-gray-50 text-xs text-gray-500 uppercase">
              <tr>
                <th class="px-4 py-3 text-left">User</th>
                <th class="px-4 py-3 text-left">Action</th>
                <th class="px-4 py-3 text-left">Details</th>
                <th class="px-4 py-3 text-left">When</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="log in actionLogs" :key="log.id" class="hover:bg-gray-50">
                <td class="px-4 py-3 text-gray-700">{{ log.user }}</td>
                <td class="px-4 py-3">
                  <span class="font-mono text-xs bg-gray-100 px-1.5 py-0.5 rounded">{{ log.action }}</span>
                </td>
                <td class="px-4 py-3 text-gray-500 max-w-xs truncate">{{ log.details ?? '—' }}</td>
                <td class="px-4 py-3 text-gray-400 whitespace-nowrap">{{ fmtTime(log.timestamp) }}</td>
              </tr>
            </tbody>
          </table>
        </section>
      </template>
    </div>

    <!-- ── Branding ──────────────────────────────────────────────────────── -->
    <div v-if="activeTab === 'branding'" class="space-y-6">
      <div v-if="loadingBranding" class="text-center py-10 text-gray-400">Loading…</div>
      <template v-else-if="branding">
        <section class="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
          <h2 class="font-semibold text-gray-800">Email Sender Identity</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">From Name</label>
              <input v-model="brandingDraft.email_from_name" class="input" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">From Address</label>
              <input v-model="brandingDraft.email_from_address" class="input" type="email" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Reply-To Address</label>
              <input v-model="brandingDraft.email_reply_to" class="input" type="email" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Subject Prefix</label>
              <input v-model="brandingDraft.email_subject_prefix" class="input" placeholder="[SiteName]" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Notification Subject Prefix</label>
              <input v-model="brandingDraft.notification_subject_prefix" class="input" />
            </div>
          </div>
        </section>

        <section class="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
          <h2 class="font-semibold text-gray-800">Email Template</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Logo URL</label>
              <input v-model="brandingDraft.email_logo_url" class="input" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Header Color</label>
              <input v-model="brandingDraft.email_header_color" class="input" type="color" />
            </div>
            <div class="md:col-span-2">
              <label class="block text-xs font-medium text-gray-600 mb-1">Footer Text</label>
              <textarea v-model="brandingDraft.email_footer_text" class="input h-20 resize-none" />
            </div>
          </div>
        </section>

        <div class="flex justify-end">
          <button @click="saveBranding" :disabled="savingBranding" class="btn-primary text-sm">
            {{ savingBranding ? 'Saving…' : 'Save Branding' }}
          </button>
        </div>
      </template>
    </div>

    <!-- ── Features ──────────────────────────────────────────────────────── -->
    <div v-if="activeTab === 'features'" class="space-y-6">
      <div v-if="loadingFeatures" class="text-center py-10 text-gray-400">Loading…</div>
      <template v-else-if="featureToggle">
        <section class="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
          <h2 class="font-semibold text-gray-800">Authentication</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            <label v-for="flag in authFlags" :key="flag.key" class="flex items-center gap-3 cursor-pointer p-3 border border-gray-100 rounded-lg hover:bg-gray-50">
              <input
                type="checkbox"
                :checked="featureDraft[flag.key] as boolean"
                @change="featureDraft[flag.key] = ($event.target as HTMLInputElement).checked"
                class="rounded"
              />
              <span class="text-sm text-gray-700">{{ flag.label }}</span>
            </label>
          </div>
        </section>

        <section class="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
          <h2 class="font-semibold text-gray-800">Order & Workflow</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            <label v-for="flag in orderFlags" :key="flag.key" class="flex items-center gap-3 cursor-pointer p-3 border border-gray-100 rounded-lg hover:bg-gray-50">
              <input
                type="checkbox"
                :checked="featureDraft[flag.key] as boolean"
                @change="featureDraft[flag.key] = ($event.target as HTMLInputElement).checked"
                class="rounded"
              />
              <span class="text-sm text-gray-700">{{ flag.label }}</span>
            </label>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Max Order Size (pages)</label>
              <input v-model.number="featureDraft.max_order_size_pages" class="input" type="number" min="1" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Max Order Size (slides)</label>
              <input v-model.number="featureDraft.max_order_size_slides" class="input" type="number" min="1" />
            </div>
          </div>
        </section>

        <section class="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
          <h2 class="font-semibold text-gray-800">Platform Features</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            <label v-for="flag in platformFlags" :key="flag.key" class="flex items-center gap-3 cursor-pointer p-3 border border-gray-100 rounded-lg hover:bg-gray-50">
              <input
                type="checkbox"
                :checked="featureDraft[flag.key] as boolean"
                @change="featureDraft[flag.key] = ($event.target as HTMLInputElement).checked"
                class="rounded"
              />
              <span class="text-sm text-gray-700">{{ flag.label }}</span>
            </label>
          </div>
        </section>

        <div class="flex justify-end">
          <button @click="saveFeatures" :disabled="savingFeatures" class="btn-primary text-sm">
            {{ savingFeatures ? 'Saving…' : 'Save Feature Toggles' }}
          </button>
        </div>
      </template>
    </div>

    <!-- ── Integrations ──────────────────────────────────────────────────── -->
    <div v-if="activeTab === 'integrations'" class="space-y-6">
      <div class="flex items-center justify-between">
        <p class="text-sm text-gray-500">Third-party service connections. API keys are masked after save.</p>
        <button @click="showAddIntegration = true" class="btn-primary text-sm">+ Add Integration</button>
      </div>

      <div v-if="loadingIntegrations" class="text-center py-10 text-gray-400">Loading…</div>
      <div v-else-if="!integrations.length" class="text-center py-10 text-gray-400 text-sm">No integrations configured.</div>
      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          v-for="intg in integrations"
          :key="intg.id"
          class="bg-white rounded-xl border border-gray-200 p-5 space-y-3"
        >
          <div class="flex items-start justify-between">
            <div>
              <p class="font-semibold text-gray-800 text-sm">{{ intg.name ?? intg.integration_type }}</p>
              <p class="text-xs text-gray-400 font-mono">{{ intg.integration_type }}</p>
            </div>
            <span :class="intg.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'" class="text-xs font-medium px-2 py-0.5 rounded-full">
              {{ intg.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
          <p v-if="intg.description" class="text-xs text-gray-500">{{ intg.description }}</p>
          <div class="space-y-1 text-xs font-mono text-gray-500">
            <p v-if="intg.api_key">API Key: <span class="bg-gray-100 px-1.5 py-0.5 rounded">{{ intg.api_key }}</span></p>
            <p v-if="intg.access_token">Token: <span class="bg-gray-100 px-1.5 py-0.5 rounded">{{ intg.access_token }}</span></p>
          </div>
          <div class="flex gap-2 pt-1">
            <button @click="toggleIntegration(intg)" class="text-xs px-3 py-1.5 rounded border border-gray-200 hover:bg-gray-50">
              {{ intg.is_active ? 'Disable' : 'Enable' }}
            </button>
            <button @click="confirmDeleteIntegration(intg.id)" class="text-xs px-3 py-1.5 rounded border border-red-200 text-red-500 hover:bg-red-50">
              Remove
            </button>
          </div>
        </div>
      </div>

      <!-- Add integration dialog -->
      <div v-if="showAddIntegration" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-6 space-y-4">
          <h3 class="font-semibold text-gray-800">Add Integration</h3>
          <div class="space-y-3">
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Integration Type</label>
              <input v-model="newIntg.integration_type" class="input" placeholder="e.g. stripe, paypal, mailchimp" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Name (optional)</label>
              <input v-model="newIntg.name" class="input" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Description (optional)</label>
              <input v-model="newIntg.description" class="input" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">API Key</label>
              <input v-model="newIntg.api_key" class="input" type="password" autocomplete="off" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Secret Key</label>
              <input v-model="newIntg.secret_key" class="input" type="password" autocomplete="off" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Access Token</label>
              <input v-model="newIntg.access_token" class="input" type="password" autocomplete="off" />
            </div>
          </div>
          <div class="flex justify-end gap-3 pt-2">
            <button @click="showAddIntegration = false" class="text-sm text-gray-500 hover:text-gray-700">Cancel</button>
            <button @click="createIntegration" :disabled="savingIntegration" class="btn-primary text-sm">
              {{ savingIntegration ? 'Saving…' : 'Add Integration' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Delete confirm dialog -->
      <div v-if="deleteIntegrationId !== null" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 space-y-4">
          <h3 class="font-semibold text-gray-800">Remove Integration</h3>
          <p class="text-sm text-gray-500">This will permanently delete this integration configuration. Are you sure?</p>
          <div class="flex justify-end gap-3">
            <button @click="deleteIntegrationId = null" class="text-sm text-gray-500 hover:text-gray-700">Cancel</button>
            <button @click="doDeleteIntegration" :disabled="actioning" class="text-sm px-4 py-2 rounded-lg bg-red-600 text-white hover:bg-red-700 disabled:opacity-50">
              {{ actioning ? 'Removing…' : 'Remove' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Soft-delete confirm dialog -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 space-y-4">
        <h3 class="font-semibold text-gray-800">Soft-delete Site?</h3>
        <p class="text-sm text-gray-500">The site will be marked as deleted but can be restored later.</p>
        <div class="flex justify-end gap-3">
          <button @click="showDeleteConfirm = false" class="text-sm text-gray-500 hover:text-gray-700">Cancel</button>
          <button @click="doSoftDelete" :disabled="actioning" class="text-sm px-4 py-2 rounded-lg bg-red-600 text-white hover:bg-red-700 disabled:opacity-50">
            {{ actioning ? 'Deleting…' : 'Delete' }}
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
import { ref, reactive, computed, onMounted } from "vue";
import { websitesApi } from "@/api/websites";
import type { Website, TenantBranding, TenantFeatureToggle, WebsiteIntegrationConfig, WebsiteActionLog } from "@/api/websites";

const tabs = [
  { key: "settings", label: "Site Settings" },
  { key: "branding", label: "Branding" },
  { key: "features", label: "Features" },
  { key: "integrations", label: "Integrations" },
] as const;

type TabKey = (typeof tabs)[number]["key"];
const activeTab = ref<TabKey>("settings");

// ── State ──────────────────────────────────────────────────────────────────
const website = ref<Website | null>(null);
const branding = ref<TenantBranding | null>(null);
const featureToggle = ref<TenantFeatureToggle | null>(null);
const integrations = ref<WebsiteIntegrationConfig[]>([]);
const actionLogs = ref<WebsiteActionLog[]>([]);

const loadingWebsite = ref(false);
const loadingBranding = ref(false);
const loadingFeatures = ref(false);
const loadingIntegrations = ref(false);
const loadingLogs = ref(false);

const savingSettings = ref(false);
const savingSeo = ref(false);
const savingBranding = ref(false);
const savingFeatures = ref(false);
const savingIntegration = ref(false);
const actioning = ref(false);

const showDeleteConfirm = ref(false);
const showAddIntegration = ref(false);
const deleteIntegrationId = ref<number | null>(null);

const toast = ref<{ message: string; type: "success" | "error" } | null>(null);

// ── Drafts ─────────────────────────────────────────────────────────────────
const settingsDraft = reactive<Partial<Website>>({});
const brandingDraft = reactive<Partial<TenantBranding>>({});
const featureDraft = reactive<Partial<TenantFeatureToggle> & Record<string, unknown>>({});
const newIntg = reactive({
  integration_type: "",
  name: "",
  description: "",
  api_key: "",
  secret_key: "",
  access_token: "",
});

// ── Flag definitions ───────────────────────────────────────────────────────
const authFlags = [
  { key: "magic_link_enabled", label: "Magic Link Login" },
  { key: "two_factor_required", label: "Two-Factor Required" },
  { key: "password_reset_enabled", label: "Password Reset" },
  { key: "messaging_enabled", label: "Messaging" },
] as const;

const orderFlags = [
  { key: "allow_order_drafts", label: "Order Drafts" },
  { key: "allow_order_presets", label: "Order Presets" },
  { key: "allow_class_orders", label: "Class Orders" },
] as const;

const platformFlags = [
  { key: "allow_writer_portfolios", label: "Writer Portfolios" },
  { key: "allow_writer_feedback", label: "Writer Feedback" },
  { key: "allow_wallet", label: "Wallet" },
  { key: "allow_advance_payments", label: "Advance Payments" },
  { key: "allow_disputes", label: "Disputes" },
  { key: "allow_escalations", label: "Escalations" },
] as const;

// ── Helpers ────────────────────────────────────────────────────────────────
function showToast(message: string, type: "success" | "error" = "success") {
  toast.value = { message, type };
  setTimeout(() => (toast.value = null), 3500);
}

function fmtTime(ts: string) {
  return new Date(ts).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

function syncSettingsDraft(w: Website) {
  Object.assign(settingsDraft, {
    name: w.name,
    domain: w.domain,
    contact_email: w.contact_email,
    contact_phone: w.contact_phone,
    admin_notifications_email: w.admin_notifications_email,
    theme_color: w.theme_color ?? "#6366f1",
    allow_registration: w.allow_registration,
    allow_guest_checkout: w.allow_guest_checkout,
    guest_requires_email_verification: w.guest_requires_email_verification,
    guest_max_order_amount: w.guest_max_order_amount,
    guest_block_urgent_before_hours: w.guest_block_urgent_before_hours,
    guest_magic_link_ttl_hours: w.guest_magic_link_ttl_hours,
    meta_title: w.meta_title,
    meta_description: w.meta_description,
    google_analytics_id: w.google_analytics_id,
    google_search_console_id: w.google_search_console_id,
    bing_webmaster_id: w.bing_webmaster_id,
    enable_live_chat: w.enable_live_chat,
    tawkto_property_id: w.tawkto_property_id,
    tawkto_widget_id: w.tawkto_widget_id,
  });
}

function syncBrandingDraft(b: TenantBranding) {
  Object.assign(brandingDraft, {
    email_from_name: b.email_from_name,
    email_from_address: b.email_from_address,
    email_reply_to: b.email_reply_to,
    email_subject_prefix: b.email_subject_prefix,
    notification_subject_prefix: b.notification_subject_prefix,
    email_logo_url: b.email_logo_url,
    email_header_color: b.email_header_color ?? "#6366f1",
    email_footer_text: b.email_footer_text,
  });
}

function syncFeatureDraft(ft: TenantFeatureToggle) {
  Object.assign(featureDraft, {
    magic_link_enabled: ft.magic_link_enabled,
    two_factor_required: ft.two_factor_required,
    password_reset_enabled: ft.password_reset_enabled,
    messaging_enabled: ft.messaging_enabled,
    allow_order_drafts: ft.allow_order_drafts,
    allow_order_presets: ft.allow_order_presets,
    allow_class_orders: ft.allow_class_orders,
    allow_writer_portfolios: ft.allow_writer_portfolios,
    allow_writer_feedback: ft.allow_writer_feedback,
    allow_wallet: ft.allow_wallet,
    allow_advance_payments: ft.allow_advance_payments,
    allow_disputes: ft.allow_disputes,
    allow_escalations: ft.allow_escalations,
    max_order_size_pages: ft.max_order_size_pages,
    max_order_size_slides: ft.max_order_size_slides,
  });
}

// ── Fetch ──────────────────────────────────────────────────────────────────
async function loadWebsite() {
  loadingWebsite.value = true;
  loadingLogs.value = true;
  try {
    const [wsResp, logsResp] = await Promise.all([
      websitesApi.list(),
      websitesApi.actionLogs(),
    ]);
    const wsData = wsResp.data;
    const sites = Array.isArray(wsData) ? wsData : wsData.results;
    if (sites.length) {
      website.value = sites[0];
      syncSettingsDraft(sites[0]);
    }
    const logsData = logsResp.data;
    actionLogs.value = Array.isArray(logsData) ? logsData : logsData.results;
  } catch {
    showToast("Failed to load website data", "error");
  } finally {
    loadingWebsite.value = false;
    loadingLogs.value = false;
  }
}

async function loadBranding() {
  loadingBranding.value = true;
  try {
    const resp = await websitesApi.currentBranding();
    branding.value = resp.data;
    syncBrandingDraft(resp.data);
  } catch {
    showToast("Failed to load branding", "error");
  } finally {
    loadingBranding.value = false;
  }
}

async function loadFeatures() {
  loadingFeatures.value = true;
  try {
    const resp = await websitesApi.currentFeatureToggle();
    featureToggle.value = resp.data;
    syncFeatureDraft(resp.data);
  } catch {
    showToast("Failed to load feature toggles", "error");
  } finally {
    loadingFeatures.value = false;
  }
}

async function loadIntegrations() {
  loadingIntegrations.value = true;
  try {
    const resp = await websitesApi.integrations();
    const data = resp.data;
    integrations.value = Array.isArray(data) ? data : data.results;
  } catch {
    showToast("Failed to load integrations", "error");
  } finally {
    loadingIntegrations.value = false;
  }
}

// ── Save ───────────────────────────────────────────────────────────────────
async function saveSettings() {
  if (!website.value) return;
  savingSettings.value = true;
  try {
    const resp = await websitesApi.update(website.value.id, settingsDraft);
    website.value = resp.data;
    showToast("Settings saved");
  } catch {
    showToast("Failed to save settings", "error");
  } finally {
    savingSettings.value = false;
  }
}

async function saveSeoSettings() {
  if (!website.value) return;
  savingSeo.value = true;
  try {
    await websitesApi.updateSeoSettings(website.value.id, {
      meta_title: settingsDraft.meta_title,
      meta_description: settingsDraft.meta_description,
      google_analytics_id: settingsDraft.google_analytics_id,
      google_search_console_id: settingsDraft.google_search_console_id,
      bing_webmaster_id: settingsDraft.bing_webmaster_id,
    });
    showToast("SEO settings saved");
  } catch {
    showToast("Failed to save SEO settings", "error");
  } finally {
    savingSeo.value = false;
  }
}

async function saveBranding() {
  if (!branding.value) return;
  savingBranding.value = true;
  try {
    const resp = await websitesApi.updateBranding(branding.value.id, brandingDraft);
    branding.value = resp.data;
    showToast("Branding saved");
  } catch {
    showToast("Failed to save branding", "error");
  } finally {
    savingBranding.value = false;
  }
}

async function saveFeatures() {
  if (!featureToggle.value) return;
  savingFeatures.value = true;
  try {
    const resp = await websitesApi.updateFeatureToggle(featureToggle.value.id, featureDraft as Partial<TenantFeatureToggle>);
    featureToggle.value = resp.data;
    showToast("Feature toggles saved");
  } catch {
    showToast("Failed to save features", "error");
  } finally {
    savingFeatures.value = false;
  }
}

// ── Integration actions ────────────────────────────────────────────────────
async function createIntegration() {
  if (!website.value || !newIntg.integration_type.trim()) return;
  savingIntegration.value = true;
  try {
    const resp = await websitesApi.createIntegration({
      website: website.value.id,
      integration_type: newIntg.integration_type.trim(),
      name: newIntg.name || undefined,
      description: newIntg.description || undefined,
      api_key: newIntg.api_key || undefined,
      secret_key: newIntg.secret_key || undefined,
      access_token: newIntg.access_token || undefined,
    });
    integrations.value.unshift(resp.data);
    Object.assign(newIntg, { integration_type: "", name: "", description: "", api_key: "", secret_key: "", access_token: "" });
    showAddIntegration.value = false;
    showToast("Integration added");
  } catch {
    showToast("Failed to add integration", "error");
  } finally {
    savingIntegration.value = false;
  }
}

async function toggleIntegration(intg: WebsiteIntegrationConfig) {
  try {
    const resp = await websitesApi.updateIntegration(intg.id, { is_active: !intg.is_active });
    const idx = integrations.value.findIndex((i) => i.id === intg.id);
    if (idx !== -1) integrations.value[idx] = resp.data;
    showToast(`Integration ${resp.data.is_active ? "enabled" : "disabled"}`);
  } catch {
    showToast("Failed to update integration", "error");
  }
}

function confirmDeleteIntegration(id: number) {
  deleteIntegrationId.value = id;
}

async function doDeleteIntegration() {
  if (deleteIntegrationId.value === null) return;
  actioning.value = true;
  try {
    await websitesApi.deleteIntegration(deleteIntegrationId.value);
    integrations.value = integrations.value.filter((i) => i.id !== deleteIntegrationId.value);
    deleteIntegrationId.value = null;
    showToast("Integration removed");
  } catch {
    showToast("Failed to remove integration", "error");
  } finally {
    actioning.value = false;
  }
}

// ── Site lifecycle ─────────────────────────────────────────────────────────
function confirmSoftDelete() {
  showDeleteConfirm.value = true;
}

async function doSoftDelete() {
  if (!website.value) return;
  actioning.value = true;
  try {
    await websitesApi.softDelete(website.value.id);
    website.value = { ...website.value, is_deleted: true };
    showDeleteConfirm.value = false;
    showToast("Site marked as deleted");
  } catch {
    showToast("Failed to delete site", "error");
  } finally {
    actioning.value = false;
  }
}

async function doRestore() {
  if (!website.value) return;
  actioning.value = true;
  try {
    await websitesApi.restore(website.value.id);
    website.value = { ...website.value, is_deleted: false };
    showToast("Site restored");
  } catch {
    showToast("Failed to restore site", "error");
  } finally {
    actioning.value = false;
  }
}

// ── Init ───────────────────────────────────────────────────────────────────
onMounted(() => {
  loadWebsite();
  loadBranding();
  loadFeatures();
  loadIntegrations();
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
