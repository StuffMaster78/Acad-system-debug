<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterLink, useRoute } from "vue-router";
import {
  ArrowLeft,
  CheckCircle2,
  ExternalLink,
  Loader2,
  RotateCcw,
  Send,
  Siren,
} from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { supportApi } from "@/api/support";
import { useSupportWorkspaceStore } from "@/stores/supportWorkspace";
import type { SupportTicketRecord } from "@/types/support";

type TicketMessage = {
  id?: number;
  body?: string;
  sender?: string;
  sender_display?: string;
  created_at?: string;
};

const route = useRoute();
const support = useSupportWorkspaceStore();

const ticketId = computed(() => Number(route.params.id));
const ticket = ref<SupportTicketRecord | null>(null);
const isLoading = ref(true);
const loadError = ref("");
const messages = ref<TicketMessage[]>([]);
const isLoadingMessages = ref(false);
const replyBody = ref("");
const isSending = ref(false);
const sendError = ref("");
const sendNotice = ref("");

function statusTone(status?: string | null): "danger" | "warning" | "success" | "neutral" {
  const s = (status ?? "").toLowerCase();
  if (s.includes("critical") || s.includes("escalated") || s.includes("breach")) return "danger";
  if (s.includes("open") || s.includes("progress") || s.includes("pending") || s.includes("high")) return "warning";
  if (s.includes("closed") || s.includes("resolved")) return "success";
  return "neutral";
}

