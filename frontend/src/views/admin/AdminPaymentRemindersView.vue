<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { Bell, Plus, Pencil, Trash2, RefreshCw, CheckCircle, XCircle, Mail, MessageSquare } from "@lucide/vue";
import { api, apiPath } from "@/api/client";
import { useAuthStore } from "@/stores/auth";
import BaseModal from "@/components/ui/BaseModal.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";

const auth = useAuthStore();
const isSuperadmin = computed(() => auth.role === "superadmin");

const BASE = "/admin-management/payment-reminders";

// ── Types ────────────────────────────────────────────────────────────────────

interface ReminderConfig {
  id: number;
  website: number;
  website_name: string;
  name: string;
  deadline_percentage: string;
  message: string;
  send_as_notification: boolean;
  send_as_email: boolean;
  email_subject: string;
  is_active: boolean;
  display_order: number;
  created_at: string;
  updated_at: string;
}

interface DeletionMessage {
  id: number;
  website: number;
  website_name: string;
  message: string;
  send_as_notification: boolean;
  send_as_email: boolean;
  email_subject: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface SentRecord {
  id: number;
  reminder_name: string;
  deadline_percentage: string;
  client_email: string;
  order: number | null;
  sent_at: string;
  sent_as_notification: boolean;
  sent_as_email: boolean;
}

interface Stats { total: number; active: number; sent_last_7_days: number; }

// ── State ────────────────────────────────────────────────────────────────────

const tab = ref<"configs" | "deletions" | "log">("configs");
const isLoading = ref(false);
const error = ref("");
const notice = ref("");

const stats = ref<Stats>({ total: 0, active: 0, sent_last_7_days: 0 });
const configs = ref<ReminderConfig[]>([]);
const deletions = ref<DeletionMessage[]>([]);
const sentLog = ref<SentRecord[]>([]);

// Modal
const showModal = ref(false);
const modalMode = ref<"create-config" | "edit-config" | "create-deletion" | "edit-deletion">("create-config");
const saving = ref(false);

const configDraft = reactive({
  id: 0,
  name: "",
  deadline_percentage: "",
  message: "",
  send_as_notification: true,
  send_as_email: true,
  email_subject: "",
  is_active: true,
  display_order: 0,
});

const deletionDraft = reactive({
  id: 0,
  message: "",
  send_as_notification: true,
  send_as_email: true,
  email_subject: "",
  is_active: true,
});

const isConfigModal = computed(() => modalMode.value === "create-config" || modalMode.value === "edit-config");
const isEditModal = computed(() => modalMode.value === "edit-config" || modalMode.value === "edit-deletion");

// ── API helpers ───────────────────────────────────────────────────────────────

async function load() {
  isLoading.value = true;
  error.value = "";
  try {
    const [statsRes, cfgRes, delRes, logRes] = await Promise.allSettled([
      api.get<Stats>(apiPath(`${BASE}/configs/stats/`)),
      api.get<{ results: ReminderConfig[] } | ReminderConfig[]>(apiPath(`${BASE}/configs/`)),
      api.get<{ results: DeletionMessage[] } | DeletionMessage[]>(apiPath(`${BASE}/deletion-messages/`)),
      api.get<{ results: SentRecord[] } | SentRecord[]>(apiPath(`${BASE}/sent/`)),
    ]);
    if (statsRes.status === "fulfilled") stats.value = statsRes.value.data;
    if (cfgRes.status === "fulfilled") {
      const d = cfgRes.value.data;
      configs.value = Array.isArray(d) ? d : d.results;
    }
    if (delRes.status === "fulfilled") {
      const d = delRes.value.data;
      deletions.value = Array.isArray(d) ? d : d.results;
    }
    if (logRes.status === "fulfilled") {
      const d = logRes.value.data;
      sentLog.value = Array.isArray(d) ? d : d.results;
    }
  } finally {
    isLoading.value = false;
  }
}

function openCreateConfig() {
  Object.assign(configDraft, { id: 0, name: "", deadline_percentage: "", message: "", send_as_notification: true, send_as_email: true, email_subject: "", is_active: true, display_order: 0 });
  modalMode.value = "create-config";
  showModal.value = true;
}

function openEditConfig(r: ReminderConfig) {
  Object.assign(configDraft, { id: r.id, name: r.name, deadline_percentage: r.deadline_percentage, message: r.message, send_as_notification: r.send_as_notification, send_as_email: r.send_as_email, email_subject: r.email_subject, is_active: r.is_active, display_order: r.display_order });
  modalMode.value = "edit-config";
  showModal.value = true;
}

function openCreateDeletion() {
  Object.assign(deletionDraft, { id: 0, message: "", send_as_notification: true, send_as_email: true, email_subject: "", is_active: true });
  modalMode.value = "create-deletion";
  showModal.value = true;
}

function openEditDeletion(d: DeletionMessage) {
  Object.assign(deletionDraft, { id: d.id, message: d.message, send_as_notification: d.send_as_notification, send_as_email: d.send_as_email, email_subject: d.email_subject, is_active: d.is_active });
  modalMode.value = "edit-deletion";
  showModal.value = true;
}

async function saveModal() {
  saving.value = true;
  error.value = "";
  try {
    if (isConfigModal.value) {
      const payload = {
        name: configDraft.name,
        deadline_percentage: Number(configDraft.deadline_percentage),
        message: configDraft.message,
        send_as_notification: configDraft.send_as_notification,
        send_as_email: configDraft.send_as_email,
        email_subject: configDraft.email_subject,
        is_active: configDraft.is_active,
        display_order: configDraft.display_order,
      };
      if (isEditModal.value) {
        await api.patch(apiPath(`${BASE}/configs/${configDraft.id}/`), payload);
      } else {
        await api.post(apiPath(`${BASE}/configs/`), payload);
      }
    } else {
      const payload = {
        message: deletionDraft.message,
        send_as_notification: deletionDraft.send_as_notification,
        send_as_email: deletionDraft.send_as_email,
        email_subject: deletionDraft.email_subject,
        is_active: deletionDraft.is_active,
      };
      if (isEditModal.value) {
        await api.patch(apiPath(`${BASE}/deletion-messages/${deletionDraft.id}/`), payload);
      } else {
        await api.post(apiPath(`${BASE}/deletion-messages/`), payload);
      }
    }
    showModal.value = false;
    notice.value = `${isEditModal.value ? "Updated" : "Created"} successfully.`;
    await load();
  } catch (e: unknown) {
    const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    error.value = msg || "Save failed. Check your inputs.";
  } finally {
    saving.value = false;
  }
}

async function deleteConfig(id: number) {
  if (!confirm("Delete this reminder? This cannot be undone.")) return;
  try {
    await api.delete(apiPath(`${BASE}/configs/${id}/`));
    notice.value = "Reminder deleted.";
    await load();
  } catch {
    error.value = "Delete failed.";
  }
}

async function deleteDeletion(id: number) {
  if (!confirm("Delete this message? This cannot be undone.")) return;
  try {
    await api.delete(apiPath(`${BASE}/deletion-messages/${id}/`));
    notice.value = "Message deleted.";
    await load();
  } catch {
    error.value = "Delete failed.";
  }
}

function fmtDate(v: string) {
  return new Date(v).toLocaleString("en-US", { month: "short", day: "numeric", year: "numeric", hour: "2-digit", minute: "2-digit" });
}

onMounted(load);
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <Bell class="h-6 w-6 text-signal" />
        <div>
          <h1 class="text-xl font-semibold text-ink">Payment Reminders</h1>
          <p class="text-sm text-graphite">Configure messages sent to clients with unpaid orders.</p>
        </div>
      </div>
      <button class="inline-flex items-center gap-1.5 text-sm text-graphite hover:text-ink" @click="load">
        <RefreshCw class="h-4 w-4" /> Refresh
      </button>
    </div>

