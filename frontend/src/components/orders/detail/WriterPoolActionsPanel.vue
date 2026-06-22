<template>
  <div v-if="isPoolOrder" class="rounded-xl border border-signal/30 bg-signal/5 p-5 space-y-4">
    <div class="flex items-start justify-between gap-3">
      <div>
        <p class="text-sm font-semibold text-ink">This order is open for bidding</p>
        <p class="mt-0.5 text-xs text-graphite">
          Submit a bid with your price and delivery time, or take the order directly if you're ready to start.
        </p>
      </div>
      <span class="shrink-0 rounded-full bg-signal/10 px-2.5 py-0.5 text-xs font-semibold text-signal">Pool order</span>
    </div>

    <!-- Eligibility warning -->
    <div
      v-if="eligibility && !eligibility.is_eligible"
      class="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800"
    >
      {{ eligibility.reason ?? "You may not be eligible to take this order." }}
    </div>

    <!-- Bid form -->
    <div v-if="showBidForm" class="space-y-3 border-t border-signal/20 pt-4">
      <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Your Bid</p>

      <div class="flex items-center justify-between text-xs text-graphite">
        <span v-if="eligibility?.rate_breakdown?.per_page">
          Your rate: ${{ eligibility.rate_breakdown.per_page }}/page
          <template v-if="parseFloat(eligibility.rate_breakdown.per_slide ?? '0') > 0">
            · ${{ eligibility.rate_breakdown.per_slide }}/slide
          </template>
        </span>
        <span v-if="eligibility?.suggested_bid_price" class="text-signal font-medium">
          Suggested: ${{ eligibility.suggested_bid_price }}
        </span>
      </div>

      <div class="grid grid-cols-2 gap-3">
        <label class="block">
          <span class="text-xs font-medium text-graphite">Your price ($) *</span>
          <div class="relative mt-1">
            <DollarSign class="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
            <input
              v-model="bids.bidForm.price"
              type="number" min="1" step="0.01"
              placeholder="e.g. 45.00"
              class="focus-ring h-9 w-full rounded-md border border-slate-300 pl-8 pr-3 text-sm"
            />
          </div>
        </label>
        <label class="block">
          <span class="text-xs font-medium text-graphite">Delivery time *</span>
          <select v-model.number="bids.bidForm.delivery_hours" class="focus-ring mt-1 h-9 w-full rounded-md border border-slate-300 px-3 text-sm bg-white">
            <option :value="6">6 hours</option>
            <option :value="12">12 hours</option>
            <option :value="24">24 hours</option>
            <option :value="48">48 hours</option>
            <option :value="72">3 days</option>
            <option :value="120">5 days</option>
          </select>
        </label>
      </div>

      <label class="block">
        <span class="text-xs font-medium text-graphite">Pitch message (optional)</span>
        <textarea
          v-model="bids.bidForm.pitch"
          class="focus-ring mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          rows="2"
          placeholder="Why are you the best fit? Keep it brief."
        />
      </label>

      <p v-if="bids.error" class="text-xs text-rose-600">{{ bids.error }}</p>

      <div class="flex gap-2 pt-1">
        <button
          class="focus-ring inline-flex items-center gap-2 rounded-md bg-signal px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
          type="button"
          :disabled="bids.isSaving || !bids.bidForm.price"
          @click="submitBid"
        >
          <Loader2 v-if="bids.isSaving" class="h-3.5 w-3.5 animate-spin" />
          <Send v-else class="h-3.5 w-3.5" />
          Submit bid
        </button>
        <button
          class="focus-ring rounded-md border border-slate-300 px-4 py-2.5 text-sm font-semibold text-ink"
          type="button"
          @click="showBidForm = false"
        >
          Cancel
        </button>
      </div>
    </div>

    <!-- Action buttons (when bid form is closed) -->
    <div v-else class="flex flex-wrap gap-3">
      <button
        class="focus-ring inline-flex items-center gap-2 rounded-md bg-signal px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
        type="button"
        :disabled="loadingEligibility"
        @click="openBidForm"
      >
        <Loader2 v-if="loadingEligibility" class="h-3.5 w-3.5 animate-spin" />
        <DollarSign v-else class="h-3.5 w-3.5" />
        Submit a bid
      </button>

      <button
        v-if="eligibility?.can_take !== false"
        class="focus-ring inline-flex items-center gap-2 rounded-md border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-ink disabled:opacity-60"
        type="button"
        :disabled="takingOrder"
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
import { CheckCircle2, DollarSign, Loader2, Send } from "@lucide/vue";
import { useOrderStore } from "@/stores/orders";
import { useBidsStore } from "@/stores/bids";
import { writerApi } from "@/api/writer";
import { useWriterWorkspaceStore } from "@/stores/writerWorkspace";

const props = defineProps<{ orderId: string | number }>();

const router = useRouter();
const orders = useOrderStore();
const bids = useBidsStore();
const workspace = useWriterWorkspaceStore();

const order = computed(() => orders.selectedOrder);

const isPoolOrder = computed(() =>
  order.value?.visibility_mode === "pool" ||
  order.value?.status === "ready_for_staffing"
);

const showBidForm = ref(false);
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
    if (data.suggested_bid_price && !bids.bidForm.price) {
      bids.bidForm.price = data.suggested_bid_price;
    }
  } catch { /* non-critical */ } finally {
    loadingEligibility.value = false;
  }
}

function openBidForm() {
  bids.openBidForm(Number(props.orderId));
  showBidForm.value = true;
  void loadEligibility();
}

async function submitBid() {
  await bids.submitBid();
  if (!bids.error) {
    showBidForm.value = false;
    await orders.fetchOrder(String(props.orderId));
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
