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
  <div class="space-y-4">
    <section class="border-b border-slate-200 pb-6">
      <p class="text-sm font-semibold uppercase tracking-wide text-signal">Writer</p>
      <h1 class="mt-2 text-3xl font-semibold text-ink">Messages</h1>
      <p class="mt-2 max-w-2xl text-sm leading-6 text-graphite">
        Order-scoped conversations with clients, editors, and support.
      </p>
    </section>

    <div v-if="comms.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ comms.error }}
    </div>

    <MessageThread role="writer" order-base-url="/writer/orders" />
  </div>
</template>
