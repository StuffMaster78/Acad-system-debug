<script setup lang="ts">
import { onMounted, ref } from "vue";
import {
  BarChart3,
  BellRing,
  CheckCircle2,
  FileText,
  Loader2,
  Mail,
  Megaphone,
  MessageSquare,
  Pin,
  PinOff,
  Plus,
  RefreshCw,
  Search,
  Trash2,
} from "@lucide/vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import RichTextEditor from "@/components/forms/RichTextEditor.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useAdminCommsStore } from "@/stores/adminComms";
import { announcementsApi, type AnnouncementRecord, type CreateAnnouncementPayload } from "@/api/announcements";
import {
  adminCommsApi,
  type CampaignAnalyticsRow,
  type EmailTemplate,
  type CreateEmailTemplatePayload,
} from "@/api/adminComms";

const comms = useAdminCommsStore();

// ─── Announcements ──────────────────────────────────────────────────────────
const announcements = ref<AnnouncementRecord[]>([]);
const annLoading = ref(false);
const annError = ref("");
const annSuccess = ref("");
const showAnnForm = ref(false);
const annMutating = ref(false);
const pendingDeleteAnnId = ref<number | null>(null);

const annForm = ref<CreateAnnouncementPayload>({
  title: "",
  message: "",
  category: "general",
  target_roles: [],
  pinned: false,
  require_acknowledgement: false,
});

const CATEGORIES = ["general", "news", "update", "maintenance", "promotion"];
const ROLES = ["writer", "client", "editor", "support", "admin"];

async function fetchAnnouncements() {
  annLoading.value = true;
  annError.value = "";
  try {
    const { data } = await announcementsApi.list({ ordering: "-broadcast__pinned,-created_at" });
    announcements.value = Array.isArray(data) ? data : (data as { results: AnnouncementRecord[] }).results ?? [];
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    annError.value = detail ?? "Could not load announcements.";
  } finally {
    annLoading.value = false;
  }
}

async function createAnnouncement() {
  if (!annForm.value.title || !annForm.value.message) return;
  annMutating.value = true;
  annError.value = "";
  annSuccess.value = "";
  try {
    const { data } = await announcementsApi.create(annForm.value);
    announcements.value.unshift(data);
    annSuccess.value = "Announcement created and broadcast.";
    showAnnForm.value = false;
    annForm.value = { title: "", message: "", category: "general", target_roles: [], pinned: false, require_acknowledgement: false };
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string; title?: string[] } } })?.response?.data;
    annError.value = detail?.detail ?? detail?.title?.[0] ?? "Failed to create announcement.";
  } finally {
    annMutating.value = false;
  }
}

async function togglePin(item: AnnouncementRecord) {
  annMutating.value = true;
  try {
    if (item.is_pinned) {
      await announcementsApi.unpin(item.id);
      item.is_pinned = false;
    } else {
      await announcementsApi.pin(item.id);
      item.is_pinned = true;
    }
  } catch {
    // non-critical
  } finally {
    annMutating.value = false;
  }
}

async function deleteAnnouncement(item: AnnouncementRecord) {
  if (pendingDeleteAnnId.value !== item.id) { pendingDeleteAnnId.value = item.id; return; }
  pendingDeleteAnnId.value = null;
  annMutating.value = true;
  try {
    await announcementsApi.delete(item.id);
    announcements.value = announcements.value.filter((a) => a.id !== item.id);
  } catch {
    annError.value = "Delete failed.";
  } finally {
    annMutating.value = false;
  }
}

function categoryTone(cat: string) {
  if (cat === "maintenance") return "warning";
  if (cat === "update" || cat === "promotion") return "success";
  return "neutral";
}

function annDate(value: string) {
  return new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(value));
}

// ─── End Announcements ───────────────────────────────────────────────────────

const metricToneClasses = {
  neutral: "border-slate-200 bg-white",
  good: "border-emerald-200 bg-emerald-50",
  warn: "border-amber-200 bg-amber-50",
  risk: "border-rose-200 bg-rose-50",
};