    <!-- Feedback -->
    <div v-if="notice" class="rounded-md bg-green-50 border border-green-200 px-4 py-3 text-sm text-green-800 flex items-center justify-between">
      {{ notice }}
      <button class="ml-3 text-green-600 hover:text-green-800" @click="notice = ''">✕</button>
    </div>
    <div v-if="error" class="rounded-md bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-800 flex items-center justify-between">
      {{ error }}
      <button class="ml-3 text-red-600 hover:text-red-800" @click="error = ''">✕</button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-3 gap-4">
      <div class="rounded-lg border border-slate-200 bg-white p-4">
        <p class="text-xs font-medium uppercase text-graphite">Total Configs</p>
        <p class="mt-1 text-2xl font-bold text-ink">{{ stats.total }}</p>
      </div>
      <div class="rounded-lg border border-slate-200 bg-white p-4">
        <p class="text-xs font-medium uppercase text-graphite">Active</p>
        <p class="mt-1 text-2xl font-bold text-green-600">{{ stats.active }}</p>
      </div>
      <div class="rounded-lg border border-slate-200 bg-white p-4">
        <p class="text-xs font-medium uppercase text-graphite">Sent (last 7 days)</p>
        <p class="mt-1 text-2xl font-bold text-signal">{{ stats.sent_last_7_days }}</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-slate-200">
      <nav class="-mb-px flex gap-6">
        <button
          v-for="t in [{ key: 'configs', label: 'Reminders' }, { key: 'deletions', label: 'Deletion Messages' }, { key: 'log', label: 'Sent Log' }] as const"
          :key="t.key"
          class="border-b-2 pb-3 text-sm font-medium transition-colors"
          :class="tab === t.key ? 'border-signal text-signal' : 'border-transparent text-graphite hover:text-ink'"
          @click="tab = t.key"
        >
          {{ t.label }}
        </button>
      </nav>
    </div>

