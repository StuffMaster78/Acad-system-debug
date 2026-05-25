<script setup lang="ts">
import { onMounted } from "vue";
import {
  BellRing,
  Mail,
  Megaphone,
  MessageSquare,
  RefreshCw,
  Search,
} from "@lucide/vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import RichTextEditor from "@/components/forms/RichTextEditor.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useAdminCommsStore } from "@/stores/adminComms";

const comms = useAdminCommsStore();

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
  </div>
</template>
