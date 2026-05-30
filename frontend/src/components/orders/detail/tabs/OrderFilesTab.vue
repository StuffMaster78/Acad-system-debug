<template>
  <div class="space-y-4">
    <!-- Upload panel -->
    <div class="rounded-lg border border-slate-200 bg-white">
      <div class="border-b border-slate-200 px-5 py-4">
        <h2 class="text-base font-semibold text-ink">Upload files</h2>
        <p class="mt-1 text-xs text-graphite">
          {{ role === 'writer' ? 'Upload your draft or final deliverable, plus any supporting files.' : 'Attach reference or instruction files.' }}
        </p>
      </div>

      <div class="p-5 space-y-4">
        <!-- Writer: multi-file queue upload -->
        <template v-if="role === 'writer'">
          <label class="block">
            <span class="text-xs font-medium text-graphite">Default purpose</span>
            <select v-model="defaultPurpose" class="focus-ring mt-1 h-9 w-full rounded-md border border-slate-200 px-2 text-sm">
              <option value="order_final">Final deliverable</option>
              <option value="order_draft">Draft</option>
              <option value="order_revision">Revision support</option>
              <option value="order_reference">Reference</option>
              <option value="style_reference">Style reference</option>
            </select>
          </label>

          <label class="flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed border-slate-300 p-6 text-center hover:border-slate-400 hover:bg-slate-50">
            <Plus class="h-6 w-6 text-slate-400" />
            <span class="text-sm font-medium text-ink">Add files</span>
            <span class="text-xs text-graphite">Click to browse — multiple files supported</span>
            <input class="sr-only" type="file" multiple @change="onFilePick" />
          </label>

          <div v-if="files.uploadQueue.length" class="space-y-2">
            <div v-for="item in files.uploadQueue" :key="item.id" class="rounded-md border border-slate-200 bg-slate-50 p-3">
              <div class="flex items-center gap-3">
                <div class="min-w-0 flex-1">
                  <p class="truncate text-sm font-medium text-ink">{{ item.file.name }}</p>
                  <p class="mt-0.5 text-xs text-graphite">{{ fileSize(item.file.size) }}</p>
                </div>
                <span class="shrink-0" :class="queueTone(item)">
                  <Loader2 v-if="item.status === 'uploading'" class="h-3.5 w-3.5 animate-spin" />
                  <CheckCircle2 v-else-if="item.status === 'done'" class="h-3.5 w-3.5" />
                  <AlertCircle v-else-if="item.status === 'error'" class="h-3.5 w-3.5" />
                  <span v-else class="text-xs capitalize text-graphite">{{ item.status }}</span>
                </span>
                <button
                  v-if="item.status !== 'uploading'"
                  class="focus-ring shrink-0 rounded p-0.5 text-slate-400 hover:text-ink"
                  @click="files.removeFromQueue(item.id)"
                >
                  <X class="h-3.5 w-3.5" />
                </button>
              </div>
              <div v-if="item.status === 'pending'" class="mt-2">
                <select
                  :value="item.purpose"
                  class="focus-ring h-8 w-full rounded border border-slate-200 bg-white px-2 text-xs"
                  @change="item.purpose = ($event.target as HTMLSelectElement).value as FilePurpose"
                >
                  <option value="order_final">Final deliverable</option>
                  <option value="order_draft">Draft</option>
                  <option value="order_revision">Revision support</option>
                  <option value="order_reference">Reference</option>
                  <option value="style_reference">Style reference</option>
                </select>
              </div>
              <p v-if="item.error" class="mt-1 text-xs text-berry">{{ item.error }}</p>
            </div>

            <div class="flex gap-2 pt-1">
              <button
                class="focus-ring inline-flex flex-1 items-center justify-center gap-2 rounded-md bg-ink px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
                type="button"
                :disabled="files.isUploading || !pendingCount"
                @click="files.uploadFiles(orderId)"
              >
                <Loader2 v-if="files.isUploading" class="h-4 w-4 animate-spin" />
                <FileUp v-else class="h-4 w-4" />
                Upload {{ pendingCount > 0 ? `${pendingCount} file${pendingCount !== 1 ? 's' : ''}` : 'all' }}
              </button>
              <button
                class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-slate-200 px-3 py-2 text-sm text-graphite hover:bg-slate-50 disabled:opacity-50"
                type="button"
                :disabled="files.isUploading"
                @click="files.clearQueue()"
              >
                <Trash2 class="h-3.5 w-3.5" />
              </button>
            </div>
          </div>

          <!-- Writer submit work -->
          <div class="border-t border-slate-200 pt-4">
            <div class="flex items-center gap-2">
              <Send class="h-5 w-5 text-signal" />
              <h3 class="text-sm font-semibold text-ink">{{ hasRevision ? 'Submit revised work' : 'Submit work' }}</h3>
            </div>
            <div v-if="!hasDeliverable" class="mt-3 flex items-start gap-2 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-900">
              <AlertCircle class="mt-0.5 h-4 w-4 shrink-0" />
              Upload a Final deliverable or Draft first.
            </div>
            <label class="mt-3 block">
              <span class="text-xs font-medium text-graphite">Submission note (optional)</span>
              <textarea v-model.trim="submissionNote" class="focus-ring mt-1 min-h-16 w-full rounded-md border border-slate-200 px-3 py-2 text-sm" placeholder="Any notes for the client or editor…" />
            </label>
            <p v-if="submitError" class="mt-2 text-xs text-berry">{{ submitError }}</p>
            <p v-if="submitNotice" class="mt-2 text-xs text-signal">{{ submitNotice }}</p>
            <button
              class="focus-ring mt-3 inline-flex w-full items-center justify-center gap-2 rounded-md bg-signal px-4 py-3 text-sm font-semibold text-white disabled:opacity-60"
              type="button"
              :disabled="isSubmitting || !hasDeliverable"
              @click="submitWork"
            >
              <Loader2 v-if="isSubmitting" class="h-4 w-4 animate-spin" />
              <Send v-else class="h-4 w-4" />
              {{ hasRevision ? 'Submit revised work' : 'Submit work' }}
            </button>
          </div>
        </template>

        <!-- Client/staff: single file upload -->
        <template v-else>
          <form @submit.prevent="singleUpload">
            <label class="block text-sm font-medium text-ink">
              File
              <input class="focus-ring mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm" type="file" @change="onSinglePick" />
            </label>
            <div class="mt-3">
              <span class="text-xs font-medium text-graphite">Purpose</span>
              <select v-model="singlePurpose" class="focus-ring mt-1 h-9 w-full rounded-md border border-slate-200 px-2 text-sm">
                <option value="order_reference">Reference</option>
                <option value="order_instruction">Instruction</option>
                <option value="style_reference">Style reference</option>
                <option value="order_revision">Revision support</option>
              </select>
            </div>
            <button
              class="focus-ring mt-3 inline-flex items-center gap-2 rounded-md border border-slate-300 px-4 py-2 text-sm font-semibold text-ink disabled:opacity-60"
              type="submit"
              :disabled="files.isUploading || !singleFile"
            >
              <Loader2 v-if="files.isUploading" class="h-4 w-4 animate-spin" />
              <FileUp class="h-4 w-4" />
              Attach file
            </button>
          </form>
        </template>

        <div v-if="files.error" class="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-berry">{{ files.error }}</div>
        <div v-if="files.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-signal">{{ files.notice }}</div>
      </div>
    </div>

    <!-- Attached files list -->
    <div class="rounded-lg border border-slate-200 bg-white">
      <div class="border-b border-slate-200 px-5 py-4">
        <h2 class="text-base font-semibold text-ink">Attached files</h2>
        <p class="mt-0.5 text-xs text-graphite">{{ files.attachments.length }} file{{ files.attachments.length !== 1 ? 's' : '' }} attached</p>
      </div>
      <div v-if="files.isLoadingAttachments" class="space-y-px">
        <div v-for="n in 3" :key="n" class="animate-pulse px-5 py-4">
          <div class="h-3 w-48 rounded bg-slate-200" />
          <div class="mt-2 h-3 w-32 rounded bg-slate-100" />
        </div>
      </div>
      <div v-else-if="!files.attachments.length" class="px-5 py-10 text-center">
        <Paperclip class="mx-auto mb-2 size-7 text-slate-300" />
        <p class="text-sm text-graphite">No files attached yet.</p>
      </div>
      <!-- Delivery blocked banner -->
      <div
        v-if="files.deliveryBlocked"
        class="mx-4 mb-2 mt-1 rounded-md border border-amber-200 bg-amber-50 px-4 py-3"
      >
        <p class="text-sm font-semibold text-amber-900">
          <template v-if="files.deliveryBlocked.blocked_reason === 'balance_due'">
            Download locked — outstanding balance
            <span v-if="files.deliveryBlocked.amount_due" class="font-bold">
              ({{ files.deliveryBlocked.amount_due }} remaining)
            </span>
          </template>
          <template v-else-if="files.deliveryBlocked.blocked_reason === 'scan_pending'">
            File is being scanned — download available once scan passes.
          </template>
          <template v-else-if="files.deliveryBlocked.blocked_reason === 'not_submitted'">
            The writer has not yet submitted this file for delivery.
          </template>
          <template v-else>
            Download not available: {{ files.deliveryBlocked.blocked_reason.replace(/_/g, ' ') }}
          </template>
        </p>
        <button
          v-if="files.deliveryBlocked.blocked_reason === 'balance_due'"
          class="focus-ring mt-2 inline-flex items-center gap-1.5 rounded-md bg-amber-700 px-3 py-1.5 text-xs font-semibold text-white hover:bg-amber-800"
          @click="emit('go-to-payments')"
        >
          Pay remaining balance
        </button>
      </div>

      <div v-else class="divide-y divide-slate-100">
        <div v-for="att in files.attachments" :key="att.id" class="flex items-start gap-4 px-5 py-4">
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-medium text-ink">
              {{ att.display_name ?? att.managed_file?.original_filename ?? att.external_link?.title ?? `Attachment #${att.id}` }}
            </p>
            <div class="mt-1 flex flex-wrap items-center gap-2 text-xs text-graphite">
              <span class="capitalize">{{ purposeLabel(att.purpose) }}</span>
              <span v-if="att.managed_file?.file_size_bytes"> · {{ fileSize(att.managed_file.file_size_bytes) }}</span>
              <!-- Scan status badge -->
              <span
                v-if="att.managed_file?.scan_status && att.managed_file.scan_status !== 'not_scanned'"
                class="rounded-full px-1.5 py-0.5 text-xs font-semibold"
                :class="scanBadge(att.managed_file.scan_status)"
              >
                {{ att.managed_file.scan_status.replace(/_/g, ' ') }}
              </span>
              <!-- Delivery status badge (final files) -->
              <span
                v-if="att.purpose === 'order_final' && att.delivery_status"
                class="rounded-full px-1.5 py-0.5 text-xs font-semibold"
                :class="deliveryBadge(att.delivery_status)"
              >
                {{ deliveryLabel(att.delivery_status) }}
              </span>
              <!-- External link indicator -->
              <span v-if="att.external_link" class="rounded-full bg-blue-100 px-1.5 py-0.5 text-xs font-semibold text-blue-700">
                External link
              </span>
            </div>
          </div>

          <div class="flex shrink-0 items-center gap-2">
            <!-- Writer: Submit Final action for unsubmitted final files -->
            <button
              v-if="role === 'writer' && att.purpose === 'order_final' && !att.is_submitted"
              class="focus-ring inline-flex items-center gap-1.5 rounded-md bg-signal px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-700 disabled:opacity-60"
              :disabled="submittingFinal === att.id"
              @click="submitFinal(att.id)"
            >
              <Loader2 v-if="submittingFinal === att.id" class="h-3.5 w-3.5 animate-spin" />
              <Send v-else class="h-3.5 w-3.5" />
              Submit for delivery
            </button>

            <!-- Download -->
            <a
              v-if="att.external_link?.url"
              :href="att.external_link.url"
              target="_blank"
              rel="noreferrer"
              class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-slate-200 px-3 py-1.5 text-xs font-semibold text-ink hover:bg-slate-50"
            >
              <ExternalLink class="h-3.5 w-3.5" />
              Open
            </a>
            <!-- Locked final file (client sees it but cannot download until paid) -->
            <span
              v-else-if="att.purpose === 'order_final' && role === 'client' && att.delivery_status && att.delivery_status !== 'approved'"
              class="inline-flex items-center gap-1.5 rounded-md border border-amber-200 bg-amber-50 px-3 py-1.5 text-xs font-semibold text-amber-700"
            >
              <Lock class="h-3.5 w-3.5" />
              {{ att.delivery_status === 'pending' || att.delivery_status === 'submitted' ? 'Payment required' : deliveryLabel(att.delivery_status) }}
            </span>
            <button
              v-else-if="att.managed_file && att.managed_file.scan_status !== 'infected'"
              class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-slate-200 px-3 py-1.5 text-xs font-semibold text-ink hover:bg-slate-50"
              :disabled="downloading === att.id"
              @click="download(att.id)"
            >
              <Loader2 v-if="downloading === att.id" class="h-3.5 w-3.5 animate-spin" />
              <Download v-else class="h-3.5 w-3.5" />
              Download
            </button>
            <span v-else-if="att.managed_file?.scan_status === 'infected'" class="text-xs font-semibold text-rose-600">
              Blocked
            </span>

            <!-- Delete request -->
            <button
              v-if="canRequestDeletion"
              class="focus-ring rounded p-1.5 text-slate-400 hover:text-rose-500"
              :title="deletingId === att.id ? 'Cancelling…' : 'Request deletion'"
              @click="openDeletePrompt(att.id)"
            >
              <Trash2 class="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete confirmation overlay -->
    <div v-if="deletingId !== null" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div class="w-full max-w-md rounded-lg border border-slate-200 bg-white p-6 shadow-xl">
        <h3 class="text-base font-semibold text-ink">Request file deletion</h3>
        <p class="mt-1 text-sm text-graphite">This submits a deletion request to staff. Provide a reason.</p>
        <textarea
          v-model.trim="deleteReason"
          class="focus-ring mt-4 min-h-20 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
          placeholder="Reason for deletion…"
        />
        <div class="mt-4 flex gap-3">
          <button
            class="focus-ring flex-1 rounded-md bg-rose-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
            :disabled="!deleteReason || deletingInFlight"
            @click="confirmDelete"
          >
            <Loader2 v-if="deletingInFlight" class="inline h-4 w-4 animate-spin" />
            <span v-else>Submit request</span>
          </button>
          <button
            class="focus-ring rounded-md border border-slate-200 px-4 py-2 text-sm font-semibold text-graphite hover:bg-slate-50"
            @click="cancelDelete"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import {
  AlertCircle, CheckCircle2, Download, ExternalLink,
  FileUp, Loader2, Lock, Paperclip, Plus, Send, Trash2, X,
} from "@lucide/vue";
import type { UserRole } from "@/types/roles";
import type { OrderSummary, OrderLifecycle } from "@/types/orders";
import { type DeliveryStatus, type FilePurpose } from "@/api/files";
import { writerApi } from "@/api/writer";
import { useFilesStore, type QueuedFile } from "@/stores/files";
import { isStaff } from "../types";

