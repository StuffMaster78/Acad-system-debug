<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Clock,
  XCircle,
} from "@lucide/vue";
import type { OrderLifecycle, OrderSummary } from "@/types/orders";
import type { CancellationRequest } from "@/types/cancellation";
import { cancellationRequestsApi } from "@/api/cancellationRequests";
import { useUiStore } from "@/stores/ui";
import { useOrderStore } from "@/stores/orders";

// ─── Props ────────────────────────────────────────────────────────────────────

const props = defineProps<{
  orderId: string;
  order: OrderSummary | null;
  lifecycle: OrderLifecycle | null;
  paymentStatus?: string | null;
}>();

// ─── State ────────────────────────────────────────────────────────────────────

const ui = useUiStore();
const orders = useOrderStore();

const request = ref<CancellationRequest | null>(null);
const loading = ref(false);
const busy = ref(false);
const showForm = ref(false);
const reason = ref("");
const submitError = ref("");

// ─── Derived ──────────────────────────────────────────────────────────────────

// Statuses from which the client can request cancellation
const CANCELLABLE_STATUSES = new Set([
  "in_progress",
  "on_hold",
  "revision_requested",
  "ready_for_staffing",
  "pending_writer_acceptance",
]);

const isOrderPaid = computed(() =>
  props.paymentStatus === "paid" || props.paymentStatus === "partially_paid",
);

// Writer has started when status moves past ready_for_staffing/pending_writer_acceptance
const writerHasStarted = computed(() =>
  ["in_progress", "on_hold", "revision_requested"].includes(props.order?.status ?? ""),
);

const canRequestCancel = computed(() =>
  CANCELLABLE_STATUSES.has(props.order?.status ?? ""),
);

const isPendingCancellation = computed(() =>
  props.order?.status === "pending_cancellation",
);

// Show the panel if the client can cancel OR already has a pending request
const showPanel = computed(() =>
  canRequestCancel.value || isPendingCancellation.value,
);

function fmt(val: string | null | undefined): string {
  if (!val) return "—";
  const n = Number(val);
  return isNaN(n) ? val : `$${n.toFixed(2)}`;
}

// ─── Load pending request ─────────────────────────────────────────────────────

async function loadRequest() {
  if (!isPendingCancellation.value) return;
  loading.value = true;
  try {
    const { data } = await cancellationRequestsApi.getCurrent(props.orderId);
    request.value = data;
  } catch {
    request.value = null;
  } finally {
    loading.value = false;
  }
}

onMounted(loadRequest);

// ─── Submit request ───────────────────────────────────────────────────────────

