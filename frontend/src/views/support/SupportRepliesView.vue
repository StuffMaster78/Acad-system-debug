<script setup lang="ts">
import { onMounted } from "vue";
import { MessageSquareText, Plus, RefreshCw } from "@lucide/vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import RichTextEditor from "@/components/forms/RichTextEditor.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useSupportWorkspaceStore } from "@/stores/supportWorkspace";

const support = useSupportWorkspaceStore();

function formatDate(value?: string | null) {
  if (!value) return "";
  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(new Date(value));
}

onMounted(() => {
  if (!support.savedReplies.length) support.hydrate().catch(() => undefined);
});
</script>

<template>
  <div class="space-y-4">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Support</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Saved replies</h1>
        <p class="mt-2 max-w-2xl text-sm text-graphite">
          Pre-written response templates for common support scenarios. Compose a new reply or use one as a starting point.
        </p>
      </div>
      <button
        class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold disabled:opacity-60"
        type="button"
        :disabled="support.isLoading"
        @click="support.hydrate().catch(() => undefined)"
      >
        <RefreshCw class="h-4 w-4" :class="support.isLoading ? 'animate-spin' : ''" />
        Refresh
      </button>
    </section>

    <p v-if="support.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ support.error }}
    </p>
    <p v-if="support.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
      {{ support.notice }}
    </p>

    <div class="grid gap-6 xl:grid-cols-[380px_1fr]">
      <section class="rounded-lg border border-slate-200 bg-white">
        <div class="flex items-center justify-between gap-3 border-b border-slate-200 px-5 py-4">
          <div class="flex items-center gap-2">
            <Plus class="h-4 w-4 text-signal" />
            <h2 class="text-base font-semibold text-ink">New reply</h2>
          </div>
        </div>

        <div class="space-y-4 p-5">
          <label class="block">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Title</span>
            <input
              v-model="support.replyComposer.title"
              class="focus-ring mt-1.5 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
              type="text"
              placeholder="e.g. File access reset"
            />
          </label>
          <label class="block">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Category</span>
            <input
              v-model="support.replyComposer.category"
              class="focus-ring mt-1.5 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
              type="text"
              placeholder="e.g. billing, files, order"
            />
          </label>
          <label class="block">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Body</span>
            <RichTextEditor v-model="support.replyComposer.body" class="mt-1.5" />
          </label>
          <button
            class="focus-ring inline-flex w-full items-center justify-center gap-2 rounded-md bg-ink px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
            type="button"
            :disabled="support.isMutating || !support.replyComposer.title"
            @click="support.createSavedReply().catch(() => undefined)"
          >
            <MessageSquareText class="h-4 w-4" />
            Save reply
          </button>
        </div>
      </section>

      <section>
        <div v-if="!support.savedReplies.length && !support.isLoading" class="rounded-lg border border-slate-200 bg-white px-6 py-12">
          <EmptyState
            :icon="MessageSquareText"
            title="No saved replies yet"
            message="Create your first saved reply using the composer on the left."
          />
        </div>

        <div v-else class="grid gap-4 sm:grid-cols-2">
          <article
            v-for="reply in support.savedReplies"
            :key="reply.id"
            class="rounded-lg border border-slate-200 bg-white p-5"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0 flex-1">
                <p class="truncate font-semibold text-ink">{{ reply.title }}</p>
                <p class="mt-0.5 text-xs text-graphite">
                  {{ reply.category || "general" }}
                  <span v-if="reply.created_at"> · {{ formatDate(reply.created_at) }}</span>
                </p>
              </div>
              <StatusPill
                :label="reply.is_active === false ? 'inactive' : 'active'"
                :tone="reply.is_active === false ? 'neutral' : 'success'"
              />
            </div>
            <div class="mt-3 rounded-md bg-slate-50 px-3 py-3 text-sm leading-6 text-graphite" v-html="reply.body" />
          </article>
        </div>
      </section>
    </div>
  </div>
</template>
