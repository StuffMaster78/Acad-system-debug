<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { RouterLink, useRoute } from "vue-router";
import {
  AlertTriangle,
  ArrowLeft,
  Download,
  FileUp,
  Gift,
  LifeBuoy,
  Loader2,
  MessageSquare,
  RefreshCw,
  RotateCcw,
  Send,
  Star,
  ThumbsUp,
  XCircle,
} from "@lucide/vue";
import { filesApi, type FilePurpose, type FileVisibility } from "@/api/files";
import { reviewsApi } from "@/api/reviews";
import type { Review } from "@/types/reviews";
import { supportApi } from "@/api/support";
import { tipsApi, type TipRecord } from "@/api/tips";
import StatusPill from "@/components/ui/StatusPill.vue";
import OrderTimeline from "@/components/orders/OrderTimeline.vue";
import { useCommunicationsStore } from "@/stores/communications";
import { useFilesStore } from "@/stores/files";
import { useOrderStore } from "@/stores/orders";

const route = useRoute();
const orders = useOrderStore();
const files = useFilesStore();
const communications = useCommunicationsStore();
const orderId = computed(() => String(route.params.id));

const revisionForm = reactive({
  reason: "",
  scope_summary: "",
  is_within_original_scope: true,
});

const cancelForm = reactive({
  reason: "",
  refund_destination: "wallet" as "wallet" | "external",
  notes: "",
});

const disputeForm = reactive({ reason: "" });

const supportTicketForm = reactive({ title: "", description: "" });
const isTicketSending = ref(false);
const ticketError = ref("");
const ticketNotice = ref("");

const fileForm = reactive<{
  file: File | null;
  purpose: FilePurpose;
  visibility: FileVisibility;
}>({
  file: null,
  purpose: "order_reference",
  visibility: "order_participants",
});

const messageForm = reactive({
  body: "",
});

const order = computed(() => orders.selectedOrder);
const lifecycle = computed(() => orders.selectedLifecycle);

const canApprove = computed(() => {
  const s = order.value?.status;
  return s === "delivered" || s === "awaiting_approval";
});

const canRequestRevision = computed(() => lifecycle.value?.is_revision_window_open ?? false);

const isTerminal = computed(() => {
  const s = order.value?.status;
  return s === "completed" || s === "cancelled" || s === "archived";
});

const canCancel = computed(() => !isTerminal.value);

const TERMINAL_STATUSES = ["completed", "reviewed", "rated", "approved", "archived"];

const canTip = computed(() => {
  const s = order.value?.status;
  return (
    TERMINAL_STATUSES.includes(s ?? "") &&
    lifecycle.value?.current_writer_id != null
  );
});

const existingReview = ref<Review | null>(null);
const reviewLoading = ref(false);
const reviewRating = ref(0);
const reviewHoverRating = ref(0);
const reviewTitle = ref("");
const reviewBody = ref("");
const reviewPublic = ref(true);
const reviewSubmitting = ref(false);
const reviewError = ref("");

const canReview = computed(() =>
  TERMINAL_STATUSES.includes(order.value?.status ?? "") &&
  lifecycle.value?.current_writer_id != null &&
  existingReview.value === null &&
  !reviewLoading.value,
);

async function fetchExistingReview() {
  reviewLoading.value = true;
  try {
    const { data } = await reviewsApi.forOrder(orderId.value);
    existingReview.value = data;
  } catch {
    existingReview.value = null;
  } finally {
    reviewLoading.value = false;
  }
}

async function submitReview() {
  reviewError.value = "";
  if (!reviewRating.value) {
    reviewError.value = "Select a star rating before submitting.";
    return;
  }
  reviewSubmitting.value = true;
  try {
    const { data } = await reviewsApi.submit(orderId.value, {
      rating: reviewRating.value,
      title: reviewTitle.value.trim() || undefined,
      body: reviewBody.value.trim() || undefined,
      is_public: reviewPublic.value,
    });
    existingReview.value = data;
    reviewRating.value = 0;
    reviewTitle.value = "";
    reviewBody.value = "";
  } catch {
    reviewError.value = "Review submission failed. Please try again.";
  } finally {
    reviewSubmitting.value = false;
  }
}