    <LoadingSpinner v-if="isLoading" />

    <!-- Reminder Configs tab -->
    <template v-else-if="tab === 'configs'">
      <div class="flex justify-end">
        <button
          class="inline-flex items-center gap-2 rounded-md bg-signal px-4 py-2 text-sm font-medium text-white hover:bg-signal/90"
          @click="openCreateConfig"
        >
          <Plus class="h-4 w-4" /> Add Reminder
        </button>
      </div>

      <div v-if="configs.length === 0" class="rounded-lg border border-slate-200 bg-white py-12 text-center text-sm text-graphite">
        No reminder configs yet. Add one to start sending payment reminders.
      </div>

      <div v-else class="overflow-hidden rounded-lg border border-slate-200 bg-white">
        <table class="min-w-full divide-y divide-slate-200 text-sm">
          <thead class="bg-slate-50 text-xs font-medium uppercase text-graphite">
            <tr>
              <th class="px-4 py-3 text-left">Name</th>
              <th class="px-4 py-3 text-left">Deadline %</th>
              <th class="px-4 py-3 text-left">Channels</th>
              <th v-if="isSuperadmin" class="px-4 py-3 text-left">Website</th>
              <th class="px-4 py-3 text-left">Status</th>
              <th class="px-4 py-3 text-left">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="r in configs" :key="r.id" class="hover:bg-slate-50">
              <td class="px-4 py-3">
                <p class="font-medium text-ink">{{ r.name }}</p>
                <p class="text-xs text-graphite line-clamp-1">{{ r.message }}</p>
              </td>
              <td class="px-4 py-3 font-mono">{{ r.deadline_percentage }}%</td>
              <td class="px-4 py-3">
                <span class="inline-flex gap-1">
                  <MessageSquare v-if="r.send_as_notification" class="h-4 w-4 text-signal" title="In-app notification" />
                  <Mail v-if="r.send_as_email" class="h-4 w-4 text-signal" title="Email" />
                </span>
              </td>
              <td v-if="isSuperadmin" class="px-4 py-3 text-graphite">{{ r.website_name }}</td>
              <td class="px-4 py-3">
                <StatusPill :label="r.is_active ? 'Active' : 'Inactive'" :tone="r.is_active ? 'success' : 'neutral'" />
              </td>
              <td class="px-4 py-3">
                <span class="inline-flex gap-2">
                  <button class="text-graphite hover:text-ink" title="Edit" @click="openEditConfig(r)">
                    <Pencil class="h-4 w-4" />
                  </button>
                  <button class="text-graphite hover:text-red-600" title="Delete" @click="deleteConfig(r.id)">
                    <Trash2 class="h-4 w-4" />
                  </button>
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <!-- Deletion Messages tab -->
    <template v-else-if="tab === 'deletions'">
      <div class="flex justify-end">
        <button
          class="inline-flex items-center gap-2 rounded-md bg-signal px-4 py-2 text-sm font-medium text-white hover:bg-signal/90"
          @click="openCreateDeletion"
        >
          <Plus class="h-4 w-4" /> Add Message
        </button>
      </div>

