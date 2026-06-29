<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { CheckCircle2, XCircle, Loader2 } from "@lucide/vue";

const route = useRoute();

const status = computed(() => String(route.query.status ?? "success"));
const ref_ = computed(() => String(route.query.ref ?? ""));

const isSuccess = computed(() => status.value === "success");

// Give the webhook a moment then show the appropriate state.
const loading = ref(true);
onMounted(() => {
  setTimeout(() => { loading.value = false; }, 1800);
});
</script>

<template>
  <div class="flex min-h-[60vh] items-center justify-center px-4 py-16">
    <div class="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-10 text-center shadow-sm">

      <!-- Loading -->
      <template v-if="loading">
        <Loader2 class="mx-auto h-10 w-10 animate-spin text-slate-400" />
        <p class="mt-4 text-sm text-graphite">Confirming your payment…</p>
      </template>

      <!-- Success -->
      <template v-else-if="isSuccess">
        <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100">
          <CheckCircle2 class="h-8 w-8 text-emerald-600" />
        </div>
        <h1 class="mt-5 text-2xl font-semibold text-ink">Payment confirmed</h1>
        <p class="mt-2 text-sm text-graphite">
          Your payment has been received. You'll get a receipt by email shortly.
        </p>
        <p v-if="ref_" class="mt-3 font-mono text-xs text-slate-400">Ref: {{ ref_ }}</p>
        <div class="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
          <RouterLink
            to="/dashboard"
            class="focus-ring inline-flex items-center justify-center rounded-lg bg-signal px-6 py-2.5 text-sm font-semibold text-white hover:bg-signal/90 transition-colors"
          >
            Go to dashboard
          </RouterLink>
          <RouterLink
            to="/client/billing"
            class="focus-ring inline-flex items-center justify-center rounded-lg border border-slate-200 px-6 py-2.5 text-sm font-semibold text-ink hover:bg-slate-50 transition-colors"
          >
            View billing
          </RouterLink>
        </div>
      </template>

      <!-- Cancelled -->
      <template v-else>
        <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-slate-100">
          <XCircle class="h-8 w-8 text-slate-500" />
        </div>
        <h1 class="mt-5 text-2xl font-semibold text-ink">Payment cancelled</h1>
        <p class="mt-2 text-sm text-graphite">
          Your payment was not completed. No charge has been made.
        </p>
        <div class="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
          <RouterLink
            to="/client/billing"
            class="focus-ring inline-flex items-center justify-center rounded-lg bg-signal px-6 py-2.5 text-sm font-semibold text-white hover:bg-signal/90 transition-colors"
          >
            Back to billing
          </RouterLink>
        </div>
      </template>

    </div>
  </div>
</template>