function formatDate(value?: string | null) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function statusTone(status?: string | null) {
  const normalized = (status ?? "").toLowerCase();
  if (normalized.includes("failed") || normalized.includes("rejected") || normalized.includes("escalated")) {
    return "danger";
  }
  if (normalized.includes("pending") || normalized.includes("draft") || normalized.includes("held")) {
    return "warning";
  }
  if (normalized.includes("sent") || normalized.includes("approved") || normalized.includes("released")) {
    return "success";
  }
  return "neutral";
}

// ─── Email Templates ─────────────────────────────────────────────────────────
const templates = ref<EmailTemplate[]>([]);
const tplLoading = ref(false);
const tplMutating = ref(false);
const tplError = ref("");
const pendingDeleteTplId = ref<number | null>(null);
const tplSuccess = ref("");
const showTplForm = ref(false);
const tplForm = ref<CreateEmailTemplatePayload>({ name: "", subject: "", body: "", is_global: true });

async function fetchTemplates() {
  tplLoading.value = true;
  tplError.value = "";
  try {
    const { data } = await adminCommsApi.templates();
    templates.value = Array.isArray(data) ? data : (data as { results: EmailTemplate[] }).results ?? [];
  } catch {
    tplError.value = "Could not load templates.";
  } finally {
    tplLoading.value = false;
  }
}

async function createTemplate() {
  if (!tplForm.value.name || !tplForm.value.subject || !tplForm.value.body) return;
  tplMutating.value = true;
  tplError.value = "";
  tplSuccess.value = "";
  try {
    const { data } = await adminCommsApi.createTemplate(tplForm.value);
    templates.value.unshift(data);
    tplSuccess.value = `Template "${data.name}" saved.`;
    showTplForm.value = false;
    tplForm.value = { name: "", subject: "", body: "", is_global: true };
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    tplError.value = detail ?? "Failed to save template.";
  } finally {
    tplMutating.value = false;
  }
}

async function deleteTemplate(tpl: EmailTemplate) {
  if (pendingDeleteTplId.value !== tpl.id) { pendingDeleteTplId.value = tpl.id; return; }
  pendingDeleteTplId.value = null;
  tplMutating.value = true;
  try {
    await adminCommsApi.deleteTemplate(tpl.id);
    templates.value = templates.value.filter((t) => t.id !== tpl.id);
  } catch {
    tplError.value = "Delete failed.";
  } finally {
    tplMutating.value = false;
  }
}

function applyTemplate(tpl: EmailTemplate) {
  comms.campaignComposer.subject = tpl.subject;
  comms.campaignComposer.body = tpl.body;
  tplSuccess.value = `Template "${tpl.name}" applied to composer.`;
}

// ─── Campaign Analytics ───────────────────────────────────────────────────────
const analyticsRows = ref<CampaignAnalyticsRow[]>([]);
const analyticsLoading = ref(false);
const analyticsError = ref("");
const analyticsStart = ref("");
const analyticsEnd = ref("");

async function fetchAnalytics() {
  analyticsLoading.value = true;
  analyticsError.value = "";
  try {
    const params: { start?: string; end?: string } = {};
    if (analyticsStart.value) params.start = analyticsStart.value;
    if (analyticsEnd.value) params.end = analyticsEnd.value;
    const { data } = await adminCommsApi.campaignAnalytics(params);
    analyticsRows.value = Array.isArray(data) ? data : [];
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    analyticsError.value = detail ?? "Could not load analytics.";
  } finally {
    analyticsLoading.value = false;
  }
}

function fmtRate(val: number): string {
  return `${(val ?? 0).toFixed(1)}%`;
}

function fmtDate(val: string | null | undefined): string {
  if (!val) return "—";
  return new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(val));
}
// ─── End Analytics ───────────────────────────────────────────────────────────

onMounted(() => {
  comms.hydrate().catch(() => undefined);
  fetchAnnouncements();
  fetchTemplates();
  fetchAnalytics();
});
</script>

