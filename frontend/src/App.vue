<script setup lang="ts">
import { onErrorCaptured, ref } from "vue";
import { RouterView, useRouter } from "vue-router";
import ToastContainer from "@/components/ui/ToastContainer.vue";

const router = useRouter();
const fatalError = ref<{ message: string } | null>(null);

onErrorCaptured((err: unknown) => {
  const e = err as Error;
  fatalError.value = { message: e?.message ?? String(err) };
  return false; // stop propagation — we own rendering now
});

function reload() {
  fatalError.value = null;
  router.go(0);
}
</script>

<template>
  <div v-if="fatalError" class="flex min-h-screen flex-col items-center justify-center bg-slate-50 px-6 text-center">
    <div class="w-full max-w-md rounded-2xl border border-rose-200 bg-white p-8 shadow-lg">
      <div class="mx-auto mb-4 flex size-14 items-center justify-center rounded-full bg-rose-100">
        <svg class="size-7 text-rose-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
        </svg>
      </div>
      <h1 class="text-xl font-bold text-ink">Something went wrong</h1>
      <p class="mt-2 text-sm text-graphite">An unexpected error occurred. Please reload or return home.</p>
      <p class="mt-3 rounded-lg bg-slate-50 px-3 py-2 text-left font-mono text-xs text-rose-700 break-words">
        {{ fatalError.message }}
      </p>
      <div class="mt-6 flex justify-center gap-3">
        <button
          class="rounded-lg bg-berry px-5 py-2.5 text-sm font-semibold text-white hover:bg-rose-700"
          @click="reload"
        >Reload page</button>
        <a href="/" class="rounded-lg border border-slate-200 px-5 py-2.5 text-sm font-semibold text-graphite hover:bg-slate-50">
          Go home
        </a>
      </div>
    </div>
  </div>

  <template v-else>
    <RouterView />
    <ToastContainer />
  </template>
</template>
