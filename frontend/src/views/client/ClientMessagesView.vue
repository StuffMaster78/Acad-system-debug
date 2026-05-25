<script setup lang="ts">
import { computed, onMounted, reactive } from "vue";
import { RouterLink } from "vue-router";
import { Inbox, Loader2, RefreshCw, Send } from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useCommunicationsStore } from "@/stores/communications";

const communications = useCommunicationsStore();
const composer = reactive({ body: "" });

const activeOrderUrl = computed(() => {
  if (!communications.activeThread) return "/client/orders";
  if (communications.activeThread.target_type !== "order") return "/client/orders";
  return `/client/orders/${communications.activeThread.target_id}`;
});

function dateLabel(value?: string | null) {
  if (!value) return "No activity";
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function unreadCount(thread: { metadata?: Record<string, unknown> }) {
  const raw = thread.metadata?.unread_count;
  return typeof raw === "number" ? raw : 0;
}

async function sendMessage() {
  if (!composer.body.trim()) return;
  await communications.sendMessage(composer.body.trim());
  composer.body = "";
}

onMounted(() => {
  communications.loadInboxThreads().catch(() => undefined);
});
</script>

<template>
  <div class="space-y-6">
    <section class="flex flex-col gap-3 border-b border-slate-200 pb-6 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Client</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Messages</h1>
        <p class="mt-2 max-w-2xl text-sm leading-6 text-graphite">
          Order-scoped conversations with writers and support.
        </p>
      </div>
      <button
        class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-300 px-4 text-sm font-semibold text-ink disabled:cursor-not-allowed disabled:opacity-60"
        type="button"
        :disabled="communications.isLoading"
        @click="communications.loadInboxThreads()"
      >
        <RefreshCw class="h-4 w-4" />
        Refresh
      </button>
    </section>

    <div v-if="communications.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ communications.error }}
    </div>
    <div v-if="communications.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
      {{ communications.notice }}
    </div>

    <section class="grid min-h-[620px] gap-5 xl:grid-cols-[360px_minmax(0,1fr)]">
      <aside class="rounded-lg border border-slate-200 bg-white shadow-panel">
        <div class="flex min-h-14 items-center justify-between border-b border-slate-200 px-4">
          <h2 class="text-base font-semibold text-ink">Inbox</h2>
          <Inbox class="h-4 w-4 text-slate-400" />
        </div>
        <div v-if="communications.isLoading && !communications.inboxThreads.length" class="p-4 text-sm text-graphite">
          Loading threads...
        </div>
        <div v-else-if="!communications.inboxThreads.length" class="p-4 text-sm text-graphite">
          No message threads yet.
        </div>
        <div v-else class="divide-y divide-slate-100">
          <button
            v-for="thread in communications.inboxThreads"
            :key="thread.id"
            class="focus-ring grid w-full gap-2 px-4 py-4 text-left hover:bg-slate-50"
            :class="thread.id === communications.activeThread?.id ? 'bg-slate-50' : 'bg-white'"
            type="button"
            @click="communications.selectThread(thread)"
          >
            <div class="flex items-start justify-between gap-3">
              <p class="line-clamp-2 text-sm font-semibold text-ink">
                #{{ thread.target_id }} {{ thread.subject || thread.reference }}
              </p>
              <StatusPill v-if="unreadCount(thread)" :label="String(unreadCount(thread))" tone="success" />
            </div>
            <div class="flex flex-wrap items-center gap-2 text-xs text-graphite">
              <span>{{ thread.kind }}</span>
              <span>{{ dateLabel(thread.last_message_at) }}</span>
            </div>
          </button>
        </div>
      </aside>

      <main class="flex min-h-[620px] flex-col rounded-lg border border-slate-200 bg-white shadow-panel">
        <div class="flex flex-col gap-3 border-b border-slate-200 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 class="text-lg font-semibold text-ink">
              {{ communications.activeThread?.subject || "Select a thread" }}
            </h2>
            <p v-if="communications.activeThread" class="mt-1 text-sm text-graphite">
              {{ communications.activeThread.kind }} · {{ communications.activeThread.status }}
            </p>
          </div>
          <RouterLink
            v-if="communications.activeThread"
            class="focus-ring inline-flex items-center justify-center rounded-md border border-slate-300 px-3 py-2 text-sm font-semibold text-ink hover:bg-slate-50"
            :to="activeOrderUrl"
          >
            Open order
          </RouterLink>
        </div>

        <div class="min-h-0 flex-1 space-y-3 overflow-y-auto bg-slate-50 p-5">
          <p v-if="communications.isLoading" class="text-sm text-graphite">Loading messages...</p>
          <p v-else-if="!communications.activeThread" class="text-sm text-graphite">
            Choose a message thread to continue.
          </p>
          <p v-else-if="!communications.messages.length" class="text-sm text-graphite">
            No messages in this thread yet.
          </p>
          <article
            v-for="message in communications.messages"
            v-else
            :key="message.id"
            class="max-w-3xl rounded-lg border border-slate-200 bg-white p-4"
          >
            <div class="flex flex-wrap items-center justify-between gap-3">
              <p class="text-sm font-semibold text-ink">{{ message.sender_display }}</p>
              <span class="text-xs text-graphite">{{ dateLabel(message.created_at) }}</span>
            </div>
            <p class="mt-3 whitespace-pre-wrap text-sm leading-6 text-graphite">{{ message.body }}</p>
          </article>
        </div>

        <form class="border-t border-slate-200 p-4" @submit.prevent="sendMessage">
          <textarea
            v-model.trim="composer.body"
            class="focus-ring min-h-24 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            placeholder="Write a message"
          />
          <div class="mt-3 flex justify-end">
            <button
              class="focus-ring inline-flex items-center justify-center gap-2 rounded-md bg-signal px-4 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
              type="submit"
              :disabled="communications.isSending || !communications.activeThread || !composer.body"
            >
              <Loader2 v-if="communications.isSending" class="h-4 w-4 animate-spin" />
              <Send v-else class="h-4 w-4" />
              Send
            </button>
          </div>
        </form>
      </main>
    </section>
  </div>
</template>