      <div v-if="deletions.length === 0" class="rounded-lg border border-slate-200 bg-white py-12 text-center text-sm text-graphite">
        No deletion messages configured. These are sent when an unpaid order is cancelled after deadline.
      </div>

      <div v-else class="overflow-hidden rounded-lg border border-slate-200 bg-white">
        <table class="min-w-full divide-y divide-slate-200 text-sm">
          <thead class="bg-slate-50 text-xs font-medium uppercase text-graphite">
            <tr>
              <th class="px-4 py-3 text-left">Message</th>
              <th class="px-4 py-3 text-left">Channels</th>
              <th v-if="isSuperadmin" class="px-4 py-3 text-left">Website</th>
              <th class="px-4 py-3 text-left">Status</th>
              <th class="px-4 py-3 text-left">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="d in deletions" :key="d.id" class="hover:bg-slate-50">
              <td class="px-4 py-3 max-w-sm">
                <p class="text-sm text-ink line-clamp-2">{{ d.message }}</p>
                <p v-if="d.email_subject" class="mt-0.5 text-xs text-graphite">Subject: {{ d.email_subject }}</p>
              </td>
              <td class="px-4 py-3">
                <span class="inline-flex gap-1">
                  <MessageSquare v-if="d.send_as_notification" class="h-4 w-4 text-signal" />
                  <Mail v-if="d.send_as_email" class="h-4 w-4 text-signal" />
                </span>
              </td>
              <td v-if="isSuperadmin" class="px-4 py-3 text-graphite">{{ d.website_name }}</td>
              <td class="px-4 py-3">
                <StatusPill :label="d.is_active ? 'Active' : 'Inactive'" :tone="d.is_active ? 'success' : 'neutral'" />
              </td>
              <td class="px-4 py-3">
                <span class="inline-flex gap-2">
                  <button class="text-graphite hover:text-ink" title="Edit" @click="openEditDeletion(d)">
                    <Pencil class="h-4 w-4" />
                  </button>
                  <button class="text-graphite hover:text-red-600" title="Delete" @click="deleteDeletion(d.id)">
                    <Trash2 class="h-4 w-4" />
                  </button>
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <!-- Sent Log tab -->
    <template v-else-if="tab === 'log'">
      <div v-if="sentLog.length === 0" class="rounded-lg border border-slate-200 bg-white py-12 text-center text-sm text-graphite">
        No reminders sent yet.
      </div>
      <div v-else class="overflow-hidden rounded-lg border border-slate-200 bg-white">
        <table class="min-w-full divide-y divide-slate-200 text-sm">
          <thead class="bg-slate-50 text-xs font-medium uppercase text-graphite">
            <tr>
              <th class="px-4 py-3 text-left">Reminder</th>
              <th class="px-4 py-3 text-left">Client</th>
              <th class="px-4 py-3 text-left">Order</th>
              <th class="px-4 py-3 text-left">Sent At</th>
              <th class="px-4 py-3 text-left">Channels</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="s in sentLog" :key="s.id" class="hover:bg-slate-50">
              <td class="px-4 py-3">
                <p class="font-medium text-ink">{{ s.reminder_name }}</p>
                <p class="text-xs text-graphite">{{ s.deadline_percentage }}% deadline</p>
              </td>
              <td class="px-4 py-3 text-graphite">{{ s.client_email }}</td>
              <td class="px-4 py-3 text-graphite">{{ s.order ? `#${s.order}` : '—' }}</td>
              <td class="px-4 py-3 text-graphite whitespace-nowrap">{{ fmtDate(s.sent_at) }}</td>
              <td class="px-4 py-3">
                <span class="inline-flex gap-1">
                  <CheckCircle v-if="s.sent_as_notification" class="h-4 w-4 text-green-500" title="Notification sent" />
                  <XCircle v-else class="h-4 w-4 text-slate-300" title="Notification not sent" />
                  <Mail v-if="s.sent_as_email" class="h-4 w-4 text-signal" title="Email sent" />
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <!-- Modal -->
    <BaseModal :open="showModal" :title="isEditModal ? 'Edit' : 'New'" @close="showModal = false">
      <form class="space-y-4" @submit.prevent="saveModal">
        <template v-if="isConfigModal">
          <div>
            <label class="block text-sm font-medium text-ink mb-1">Name</label>
            <input v-model="configDraft.name" required class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal" placeholder="e.g. First Reminder" />
          </div>
          <div>
            <label class="block text-sm font-medium text-ink mb-1">Deadline % elapsed</label>
            <input v-model="configDraft.deadline_percentage" type="number" min="0" max="100" step="0.01" required class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal" placeholder="e.g. 30" />
            <p class="mt-1 text-xs text-graphite">Send when this percentage of the deadline window has elapsed (0–100).</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-ink mb-1">Display order</label>
            <input v-model.number="configDraft.display_order" type="number" min="0" class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal" placeholder="0" />
          </div>
        </template>

