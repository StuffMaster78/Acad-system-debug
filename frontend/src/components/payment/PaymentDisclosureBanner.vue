<script setup lang="ts">
import { ShieldCheck } from "@lucide/vue";
import { usePortalContextStore } from "@/stores/portalContext";

const props = withDefaults(
  defineProps<{
    /** "pre" = full notice shown before pay button; "post" = shorter confirmation copy */
    variant?: "pre" | "post";
  }>(),
  { variant: "pre" },
);

const portalCtx = usePortalContextStore();
</script>

<template>
  <div
    v-if="portalCtx.paymentDisclosure"
    class="flex items-start gap-2.5 rounded-md border border-slate-200 bg-slate-50 px-3.5 py-3 text-xs text-graphite"
  >
    <ShieldCheck class="mt-0.5 h-3.5 w-3.5 shrink-0 text-slate-400" aria-hidden="true" />
    <p>
      {{ variant === "pre"
          ? portalCtx.paymentDisclosure.pre_payment_notice
          : portalCtx.paymentDisclosure.text }}
    </p>
  </div>
</template>
