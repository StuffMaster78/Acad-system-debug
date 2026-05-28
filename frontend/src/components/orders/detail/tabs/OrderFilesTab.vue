<template>
  <div class="space-y-6">
    <!-- Upload panel -->
    <div class="rounded-lg border border-slate-200 bg-white shadow-panel">
      <div class="border-b border-slate-200 px-5 py-4">
        <h2 class="text-base font-semibold text-ink">Upload files</h2>
        <p class="mt-1 text-xs text-graphite">
          {{ role === 'writer' ? 'Add deliverable and reference files. Set purpose per file.' : 'Attach reference or instruction files.' }}
        </p>
      </div>

      <div class="p-5 space-y-4">
        <!-- Writer: multi-file queue upload -->
        <template v-if="role === 'writer'">
          <div class="grid gap-3 sm:grid-cols-2">
            <label class="block">
              <span class="text-xs font-medium text-graphite">Default purpose</span>
              <select v-model="defaultPurpose" class="focus-ring mt-1 h-9 w-full rounded-md border border-slate-200 px-2 text-sm">
                <option value="order_deliverable">Deliverable</option>
                <option value="order_reference">Reference</option>
                <option value="order_revision">Revision support</option>
                <option value="style_reference">Style reference</option>
              </select>
            </label>
            <label class="block">
              <span class="text-xs font-medium text-graphite">Default visibility</span>
              <select v-model="defaultVisibility" class="focus-ring mt-1 h-9 w-full rounded-md border border-slate-200 px-2 text-sm">
                <option value="order_participants">Order participants</option>
                <option value="client_and_staff">Client & staff</option>
              </select>
            </label>
          </div>

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
                <span class="shrink-0 text-xs font-semibold" :class="queueTone(item)">
                  <Loader2 v-if="item.status === 'uploading'" class="h-3.5 w-3.5 animate-spin" />
                  <CheckCircle2 v-else-if="item.status === 'done'" class="h-3.5 w-3.5 text-signal" />
                  <AlertCircle v-else-if="item.status === 'error'" class="h-3.5 w-3.5 text-berry" />
                  <span v-else class="capitalize text-graphite">{{ item.status }}</span>
                </span>
                <button v-if="item.status !== 'uploading'" class="focus-ring shrink-0 rounded p-0.5 text-slate-400 hover:text-ink" @click="files.removeFromQueue(item.id)">
                  <X class="h-3.5 w-3.5" />
                </button>
              </div>
              <div v-if="item.status === 'pending'" class="mt-2 grid gap-2 sm:grid-cols-2">
                <select :value="item.purpose" class="focus-ring h-8 w-full rounded border border-slate-200 bg-white px-2 text-xs" @change="item.purpose = ($event.target as HTMLSelectElement).value as FilePurpose">
                  <option v-for="(label, key) in purposeLabels" :key="key" :value="key">{{ label }}</option>
                </select>
                <select :value="item.visibility" class="focus-ring h-8 w-full rounded border border-slate-200 bg-white px-2 text-xs" @change="item.visibility = ($event.target as HTMLSelectElement).value as FileVisibility">
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
                @click="files.uploadFiles(orderId)"
              >
                <Loader2 v-if="files.isUploading" class="h-4 w-4 animate-spin" />
                <FileUp v-else class="h-4 w-4" />
                Upload {{ pendingCount > 0 ? `${pendingCount} file${pendingCount !== 1 ? 's' : ''}` : 'all' }}
              </button>
              <button class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-slate-200 px-3 py-2 text-sm text-graphite hover:bg-slate-50 disabled:opacity-50" type="button" :disabled="files.isUploading" @click="files.clearQueue()">
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
              Upload a Deliverable file first.
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
            <div class="mt-3 grid gap-3 sm:grid-cols-2">
              <label class="block">
                <span class="text-xs font-medium text-graphite">Purpose</span>
                <select v-model="singlePurpose" class="focus-ring mt-1 h-9 w-full rounded-md border border-slate-200 px-2 text-sm">
                  <option value="order_reference">Reference</option>
                  <option value="order_instruction">Instruction</option>
                  <option value="style_reference">Style reference</option>
                  <option value="order_revision">Revision support</option>
                </select>
              </label>
              <label class="block">
                <span class="text-xs font-medium text-graphite">Visibility</span>
                <select v-model="singleVisibility" class="focus-ring mt-1 h-9 w-full rounded-md border border-slate-200 px-2 text-sm">
                  <option value="order_participants">Order participants</option>
                  <option value="client_and_staff">Client & staff</option>
                  <option value="owner_only">Owner only</option>
                </select>
              </label>
            </div>
            <button class="focus-ring mt-3 inline-flex items-center gap-2 rounded-md border border-slate-300 px-4 py-2 text-sm font-semibold text-ink disabled:opacity-60" type="submit" :disabled="files.isUploading || !singleFile">
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
    <div class="rounded-lg border border-slate-200 bg-white shadow-panel">
      <div class="border-b border-slate-200 px-5 py-4">
        <h2 class="text-base font-semibold text-ink">Attached files</h2>
      </div>
      <div v-if="files.isLoadingAttachments" class="px-5 py-6 text-sm text-graphite">Loading…</div>
      <div v-else-if="!files.attachments.length" class="px-5 py-8 text-center text-sm text-graphite">No files attached yet.</div>
      <div v-else class="divide-y divide-slate-100">
        <div v-for="att in files.attachments" :key="att.id" class="flex items-center gap-4 px-5 py-3">
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-medium text-ink">
              {{ att.managed_file?.original_filename ?? `File #${att.id}` }}
            </p>
            <p class="mt-0.5 text-xs text-graphite">
              {{ purposeLabels[att.purpose as FilePurpose] ?? att.purpose }}
              <span v-if="att.visibility"> · {{ att.visibility }}</span>
              <span v-if="att.managed_file?.file_size_bytes"> · {{ fileSize(att.managed_file.file_size_bytes) }}</span>
            </p>
          </div>
          <!-- Staff: show scan status (TODO: add virus_scan_status to managed file type server-side) -->
          <a
            v-if="att.managed_file?.download_url || att.managed_file?.public_url"
            :href="att.managed_file.download_url || att.managed_file.public_url || filesApi.downloadUrl(att.id)"
            target="_blank"
            rel="noreferrer"
            class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-slate-200 px-3 py-1.5 text-xs font-semibold text-ink hover:bg-slate-50"
          >
            <Download class="h-3.5 w-3.5" />
            Download
          </a>
          <span v-else class="text-xs text-slate-400">Preview only</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { AlertCircle, CheckCircle2, Download, FileUp, Loader2, Plus, Send, Trash2, X } from "@lucide/vue";