const props = defineProps<{
  orderId: string;
  order: OrderSummary;
  lifecycle: OrderLifecycle | null;
  role: UserRole;
}>();

const emit = defineEmits<{
  (e: "go-to-payments"): void;
}>();

const files = useFilesStore();
const isStaffRole = computed(() => isStaff(props.role));
const canRequestDeletion = computed(() => props.role === "client" || isStaffRole.value);

const hasRevision = computed(() =>
  props.order.status === "revision_requested" ||
  (props.lifecycle?.latest_revision_status != null &&
    !["resolved", "rejected", "withdrawn"].includes(props.lifecycle.latest_revision_status ?? ""))
);

// ── Helpers ──────────────────────────────────────────────────────────────────

function fileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

const PURPOSE_LABELS: Record<string, string> = {
  order_instruction: "Instruction",
  order_reference: "Reference",
  order_draft: "Draft",
  order_final: "Final deliverable",
  order_revision: "Revision support",
  style_reference: "Style reference",
  extra_service_file: "Extra service",
  message_attachment: "Message attachment",
};

function purposeLabel(p: string): string {
  return PURPOSE_LABELS[p] ?? p.replace(/_/g, " ");
}

function scanBadge(status: string): string {
  if (status === "clean") return "bg-emerald-100 text-emerald-700";
  if (status === "infected") return "bg-rose-100 text-rose-700";
  if (status === "scanning") return "bg-blue-100 text-blue-700";
  return "bg-amber-100 text-amber-700";
}