        <div>
          <label class="block text-sm font-medium text-ink mb-1">Message</label>
          <textarea v-model="isConfigModal ? configDraft.message : deletionDraft.message" required rows="4" class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal" placeholder="Message body sent to the client…" />
        </div>

        <div>
          <label class="block text-sm font-medium text-ink mb-1">Email subject (optional)</label>
          <input v-model="isConfigModal ? configDraft.email_subject : deletionDraft.email_subject" class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal" placeholder="e.g. Action required: complete your payment" />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <label class="flex items-center gap-2 text-sm">
            <input v-model="isConfigModal ? configDraft.send_as_notification : deletionDraft.send_as_notification" type="checkbox" class="rounded border-slate-300 text-signal" />
            Send as notification
          </label>
          <label class="flex items-center gap-2 text-sm">
            <input v-model="isConfigModal ? configDraft.send_as_email : deletionDraft.send_as_email" type="checkbox" class="rounded border-slate-300 text-signal" />
            Send as email
          </label>
        </div>

        <label class="flex items-center gap-2 text-sm">
          <input v-model="isConfigModal ? configDraft.is_active : deletionDraft.is_active" type="checkbox" class="rounded border-slate-300 text-signal" />
          Active
        </label>

        <div v-if="error" class="rounded-md bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-800">
          {{ error }}
        </div>

        <div class="flex justify-end gap-3">
          <button type="button" class="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-ink hover:bg-slate-50" @click="showModal = false">
            Cancel
          </button>
          <button type="submit" :disabled="saving" class="rounded-md bg-signal px-4 py-2 text-sm font-medium text-white hover:bg-signal/90 disabled:opacity-50">
            {{ saving ? "Saving…" : (isEditModal ? "Save changes" : "Create") }}
          </button>
        </div>
      </form>
    </BaseModal>
  </div>
</template>