async function submitRequest() {
  if (!reason.value.trim()) return;
  busy.value = true;
  submitError.value = "";
  try {
    const { data } = await cancellationRequestsApi.create(
      props.orderId,
      reason.value.trim(),
    );
    request.value = data;
    showForm.value = false;
    reason.value = "";
    await orders.fetchOrder(props.orderId);
    ui.toast("Cancellation request submitted. Staff will review shortly.", "success");
  } catch (e: unknown) {
    const detail = (e as { response?: { data?: { detail?: string } } })
      ?.response?.data?.detail;
    submitError.value = detail ?? "Failed to submit request. Please try again.";
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <div v-if="showPanel" class="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">

    <!-- ── Pending review state ─────────────────────────────── -->
    <template v-if="isPendingCancellation">
      <div class="flex items-center justify-between border-b border-amber-200 bg-amber-50 px-5 py-4">
        <div class="flex items-center gap-2">
          <Clock class="h-4 w-4 text-amber-600" />
          <span class="text-sm font-semibold text-amber-900">Cancellation under review</span>
        </div>
      </div>

      <div v-if="loading" class="px-5 py-6 text-sm text-graphite">Loading request details…</div>

      <div v-else-if="request" class="px-5 py-4 space-y-4">
        <p class="text-sm text-graphite">
          Your cancellation request has been received and is being reviewed by our team.
          You will be notified once a decision is made.
        </p>

        <!-- Request details card -->
        <div class="rounded-lg border border-slate-100 bg-slate-50 p-4 space-y-3 text-sm">
          <div>
            <p class="text-xs font-medium text-graphite">Your reason</p>
            <p class="mt-0.5 text-ink">{{ request.reason }}</p>
          </div>

          <!-- Forfeiture breakdown -->
          <div class="grid grid-cols-3 gap-3 pt-2 border-t border-slate-200">
            <div>
              <p class="text-xs font-medium text-graphite">Forfeiture</p>
              <p class="mt-0.5 font-semibold" :class="Number(request.forfeiture_pct) > 0 ? 'text-berry' : 'text-emerald-700'">
                {{ request.forfeiture_pct }}%
              </p>
            </div>
            <div>
              <p class="text-xs font-medium text-graphite">Amount forfeited</p>
              <p class="mt-0.5 font-semibold text-ink">{{ fmt(request.forfeiture_amount) }}</p>
            </div>
            <div>
              <p class="text-xs font-medium text-graphite">Estimated refund</p>
              <p class="mt-0.5 font-semibold text-emerald-700">{{ fmt(request.refund_amount) }}</p>
            </div>
          </div>

          <p class="text-xs text-graphite border-t border-slate-200 pt-2">
            Final refund amount may be adjusted by staff. Submitted
            {{ new Date(request.requested_at).toLocaleDateString("en", { dateStyle: "medium" }) }}.
          </p>
        </div>
      </div>

      <div v-else class="px-5 py-4 text-sm text-graphite">
        Your cancellation request is pending staff review.
      </div>
    </template>

    <!-- ── Request form ─────────────────────────────────────── -->
    <template v-else-if="canRequestCancel">

      <!-- Collapsed trigger -->
      <button
        class="flex w-full items-center justify-between px-5 py-4 text-left hover:bg-slate-50 transition-colors"
        @click="showForm = !showForm"
      >
        <div class="flex items-center gap-2">
          <XCircle class="h-4 w-4 text-graphite" />
          <span class="text-sm font-medium text-graphite">Need to cancel this order?</span>
        </div>
        <component :is="showForm ? ChevronUp : ChevronDown" class="h-4 w-4 text-graphite" />
      </button>

      <!-- Expanded form -->
      <Transition name="slide-down">
        <div v-if="showForm" class="border-t border-slate-200 p-5 space-y-4">

          <!-- Context-aware cancellation notice -->
          <div v-if="!isOrderPaid" class="flex items-start gap-3 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm">
            <CheckCircle2 class="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" />
            <div class="text-emerald-900 space-y-1">
              <p class="font-semibold">No charges — this order hasn't been paid</p>
              <p class="text-emerald-800 text-xs">
                Since payment has not been made, cancelling this order incurs no fees and
                no refund is issued. The order will simply be closed.
              </p>
            </div>
          </div>
          <div v-else-if="!writerHasStarted" class="flex items-start gap-3 rounded-lg border border-blue-200 bg-blue-50 p-3 text-sm">
            <CheckCircle2 class="mt-0.5 h-4 w-4 shrink-0 text-blue-600" />
            <div class="text-blue-900 space-y-1">
              <p class="font-semibold">Full refund likely — work hasn't started yet</p>
              <p class="text-blue-800 text-xs">
                Your order is waiting for a writer to be assigned. Since no work has begun,
                a full refund is typically approved. Staff will confirm and process your refund.
              </p>
            </div>
          </div>
          <div v-else class="flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm">
            <AlertTriangle class="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />
            <div class="text-amber-900 space-y-1">
              <p class="font-semibold">Partial forfeiture may apply — work is in progress</p>
              <p class="text-amber-800 text-xs">
                Your writer has already started working. A portion of your payment may be
                retained based on how much work has been completed. Staff will review your
                request and confirm the final refund amount before any money is returned.
              </p>
            </div>
          </div>

          <!-- Reason field -->
          <label class="block">
            <span class="text-sm font-medium text-graphite">
              Reason for cancellation <span class="text-rose-400">*</span>
            </span>
            <textarea
              v-model.trim="reason"
              rows="3"
              class="focus-ring mt-1.5 w-full rounded-md border border-slate-200 px-3 py-2 text-sm resize-none"
              placeholder="Please describe why you need to cancel this order…"
            />
          </label>

          <p v-if="submitError" class="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-berry">
            {{ submitError }}
          </p>

          <!-- Actions -->
          <div class="flex flex-wrap gap-2">
            <button
              class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-rose-300 bg-rose-50 px-4 py-2 text-sm font-semibold text-berry disabled:opacity-60 hover:bg-rose-100"
              :disabled="busy || !reason.trim()"
              @click="submitRequest"
            >
              <XCircle class="h-4 w-4" />
              {{ busy ? "Submitting…" : "Request cancellation" }}
            </button>
            <button
              class="focus-ring inline-flex items-center rounded-md border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-graphite hover:bg-slate-50"
              @click="showForm = false; reason = ''; submitError = ''"
            >
              Keep my order
            </button>
          </div>

        </div>
      </Transition>
    </template>

  </div>
</template>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.18s ease;
  overflow: hidden;
}
.slide-down-enter-from,
.slide-down-leave-to {
  max-height: 0;
  opacity: 0;
}
.slide-down-enter-to,
.slide-down-leave-from {
  max-height: 600px;
  opacity: 1;
}
</style>