function queueTone(item: QueuedFile): string {
  if (item.status === "done") return "text-signal";
  if (item.status === "error") return "text-berry";
  if (item.status === "uploading") return "text-saffron";
  return "text-graphite";
}

// ── Writer multi-file queue ──────────────────────────────────────────────────
const defaultPurpose = ref<FilePurpose>("order_final");

function onFilePick(event: Event) {
  const input = event.target as HTMLInputElement;
  if (!input.files?.length) return;
  files.addToQueue(input.files, defaultPurpose.value);
  input.value = "";
}

const pendingCount = computed(() => files.uploadQueue.filter((q) => q.status === "pending").length);

const hasDeliverable = computed(() =>
  files.attachments.some((a) => a.purpose === "order_final" || a.purpose === "order_draft") ||
  files.uploadQueue.some((q) => q.status === "done" && (q.purpose === "order_final" || q.purpose === "order_draft"))
);

// ── Writer submit work ───────────────────────────────────────────────────────
const submissionNote = ref("");
const isSubmitting = ref(false);
const submitError = ref("");
const submitNotice = ref("");

async function submitWork() {
  submitError.value = "";
  submitNotice.value = "";
  isSubmitting.value = true;
  try {
    const { data } = await writerApi.submitOrder(props.orderId, { note: submissionNote.value || undefined });
    submitNotice.value = (data as { message?: string }).message ?? "Work submitted.";
    submissionNote.value = "";
  } catch {
    submitError.value = "Submission failed. Make sure a deliverable file is uploaded first.";
  } finally {
    isSubmitting.value = false;
  }
}