function formatDate(value?: string | null) {
  if (!value) return "—";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

async function loadTicket() {
  isLoading.value = true;
  loadError.value = "";
  try {
    const { data } = await supportApi.getTicket(ticketId.value);
    ticket.value = data;
  } catch {
    loadError.value = "Could not load this ticket. It may not exist or you may not have access.";
  } finally {
    isLoading.value = false;
  }
}

async function loadMessages() {
  isLoadingMessages.value = true;
  try {
    const { data } = await supportApi.ticketMessages(ticketId.value);
    const raw = Array.isArray(data) ? data : (data as { results?: TicketMessage[] }).results ?? [];
    messages.value = raw as TicketMessage[];
  } catch {
    // messages endpoint may not exist yet — silence gracefully
  } finally {
    isLoadingMessages.value = false;
  }
}

async function sendReply() {
  if (!replyBody.value.trim()) return;
  isSending.value = true;
  sendError.value = "";
  sendNotice.value = "";
  try {
    await supportApi.addMessage(ticketId.value, replyBody.value.trim());
    sendNotice.value = "Reply sent.";
    replyBody.value = "";
    await loadMessages();
  } catch {
    sendError.value = "Could not send reply. Please try again.";
  } finally {
    isSending.value = false;
  }
}

async function doClose() {
  await support.closeTicket(ticketId.value);
  if (ticket.value) ticket.value = { ...ticket.value, status: "closed" };
}

async function doReopen() {
  await support.reopenTicket(ticketId.value);
  if (ticket.value) ticket.value = { ...ticket.value, status: "open" };
}

async function doEscalate() {
  await support.escalateTicket(ticketId.value);
  if (ticket.value) ticket.value = { ...ticket.value, is_escalated: true, priority: "critical" };
}

onMounted(() => {
  void loadTicket();
  void loadMessages();
});
</script>

<template>
  <div class="space-y-6">
    <RouterLink
      class="focus-ring inline-flex items-center gap-2 rounded-md px-2 py-1 text-sm font-semibold text-graphite hover:bg-slate-100"
      to="/support/tickets"
    >
      <ArrowLeft class="h-4 w-4" />
      Ticket queue
    </RouterLink>

    <section
      v-if="isLoading"
      class="rounded-lg border border-slate-200 bg-white p-8 text-sm text-graphite shadow-panel"
    >
      Loading ticket…
    </section>

    <div
      v-else-if="loadError"
      class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
    >
      {{ loadError }}
    </div>

    <template v-else-if="ticket">
      <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-start lg:justify-between">
        <div class="min-w-0 flex-1">
          <p class="text-sm font-semibold uppercase tracking-wide text-signal">Support ticket #{{ ticket.id }}</p>
          <h1 class="mt-2 text-3xl font-semibold text-ink">{{ ticket.title }}</h1>
          <p v-if="ticket.description" class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
            {{ ticket.description }}
          </p>
        </div>
        <div class="flex flex-wrap gap-2 lg:justify-end">
          <StatusPill :label="ticket.status" :tone="statusTone(ticket.status)" />
          <StatusPill :label="ticket.priority" :tone="statusTone(ticket.priority)" />
          <StatusPill v-if="ticket.is_escalated" label="escalated" tone="danger" />
          <StatusPill v-if="ticket.has_sla" label="SLA" tone="warning" />
        </div>
      </section>

      <div v-if="support.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
        {{ support.error }}
      </div>
      <div v-if="support.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
        {{ support.notice }}
      </div>

      <div class="grid gap-6 xl:grid-cols-[360px_1fr]">
        <aside class="space-y-5">
          <section class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
            <h2 class="text-base font-semibold text-ink">Details</h2>
            <dl class="mt-4 space-y-3 text-sm">
              <div class="flex items-start justify-between gap-3">
                <dt class="shrink-0 text-graphite">Category</dt>
                <dd class="text-right font-medium capitalize text-ink">{{ ticket.category || "general" }}</dd>
              </div>
              <div class="flex items-start justify-between gap-3">
                <dt class="shrink-0 text-graphite">Requester</dt>
                <dd class="text-right font-medium text-ink">{{ ticket.created_by_name || "Unknown" }}</dd>
              </div>
              <div class="flex items-start justify-between gap-3">
                <dt class="shrink-0 text-graphite">Assigned to</dt>
                <dd class="text-right font-medium text-ink">{{ ticket.assigned_to_name || "Unassigned" }}</dd>
              </div>
              <div class="flex items-start justify-between gap-3">
                <dt class="shrink-0 text-graphite">Created</dt>
                <dd class="text-right font-medium text-ink">{{ formatDate(ticket.created_at) }}</dd>
              </div>
              <div class="flex items-start justify-between gap-3">
                <dt class="shrink-0 text-graphite">Updated</dt>
                <dd class="text-right font-medium text-ink">{{ formatDate(ticket.updated_at) }}</dd>
              </div>
            </dl>

            <div v-if="ticket.object_id" class="mt-5 border-t border-slate-200 pt-4">
              <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-graphite">Linked record</p>
              <RouterLink
                class="focus-ring inline-flex items-center gap-2 rounded-md border border-slate-200 px-3 py-2 text-sm font-semibold text-ink hover:bg-slate-50"
                to="/support/orders"
              >
                <ExternalLink class="h-4 w-4" />
                Order #{{ ticket.object_id }}
              </RouterLink>
            </div>
          </section>

          <section class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
            <h2 class="text-base font-semibold text-ink">Actions</h2>
            <div class="mt-4 flex flex-col gap-2">
              <button
                v-if="ticket.status !== 'closed'"
                class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-slate-300 px-4 py-2.5 text-sm font-semibold text-ink disabled:cursor-not-allowed disabled:opacity-60"
                type="button"
                :disabled="support.isMutating"
                @click="doClose"
              >
                <Loader2 v-if="support.isMutating" class="h-4 w-4 animate-spin" />
                <CheckCircle2 v-else class="h-4 w-4 text-signal" />
                Close ticket
              </button>
              <button
                v-else
                class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-slate-300 px-4 py-2.5 text-sm font-semibold text-ink disabled:cursor-not-allowed disabled:opacity-60"
                type="button"
                :disabled="support.isMutating"
                @click="doReopen"
              >
                <RotateCcw class="h-4 w-4" />
                Reopen ticket
              </button>
              <button
                v-if="!ticket.is_escalated"
                class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-rose-200 px-4 py-2.5 text-sm font-semibold text-rose-700 disabled:cursor-not-allowed disabled:opacity-60"
                type="button"
                :disabled="support.isMutating"
                @click="doEscalate"
              >
                <Siren class="h-4 w-4" />
                Escalate
              </button>
            </div>
          </section>
        </aside>

        <div class="rounded-lg border border-slate-200 bg-white shadow-panel">
          <div class="border-b border-slate-200 px-5 py-4">
            <h2 class="text-base font-semibold text-ink">Conversation</h2>
            <p class="mt-1 text-sm text-graphite">Internal notes and replies on this ticket.</p>
          </div>

          <div class="min-h-48 space-y-3 bg-slate-50 p-5">
            <p v-if="isLoadingMessages" class="text-sm text-graphite">Loading messages…</p>
            <p v-else-if="!messages.length" class="text-sm text-graphite">
              No messages yet. Add the first reply below.
            </p>
            <article
              v-for="(msg, idx) in messages"
              v-else
              :key="msg.id ?? idx"
              class="rounded-lg border border-slate-200 bg-white p-4"
            >
              <div class="flex items-center justify-between gap-3">
                <p class="text-xs font-semibold text-ink">
                  {{ msg.sender_display ?? msg.sender ?? "Support" }}
                </p>
                <p class="text-xs text-graphite">{{ formatDate(msg.created_at) }}</p>
              </div>
              <p class="mt-2 whitespace-pre-wrap text-sm leading-6 text-graphite">{{ msg.body }}</p>
            </article>
          </div>

          <div class="border-t border-slate-200 p-5">
            <div
              v-if="sendError"
              class="mb-3 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900"
            >
              {{ sendError }}
            </div>
            <div
              v-if="sendNotice"
              class="mb-3 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-900"
            >
              {{ sendNotice }}
            </div>
            <form class="flex flex-col gap-3" @submit.prevent="sendReply">
              <textarea
                v-model.trim="replyBody"
                class="focus-ring min-h-28 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                placeholder="Write a reply or internal note for this ticket…"
              />
              <button
                class="focus-ring inline-flex items-center justify-center gap-2 self-start rounded-md bg-signal px-4 py-2.5 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
                type="submit"
                :disabled="isSending || !replyBody.trim()"
              >
                <Loader2 v-if="isSending" class="h-4 w-4 animate-spin" />
                <Send v-else class="h-4 w-4" />
                Send reply
              </button>
            </form>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
