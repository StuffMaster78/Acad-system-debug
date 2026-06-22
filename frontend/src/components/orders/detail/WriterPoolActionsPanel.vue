<template>
  <div v-if="isPoolOrder" class="rounded-xl border border-signal/30 bg-signal/5 p-5 space-y-4">
    <div class="flex items-start justify-between gap-3">
      <div>
        <p class="text-sm font-semibold text-ink">This order is open for expressions of interest</p>
        <p class="mt-0.5 text-xs text-graphite">
          Read the full brief, then express interest. Compensation is set by your writer tier.
        </p>
      </div>
      <span class="shrink-0 rounded-full bg-signal/10 px-2.5 py-0.5 text-xs font-semibold text-signal">Pool order</span>
    </div>

    <!-- Eligibility warning -->
    <div
      v-if="eligibility && !eligibility.is_eligible"
      class="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800"
    >
      {{ eligibility.reason ?? "You may not be eligible for this order." }}
    </div>

    <!-- Compensation preview (read-only) -->
    <div v-if="eligibility?.suggested_bid_price || eligibility?.rate_breakdown" class="rounded-lg border border-slate-200 bg-white px-4 py-3">
      <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-2">Your compensation</p>
      <div class="flex flex-wrap gap-x-6 gap-y-1 text-sm">
        <div v-if="eligibility?.suggested_bid_price" class="flex items-baseline gap-1.5">
          <span class="text-2xl font-bold text-ink">${{ eligibility.suggested_bid_price }}</span>
          <span class="text-xs text-graphite">estimated</span>
        </div>
        <div v-if="eligibility?.rate_breakdown?.per_page" class="flex items-center gap-1 text-xs text-graphite">
          ${{ eligibility.rate_breakdown.per_page }}/page
          <template v-if="parseFloat(eligibility.rate_breakdown.per_slide ?? '0') > 0">
            · ${{ eligibility.rate_breakdown.per_slide }}/slide
          </template>
        </div>
      </div>
      <p class="mt-1.5 text-xs text-graphite">Rate is determined by your writer tier and cannot be negotiated.</p>
    </div>

    <!-- Interest form -->
    <div v-if="showForm" class="space-y-3 border-t border-signal/20 pt-4">
      <label class="block">
        <span class="text-xs font-medium text-graphite">Message to admin <span class="font-normal text-slate-400">(optional)</span></span>
        <textarea
          v-model="message"
          class="focus-ring mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          rows="3"
          placeholder="Why are you the right fit? Any relevant experience, certifications, or notes for the admin…"
        />
      </label>

      <p v-if="error" class="text-xs text-rose-600">{{ error }}</p>

      <div class="flex gap-2 pt-1">
        <button
          class="focus-ring inline-flex items-center gap-2 rounded-md bg-signal px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
          type="button"
          :disabled="submitting"
          @click="submit"
        >
          <Loader2 v-if="submitting" class="h-3.5 w-3.5 animate-spin" />
          <Send v-else class="h-3.5 w-3.5" />
          Express interest
        </button>
        <button
          class="focus-ring rounded-md border border-slate-300 px-4 py-2.5 text-sm font-semibold text-ink"
          type="button"
          @click="showForm = false"
        >
          Cancel
        </button>
      </div>
    </div>

    <!-- CTA buttons (when form is closed) -->
    <div v-else class="flex flex-wrap gap-3">
      <button
        class="focus-ring inline-flex items-center gap-2 rounded-md bg-signal px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
        type="button"
        :disabled="loadingEligibility || (eligibility !== null && !eligibility.is_eligible)"
        @click="showForm = true"
      >
        <Loader2 v-if="loadingEligibility" class="h-3.5 w-3.5 animate-spin" />
        <ThumbsUp v-else class="h-3.5 w-3.5" />
        Express interest
      </button>

      <button
        v-if="eligibility?.can_take !== false"
        class="focus-ring inline-flex items-center gap-2 rounded-md border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-ink disabled:opacity-60"
        type="button"
        :disabled="takingOrder || (eligibility !== null && !eligibility.is_eligible)"
        @click="takeOrder"
      >
        <Loader2 v-if="takingOrder" class="h-3.5 w-3.5 animate-spin" />
        <CheckCircle2 v-else class="h-3.5 w-3.5" />
        Take order directly
      </button>
    </div>

    <p v-if="takeError" class="text-xs text-rose-600">{{ takeError }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { CheckCircle2, Loader2, Send, ThumbsUp } from "@lucide/vue";
import { useOrderStore } from "@/stores/orders";
import { useWriterWorkspaceStore } from "@/stores/writerWorkspace";
import { writerApi } from "@/api/writer";

const props = defineProps<{ orderId: string | number }>();

const router = useRouter();
const orders = useOrderStore();
const workspace = useWriterWorkspaceStore();

const order = computed(() => orders.selectedOrder);

const isPoolOrder = computed(() =>
  order.value?.visibility_mode === "pool" ||
  order.value?.status === "ready_for_staffing"
);

const showForm = ref(false);
const message = ref("");
const submitting = ref(false);
const error = ref<string | null>(null);
const loadingEligibility = ref(false);
const takingOrder = ref(false);
const takeError = ref<string | null>(null);

type EligibilityResult = Awaited<ReturnType<typeof writerApi.orderEligibility>>["data"];
const eligibility = ref<EligibilityResult | null>(null);

async function loadEligibility() {
  if (!props.orderId || eligibility.value) return;
  loadingEligibility.value = true;
  try {
    const { data } = await writerApi.orderEligibility(Number(props.orderId));
    eligibility.value = data;
  } catch { /* non-critical */ } finally {
    loadingEligibility.value = false;
  }
}

async function submit() {
  submitting.value = true;
  error.value = null;
  try {
    await workspace.expressInterest(Number(props.orderId), message.value);
    if (workspace.error) {
      error.value = workspace.error;
    } else {
      showForm.value = false;
      message.value = "";
      await orders.fetchOrder(String(props.orderId));
    }
  } catch {
    error.value = "Something went wrong. Please try again.";
  } finally {
    submitting.value = false;
  }
}

async function takeOrder() {
  takingOrder.value = true;
  takeError.value = null;
  try {
    await workspace.takeOrder(Number(props.orderId));
    if (workspace.error) {
      takeError.value = workspace.error;
    } else {
      await orders.fetchOrder(String(props.orderId));
      router.push("/writer/assignments");
    }
  } catch {
    takeError.value = "Something went wrong. Please try again.";
  } finally {
    takingOrder.value = false;
  }
}

onMounted(() => {
  void loadEligibility();
});
</script>