<template>
  <div class="space-y-8">
    <section class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase text-signal">Admin</p>
        <h1 class="mt-2 text-3xl font-semibold">Communications</h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
          Live message queues, notifications, broadcasts, and mass email
          campaign operations in one admin surface.
        </p>
      </div>
      <button
        class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold"
        type="button"
        @click="comms.hydrate"
      >
        <RefreshCw class="h-4 w-4" />
        Refresh
      </button>
    </section>

    <p
      v-if="comms.error"
      class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
    >
      {{ comms.error }} Preview mode will still show the layout.
    </p>

    <p
      v-if="comms.notice"
      class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900"
    >
      {{ comms.notice }}
    </p>

    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div
        v-for="metric in comms.metrics"
        :key="metric.label"
        class="min-h-32 rounded-md border p-4"
        :class="metricToneClasses[metric.tone]"
      >
        <p class="text-sm font-medium text-graphite">{{ metric.label }}</p>
        <p class="mt-3 text-3xl font-semibold text-ink">{{ metric.value }}</p>
        <p class="mt-2 text-sm leading-5 text-graphite">{{ metric.detail }}</p>
      </div>
    </section>

    <section class="grid gap-6 xl:grid-cols-[minmax(0,1.2fr)_minmax(380px,0.8fr)]">
      <div class="space-y-4">
        <section class="rounded-md border border-slate-200 bg-white">
          <div class="flex flex-col gap-4 border-b border-slate-200 px-4 py-4 md:flex-row md:items-center md:justify-between">
            <div class="flex items-center gap-2">
              <MessageSquare class="h-5 w-5 text-signal" />
              <div>
                <h2 class="text-base font-semibold">Message command queue</h2>
                <p class="text-sm text-graphite">Threads across orders, special orders, classes, and support work.</p>
              </div>
            </div>
            <label class="relative block min-w-64">
              <Search class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-graphite" />
              <input
                v-model="comms.query"
                class="focus-ring h-10 w-full rounded-md border border-slate-200 bg-white pl-9 pr-3 text-sm"
                type="search"
                placeholder="Search messages"
              >
            </label>
          </div>

          <div v-if="comms.filteredThreads.length" class="divide-y divide-slate-100">
            <article
              v-for="thread in comms.filteredThreads"
              :key="thread.id"
              class="grid gap-3 px-4 py-4 md:grid-cols-[minmax(0,1fr)_auto]"
            >
              <div>
                <div class="flex flex-wrap items-center gap-2">
                  <p class="font-semibold text-ink">{{ thread.subject }}</p>
                  <StatusPill :label="thread.status" :tone="statusTone(thread.status)" />
                </div>
                <p class="mt-1 text-sm text-graphite">
                  {{ thread.reference || `Thread #${thread.id}` }} · {{ thread.kind }} · {{ thread.target_type || "target" }} #{{ thread.target_id || "n/a" }}
                </p>
              </div>
              <p class="text-sm text-graphite md:text-right">
                Last message<br>
                <span class="font-medium text-ink">{{ formatDate(thread.last_message_at) }}</span>
              </p>
            </article>
          </div>

          <div v-else class="p-4">
            <EmptyState
              :icon="MessageSquare"
              title="No threads found"
              message="Adjust the search or refresh after the backend is connected."
            />
          </div>
        </section>
      </div>

      <aside class="space-y-4">
        <section class="rounded-md border border-slate-200 bg-white p-4">
          <div class="flex items-center justify-between gap-3">
            <div class="flex items-center gap-2">
              <Megaphone class="h-5 w-5 text-signal" />
              <h2 class="text-base font-semibold">Broadcast composer</h2>
            </div>
            <button
              class="focus-ring inline-flex h-9 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold"
              type="button"
              :disabled="comms.isMutating"
              @click="comms.sendBroadcast().catch(() => undefined)"
            >
              <BellRing class="h-4 w-4" />
              Queue
            </button>
          </div>

          <div class="mt-4 space-y-3">
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Title</span>
              <input
                v-model="comms.broadcastComposer.title"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                type="text"
              >
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Message</span>
              <RichTextEditor
                v-model="comms.broadcastComposer.message"
              />
            </label>
            <div class="grid gap-2 sm:grid-cols-2">
              <label class="flex min-h-10 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm">
                <input
                  v-model="comms.broadcastComposer.require_acknowledgement"
                  type="checkbox"
                >
                Require ack
              </label>
              <label class="flex min-h-10 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm">
                <input
                  v-model="comms.broadcastComposer.is_blocking"
                  type="checkbox"
                >
                Blocking
              </label>
            </div>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Priority</span>
              <select
                v-model="comms.broadcastComposer.priority"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
              >
                <option value="normal">Normal</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </label>
          </div>

          <h3 class="mt-5 text-sm font-semibold text-ink">Recent broadcasts</h3>
          <div class="mt-4 space-y-3">
            <article
              v-for="broadcast in comms.broadcasts"
              :key="broadcast.id"
              class="rounded-md border border-slate-200 p-3"
            >
              <p class="font-semibold text-ink">{{ broadcast.title }}</p>
              <div class="mt-1 text-sm leading-5 text-graphite" v-html="broadcast.message" />
              <div class="mt-3 flex flex-wrap gap-2">
                <StatusPill :label="broadcast.is_active === false ? 'inactive' : 'active'" :tone="broadcast.is_active === false ? 'neutral' : 'success'" />
                <StatusPill v-if="broadcast.is_blocking" label="blocking" tone="warning" />
                <StatusPill v-if="broadcast.require_acknowledgement" label="ack required" tone="warning" />
              </div>
            </article>
          </div>
        </section>

        <section class="rounded-md border border-slate-200 bg-white p-4">
          <div class="flex items-center gap-2">
            <Mail class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold">Mass email composer</h2>
          </div>

          <div class="mt-4 space-y-3">
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Campaign title</span>
              <input
                v-model="comms.campaignComposer.title"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                type="text"
              >
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Subject</span>
              <input
                v-model="comms.campaignComposer.subject"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                type="text"
              >
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Rich body</span>
              <RichTextEditor
                v-model="comms.campaignComposer.body"
              />
            </label>
            <div class="rounded-md border border-slate-200 bg-slate-50 p-3">
              <p class="text-xs font-semibold uppercase text-graphite">Preview</p>
              <div class="mt-2 rounded-md bg-white p-3 text-sm leading-6 text-ink" v-html="comms.campaignComposer.body" />
            </div>
            <div class="grid gap-2 sm:grid-cols-2">
              <button
                class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold"
                type="button"
                :disabled="comms.isMutating"
                @click="comms.createCampaign(false).catch(() => undefined)"
              >
                Save draft
              </button>
              <button
                class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md bg-ink px-3 text-sm font-semibold text-white"
                type="button"
                :disabled="comms.isMutating"
                @click="comms.createCampaign(true).catch(() => undefined)"
              >
                Send test
              </button>
            </div>
          </div>

          <h3 class="mt-5 text-sm font-semibold text-ink">Campaigns</h3>
          <div class="mt-4 space-y-3">
            <article
              v-for="campaign in comms.campaigns"
              :key="campaign.id"
              class="rounded-md border border-slate-200 p-3"
            >
              <div class="flex items-start justify-between gap-3">
                <div>
                  <p class="font-semibold text-ink">{{ campaign.title }}</p>
                  <p class="mt-1 text-sm text-graphite">{{ campaign.subject }}</p>
                </div>
                <StatusPill :label="campaign.status" :tone="statusTone(campaign.status)" />
              </div>
              <p class="mt-2 text-xs text-graphite">
                {{ campaign.email_type || "campaign" }} · {{ formatDate(campaign.scheduled_time || campaign.sent_time || campaign.created_at) }}
              </p>
              <button
                class="focus-ring mt-3 inline-flex h-9 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold"
                type="button"
                :disabled="comms.isMutating"
                @click="comms.sendCampaignTest(campaign.id).catch(() => undefined)"
              >
                Send test
              </button>
            </article>
          </div>
        </section>
      </aside>
    </section>

    <!-- ─── Announcements ─────────────────────────────────────────────────── -->
    <section class="space-y-4">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex items-center gap-2">
          <Megaphone class="h-5 w-5 text-signal" />
          <h2 class="text-lg font-semibold text-ink">Announcements</h2>
          <span v-if="announcements.length" class="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-semibold text-graphite">
            {{ announcements.length }}
          </span>
        </div>
        <button
          class="focus-ring inline-flex items-center gap-2 rounded-md bg-ink px-4 py-2.5 text-sm font-semibold text-white"
          type="button"
          @click="showAnnForm = !showAnnForm"
        >
          <Megaphone class="h-4 w-4" />
          {{ showAnnForm ? "Cancel" : "New Announcement" }}
        </button>
      </div>

      <p v-if="annError" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">{{ annError }}</p>
      <p v-if="annSuccess" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">{{ annSuccess }}</p>

      <!-- Create form -->
      <div v-if="showAnnForm" class="rounded-lg border border-slate-200 bg-white p-5 space-y-4">
        <h3 class="text-sm font-semibold text-ink">Create announcement</h3>
        <label class="block">
          <span class="text-xs font-semibold uppercase text-graphite">Title</span>
          <input
            v-model="annForm.title"
            type="text"
            class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
            placeholder="Announcement title"
          />
        </label>
        <label class="block">
          <span class="text-xs font-semibold uppercase text-graphite">Message</span>
          <RichTextEditor v-model="annForm.message" />
        </label>
        <div class="grid gap-3 sm:grid-cols-2">
          <label class="block">
            <span class="text-xs font-semibold uppercase text-graphite">Category</span>
            <select v-model="annForm.category" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm">
              <option v-for="cat in CATEGORIES" :key="cat" :value="cat">{{ cat.charAt(0).toUpperCase() + cat.slice(1) }}</option>
            </select>
          </label>
          <div>
            <span class="text-xs font-semibold uppercase text-graphite">Target roles</span>
            <div class="mt-1.5 flex flex-wrap gap-2">
              <label
                v-for="r in ROLES"
                :key="r"
                class="inline-flex cursor-pointer items-center gap-1.5 rounded-md border border-slate-200 px-2.5 py-1 text-xs font-medium"
                :class="annForm.target_roles?.includes(r) ? 'border-signal bg-signal/5 text-signal' : 'text-graphite hover:bg-slate-50'"
              >
                <input
                  type="checkbox"
                  class="sr-only"
                  :value="r"
                  :checked="annForm.target_roles?.includes(r)"
                  @change="(e) => {
                    const checked = (e.target as HTMLInputElement).checked;
                    annForm.target_roles = checked
                      ? [...(annForm.target_roles ?? []), r]
                      : (annForm.target_roles ?? []).filter((x) => x !== r);
                  }"
                />
                {{ r }}
              </label>
            </div>
          </div>
        </div>
        <div class="flex flex-wrap gap-4">
          <label class="inline-flex cursor-pointer items-center gap-2 text-sm">
            <input v-model="annForm.pinned" type="checkbox" class="h-4 w-4 rounded border-slate-300" />
            Pin announcement
          </label>
          <label class="inline-flex cursor-pointer items-center gap-2 text-sm">
            <input v-model="annForm.require_acknowledgement" type="checkbox" class="h-4 w-4 rounded border-slate-300" />
            Require acknowledgement
          </label>
        </div>
        <div class="flex gap-3">
          <button
            class="focus-ring inline-flex items-center gap-2 rounded-md bg-ink px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
            type="button"
            :disabled="annMutating || !annForm.title || !annForm.message"
            @click="createAnnouncement"
          >
            <Loader2 v-if="annMutating" class="h-4 w-4 animate-spin" />
            <BellRing v-else class="h-4 w-4" />
            Broadcast
          </button>
        </div>
      </div>

      <!-- Announcements list -->
      <div v-if="annLoading && !announcements.length" class="space-y-3">
        <div v-for="n in 2" :key="n" class="animate-pulse rounded-lg border border-slate-200 bg-white p-5">
          <div class="h-4 w-1/3 rounded bg-slate-200" />
          <div class="mt-3 h-3 w-2/3 rounded bg-slate-100" />
        </div>
      </div>

      <div v-else-if="!annLoading && !announcements.length" class="rounded-lg border border-slate-200 bg-white p-8 text-center">
        <EmptyState :icon="Megaphone" title="No announcements" message="Create your first platform announcement above." />
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="ann in announcements"
          :key="ann.id"
          class="flex items-start gap-4 rounded-lg border bg-white px-5 py-4"
          :class="ann.is_pinned ? 'border-signal/30 bg-signal/[0.02]' : 'border-slate-200'"
        >
          <div class="min-w-0 flex-1">
            <div class="flex flex-wrap items-center gap-2">
              <Pin v-if="ann.is_pinned" class="h-3.5 w-3.5 shrink-0 text-signal" />
              <p class="font-semibold text-ink">{{ ann.title }}</p>
              <StatusPill :label="ann.category" :tone="categoryTone(ann.category)" />
            </div>
            <p class="mt-1 text-sm text-graphite line-clamp-2" v-html="ann.message" />
            <p class="mt-2 text-xs text-slate-400">
              {{ annDate(ann.created_at) }}
              <span v-if="ann.created_by_name"> · {{ ann.created_by_name }}</span>
              · {{ ann.view_count }} views
            </p>
          </div>
          <div class="flex shrink-0 items-center gap-1">
            <button
              class="focus-ring rounded-md p-2 text-graphite hover:bg-slate-100"
              type="button"
              :title="ann.is_pinned ? 'Unpin' : 'Pin'"
              :disabled="annMutating"
              @click="togglePin(ann)"
            >
              <PinOff v-if="ann.is_pinned" class="h-4 w-4" />
              <Pin v-else class="h-4 w-4" />
            </button>
            <template v-if="pendingDeleteAnnId === ann.id">
              <button class="focus-ring rounded-md bg-rose-600 px-2 py-1 text-xs font-semibold text-white hover:bg-rose-700" type="button" @click="deleteAnnouncement(ann)">Confirm</button>
              <button class="focus-ring rounded-md border border-slate-200 px-2 py-1 text-xs text-graphite hover:bg-slate-50" type="button" @click="pendingDeleteAnnId = null">Cancel</button>
            </template>
            <button
              v-else
              class="focus-ring rounded-md p-2 text-graphite hover:bg-rose-50 hover:text-berry"
              type="button"
              title="Delete"
              :disabled="annMutating"
              @click="deleteAnnouncement(ann)"
            >
              <Trash2 class="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- ─── Email Templates ───────────────────────────────────────────────── -->
    <section class="space-y-4">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex items-center gap-2">
          <FileText class="h-5 w-5 text-signal" />
          <h2 class="text-lg font-semibold text-ink">Email Templates</h2>
          <span v-if="templates.length" class="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-semibold text-graphite">{{ templates.length }}</span>
        </div>
        <button
          class="focus-ring inline-flex items-center gap-2 rounded-md border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold"
          type="button"
          @click="showTplForm = !showTplForm"
        >
          <Plus class="h-4 w-4" />
          {{ showTplForm ? "Cancel" : "New Template" }}
        </button>
      </div>

      <p v-if="tplError" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">{{ tplError }}</p>
      <p v-if="tplSuccess" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">{{ tplSuccess }}</p>

      <!-- Create form -->
      <div v-if="showTplForm" class="rounded-lg border border-slate-200 bg-white p-5 space-y-3">
        <h3 class="text-sm font-semibold text-ink">New email template</h3>
        <label class="block">
          <span class="text-xs font-semibold uppercase text-graphite">Template name</span>
          <input v-model="tplForm.name" type="text" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" placeholder="e.g. Welcome email" />
        </label>
        <label class="block">
          <span class="text-xs font-semibold uppercase text-graphite">Subject line</span>
          <input v-model="tplForm.subject" type="text" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" placeholder="Email subject" />
        </label>
        <label class="block">
          <span class="text-xs font-semibold uppercase text-graphite">Body</span>
          <RichTextEditor v-model="tplForm.body" />
        </label>
        <label class="inline-flex cursor-pointer items-center gap-2 text-sm">
          <input v-model="tplForm.is_global" type="checkbox" class="h-4 w-4 rounded border-slate-300" />
          Global (available to all admins)
        </label>
        <button
          class="focus-ring inline-flex items-center gap-2 rounded-md bg-ink px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
          type="button"
          :disabled="tplMutating || !tplForm.name || !tplForm.subject || !tplForm.body"
          @click="createTemplate"
        >
          <Loader2 v-if="tplMutating" class="h-4 w-4 animate-spin" />
          Save Template
        </button>
      </div>

      <!-- Templates list -->
      <div v-if="tplLoading && !templates.length" class="space-y-2">
        <div v-for="n in 3" :key="n" class="animate-pulse rounded-lg border border-slate-200 bg-white p-4">
          <div class="h-3 w-1/4 rounded bg-slate-200" />
          <div class="mt-2 h-3 w-1/2 rounded bg-slate-100" />
        </div>
      </div>

      <div v-else-if="!templates.length" class="rounded-lg border border-slate-200 bg-white p-8 text-center">
        <EmptyState :icon="FileText" title="No templates yet" message="Create a reusable template to speed up campaign drafting." />
      </div>

      <div v-else class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="tpl in templates"
          :key="tpl.id"
          class="flex flex-col gap-3 rounded-lg border border-slate-200 bg-white p-4"
        >
          <div class="flex items-start justify-between gap-2">
            <div class="min-w-0">
              <p class="font-semibold text-ink">{{ tpl.name }}</p>
              <p class="mt-0.5 truncate text-xs text-graphite">{{ tpl.subject }}</p>
            </div>
            <span v-if="tpl.is_global" class="shrink-0 rounded-full bg-slate-100 px-2 py-0.5 text-xs text-graphite">Global</span>
          </div>
          <div class="flex-1 rounded-md bg-slate-50 p-2 text-xs leading-5 text-graphite line-clamp-3" v-html="tpl.body" />
          <div class="flex gap-2">
            <button
              class="focus-ring flex-1 rounded-md border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-ink hover:bg-slate-50"
              type="button"
              @click="applyTemplate(tpl)"
            >
              Use in campaign
            </button>
            <template v-if="pendingDeleteTplId === tpl.id">
              <button class="focus-ring rounded-md bg-rose-600 px-2 py-1 text-xs font-semibold text-white hover:bg-rose-700" type="button" @click="deleteTemplate(tpl)">Confirm</button>
              <button class="focus-ring rounded-md border border-slate-200 px-2 py-1 text-xs text-graphite hover:bg-slate-50" type="button" @click="pendingDeleteTplId = null">Cancel</button>
            </template>
            <button
              v-else
              class="focus-ring rounded-md p-2 text-graphite hover:bg-rose-50 hover:text-berry"
              type="button"
              :disabled="tplMutating"
              @click="deleteTemplate(tpl)"
            >
              <Trash2 class="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- ─── Campaign Analytics ────────────────────────────────────────────── -->
    <section class="space-y-4">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex items-center gap-2">
          <BarChart3 class="h-5 w-5 text-signal" />
          <h2 class="text-lg font-semibold text-ink">Campaign Analytics</h2>
        </div>
        <div class="flex flex-wrap items-end gap-3">
          <label class="block">
            <span class="text-xs font-semibold text-graphite">From</span>
            <input v-model="analyticsStart" type="date" class="focus-ring mt-0.5 h-9 rounded-md border border-slate-200 bg-white px-3 text-sm" />
          </label>
          <label class="block">
            <span class="text-xs font-semibold text-graphite">To</span>
            <input v-model="analyticsEnd" type="date" class="focus-ring mt-0.5 h-9 rounded-md border border-slate-200 bg-white px-3 text-sm" />
          </label>
          <button
            class="focus-ring inline-flex items-center gap-2 rounded-md border border-slate-200 bg-white px-4 py-2 text-sm font-semibold disabled:opacity-60"
            type="button"
            :disabled="analyticsLoading"
            @click="fetchAnalytics"
          >
            <Loader2 v-if="analyticsLoading" class="h-4 w-4 animate-spin" />
            <RefreshCw v-else class="h-4 w-4" />
            Run
          </button>
        </div>
      </div>

      <p v-if="analyticsError" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">{{ analyticsError }}</p>

      <div v-if="analyticsLoading" class="animate-pulse rounded-lg border border-slate-200 bg-white p-6">
        <div class="h-4 w-1/3 rounded bg-slate-200" />
        <div class="mt-4 space-y-3">
          <div v-for="n in 4" :key="n" class="h-3 rounded bg-slate-100" />
        </div>
      </div>

      <div v-else-if="!analyticsRows.length" class="rounded-lg border border-slate-200 bg-white p-8 text-center">
        <EmptyState :icon="BarChart3" title="No data" message="Select a date range and click Run, or send some campaigns first." />
      </div>

      <div v-else class="rounded-lg border border-slate-200 bg-white overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-200 text-sm">
          <thead class="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-graphite">
            <tr>
              <th class="px-3 py-2">Campaign</th>
              <th class="px-3 py-2 text-right">Sent</th>
              <th class="px-3 py-2 text-right">Opens</th>
              <th class="px-3 py-2 text-right">Open rate</th>
              <th class="px-3 py-2 text-right">Clicks</th>
              <th class="px-3 py-2 text-right">Click rate</th>
              <th class="px-3 py-2 text-right">Unsub rate</th>
              <th class="px-3 py-2 text-right">Date</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="row in analyticsRows" :key="row.campaign_id" class="hover:bg-slate-50">
              <td class="px-3 py-2 font-medium text-ink">{{ row.title }}</td>
              <td class="px-3 py-2 text-right text-graphite">{{ row.recipients.toLocaleString() }}</td>
              <td class="px-3 py-2 text-right text-graphite">{{ row.opens.toLocaleString() }}</td>
              <td class="px-3 py-2 text-right font-semibold" :class="row.open_rate >= 20 ? 'text-signal' : 'text-ink'">
                {{ fmtRate(row.open_rate) }}
              </td>
              <td class="px-3 py-2 text-right text-graphite">{{ row.clicks.toLocaleString() }}</td>
              <td class="px-3 py-2 text-right font-semibold" :class="row.click_rate >= 5 ? 'text-signal' : 'text-ink'">
                {{ fmtRate(row.click_rate) }}
              </td>
              <td class="px-3 py-2 text-right" :class="row.unsubscribe_rate >= 2 ? 'text-berry' : 'text-graphite'">
                {{ fmtRate(row.unsubscribe_rate) }}
              </td>
              <td class="px-3 py-2 text-right text-graphite">{{ fmtDate(row.sent_time) }}</td>
            </tr>
          </tbody>
        </table>

        <!-- Summary row -->
        <div class="border-t border-slate-200 bg-slate-50 px-5 py-3 text-xs text-graphite">
          {{ analyticsRows.length }} campaigns ·
          avg open rate {{ fmtRate(analyticsRows.reduce((s, r) => s + r.open_rate, 0) / analyticsRows.length) }} ·
          avg click rate {{ fmtRate(analyticsRows.reduce((s, r) => s + r.click_rate, 0) / analyticsRows.length) }}
        </div>
      </div>
    </section>
  </div>
</template>