const TIP_PRESETS = [500, 1000, 2000, 5000]; // cents: $5, $10, $20, $50
const tipPreset = ref<number | null>(null);
const tipCustomCents = ref("");
const tipMessage = ref("");
const isTipping = ref(false);
const tipError = ref("");
const tipSuccess = ref<TipRecord | null>(null);

const tipAmount = computed(() => {
  if (tipPreset.value !== null) return tipPreset.value;
  const n = Math.round(Number(tipCustomCents.value) * 100);
  return Number.isFinite(n) && n > 0 ? n : null;
});

function selectTipPreset(cents: number) {
  tipPreset.value = tipPreset.value === cents ? null : cents;
  tipCustomCents.value = "";
}

function onCustomTipInput() {
  tipPreset.value = null;
}

function centsToDisplay(cents: number) {
  return `$${(cents / 100).toFixed(2)}`;
}

async function submitTip() {
  const writerId = lifecycle.value?.current_writer_id;
  const amount = tipAmount.value;
  if (!writerId || !amount) return;
  isTipping.value = true;
  tipError.value = "";
  try {
    const { data } = await tipsApi.create({
      receiver_id: writerId,
      gross_amount_cents: amount,
      currency: "USD",
      context_type: "order",
      message: tipMessage.value.trim() || undefined,
      idempotency_key: crypto.randomUUID(),
    });
    tipSuccess.value = data;
    tipPreset.value = null;
    tipCustomCents.value = "";
    tipMessage.value = "";
  } catch {
    tipError.value = "Unable to send tip. Please try again.";
  } finally {
    isTipping.value = false;
  }
}

function money(amount: string | number | undefined | null, currency = "USD") {
  if (amount === undefined || amount === null || amount === "") return `${currency} 0.00`;
  return `${currency} ${amount}`;
}

function dateLabel(value: string | undefined | null) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

async function submitRevision() {
  if (!revisionForm.reason || !revisionForm.scope_summary) return;
  await orders.requestRevision(orderId.value, {
    reason: revisionForm.reason,
    scope_summary: revisionForm.scope_summary,
    is_within_original_scope: revisionForm.is_within_original_scope,
  });
  revisionForm.reason = "";
  revisionForm.scope_summary = "";
}

async function submitCancel() {
  if (!cancelForm.reason) return;
  await orders.cancelOrder(orderId.value, {
    reason: cancelForm.reason,
    refund_destination: cancelForm.refund_destination,
    notes: cancelForm.notes,
  });
  cancelForm.reason = "";
  cancelForm.notes = "";
}

async function submitDispute() {
  if (!disputeForm.reason) return;
  await orders.raiseDispute(orderId.value, disputeForm.reason);
  disputeForm.reason = "";
}

async function submitSupportTicket() {
  if (!supportTicketForm.title || !supportTicketForm.description) return;
  isTicketSending.value = true;
  ticketError.value = "";
  ticketNotice.value = "";
  try {
    await supportApi.createTicket({
      title: supportTicketForm.title,
      description: supportTicketForm.description,
      category: "order",
      object_id: orderId.value,
    });
    ticketNotice.value = "Support ticket created. Our team will follow up shortly.";
    supportTicketForm.title = "";
    supportTicketForm.description = "";
  } catch {
    ticketError.value = "Unable to create support ticket.";
  } finally {
    isTicketSending.value = false;
  }
}

function selectFile(event: Event) {
  const input = event.target as HTMLInputElement;
  fileForm.file = input.files?.[0] ?? null;
  files.clearMessages();
}

async function submitFileUpload() {
  if (!fileForm.file) return;
  await files.uploadAndAttachToOrder({
    orderId: orderId.value,
    file: fileForm.file,
    purpose: fileForm.purpose,
    visibility: fileForm.visibility,
  });
  fileForm.file = null;
}