// ── Client single upload ─────────────────────────────────────────────────────
const singleFile = ref<File | null>(null);
const singlePurpose = ref<FilePurpose>("order_reference");

function onSinglePick(event: Event) {
  const input = event.target as HTMLInputElement;
  singleFile.value = input.files?.[0] ?? null;
  files.clearMessages();
}

async function singleUpload() {
  if (!singleFile.value) return;
  await files.uploadSingleFile(props.orderId, singleFile.value, singlePurpose.value);
  singleFile.value = null;
}

// ── Delivery helpers ─────────────────────────────────────────────────────────

const DELIVERY_LABELS: Record<DeliveryStatus, string> = {
  pending:   "Awaiting submission",
  submitted: "Submitted",
  locked:    "Payment required",
  approved:  "Ready to download",
  rejected:  "Rejected",
};

function deliveryLabel(s: DeliveryStatus): string {
  return DELIVERY_LABELS[s] ?? s.replace(/_/g, " ");
}

function deliveryBadge(s: DeliveryStatus): string {
  if (s === "approved")  return "bg-emerald-100 text-emerald-700";
  if (s === "submitted") return "bg-blue-100 text-blue-700";
  if (s === "rejected")  return "bg-rose-100 text-rose-700";
  return "bg-amber-100 text-amber-700";
}

