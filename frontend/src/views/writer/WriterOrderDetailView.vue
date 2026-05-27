<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterLink, useRoute } from "vue-router";
import {
  AlertCircle,
  ArrowLeft,
  BookOpen,
  CheckCircle2,
  Clock3,
  Download,
  FileText,
  FileUp,
  Loader2,
  MessageSquare,
  Plus,
  RefreshCw,
  RotateCcw,
  Send,
  Trash2,
  X,
  Zap,
} from "@lucide/vue";
import type { RevisionRequest } from "@/types/orders";
import { ordersApi } from "@/api/orders";
import StatusPill from "@/components/ui/StatusPill.vue";
import OrderTimeline from "@/components/orders/OrderTimeline.vue";
import { filesApi, type FilePurpose, type FileVisibility } from "@/api/files";
import { writerApi } from "@/api/writer";
import { useFilesStore, type QueuedFile } from "@/stores/files";
import { useOrderStore } from "@/stores/orders";
import { useCommunicationsStore } from "@/stores/communications";

const route = useRoute();
const orders = useOrderStore();
const files = useFilesStore();
const comms = useCommunicationsStore();

const messageBody = ref("");

const orderId = computed(() => String(route.params.id));
const order = computed(() => orders.selectedOrder);
const lifecycle = computed(() => orders.selectedLifecycle);
const latestRevision = ref<RevisionRequest | null>(null);

const isRevisionRequested = computed(() =>
  order.value?.status === "revision_requested" ||
  (lifecycle.value?.latest_revision_status != null &&
    !["resolved", "rejected", "withdrawn"].includes(lifecycle.value.latest_revision_status)),
);

const defaultPurpose = ref<FilePurpose>("order_deliverable");
const defaultVisibility = ref<FileVisibility>("order_participants");

const isSubmitting = ref(false);
const submitError = ref("");
const submitNotice = ref("");
const submissionNote = ref("");

const purposeLabels: Record<FilePurpose, string> = {
  order_deliverable: "Deliverable",
  order_reference: "Reference",
  order_instruction: "Instruction",
  order_revision: "Revision support",
  style_reference: "Style reference",
  message_attachment: "Message attachment",
};

const visibilityLabels: Record<FileVisibility, string> = {
  order_participants: "Order participants",
  client_writer_staff: "Client, writer & staff",
  client_and_staff: "Client & staff",
  owner_only: "Owner only",
};

function fileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function dateLabel(value: string | undefined | null): string {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function deadlineUrgency(value: string | null | undefined): "danger" | "warning" | "neutral" {
  if (!value) return "neutral";
  const h = (new Date(value).getTime() - Date.now()) / 3600000;
  if (h < 0) return "danger";
  if (h < 12) return "warning";
  return "neutral";
}

function deadlineLabel(value: string | null | undefined): string {
  if (!value) return "No deadline";
  const h = (new Date(value).getTime() - Date.now()) / 3600000;
  if (h < 0) return `${Math.round(Math.abs(h))}h overdue`;
  if (h < 24) return `${Math.round(h)}h left`;
  return `${Math.round(h / 24)}d left`;
}

function onFilePick(event: Event) {
  const input = event.target as HTMLInputElement;
  if (!input.files?.length) return;
  files.addToQueue(input.files, {
    purpose: defaultPurpose.value,
    visibility: defaultVisibility.value,
  });
  input.value = "";
}

function queueItemTone(item: QueuedFile) {
  if (item.status === "done") return "text-signal";
  if (item.status === "error") return "text-berry";
  if (item.status === "uploading") return "text-saffron";
  return "text-graphite";
}

async function uploadAll() {
  await files.uploadFiles(orderId.value);
}

async function submitWork() {
  submitError.value = "";
  submitNotice.value = "";
  isSubmitting.value = true;
  try {
    const { data } = await writerApi.submitOrder(orderId.value, {
      note: submissionNote.value || undefined,
    });
    submitNotice.value = data.message ?? "Work submitted successfully.";
    submissionNote.value = "";
    await orders.fetchOrder(orderId.value);
  } catch {
    submitError.value = "Submission failed. Make sure deliverable files are uploaded first.";
  } finally {
    isSubmitting.value = false;
  }
}

const pendingCount = computed(() => files.uploadQueue.filter((q) => q.status === "pending").length);
const hasDeliverable = computed(() =>
  files.attachments.some((a) => a.purpose === "order_deliverable") ||
  files.uploadQueue.some((q) => q.status === "done" && q.purpose === "order_deliverable"),
);

async function sendMessage() {
  if (!messageBody.value.trim()) return;
  await comms.sendMessage(messageBody.value.trim());
  messageBody.value = "";
}

async function fetchRevisions() {
  try {
    const { data } = await ordersApi.revisions(orderId.value);
    const list = Array.isArray(data) ? data : data.results;
    latestRevision.value = list[0] ?? null;
  } catch {
    // non-fatal
  }
}

onMounted(async () => {
  files.clearMessages();
  files.uploadQueue.splice(0);
  await orders.fetchOrder(orderId.value);
  await Promise.all([
    files.fetchOrderAttachments(orderId.value),
    fetchRevisions(),
  ]);
  comms.loadOrderThread(orderId.value).catch(() => undefined);
});
</script>

<template>
  <div class="space-y-6">
    <RouterLink
      class="focus-ring inline-flex items-center gap-2 rounded-md px-2 py-1 text-sm font-semibold text-graphite hover:bg-slate-100"
      to="/writer/assignments"
    >
      <ArrowLeft class="h-4 w-4" />
      Assignments
    </RouterLink>

    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Writer</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">
          <template v-if="order">#{{ order.id }} {{ order.topic }}</template>
          <template v-else>Order #{{ orderId }}</template>
        </h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
          Order instructions, file delivery, and work submission.
        </p>
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <StatusPill v-if="order" :label="order.status" />
        <span
          v-if="order?.is_urgent"
          class="inline-flex items-center gap-1 rounded-full bg-red-100 px-2 py-0.5 text-xs font-semibold text-red-700"
        >
          <Zap class="h-3 w-3" />
          Urgent
        </span>
        <button
          class="focus-ring inline-flex items-center gap-2 rounded-md border border-slate-200 px-3 py-2 text-xs font-semibold text-graphite hover:bg-slate-50 disabled:opacity-50"
          type="button"
          :disabled="orders.isLoading"
          @click="orders.fetchOrder(orderId)"
        >
          <Loader2 v-if="orders.isLoading" class="h-3.5 w-3.5 animate-spin" />
          <RefreshCw v-else class="h-3.5 w-3.5" />
          Refresh
        </button>
      </div>
    </section>

    <div v-if="orders.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ orders.error }}
    </div>
    <div v-if="files.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ files.error }}
    </div>
    <div v-if="files.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
      {{ files.notice }}
    </div>

    <section v-if="orders.isLoading && !order" class="rounded-lg border border-slate-200 bg-white p-8 text-center text-sm text-graphite shadow-panel">
      Loading order…
    </section>

    <template v-else-if="order">
      <section v-if="isRevisionRequested" class="rounded-lg border-2 border-saffron bg-amber-50 p-5 shadow-panel">
        <div class="flex items-start gap-3">
          <RotateCcw class="mt-0.5 h-5 w-5 shrink-0 text-saffron" />
          <div class="min-w-0 flex-1">
            <h2 class="text-base font-semibold text-ink">Revision requested</h2>
            <p class="mt-1 text-sm text-graphite">
              The client has requested changes. Review the details below, upload your revised work, and re-submit.
            </p>

            <div v-if="latestRevision" class="mt-4 grid gap-3 sm:grid-cols-2">
              <div class="rounded-md border border-amber-200 bg-white px-4 py-3">
                <p class="text-xs font-semibold uppercase tracking-wide text-amber-700">Reason</p>
                <p class="mt-1 text-sm text-ink">{{ latestRevision.reason }}</p>
              </div>
              <div class="rounded-md border border-amber-200 bg-white px-4 py-3">
                <p class="text-xs font-semibold uppercase tracking-wide text-amber-700">Scope</p>
                <p class="mt-1 text-sm text-ink">{{ latestRevision.scope_summary }}</p>
              </div>
              <div class="rounded-md border border-amber-200 bg-white px-4 py-3 sm:col-span-2">
                <span
                  class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold"
                  :class="latestRevision.is_within_original_scope
                    ? 'bg-emerald-100 text-emerald-800'
                    : 'bg-rose-100 text-rose-800'"
                >
                  <CheckCircle2 v-if="latestRevision.is_within_original_scope" class="h-3.5 w-3.5" />
                  <AlertCircle v-else class="h-3.5 w-3.5" />
                  {{ latestRevision.is_within_original_scope ? "Within original scope — free revision" : "Outside original scope — may require adjustment" }}
                </span>
              </div>
            </div>
            <p v-else class="mt-3 text-sm text-graphite">Revision details are loading…</p>
          </div>
        </div>
      </section>

      <div class="grid gap-6 xl:grid-cols-[1fr_400px]">
        <div class="space-y-6">
          <section class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
            <h2 class="text-base font-semibold text-ink">Order details</h2>

            <dl class="mt-4 grid gap-4 sm:grid-cols-2">
              <div>
                <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Writer deadline</dt>
                <dd class="mt-1 flex items-center gap-2">
                  <Clock3 class="h-4 w-4 shrink-0 text-slate-400" />
                  <span class="text-sm font-medium text-ink">{{ dateLabel(order.writer_deadline ?? order.client_deadline) }}</span>
                  <StatusPill
                    :label="deadlineLabel(order.writer_deadline ?? order.client_deadline)"
                    :tone="deadlineUrgency(order.writer_deadline ?? order.client_deadline)"
                  />
                </dd>
              </div>

              <div>
                <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Compensation</dt>
                <dd class="mt-1 text-sm font-semibold text-ink">
                  {{ order.writer_compensation
                    ? new Intl.NumberFormat("en-US", { style: "currency", currency: order.currency ?? "USD" }).format(Number(order.writer_compensation))
                    : "Not set" }}
                </dd>
              </div>

              <div v-if="order.academic_level">
                <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Academic level</dt>
                <dd class="mt-1 text-sm text-ink">{{ order.academic_level }}</dd>
              </div>

              <div v-if="order.number_of_pages">
                <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Pages</dt>
                <dd class="mt-1 flex items-center gap-1.5 text-sm text-ink">
                  <FileText class="h-3.5 w-3.5 text-slate-400" />
                  {{ order.number_of_pages }} page{{ Number(order.number_of_pages) !== 1 ? "s" : "" }}
                  <span v-if="order.spacing" class="text-graphite">({{ order.spacing }})</span>
                </dd>
              </div>

              <div v-if="order.subject">
                <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Subject</dt>
                <dd class="mt-1 text-sm text-ink">{{ order.subject }}</dd>
              </div>

              <div v-if="order.service_code">
                <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Service</dt>
                <dd class="mt-1 text-sm text-ink">{{ order.service_code }}</dd>
              </div>
            </dl>

            <div v-if="order.order_instructions || order.instructions" class="mt-5 border-t border-slate-100 pt-4">
              <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Instructions</dt>
              <dd class="mt-2 whitespace-pre-wrap rounded-md bg-slate-50 p-4 text-sm leading-6 text-ink">
                {{ order.order_instructions ?? order.instructions }}
              </dd>
            </div>
          </section>

          <section class="rounded-lg border border-slate-200 bg-white shadow-panel">
            <div class="border-b border-slate-200 px-5 py-4">
              <h2 class="text-base font-semibold text-ink">Attached files</h2>
              <p class="mt-1 text-xs text-graphite">Files attached to this order from all participants.</p>
            </div>

            <div v-if="files.isLoadingAttachments" class="px-5 py-6 text-sm text-graphite">
              Loading attachments…
            </div>
            <div v-else-if="!files.attachments.length" class="px-5 py-6 text-center">
              <BookOpen class="mx-auto h-7 w-7 text-slate-300" />
              <p class="mt-2 text-sm text-graphite">No files attached yet.</p>
            </div>
            <div v-else class="divide-y divide-slate-100">
              <div
                v-for="attachment in files.attachments"
                :key="attachment.id"
                class="flex items-center gap-4 px-5 py-3"
              >
                <div class="min-w-0 flex-1">
                  <p class="truncate text-sm font-medium text-ink">
                    {{ attachment.managed_file?.original_filename ?? `Attachment #${attachment.id}` }}
                  </p>
                  <p class="mt-0.5 text-xs text-graphite">
                    {{ purposeLabels[attachment.purpose as FilePurpose] ?? attachment.purpose }}
                    <span v-if="attachment.managed_file?.file_size_bytes">
                      · {{ fileSize(attachment.managed_file.file_size_bytes) }}
                    </span>
                  </p>
                </div>
                <a
                  v-if="attachment.managed_file?.download_url || attachment.managed_file?.public_url"
                  class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-slate-200 px-3 py-1.5 text-xs font-semibold text-ink hover:bg-slate-50"
                  :href="attachment.managed_file.download_url || attachment.managed_file.public_url || filesApi.downloadUrl(attachment.id)"
                  target="_blank"
                  rel="noreferrer"
                >
                  <Download class="h-3.5 w-3.5" />
                  Download
                </a>
                <span v-else class="text-xs text-slate-400">Preview only</span>
              </div>
            </div>
          </section>

          <OrderTimeline :order-id="orderId" />
        </div>

        <aside class="space-y-6">
          <section class="rounded-lg border border-slate-200 bg-white shadow-panel">
            <div class="border-b border-slate-200 px-5 py-4">
              <h2 class="text-base font-semibold text-ink">Upload files</h2>
              <p class="mt-1 text-xs text-graphite">
                Add multiple files at once. Set purpose and visibility per file before uploading.
              </p>
            </div>

            <div class="p-5 space-y-4">
              <div class="grid gap-3 sm:grid-cols-2">
                <label class="block">
                  <span class="text-xs font-medium text-graphite">Default purpose</span>
                  <select
                    v-model="defaultPurpose"
                    class="focus-ring mt-1 h-9 w-full rounded-md border border-slate-200 px-2 text-sm"
                  >
                    <option value="order_deliverable">Deliverable</option>
                    <option value="order_reference">Reference</option>
                    <option value="order_revision">Revision support</option>
                    <option value="style_reference">Style reference</option>
                  </select>
                </label>
                <label class="block">
                  <span class="text-xs font-medium text-graphite">Default visibility</span>
                  <select
                    v-model="defaultVisibility"
                    class="focus-ring mt-1 h-9 w-full rounded-md border border-slate-200 px-2 text-sm"
                  >
                    <option value="order_participants">Order participants</option>
                    <option value="client_writer_staff">Client, writer & staff</option>
                    <option value="client_and_staff">Client & staff</option>
                  </select>
                </label>
              </div>

              <label
                class="flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed border-slate-300 p-6 text-center transition-colors hover:border-slate-400 hover:bg-slate-50"
              >
                <Plus class="h-6 w-6 text-slate-400" />
                <span class="text-sm font-medium text-ink">Add files</span>
                <span class="text-xs text-graphite">Click to browse — multiple files supported</span>
                <input
                  class="sr-only"
                  type="file"
                  multiple
                  @change="onFilePick"
                />
              </label>

              <div v-if="files.uploadQueue.length" class="space-y-2">
                <div
                  v-for="item in files.uploadQueue"
                  :key="item.id"
                  class="rounded-md border border-slate-200 bg-slate-50 p-3"
                >
                  <div class="flex items-start gap-3">
                    <div class="min-w-0 flex-1">
                      <p class="truncate text-sm font-medium text-ink">{{ item.file.name }}</p>
                      <p class="mt-0.5 text-xs text-graphite">{{ fileSize(item.file.size) }}</p>
                    </div>
                    <span
                      class="shrink-0 text-xs font-semibold"
                      :class="queueItemTone(item)"
                    >
                      <Loader2 v-if="item.status === 'uploading'" class="h-3.5 w-3.5 animate-spin" />
                      <CheckCircle2 v-else-if="item.status === 'done'" class="h-3.5 w-3.5" />
                      <AlertCircle v-else-if="item.status === 'error'" class="h-3.5 w-3.5" />
                      <span v-else class="capitalize">{{ item.status }}</span>
                    </span>
                    <button
                      v-if="item.status !== 'uploading'"
                      class="focus-ring shrink-0 rounded p-0.5 text-slate-400 hover:text-ink"
                      type="button"
                      aria-label="Remove"
                      @click="files.removeFromQueue(item.id)"
                    >
                      <X class="h-3.5 w-3.5" />
                    </button>
                  </div>

                  <div v-if="item.status === 'pending'" class="mt-2 grid gap-2 sm:grid-cols-2">
                    <select
                      :value="item.purpose"
                      class="focus-ring h-8 w-full rounded border border-slate-200 bg-white px-2 text-xs"
                      @change="item.purpose = ($event.target as HTMLSelectElement).value as FilePurpose"
                    >
                      <option v-for="(label, key) in purposeLabels" :key="key" :value="key">{{ label }}</option>
                    </select>
                    <select
                      :value="item.visibility"
                      class="focus-ring h-8 w-full rounded border border-slate-200 bg-white px-2 text-xs"
                      @change="item.visibility = ($event.target as HTMLSelectElement).value as FileVisibility"
                    >
                      <option v-for="(label, key) in visibilityLabels" :key="key" :value="key">{{ label }}</option>
                    </select>
                  </div>

                  <p v-if="item.error" class="mt-1 text-xs text-berry">{{ item.error }}</p>
                </div>

                <div class="flex gap-2 pt-1">
                  <button
                    class="focus-ring inline-flex flex-1 items-center justify-center gap-2 rounded-md bg-ink px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
                    type="button"
                    :disabled="files.isUploading || !pendingCount"
                    @click="uploadAll"
                  >
                    <Loader2 v-if="files.isUploading" class="h-4 w-4 animate-spin" />
                    <FileUp v-else class="h-4 w-4" />
                    Upload {{ pendingCount > 0 ? `${pendingCount} file${pendingCount !== 1 ? "s" : ""}` : "all" }}
                  </button>
                  <button
                    class="focus-ring inline-flex items-center justify-center gap-1.5 rounded-md border border-slate-200 px-3 py-2.5 text-sm font-semibold text-graphite hover:bg-slate-50"
                    type="button"
                    :disabled="files.isUploading"
                    @click="files.clearQueue()"
                  >
                    <Trash2 class="h-3.5 w-3.5" />
                    Clear done
                  </button>
                </div>
              </div>
            </div>
          </section>

          <section class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel" :class="isRevisionRequested ? 'ring-2 ring-saffron/40' : ''">
            <div class="flex items-center gap-2">
              <RotateCcw v-if="isRevisionRequested" class="h-5 w-5 text-saffron" />
              <Send v-else class="h-5 w-5 text-signal" />
              <h2 class="text-base font-semibold text-ink">{{ isRevisionRequested ? "Submit revised work" : "Submit work" }}</h2>
            </div>
            <p class="mt-2 text-sm text-graphite">
              <template v-if="isRevisionRequested">
                Upload your revised file above, then re-submit to resolve the revision request.
              </template>
              <template v-else>
                Upload your deliverable file above, then submit to notify the client and trigger approval.
              </template>
            </p>

            <div
              v-if="!hasDeliverable"
              class="mt-4 flex items-start gap-2 rounded-md border border-amber-200 bg-amber-50 px-3 py-2.5 text-xs text-amber-900"
            >
              <AlertCircle class="mt-0.5 h-4 w-4 shrink-0" />
              No deliverable file attached yet. Upload a file with purpose "Deliverable" first.
            </div>

            <label class="mt-4 block">
              <span class="text-xs font-medium text-graphite">Submission note (optional)</span>
              <textarea
                v-model.trim="submissionNote"
                class="focus-ring mt-1 min-h-20 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                placeholder="Any notes for the client or editor…"
              />
            </label>

            <p v-if="submitError" class="mt-3 rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-berry">
              {{ submitError }}
            </p>
            <p v-if="submitNotice" class="mt-3 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs text-signal">
              {{ submitNotice }}
            </p>

            <button
              class="focus-ring mt-4 inline-flex w-full items-center justify-center gap-2 rounded-md bg-signal px-4 py-3 text-sm font-semibold text-white disabled:opacity-60"
              type="button"
              :disabled="isSubmitting || !hasDeliverable"
              @click="submitWork"
            >
              <Loader2 v-if="isSubmitting" class="h-4 w-4 animate-spin" />
              <Send v-else class="h-4 w-4" />
              {{ isSubmitting ? "Submitting…" : isRevisionRequested ? "Submit revised work" : "Submit work" }}
            </button>
          </section>

          <section class="rounded-lg border border-slate-200 bg-white shadow-panel">
            <div class="flex items-center gap-2 border-b border-slate-200 px-5 py-4">
              <MessageSquare class="h-4 w-4 text-signal" />
              <h2 class="text-base font-semibold text-ink">Order thread</h2>
            </div>

            <div class="min-h-40 space-y-3 bg-slate-50 p-4">
              <p v-if="comms.isLoading" class="text-sm text-graphite">Loading messages…</p>
              <p v-else-if="!comms.activeThread" class="text-sm text-graphite">No thread loaded for this order.</p>
              <p v-else-if="!comms.messages.length" class="text-sm text-graphite">No messages in this thread yet.</p>
              <article
                v-for="msg in comms.messages"
                v-else
                :key="msg.id"
                class="rounded-lg border border-slate-200 bg-white p-3"
              >
                <div class="flex items-center justify-between gap-2">
                  <p class="text-xs font-semibold text-ink">{{ msg.sender_display }}</p>
                  <p class="text-xs text-graphite">
                    {{ msg.created_at ? new Intl.DateTimeFormat("en", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }).format(new Date(msg.created_at)) : "" }}
                  </p>
                </div>
                <p class="mt-2 whitespace-pre-wrap text-sm leading-5 text-graphite">{{ msg.body }}</p>
              </article>
            </div>

            <form class="border-t border-slate-200 p-4" @submit.prevent="sendMessage">
              <textarea
                v-model.trim="messageBody"
                class="focus-ring min-h-20 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                placeholder="Ask a question or leave a note for support or the client…"
              />
              <button
                class="focus-ring mt-2 inline-flex w-full items-center justify-center gap-2 rounded-md bg-ink px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
                type="submit"
                :disabled="comms.isSending || !comms.activeThread || !messageBody.trim()"
              >
                <Loader2 v-if="comms.isSending" class="h-4 w-4 animate-spin" />
                <Send v-else class="h-4 w-4" />
                Send
              </button>
            </form>
          </section>
        </aside>
      </div>
    </template>
  </div>
</template>