async function createMessageThread() {
  await communications.createOrderThread({
    orderId: orderId.value,
    subject: order.value?.topic || `Order #${orderId.value}`,
  });
}

async function sendOrderMessage() {
  if (!messageForm.body.trim()) return;
  await communications.sendMessage(messageForm.body.trim());
  messageForm.body = "";
}

function attachmentName(attachmentId: number, filename?: string) {
  return filename || `Attachment #${attachmentId}`;
}

onMounted(() => {
  void orders.fetchOrder(orderId.value);
  communications.loadOrderThread(orderId.value).catch(() => undefined);
  fetchExistingReview();
});
</script>

<template>
  <div class="space-y-6">
    <RouterLink
      class="focus-ring inline-flex items-center gap-2 rounded-md px-2 py-1 text-sm font-semibold text-graphite hover:bg-slate-100"
      to="/client/orders"
    >
      <ArrowLeft class="h-4 w-4" />
      Orders
    </RouterLink>

    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Client order</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">
          <template v-if="order">#{{ order.id }} {{ order.topic }}</template>
          <template v-else>Order #{{ orderId }}</template>
        </h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
          Review delivery state, lifecycle signals, files, revision eligibility, and final approval.
        </p>
      </div>
      <div class="flex flex-wrap gap-2">
        <StatusPill :label="order?.status ?? 'loading'" />
        <StatusPill :label="order?.payment_status ?? 'payment pending'" tone="warning" />
      </div>
    </section>

    <div v-if="orders.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ orders.error }}
    </div>
    <div v-if="orders.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
      {{ orders.notice }}
    </div>
    <div v-if="files.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ files.error }}
    </div>
    <div v-if="files.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
      {{ files.notice }}
    </div>
    <div v-if="communications.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ communications.error }}
    </div>
    <div v-if="communications.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
      {{ communications.notice }}
    </div>

    <section v-if="orders.isLoading && !order" class="rounded-lg border border-slate-200 bg-white p-8 text-sm text-graphite shadow-panel">
      Loading order workspace...
    </section>

    <template v-else>
      <section class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <div class="rounded-md border border-slate-200 bg-white p-4 shadow-panel">
          <p class="text-sm font-medium text-graphite">Total</p>
          <p class="mt-3 text-2xl font-semibold text-ink">{{ money(order?.total_price, order?.currency) }}</p>
          <p class="mt-2 text-sm text-graphite">Paid {{ money(order?.amount_paid, order?.currency) }}</p>
        </div>
        <div class="rounded-md border border-slate-200 bg-white p-4 shadow-panel">
          <p class="text-sm font-medium text-graphite">Balance</p>
          <p class="mt-3 text-2xl font-semibold text-ink">{{ money(order?.remaining_balance, order?.currency) }}</p>
          <p class="mt-2 text-sm text-graphite">{{ order?.payment_status ?? "Awaiting payment state" }}</p>
        </div>
        <div class="rounded-md border border-slate-200 bg-white p-4 shadow-panel">
          <p class="text-sm font-medium text-graphite">Client deadline</p>
          <p class="mt-3 text-lg font-semibold text-ink">{{ dateLabel(order?.client_deadline) }}</p>
          <p class="mt-2 text-sm text-graphite">Writer: {{ dateLabel(order?.writer_deadline) }}</p>
        </div>
        <div class="rounded-md border border-slate-200 bg-white p-4 shadow-panel">
          <p class="text-sm font-medium text-graphite">Revision window</p>
          <p class="mt-3 text-2xl font-semibold text-ink">
            {{ lifecycle?.is_revision_window_open ? "Open" : "Closed" }}
          </p>
          <p class="mt-2 text-sm text-graphite">{{ lifecycle?.revision_window_days ?? 0 }} day window</p>
        </div>
      </section>

      <section v-if="canApprove" class="rounded-lg border-2 border-signal bg-emerald-50 p-5 shadow-panel">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div class="flex items-start gap-3">
            <ThumbsUp class="mt-0.5 h-5 w-5 shrink-0 text-signal" />
            <div>
              <h2 class="text-lg font-semibold text-ink">Your work is ready for review</h2>
              <p class="mt-1 text-sm leading-6 text-graphite">
                Download the deliverable below and accept when you're satisfied. You have
                {{ lifecycle?.revision_window_days ?? 7 }} days to request a free revision after accepting.
              </p>
            </div>
          </div>
          <button
            class="focus-ring inline-flex shrink-0 items-center justify-center gap-2 rounded-md bg-signal px-5 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
            type="button"
            :disabled="orders.isMutating"
            @click="orders.approveOrder(orderId)"
          >
            <Loader2 v-if="orders.isMutating" class="h-4 w-4 animate-spin" />
            <ThumbsUp v-else class="h-4 w-4" />
            Accept delivery
          </button>
        </div>
      </section>

      <section v-if="isTerminal" class="rounded-lg border border-slate-200 bg-slate-50 p-5 shadow-panel">
        <p class="text-sm font-semibold capitalize text-ink">Order {{ order?.status }}</p>
        <p class="mt-2 text-sm leading-6 text-graphite">
          <template v-if="order?.status === 'completed'">
            This order is complete. Your deliverable files remain available above for download.
          </template>
          <template v-else-if="order?.status === 'cancelled'">
            This order was cancelled. Contact support if you have questions about your refund.
          </template>
          <template v-else>
            This order is archived and no longer active.
          </template>
        </p>
      </section>

      <section class="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
          <h2 class="text-lg font-semibold text-ink">Lifecycle</h2>
          <div class="mt-5 grid gap-3 sm:grid-cols-2">
            <div class="rounded-md border border-slate-200 p-4">
              <p class="text-sm font-semibold text-ink">Assignment</p>
              <p class="mt-2 text-sm text-graphite">
                {{ lifecycle?.has_current_assignment ? `Writer #${lifecycle.current_writer_id}` : "Awaiting assignment" }}
              </p>
            </div>
            <div class="rounded-md border border-slate-200 p-4">
              <p class="text-sm font-semibold text-ink">Hold</p>
              <p class="mt-2 text-sm text-graphite">
                {{ lifecycle?.has_active_hold ? `Active hold #${lifecycle.active_hold_id}` : "No active hold" }}
              </p>
            </div>
            <div class="rounded-md border border-slate-200 p-4">
              <p class="text-sm font-semibold text-ink">Dispute</p>
              <p class="mt-2 text-sm text-graphite">
                {{ lifecycle?.has_active_dispute ? `Active dispute #${lifecycle.active_dispute_id}` : "No active dispute" }}
              </p>
            </div>
            <div class="rounded-md border border-slate-200 p-4">
              <p class="text-sm font-semibold text-ink">Latest revision</p>
              <p class="mt-2 text-sm text-graphite">
                {{ lifecycle?.latest_revision_status ?? "No revision request" }}
              </p>
            </div>
          </div>
        </div>

        <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
          <h2 class="text-lg font-semibold text-ink">Files and messages</h2>
          <form class="mt-5 grid gap-3" @submit.prevent="submitFileUpload">
            <label class="block text-sm font-medium text-ink">
              Upload file
              <input
                class="focus-ring mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                type="file"
                @change="selectFile"
              />
            </label>
            <div class="grid gap-3 sm:grid-cols-2">
              <label class="block text-sm font-medium text-ink">
                Purpose
                <select
                  v-model="fileForm.purpose"
                  class="focus-ring mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                >
                  <option value="order_reference">Reference</option>
                  <option value="order_instruction">Instruction</option>
                  <option value="style_reference">Style reference</option>
                  <option value="order_revision">Revision support</option>
                </select>
              </label>
              <label class="block text-sm font-medium text-ink">
                Visibility
                <select
                  v-model="fileForm.visibility"
                  class="focus-ring mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                >
                  <option value="order_participants">Order participants</option>
                  <option value="client_writer_staff">Client, writer, staff</option>
                  <option value="client_and_staff">Client and staff</option>
                  <option value="owner_only">Owner only</option>
                </select>
              </label>
            </div>
            <button
              class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-slate-300 px-4 py-3 text-sm font-semibold text-ink disabled:cursor-not-allowed disabled:opacity-60"
              type="submit"
              :disabled="files.isUploading || !fileForm.file"
            >
              <Loader2 v-if="files.isUploading" class="h-4 w-4 animate-spin" />
              <FileUp class="h-4 w-4" />
              Attach file
            </button>
          </form>

          <div v-if="files.attachments.length" class="mt-5 overflow-hidden rounded-md border border-slate-200">
            <div
              v-for="attachment in files.attachments"
              :key="attachment.id"
              class="grid gap-3 border-b border-slate-100 px-3 py-3 text-sm last:border-b-0 sm:grid-cols-[1fr_auto]"
            >
              <div>
                <p class="font-semibold text-ink">
                  {{ attachmentName(attachment.id, attachment.managed_file?.original_filename) }}
                </p>
                <p class="mt-1 text-xs text-graphite">
                  {{ attachment.purpose }} · {{ attachment.visibility }}
                </p>
              </div>
              <a
                v-if="!attachment.managed_file?.download_url && !attachment.managed_file?.public_url"
                class="inline-flex items-center justify-center rounded-md border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-400"
                href="#"
                aria-disabled="true"
                @click.prevent
              >
                Preview only
              </a>
              <a
                v-else
                class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-slate-300 px-3 py-2 text-xs font-semibold text-ink"
                :href="attachment.managed_file?.download_url || attachment.managed_file?.public_url || filesApi.downloadUrl(attachment.id)"
                target="_blank"
                rel="noreferrer"
              >
                <Download class="h-3.5 w-3.5" />
                Download
              </a>
            </div>
          </div>

          <div class="mt-6 border-t border-slate-200 pt-5">
            <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h3 class="text-sm font-semibold text-ink">Order thread</h3>
                <p class="mt-1 text-xs text-graphite">
                  {{ communications.activeThread ? `${communications.activeThread.kind} · ${communications.activeThread.status}` : "No thread loaded" }}
                </p>
              </div>
              <div class="flex gap-2">
                <button
                  class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-slate-300 px-3 py-2 text-xs font-semibold text-ink disabled:cursor-not-allowed disabled:opacity-60"
                  type="button"
                  :disabled="communications.isLoading"
                  @click="communications.loadOrderThread(orderId)"
                >
                  <RefreshCw class="h-3.5 w-3.5" />
                  Refresh
                </button>
                <button
                  v-if="!communications.activeThread"
                  class="focus-ring inline-flex items-center justify-center gap-2 rounded-md bg-ink px-3 py-2 text-xs font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
                  type="button"
                  :disabled="communications.isLoading"
                  @click="createMessageThread"
                >
                  <MessageSquare class="h-3.5 w-3.5" />
                  Start
                </button>
              </div>
            </div>

            <div class="mt-4 max-h-64 space-y-3 overflow-y-auto rounded-md border border-slate-200 bg-slate-50 p-3">
              <p v-if="communications.isLoading" class="text-sm text-graphite">Loading messages...</p>
              <p v-else-if="!communications.activeThread" class="text-sm text-graphite">
                Start an order thread to message around this order.
              </p>
              <p v-else-if="!communications.messages.length" class="text-sm text-graphite">
                No messages yet.
              </p>
              <article
                v-for="message in communications.messages"
                v-else
                :key="message.id"
                class="rounded-md border border-slate-200 bg-white p-3"
              >
                <div class="flex items-center justify-between gap-3">
                  <p class="text-xs font-semibold text-ink">{{ message.sender_display }}</p>
                  <StatusPill :label="message.status" />
                </div>
                <p class="mt-2 whitespace-pre-wrap text-sm leading-6 text-graphite">{{ message.body }}</p>
              </article>
            </div>

            <form class="mt-3 grid gap-3" @submit.prevent="sendOrderMessage">
              <textarea
                v-model.trim="messageForm.body"
                class="focus-ring min-h-24 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                placeholder="Write a message about this order"
              />
              <button
                class="focus-ring inline-flex items-center justify-center gap-2 rounded-md bg-signal px-4 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
                type="submit"
                :disabled="communications.isSending || !communications.activeThread || !messageForm.body"
              >
                <Loader2 v-if="communications.isSending" class="h-4 w-4 animate-spin" />
                <Send v-else class="h-4 w-4" />
                Send message
              </button>
            </form>
          </div>
          <p class="mt-4 text-sm leading-6 text-graphite">
            Uploads use the unified files service. Messages use the communications thread API for order-scoped conversation.
          </p>
        </div>
      </section>

      <form v-if="canRequestRevision" class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel" @submit.prevent="submitRevision">
        <div class="flex items-center gap-2">
          <RotateCcw class="h-5 w-5 text-saffron" />
          <h2 class="text-lg font-semibold text-ink">Request revision</h2>
        </div>
        <div class="mt-4 grid gap-4 md:grid-cols-2">
          <label class="block text-sm font-medium text-ink">
            Reason
            <input
              v-model.trim="revisionForm.reason"
              class="focus-ring mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              placeholder="What needs to change?"
            />
          </label>
          <label class="flex items-center gap-3 rounded-md border border-slate-200 px-3 py-3 text-sm font-medium text-ink">
            <input v-model="revisionForm.is_within_original_scope" class="h-4 w-4" type="checkbox" />
            Within original scope
          </label>
        </div>
        <label class="mt-4 block text-sm font-medium text-ink">
          Scope summary
          <textarea
            v-model.trim="revisionForm.scope_summary"
            class="focus-ring mt-2 min-h-24 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            placeholder="Describe the exact revision scope"
          />
        </label>
        <button
          class="focus-ring mt-4 inline-flex items-center justify-center gap-2 rounded-md bg-ink px-4 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
          type="submit"
          :disabled="orders.isMutating || !revisionForm.reason || !revisionForm.scope_summary"
        >
          Submit revision request
        </button>
      </form>

      <section v-if="lifecycle && !lifecycle.has_active_dispute && !isTerminal" class="rounded-lg border border-amber-200 bg-amber-50 p-5 shadow-panel">
        <div class="flex items-center gap-2">
          <AlertTriangle class="h-5 w-5 text-amber-700" />
          <h2 class="text-lg font-semibold text-amber-950">Raise a dispute</h2>
        </div>
        <p class="mt-2 text-sm leading-6 text-amber-900">
          Use this only if there is a serious issue that cannot be resolved through a revision request. Our team will review the dispute and respond.
        </p>
        <form class="mt-4 flex flex-col gap-3 sm:flex-row" @submit.prevent="submitDispute">
          <input
            v-model.trim="disputeForm.reason"
            class="focus-ring flex-1 rounded-md border border-amber-200 bg-white px-3 py-2 text-sm"
            placeholder="Describe the issue clearly"
          />
          <button
            class="focus-ring inline-flex items-center justify-center rounded-md bg-amber-700 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
            type="submit"
            :disabled="orders.isMutating || !disputeForm.reason"
          >
            Raise dispute
          </button>
        </form>
      </section>
      <div v-else-if="lifecycle?.has_active_dispute" class="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
        Dispute #{{ lifecycle.active_dispute_id }} is currently active on this order. Our team is reviewing it.
      </div>

      <section class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
        <div class="flex items-center gap-2">
          <LifeBuoy class="h-5 w-5 text-signal" />
          <h2 class="text-lg font-semibold text-ink">Open a support ticket</h2>
        </div>
        <p class="mt-2 text-sm leading-6 text-graphite">
          Need help with this order? Our support team will respond within 24 hours.
        </p>
        <div v-if="ticketError" class="mt-3 rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">{{ ticketError }}</div>
        <div v-if="ticketNotice" class="mt-3 rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">{{ ticketNotice }}</div>
        <form class="mt-4 grid gap-3" @submit.prevent="submitSupportTicket">
          <input
            v-model.trim="supportTicketForm.title"
            class="focus-ring w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            placeholder="Brief summary of the issue"
          />
          <textarea
            v-model.trim="supportTicketForm.description"
            class="focus-ring min-h-24 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            placeholder="Describe the issue in detail"
          />
          <button
            class="focus-ring inline-flex items-center justify-center gap-2 self-start rounded-md bg-signal px-4 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
            type="submit"
            :disabled="isTicketSending || !supportTicketForm.title || !supportTicketForm.description"
          >
            <Loader2 v-if="isTicketSending" class="h-4 w-4 animate-spin" />
            Submit ticket
          </button>
        </form>
      </section>

      <!-- Tip your writer -->
      <section v-if="canTip" class="rounded-lg border border-amber-200 bg-amber-50 p-5 shadow-panel">
        <div class="flex items-center gap-2">
          <Gift class="h-5 w-5 text-amber-700" />
          <h2 class="text-lg font-semibold text-amber-950">Tip your writer</h2>
        </div>
        <p class="mt-1 text-sm text-amber-800">
          Satisfied with the work? Send a tip to show your appreciation.
        </p>

        <div v-if="tipSuccess" class="mt-4 rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
          Tip of {{ centsToDisplay(tipSuccess.gross_amount_cents) }} sent — thank you!
        </div>

        <template v-else>
          <div class="mt-4 flex flex-wrap gap-2">
            <button
              v-for="cents in TIP_PRESETS"
              :key="cents"
              type="button"
              class="focus-ring rounded-md border px-4 py-2 text-sm font-semibold transition-colors"
              :class="tipPreset === cents
                ? 'border-amber-600 bg-amber-600 text-white'
                : 'border-amber-300 bg-white text-amber-900 hover:border-amber-500'"
              @click="selectTipPreset(cents)"
            >
              {{ centsToDisplay(cents) }}
            </button>
            <input
              v-model="tipCustomCents"
              class="focus-ring h-10 w-28 rounded-md border border-amber-300 bg-white px-3 text-sm placeholder-amber-400"
              type="number"
              min="1"
              step="0.01"
              placeholder="Custom $"
              @input="onCustomTipInput"
            />
          </div>

          <div class="mt-3">
            <input
              v-model="tipMessage"
              class="focus-ring w-full rounded-md border border-amber-300 bg-white px-3 py-2 text-sm placeholder-amber-400"
              placeholder="Add a message (optional)"
              maxlength="200"
            />
          </div>

          <p v-if="tipError" class="mt-2 text-sm text-rose-700">{{ tipError }}</p>

          <button
            class="focus-ring mt-3 inline-flex items-center gap-2 rounded-md bg-amber-600 px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
            type="button"
            :disabled="isTipping || tipAmount === null"
            @click="submitTip"
          >
            <Loader2 v-if="isTipping" class="h-4 w-4 animate-spin" />
            <Gift v-else class="h-4 w-4" />
            {{ isTipping ? "Sending tip…" : tipAmount ? `Send ${centsToDisplay(tipAmount)}` : "Select amount" }}
          </button>
        </template>
      </section>

      <!-- Rate your writer -->
      <section v-if="canReview || existingReview" class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
        <div class="flex items-center gap-2">
          <Star class="h-5 w-5 text-saffron" />
          <h2 class="text-lg font-semibold text-ink">Rate your writer</h2>
        </div>

        <!-- Already submitted -->
        <template v-if="existingReview">
          <p class="mt-2 text-sm text-graphite">You rated this order.</p>
          <div class="mt-3 flex items-center gap-1">
            <Star
              v-for="n in 5"
              :key="n"
              class="h-5 w-5"
              :class="n <= existingReview.rating ? 'text-saffron fill-saffron' : 'text-slate-300'"
            />
            <span class="ml-2 text-sm font-semibold text-ink">{{ existingReview.rating }}/5</span>
          </div>
          <p v-if="existingReview.title" class="mt-2 text-sm font-semibold text-ink">{{ existingReview.title }}</p>
          <p v-if="existingReview.body" class="mt-1 text-sm text-graphite">{{ existingReview.body }}</p>
        </template>

        <!-- Review form -->
        <template v-else>
          <p class="mt-1 text-sm text-graphite">How was the work? Your rating helps us match you with great writers.</p>

          <div class="mt-4 flex items-center gap-1">
            <button
              v-for="n in 5"
              :key="n"
              type="button"
              class="focus-ring rounded p-0.5 transition-transform hover:scale-110"
              :aria-label="`Rate ${n} star${n > 1 ? 's' : ''}`"
              @click="reviewRating = n"
              @mouseenter="reviewHoverRating = n"
              @mouseleave="reviewHoverRating = 0"
            >
              <Star
                class="h-7 w-7 transition-colors"
                :class="n <= (reviewHoverRating || reviewRating) ? 'text-saffron fill-saffron' : 'text-slate-300'"
              />
            </button>
          </div>

          <div class="mt-4 grid gap-3">
            <input
              v-model.trim="reviewTitle"
              class="focus-ring w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              placeholder="Title (optional)"
              maxlength="120"
            />
            <textarea
              v-model.trim="reviewBody"
              class="focus-ring min-h-20 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              placeholder="Share your experience (optional)"
              maxlength="1000"
            />
            <label class="flex items-center gap-2 text-sm text-graphite">
              <input v-model="reviewPublic" type="checkbox" class="h-4 w-4 rounded" />
              Make review public on writer profile
            </label>
          </div>

          <p v-if="reviewError" class="mt-2 text-sm text-berry">{{ reviewError }}</p>

          <button
            class="focus-ring mt-3 inline-flex items-center gap-2 rounded-md bg-ink px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
            type="button"
            :disabled="reviewSubmitting || !reviewRating"
            @click="submitReview"
          >
            <Loader2 v-if="reviewSubmitting" class="h-4 w-4 animate-spin" />
            <Star v-else class="h-4 w-4" />
            Submit review
          </button>
        </template>
      </section>

      <form v-if="canCancel" class="rounded-lg border border-rose-200 bg-rose-50 p-5 shadow-panel" @submit.prevent="submitCancel">
        <div class="flex items-center gap-2">
          <XCircle class="h-5 w-5 text-rose-700" />
          <h2 class="text-lg font-semibold text-rose-950">Cancel order</h2>
        </div>
        <div class="mt-4 grid gap-4 lg:grid-cols-[1fr_220px_1fr_auto]">
          <input
            v-model.trim="cancelForm.reason"
            class="focus-ring rounded-md border border-rose-200 px-3 py-2 text-sm"
            placeholder="Cancellation reason"
          />
          <select
            v-model="cancelForm.refund_destination"
            class="focus-ring rounded-md border border-rose-200 px-3 py-2 text-sm"
          >
            <option value="wallet">Wallet refund</option>
            <option value="external">External refund</option>
          </select>
          <input
            v-model.trim="cancelForm.notes"
            class="focus-ring rounded-md border border-rose-200 px-3 py-2 text-sm"
            placeholder="Optional notes"
          />
          <button
            class="focus-ring inline-flex items-center justify-center rounded-md bg-rose-700 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
            type="submit"
            :disabled="orders.isMutating || !cancelForm.reason"
          >
            Cancel
          </button>
        </div>
      </form>
      <OrderTimeline :order-id="orderId" class="mt-6" />
    </template>
  </div>
</template>
