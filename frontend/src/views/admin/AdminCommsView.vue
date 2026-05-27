<script setup lang="ts">
import { onMounted, ref } from "vue";
import {
  BellRing,
  CheckCircle2,
  Loader2,
  Mail,
  Megaphone,
  MessageSquare,
  Pin,
  PinOff,
  RefreshCw,
  Search,
  Trash2,
} from "@lucide/vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import RichTextEditor from "@/components/forms/RichTextEditor.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useAdminCommsStore } from "@/stores/adminComms";
import { announcementsApi, type AnnouncementRecord, type CreateAnnouncementPayload } from "@/api/announcements";

const comms = useAdminCommsStore();

// ─── Announcements ──────────────────────────────────────────────────────────
const announcements = ref<AnnouncementRecord[]>([]);
const annLoading = ref(false);
const annError = ref("");
const annSuccess = ref("");
const showAnnForm = ref(false);
const annMutating = ref(false);

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
  if (!confirm(`Delete "${item.title}"?`)) return;
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

onMounted(() => {
  comms.hydrate().catch(() => undefined);
  fetchAnnouncements();
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
        class="min-h-32 rounded-md border p-4 shadow-panel"
        :class="metricToneClasses[metric.tone]"
      >
        <p class="text-sm font-medium text-graphite">{{ metric.label }}</p>
        <p class="mt-3 text-3xl font-semibold text-ink">{{ metric.value }}</p>
        <p class="mt-2 text-sm leading-5 text-graphite">{{ metric.detail }}</p>
      </div>
    </section>

    <section class="grid gap-6 xl:grid-cols-[minmax(0,1.2fr)_minmax(380px,0.8fr)]">
      <div class="space-y-6">
        <section class="rounded-md border border-slate-200 bg-white shadow-panel">
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

      <aside class="space-y-6">
        <section class="rounded-md border border-slate-200 bg-white p-4 shadow-panel">
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

        <section class="rounded-md border border-slate-200 bg-white p-4 shadow-panel">
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
      <div v-if="showAnnForm" class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel space-y-4">
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
        <div v-for="n in 2" :key="n" class="animate-pulse rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
          <div class="h-4 w-1/3 rounded bg-slate-200" />
          <div class="mt-3 h-3 w-2/3 rounded bg-slate-100" />
        </div>
      </div>

      <div v-else-if="!annLoading && !announcements.length" class="rounded-lg border border-slate-200 bg-white p-8 text-center shadow-panel">
        <EmptyState :icon="Megaphone" title="No announcements" message="Create your first platform announcement above." />
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="ann in announcements"
          :key="ann.id"
          class="flex items-start gap-4 rounded-lg border bg-white px-5 py-4 shadow-panel"
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
            <button
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
  </div>
</template>
