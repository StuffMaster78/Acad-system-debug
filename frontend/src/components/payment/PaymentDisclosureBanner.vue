<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { ShieldCheck } from "@lucide/vue";
import { websitesApi } from "@/api/websites";
import { useAuthStore } from "@/stores/auth";
import { usePortalContextStore } from "@/stores/portalContext";

const props = withDefaults(
  defineProps<{
    /** "pre" = full notice shown before pay button; "post" = shorter confirmation copy */
    variant?: "pre" | "post";
    context?: string;
    referenceType?: string;
    referenceId?: string | number;
    modelValue?: boolean;
  }>(),
  { variant: "pre" },
);
const emit = defineEmits<{
  (e: "update:modelValue", value: boolean): void;
}>();

const portalCtx = usePortalContextStore();
const auth = useAuthStore();
const isAcknowledged = ref(false);
const isRecording = ref(false);

const disclosure = computed(() => portalCtx.paymentDisclosure);
const requiresAck = computed(() =>
  props.variant === "pre" && Boolean(disclosure.value?.requires_acknowledgement),
);
const noticeText = computed(() =>
  props.variant === "pre"
    ? disclosure.value?.pre_payment_notice
    : disclosure.value?.text,
);

async function recordDisclosure(event: "shown" | "acknowledged") {
  if (event === "acknowledged") {
    isAcknowledged.value = true;
    emit("update:modelValue", true);
  }
  if (!auth.isAuthenticated || auth.isPreviewSession || !disclosure.value) return;
  isRecording.value = true;
  try {
    await websitesApi.acknowledgePaymentDisclosure({
      event,
      context: props.context || props.variant,
      reference_type: props.referenceType,
      reference_id: props.referenceId,
    });
  } catch {
    // Disclosure tracking is best-effort; never block the payment UI.
  } finally {
    isRecording.value = false;
  }
}

onMounted(() => {
  if (disclosure.value) recordDisclosure("shown");
});

watch(
  [requiresAck, disclosure],
  () => {
    if (!disclosure.value || !requiresAck.value) {
      emit("update:modelValue", true);
    } else {
      emit("update:modelValue", isAcknowledged.value);
    }
  },
  { immediate: true },
);
</script>

<template>
  <div
    v-if="disclosure"
    class="flex items-start gap-2.5 rounded-md border border-slate-200 bg-slate-50 px-3.5 py-3 text-xs text-graphite"
  >
    <ShieldCheck class="mt-0.5 h-3.5 w-3.5 shrink-0 text-slate-400" aria-hidden="true" />
    <div class="min-w-0 flex-1">
      <p>{{ noticeText }}</p>
      <p v-if="disclosure.support_contact" class="mt-1">
        Billing support: <span class="font-medium text-ink">{{ disclosure.support_contact }}</span>
      </p>
      <label v-if="requiresAck" class="mt-2 flex items-start gap-2 text-ink">
        <input
          v-model="isAcknowledged"
          type="checkbox"
          class="mt-0.5 rounded accent-berry"
          :disabled="isRecording || isAcknowledged"
          @change="isAcknowledged && recordDisclosure('acknowledged')"
        />
        <span>I understand what may appear on my card or bank statement.</span>
      </label>
    </div>
  </div>
</template>
