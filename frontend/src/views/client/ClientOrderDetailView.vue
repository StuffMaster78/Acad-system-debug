<script setup lang="ts">
import { computed, onMounted, reactive } from "vue";
import { RouterLink, useRoute } from "vue-router";
import {
  ArrowLeft,
  CheckCircle2,
  Download,
  FileUp,
  Loader2,
  MessageSquare,
  RefreshCw,
  RotateCcw,
  Send,
  XCircle,
} from "@lucide/vue";
import { filesApi, type FilePurpose, type FileVisibility } from "@/api/files";
import StatusPill from "@/components/ui/StatusPill.vue";
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

      <section class="grid gap-6 xl:grid-cols-3">
        <form class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel" @submit.prevent="orders.approveOrder(orderId)">
          <div class="flex items-center gap-2">
            <CheckCircle2 class="h-5 w-5 text-signal" />
            <h2 class="text-lg font-semibold text-ink">Approve delivery</h2>
          </div>
          <p class="mt-3 text-sm leading-6 text-graphite">
            Confirms the submitted work and completes the order when the backend allows approval.
          </p>
          <button
            class="focus-ring mt-5 inline-flex w-full items-center justify-center gap-2 rounded-md bg-signal px-4 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
            type="submit"
            :disabled="orders.isMutating"
          >
            <Loader2 v-if="orders.isMutating" class="h-4 w-4 animate-spin" />
            Approve order
          </button>
        </form>

        <form class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel xl:col-span-2" @submit.prevent="submitRevision">
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
      </section>

      <form class="rounded-lg border border-rose-200 bg-rose-50 p-5 shadow-panel" @submit.prevent="submitCancel">
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
    </template>
  </div>
</template>