import type { UserRole } from "@/types/roles";
import type { OrderSummary, OrderLifecycle } from "@/types/orders";
import { filesApi, type FilePurpose, type FileVisibility } from "@/api/files";
import { writerApi } from "@/api/writer";
import { useFilesStore, type QueuedFile } from "@/stores/files";
import { isStaff } from "../types";

const props = defineProps<{
  orderId: string;
  order: OrderSummary;
  lifecycle: OrderLifecycle | null;
  role: UserRole;
}>();

const files = useFilesStore();
const isStaffRole = computed(() => isStaff(props.role));

const hasRevision = computed(() =>
  props.order.status === "revision_requested" ||
  (props.lifecycle?.latest_revision_status != null &&
    !["resolved", "rejected", "withdrawn"].includes(props.lifecycle.latest_revision_status ?? ""))
);

// ── Writer multi-file queue ──────────────────────────────────────────────────
const defaultPurpose = ref<FilePurpose>("order_deliverable");
const defaultVisibility = ref<FileVisibility>("order_participants");

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

function onFilePick(event: Event) {
  const input = event.target as HTMLInputElement;
  if (!input.files?.length) return;
  files.addToQueue(input.files, { purpose: defaultPurpose.value, visibility: defaultVisibility.value });
  input.value = "";
}

function queueTone(item: QueuedFile) {
  if (item.status === "done") return "text-signal";
  if (item.status === "error") return "text-berry";
  if (item.status === "uploading") return "text-saffron";
  return "text-graphite";
}

const pendingCount = computed(() => files.uploadQueue.filter((q) => q.status === "pending").length);
const hasDeliverable = computed(() =>
  files.attachments.some((a) => a.purpose === "order_deliverable") ||
  files.uploadQueue.some((q) => q.status === "done" && q.purpose === "order_deliverable")
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
    submitNotice.value = data.message ?? "Work submitted.";
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
const singleVisibility = ref<FileVisibility>("order_participants");

function onSinglePick(event: Event) {
  const input = event.target as HTMLInputElement;
  singleFile.value = input.files?.[0] ?? null;
  files.clearMessages();
}

async function singleUpload() {
  if (!singleFile.value) return;
  await files.uploadAndAttachToOrder({ orderId: props.orderId, file: singleFile.value, purpose: singlePurpose.value, visibility: singleVisibility.value });
  singleFile.value = null;
}
</script>