// ── Submit final (writer) ────────────────────────────────────────────────────
const submittingFinal = ref<number | null>(null);

async function submitFinal(attachmentId: number) {
  submittingFinal.value = attachmentId;
  await files.submitFinalFile(props.orderId, attachmentId);
  submittingFinal.value = null;
}

// ── Download ─────────────────────────────────────────────────────────────────
const downloading = ref<number | null>(null);

async function download(attachmentId: number) {
  downloading.value = attachmentId;
  try {
    await files.downloadFile(props.orderId, attachmentId);
  } finally {
    downloading.value = null;
  }
}

// ── Delete request ────────────────────────────────────────────────────────────
const deletingId = ref<number | null>(null);
const deleteReason = ref("");
const deletingInFlight = ref(false);

function openDeletePrompt(id: number) {
  deletingId.value = id;
  deleteReason.value = "";
}

function cancelDelete() {
  deletingId.value = null;
  deleteReason.value = "";
}

async function confirmDelete() {
  if (!deletingId.value || !deleteReason.value) return;
  deletingInFlight.value = true;
  try {
    await files.requestFileDeletion(props.orderId, deletingId.value, deleteReason.value);
    deletingId.value = null;
    deleteReason.value = "";
  } finally {
    deletingInFlight.value = false;
  }
}
</script>
