<script setup lang="ts">
import { onMounted } from "vue";
import MessageThread from "@/components/messages/MessageThread.vue";
import { useCommunicationsStore } from "@/stores/communications";

const comms = useCommunicationsStore();

onMounted(() => {
  comms.loadInboxThreads().catch(() => undefined);
});
</script>

<template>
  <div class="space-y-6">
    <section class="border-b border-slate-200 pb-6">
      <p class="text-sm font-semibold uppercase tracking-wide text-signal">Editor</p>
      <h1 class="mt-2 text-3xl font-semibold text-ink">Messages</h1>
      <p class="mt-2 max-w-2xl text-sm leading-6 text-graphite">
        Revision and QA conversations with writers and clients.
      </p>
    </section>

    <div v-if="comms.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ comms.error }}
    </div>

    <MessageThread role="editor" order-base-url="/editor/qa" />
  </div>
</template>
