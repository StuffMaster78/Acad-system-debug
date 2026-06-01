<script setup lang="ts">
import { useRouter } from "vue-router";
import { ArrowLeft } from "@lucide/vue";
import OrderDetailPage from "@/components/orders/detail/OrderDetailPage.vue";

const router = useRouter();
</script>

<template>
  <div class="space-y-4">
    <button
      class="inline-flex items-center gap-1.5 text-sm text-graphite hover:text-ink"
      @click="router.push('/editor/qa')"
    >
      <ArrowLeft class="h-3.5 w-3.5" />
      Back to QA queue
    </button>
    <!-- Tabs: details, files, messages, quality, timeline -->
    <OrderDetailPage role="editor" />
  </div>
</template>
