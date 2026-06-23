<template>
  <div class="space-y-0 divide-y divide-slate-100 rounded-xl border border-slate-200 bg-white overflow-hidden">

    <!-- System notices -->
    <div v-if="files.error" class="flex items-center gap-2 bg-rose-50 px-5 py-3 text-sm text-rose-700">
      <AlertCircle class="h-4 w-4 shrink-0" />{{ files.error }}
    </div>
    <div v-if="files.notice" class="flex items-center gap-2 bg-emerald-50 px-5 py-3 text-sm text-emerald-700">
      <CheckCircle2 class="h-4 w-4 shrink-0" />{{ files.notice }}
    </div>

    <!-- ════════════════════════════════════════════════════════
         SECTION 1 — FINAL DELIVERY  (most prominent)
         Only shown when a final file exists or writer can upload
         ════════════════════════════════════════════════════════ -->
    <section>
      <SectionHeader icon-class="text-emerald-600" :count="finalFiles.length">
        <template #icon><Trophy class="h-4 w-4" /></template>
        Final Delivery
        <template #badge><span class="rounded-full border border-emerald-300 bg-emerald-50 px-2 py-0.5 text-[10px] font-semibold text-emerald-700">Client + Writer + Staff</span></template>
        <template #desc>The delivered work. Client can download once submitted and approved.</template>
      </SectionHeader>

      <!-- Writer upload for final -->
      <div v-if="role === 'writer' || isStaffRole" class="border-b border-slate-100 bg-slate-50/60 px-5 py-4">
        <MultiUploadZone
          purpose="order_final"
          label="Upload final deliverable"
          accept=".pdf,.doc,.docx,.zip,.pptx,.xlsx"
          :order-id="orderId"
          :uploading="files.isUploading"
          @pick="(files_) => files.addToQueue(files_, 'order_final')"
          @upload="files.uploadFiles(orderId)"
        />
        <!-- Upload queue -->
        <UploadQueue v-if="files.uploadQueue.length" :queue="files.uploadQueue" class="mt-3" />
      </div>

      <!-- No final file yet -->
      <div v-if="!finalFiles.length" class="px-5 py-10 text-center">
        <Trophy class="mx-auto h-8 w-8 text-slate-200" />
        <p class="mt-2 text-sm font-medium text-graphite">No final file yet</p>
        <p class="text-xs text-slate-400">The writer's completed work will appear here.</p>
      </div>

      <!-- Final file card(s) — BIG, prominent -->
      <div v-else class="divide-y divide-emerald-100">
        <div v-for="att in finalFiles" :key="att.id"
          class="relative px-5 py-5"
          :class="att.delivery_status === 'approved' ? 'bg-emerald-50' : att.delivery_status === 'submitted' ? 'bg-blue-50' : 'bg-white'">

          <!-- Final badge ribbon -->
          <div class="mb-3 flex items-center gap-2">
            <span class="inline-flex items-center gap-1.5 rounded-full bg-emerald-600 px-3 py-1 text-xs font-bold text-white">
              <CheckCircle2 class="h-3.5 w-3.5" /> FINAL DELIVERY
            </span>
            <span v-if="att.revision_cycle && att.revision_cycle > 0"
              class="rounded-full bg-amber-100 px-2.5 py-0.5 text-[10px] font-bold text-amber-800">
              Revision {{ att.revision_cycle }}
            </span>
            <span :class="deliveryBadge(att.delivery_status as any)"
              class="ml-auto rounded-full px-2.5 py-0.5 text-[10px] font-semibold">
              {{ deliveryLabel(att.delivery_status as any) }}
            </span>
          </div>

          <!-- File info row -->
          <div class="flex items-center gap-4">
            <FileTypeIcon :attachment="att" size="lg" />
            <div class="min-w-0 flex-1">
              <p class="text-base font-semibold text-ink truncate">
                {{ fileName(att) }}
              </p>
              <div class="mt-1 flex flex-wrap items-center gap-3 text-xs text-graphite">
                <span v-if="att.managed_file?.file_size_bytes">{{ fileSize(att.managed_file.file_size_bytes) }}</span>
                <span>{{ fmtDate(att.attached_at) }}</span>
                <UploaderBadge :name="att.attached_by_name" :role="att.attached_by_role" />
                <span v-if="att.first_downloaded_at" class="text-emerald-600 font-medium">
                  ✓ Downloaded {{ fmtDate(att.first_downloaded_at) }}
                </span>
                <span v-else-if="att.is_new_for_user" class="rounded-full bg-saffron px-2 py-0.5 text-[10px] font-bold text-white">New</span>
              </div>
            </div>
            <!-- Actions -->
            <div class="flex shrink-0 items-center gap-2">
              <button v-if="att.delivery_status === 'approved' || att.delivery_status === 'submitted'"
                class="focus-ring inline-flex h-9 items-center gap-2 rounded-lg bg-emerald-600 px-4 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
                :disabled="downloading === att.id"
                @click="download(att.id)">
                <Loader2 v-if="downloading === att.id" class="h-4 w-4 animate-spin" />
                <Download v-else class="h-4 w-4" />
                Download
              </button>
              <button v-else-if="(role === 'writer' || isStaffRole) && att.delivery_status === 'pending'"
                class="focus-ring inline-flex h-9 items-center gap-2 rounded-lg border border-signal px-4 text-sm font-semibold text-signal hover:bg-signal hover:text-white disabled:opacity-50"
                :disabled="submittingFinal === att.id"
                @click="submitFinal(att.id)">
                <Loader2 v-if="submittingFinal === att.id" class="h-3.5 w-3.5 animate-spin" />
                <Send v-else class="h-3.5 w-3.5" />
                Submit for delivery
              </button>
              <DeleteRequestButton :attachment-id="att.id" :order-id="orderId" :can-delete="canRequestDeletion" />
            </div>
          </div>

          <!-- Delivery guard warning -->
          <div v-if="att.delivery_status === 'locked'"
            class="mt-3 flex items-center justify-between rounded-lg border border-amber-200 bg-amber-50 px-4 py-2.5 text-sm">
            <span class="text-amber-800">Payment required before this file can be downloaded.</span>
            <button class="text-xs font-semibold text-amber-700 underline" @click="emit('go-to-payments')">
              Go to payments
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- ════════════════════════════════════════════════════════
         SECTION 2 — CLIENT MATERIALS
         ════════════════════════════════════════════════════════ -->
    <section>
      <SectionHeader icon-class="text-slate-500" :count="clientMaterials.length">
        <template #icon><Paperclip class="h-4 w-4" /></template>
        Client Materials
        <template #badge><span class="rounded-full border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-[10px] font-semibold text-emerald-700">All participants</span></template>
        <template #desc>Instructions, samples, outlines, and other files provided by the client.</template>
      </SectionHeader>

      <div v-if="role === 'client' || isStaffRole" class="border-b border-slate-100 bg-slate-50/60 px-5 py-4">
        <form class="flex flex-wrap items-end gap-3" @submit.prevent="clientUpload">
          <div class="flex-1 min-w-48">
            <label class="block text-xs font-medium text-graphite mb-1">File(s)</label>
            <input ref="clientFileInput" type="file" multiple
              class="focus-ring block w-full rounded-md border border-slate-200 px-2 py-1.5 text-xs"
              @change="onClientFilePick" />
          </div>
          <div class="w-48">
            <label class="block text-xs font-medium text-graphite mb-1">Type</label>
            <select v-model="clientPurpose"
              class="focus-ring h-9 w-full rounded-md border border-slate-200 bg-white px-2 text-xs">
              <option value="order_instruction">📋 Instruction</option>
              <option value="order_sample">📄 Sample / Example</option>
              <option value="order_outline">📝 Outline</option>
              <option value="order_questionnaire">❓ Questionnaire</option>
              <option value="order_notes">🗒️ Notes</option>
              <option value="order_class_material">🎓 Class Material</option>
              <option value="order_reference">🔗 Reference</option>
            </select>
          </div>
          <button type="submit"
            class="focus-ring h-9 rounded-md bg-ink px-4 text-xs font-semibold text-white disabled:opacity-50"
            :disabled="!clientFiles.length || files.isUploading">
            <Loader2 v-if="files.isUploading" class="inline h-3 w-3 animate-spin mr-1" />
            Upload {{ clientFiles.length > 1 ? `${clientFiles.length} files` : 'file' }}
          </button>
        </form>
        <p v-if="clientFiles.length > 1" class="mt-1.5 text-[10px] text-graphite">
          {{ clientFiles.map(f => f.name).join(', ') }}
        </p>
      </div>

      <div v-if="!clientMaterials.length" class="px-5 py-8 text-center text-xs text-graphite">
        No client materials yet.
      </div>
      <div v-else class="divide-y divide-slate-50">
        <FileTile v-for="att in clientMaterials" :key="att.id"
          :att="att" :order-id="orderId" :role="role"
          :downloading="downloading" :can-delete="canRequestDeletion"
          @download="download" @request-delete="openDeletePrompt" />
      </div>
    </section>

    <!-- ════════════════════════════════════════════════════════
         SECTION 3 — DRAFTS  (writer work in progress)
         ════════════════════════════════════════════════════════ -->
    <section>
      <SectionHeader icon-class="text-blue-500" :count="draftFiles.length">
        <template #icon><FileEdit class="h-4 w-4" /></template>
        Drafts
        <template #badge><span class="rounded-full border border-blue-200 bg-blue-50 px-2 py-0.5 text-[10px] font-semibold text-blue-700">Client + Staff</span></template>
        <template #desc>Work-in-progress drafts shared with the client for feedback before final delivery.</template>
      </SectionHeader>

      <div v-if="role === 'writer' || isStaffRole" class="border-b border-slate-100 bg-slate-50/60 px-5 py-4">
        <MultiUploadZone
          purpose="order_draft"
          label="Upload draft"
          :order-id="orderId"
          :uploading="files.isUploading"
          @pick="(f) => files.addToQueue(f, 'order_draft')"
          @upload="files.uploadFiles(orderId)"
        />
        <UploadQueue v-if="files.uploadQueue.filter(q => q.purpose === 'order_draft').length"
          :queue="files.uploadQueue.filter(q => q.purpose === 'order_draft')" class="mt-3" />
      </div>

      <div v-if="!draftFiles.length" class="px-5 py-8 text-center text-xs text-graphite">No drafts uploaded yet.</div>
      <div v-else class="divide-y divide-slate-50">
        <FileTile v-for="att in draftFiles" :key="att.id"
          :att="att" :order-id="orderId" :role="role"
          :downloading="downloading" :can-delete="canRequestDeletion"
          @download="download" @request-delete="openDeletePrompt" />
      </div>

      <!-- Submit work panel (writer) -->
      <div v-if="role === 'writer' && (draftFiles.length || finalFiles.length)"
        class="border-t border-slate-100 bg-slate-50 px-5 py-4">
        <p class="mb-2 text-xs font-semibold text-ink">Ready to submit?</p>
        <p class="mb-3 text-xs text-graphite">Upload a Final Delivery file above, mark it as submitted, then click below to notify the client.</p>
        <div class="flex flex-wrap items-center gap-3">
          <input v-model="submissionNote" type="text" placeholder="Optional note to client…"
            class="focus-ring h-8 flex-1 min-w-48 rounded-md border border-slate-200 px-3 text-xs" />
          <button class="focus-ring h-8 rounded-md bg-signal px-4 text-xs font-semibold text-white disabled:opacity-50"
            :disabled="isSubmitting" @click="submitWork">
            <Loader2 v-if="isSubmitting" class="inline h-3 w-3 animate-spin mr-1" />
            Submit work
          </button>
        </div>
        <p v-if="submitError" class="mt-1 text-xs text-rose-600">{{ submitError }}</p>
        <p v-if="submitNotice" class="mt-1 text-xs text-emerald-600">{{ submitNotice }}</p>
      </div>
    </section>

    <!-- ════════════════════════════════════════════════════════
         SECTION 4 — REVISION FILES  (grouped by round)
         ════════════════════════════════════════════════════════ -->
    <section v-if="hasRevision || revisionFilesByRound.length">
      <SectionHeader icon-class="text-amber-600" :count="allRevisionFiles.length">
        <template #icon><RotateCcw class="h-4 w-4" /></template>
        Revision Files
        <template #badge><span class="rounded-full border border-amber-300 bg-amber-50 px-2 py-0.5 text-[10px] font-semibold text-amber-700">All participants</span></template>
        <template #desc>Files uploaded specifically for this revision round. Separate from original delivery files.</template>
      </SectionHeader>

      <!-- Writer upload for active revision -->
      <div v-if="hasRevision && (role === 'writer' || isStaffRole)"
        class="border-b border-slate-100 bg-amber-50/40 px-5 py-4">
        <div class="mb-2 flex items-center gap-2">
          <span class="rounded-full bg-amber-500 px-2 py-0.5 text-[10px] font-bold text-white">
            Revision Round {{ currentRevisionCycle }}
          </span>
          <span class="text-xs text-amber-700">Files uploaded here are tagged to this revision round.</span>
        </div>
        <MultiUploadZone
          purpose="order_revision"
          label="Upload revision file"
          :order-id="orderId"
          :uploading="files.isUploading"
          @pick="(f) => files.addToQueue(f, 'order_revision')"
          @upload="files.uploadFiles(orderId)"
        />
      </div>

      <div v-if="!allRevisionFiles.length" class="px-5 py-8 text-center text-xs text-graphite">
        No revision files yet.
      </div>

      <!-- Group by revision round -->
      <template v-for="[round, roundFiles] in revisionFilesByRound" :key="round">
        <div class="border-b border-amber-100 bg-amber-50/30 px-5 py-2 flex items-center gap-2">
          <RotateCcw class="h-3.5 w-3.5 text-amber-600" />
          <span class="text-xs font-semibold text-amber-800">
            {{ round === 0 ? 'Original Revision' : `Revision Round ${round}` }}
          </span>
          <span class="text-xs text-amber-600">({{ roundFiles.length }} file{{ roundFiles.length !== 1 ? 's' : '' }})</span>
        </div>
        <div class="divide-y divide-slate-50">
          <FileTile v-for="att in roundFiles" :key="att.id"
            :att="att" :order-id="orderId" :role="role"
            :downloading="downloading" :can-delete="canRequestDeletion"
            :show-revision-badge="false"
            @download="download" @request-delete="openDeletePrompt" />
        </div>
      </template>
    </section>

    <!-- ════════════════════════════════════════════════════════
         SECTION 5 — WRITER GUIDES  (writer + staff only)
         ════════════════════════════════════════════════════════ -->
    <section v-if="canSeeWriterGuides">
      <SectionHeader icon-class="text-signal" :count="writerGuides.length">
        <template #icon><BookOpen class="h-4 w-4" /></template>
        Writer Guides
        <template #badge><span class="rounded-full border border-blue-200 bg-blue-50 px-2 py-0.5 text-[10px] font-semibold text-blue-700">Writer + Staff</span></template>
        <template #desc>Rubrics, style guides, and context provided by staff for the assigned writer.</template>
      </SectionHeader>

      <div v-if="isStaffRole" class="border-b border-slate-100 bg-slate-50/60 p-4">
        <div class="grid gap-4 lg:grid-cols-2">
          <!-- Upload guide file -->
          <form class="space-y-2 rounded-lg border border-slate-200 bg-white p-3" @submit.prevent="uploadGuideFile">
            <div class="flex items-center gap-2 text-xs font-semibold text-ink">
              <FileUp class="h-3.5 w-3.5 text-signal" /> Upload guide file
            </div>
            <input type="file" class="focus-ring block w-full rounded-md border border-slate-200 px-2 py-1.5 text-xs" @change="onGuidePick" />
            <div class="grid grid-cols-2 gap-2">
              <select v-model="guideType" class="focus-ring h-8 w-full rounded-md border border-slate-200 bg-white px-2 text-xs">
                <option value="guide">General guide</option>
                <option value="rubric">Rubric</option>
                <option value="style_guide">Style guide</option>
                <option value="article">Article</option>
                <option value="client_context">Client context</option>
              </select>
              <input v-model="guideDescription" type="text" placeholder="Description (optional)"
                class="focus-ring h-8 w-full rounded-md border border-slate-200 px-2 text-xs" />
            </div>
            <button type="submit"
              class="focus-ring h-8 w-full rounded-md bg-signal text-xs font-semibold text-white disabled:opacity-50"
              :disabled="!guideFile || files.isUploading">Upload guide</button>
          </form>
          <!-- External link + article -->
          <div class="space-y-3">
            <form class="space-y-2 rounded-lg border border-slate-200 bg-white p-3" @submit.prevent="addGuideLink">
              <div class="flex items-center gap-2 text-xs font-semibold text-ink">
                <ExternalLink class="h-3.5 w-3.5 text-signal" /> Add external link
              </div>
              <input v-model="guideLinkUrl" type="url" placeholder="https://…"
                class="focus-ring h-8 w-full rounded-md border border-slate-200 px-2 text-xs" />
              <input v-model="guideLinkTitle" type="text" placeholder="Title (optional)"
                class="focus-ring h-8 w-full rounded-md border border-slate-200 px-2 text-xs" />
              <button type="submit"
                class="focus-ring h-8 w-full rounded-md border border-slate-200 bg-white text-xs font-semibold text-ink disabled:opacity-50"
                :disabled="!guideLinkUrl || files.isUploading">Add link</button>
            </form>
            <div class="space-y-2 rounded-lg border border-slate-200 bg-white p-3" @mouseenter="loadGuideArticles">
              <div class="flex items-center gap-2 text-xs font-semibold text-ink">
                <BookOpen class="h-3.5 w-3.5 text-signal" /> Attach help article
              </div>
              <select v-model="selectedGuideSlug" class="focus-ring h-8 w-full rounded-md border border-slate-200 bg-white px-2 text-xs">
                <option value="">— pick an article —</option>
                <option v-for="a in guideArticles" :key="a.slug" :value="a.slug">{{ a.title }}</option>
              </select>
              <button class="focus-ring h-8 w-full rounded-md border border-slate-200 bg-white text-xs font-semibold text-ink disabled:opacity-50"
                :disabled="!selectedGuideSlug || files.isUploading"
                @click="attachExistingGuide">Attach article</button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="!writerGuides.length" class="px-5 py-8 text-center text-xs text-graphite">No writer guides attached.</div>
      <div v-else class="divide-y divide-slate-50">
        <FileTile v-for="att in writerGuides" :key="att.id"
          :att="att" :order-id="orderId" :role="role"
          :downloading="downloading" :can-delete="false" :can-staff-detach="isStaffRole"
          @download="download" @staff-detach="staffDetach" />
      </div>
    </section>

    <!-- ════════════════════════════════════════════════════════
         SECTION 6 — INTERNAL FILES  (staff only)
         ════════════════════════════════════════════════════════ -->
    <section v-if="isStaffRole">
      <SectionHeader icon-class="text-amber-600" :count="internalFiles.length">
        <template #icon><Lock class="h-4 w-4" /></template>
        Internal Files
        <template #badge><span class="rounded-full border border-amber-200 bg-amber-50 px-2 py-0.5 text-[10px] font-semibold text-amber-700">Staff only</span></template>
        <template #desc>Not visible to clients or writers.</template>
      </SectionHeader>

      <div class="border-b border-slate-100 bg-slate-50/60 px-5 py-4">
        <form class="flex flex-wrap items-end gap-3" @submit.prevent="internalUpload">
          <div class="flex-1 min-w-48">
            <label class="block text-xs font-medium text-graphite mb-1">File</label>
            <input type="file" class="focus-ring block w-full rounded-md border border-slate-200 px-2 py-1.5 text-xs" @change="onInternalPick" />
          </div>
          <input v-model="internalNote" type="text" placeholder="Note (optional)"
            class="focus-ring h-9 flex-1 min-w-40 rounded-md border border-slate-200 px-3 text-xs" />
          <button type="submit"
            class="focus-ring h-9 rounded-md bg-amber-600 px-4 text-xs font-semibold text-white disabled:opacity-50"
            :disabled="!internalFile || files.isUploading">Upload internal</button>
        </form>
      </div>

      <div v-if="!internalFiles.length" class="px-5 py-8 text-center text-xs text-graphite">No internal files.</div>
      <div v-else class="divide-y divide-slate-50">
        <FileTile v-for="att in internalFiles" :key="att.id"
          :att="att" :order-id="orderId" :role="role"
          :downloading="downloading" :can-delete="false" :can-staff-detach="true"
          @download="download" @staff-detach="staffDetach" />
      </div>
    </section>

    <!-- Delete confirm modal -->
    <Teleport to="body">
      <div v-if="deletingId" class="fixed inset-0 z-50 flex items-end justify-center bg-black/40 p-4 sm:items-center">
        <div class="w-full max-w-sm space-y-4 rounded-xl bg-white p-5 shadow-xl">
          <p class="text-sm font-semibold text-ink">Request file removal</p>
          <p class="text-xs text-graphite">Files are not immediately deleted — your request will be reviewed by staff.</p>
          <textarea v-model="deleteReason" rows="2" placeholder="Reason for removal…"
            class="focus-ring w-full resize-none rounded-md border border-slate-200 px-3 py-2 text-xs" />
          <div class="flex gap-2">
            <button class="focus-ring flex-1 rounded-md border border-slate-200 py-2 text-xs font-semibold text-graphite" @click="cancelDelete">Cancel</button>
            <button class="focus-ring flex-1 rounded-md bg-rose-600 py-2 text-xs font-semibold text-white disabled:opacity-50"
              :disabled="!deleteReason.trim() || deletingInFlight"
              @click="confirmDelete">
              <Loader2 v-if="deletingInFlight" class="inline h-3 w-3 animate-spin mr-1" />
              Submit request
            </button>
          </div>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, defineComponent, h, type PropType } from "vue";
import {
  AlertCircle, BookOpen, CheckCircle2, Download, ExternalLink,
  FileEdit, FileUp, Loader2, Lock, Paperclip, RotateCcw,
  Send, Trophy, X,
} from "@lucide/vue";
import type { UserRole } from "@/types/roles";
import type { FileAttachment, DeliveryStatus } from "@/api/files";
import { legalApi, type HelpArticleSummary } from "@/api/legal";
import { writerApi } from "@/api/writer";
import { useFilesStore, type QueuedFile } from "@/stores/files";
import { isStaff } from "../types";
import type { OrderLifecycle, OrderSummary } from "../types";
import type { FilePurpose } from "@/api/files";

// ── Inline sub-components ──────────────────────────────────────────────────

/** Section header with consistent styling */
const SectionHeader = defineComponent({
  props: { iconClass: String, count: Number },
  slots: Object as any,
  setup(props, { slots }) {
    return () => h("div", {
      class: "flex flex-wrap items-center justify-between gap-2 bg-slate-50 px-5 py-3",
    }, [
      h("div", { class: "flex items-center gap-2" }, [
        h("span", { class: props.iconClass }, slots.icon?.()),
        h("h3", { class: "text-sm font-semibold text-ink" }, slots.default?.()),
        slots.badge?.(),
        props.count != null && props.count > 0
          ? h("span", { class: "rounded-full bg-slate-200 px-1.5 py-0.5 text-[10px] font-bold text-slate-600" }, String(props.count))
          : null,
      ]),
      h("p", { class: "text-xs text-graphite" }, slots.desc?.()),
    ]);
  },
});

/** File type icon / extension badge */
const FileTypeIcon = defineComponent({
  props: {
    attachment: { type: Object as () => FileAttachment, required: true },
    size: { type: String as () => "sm" | "lg", default: "sm" },
  },
  setup(props) {
    return () => {
      const att = props.attachment;
      const name = att?.managed_file?.original_filename ?? att?.display_name ?? "";
      const ext = name.includes(".") ? name.split(".").pop()?.toLowerCase() ?? "" : (att?.external_link ? "url" : "");
      const EXT_COLOR: Record<string, string> = {
        pdf: "bg-rose-100 text-rose-700", doc: "bg-blue-100 text-blue-700", docx: "bg-blue-100 text-blue-700",
        pptx: "bg-orange-100 text-orange-700", xlsx: "bg-emerald-100 text-emerald-700",
        zip: "bg-purple-100 text-purple-700", url: "bg-slate-100 text-slate-600",
      };
      const cls = EXT_COLOR[ext] ?? "bg-slate-100 text-slate-600";
      const sz = props.size === "lg" ? "h-12 w-12 text-xs" : "h-9 w-9 text-[10px]";
      return h("div", {
        class: `flex shrink-0 items-center justify-center rounded-lg border border-slate-200 font-bold uppercase ${cls} ${sz}`,
      }, ext || "file");
    };
  },
});

/** Uploader attribution badge */
const UploaderBadge = defineComponent({
  props: { name: String as () => string | null, role: String as () => string | null },
  setup(props) {
    const ROLE_CLS: Record<string, string> = {
      client: "bg-violet-100 text-violet-700",
      writer: "bg-blue-100 text-blue-700",
      admin: "bg-amber-100 text-amber-700",
      superadmin: "bg-amber-100 text-amber-700",
      support: "bg-teal-100 text-teal-700",
      editor: "bg-indigo-100 text-indigo-700",
    };
    return () => {
      if (!props.name) return null;
      const roleCls = ROLE_CLS[props.role ?? ""] ?? "bg-slate-100 text-slate-600";
      return h("span", { class: "flex items-center gap-1" }, [
        h("span", { class: `rounded-full px-1.5 py-0.5 text-[9px] font-bold uppercase ${roleCls}` },
          props.role ?? ""),
        h("span", { class: "text-xs text-graphite" }, props.name),
      ]);
    };
  },
});

/** Multi-file drag-and-drop upload zone */
const MultiUploadZone = defineComponent({
  props: {
    purpose: String as () => FilePurpose,
    label: String,
    accept: { type: String, default: "" },
    orderId: [String, Number],
    uploading: Boolean,
  },
  emits: ["pick", "upload"],
  setup(props, { emit }) {
    const input = ref<HTMLInputElement | null>(null);
    function pick(e: Event) {
      const el = e.target as HTMLInputElement;
      if (el.files?.length) emit("pick", el.files);
      if (input.value) input.value.value = "";
    }
    return () => h("div", { class: "flex items-center gap-3" }, [
      h("input", {
        ref: input, type: "file", multiple: true,
        accept: props.accept, class: "focus-ring flex-1 block w-full rounded-md border border-slate-200 px-2 py-1.5 text-xs",
        onChange: pick,
      }),
      h("button", {
        type: "button",
        class: "focus-ring h-9 rounded-md bg-slate-700 px-4 text-xs font-semibold text-white disabled:opacity-50",
        disabled: props.uploading,
        onClick: () => emit("upload"),
      }, props.uploading ? [h(Loader2, { class: "inline h-3 w-3 animate-spin mr-1" }), "Uploading…"] : [`Upload`]),
    ]);
  },
});

/** Upload queue progress list */
const UploadQueue = defineComponent({
  props: { queue: { type: Array as () => QueuedFile[], required: true } },
  setup(props) {
    const CLS: Record<string, string> = { done: "text-emerald-600", error: "text-rose-600", uploading: "text-blue-600", pending: "text-graphite" };
    return () => h("ul", { class: "space-y-1" }, props.queue.map((q) =>
      h("li", { key: q.name, class: `flex items-center gap-2 text-xs ${CLS[q.status] ?? "text-graphite"}` }, [
        q.status === "uploading" ? h(Loader2, { class: "h-3 w-3 animate-spin" })
          : q.status === "done" ? h(CheckCircle2, { class: "h-3 w-3" })
          : q.status === "error" ? h(AlertCircle, { class: "h-3 w-3" })
          : null,
        h("span", { class: "truncate max-w-xs" }, q.name),
        q.progress != null && q.status === "uploading"
          ? h("span", {}, `${q.progress}%`) : null,
      ])
    ));
  },
});

/** Delete request button */
const DeleteRequestButton = defineComponent({
  props: { attachmentId: Number, orderId: [String, Number], canDelete: Boolean },
  emits: ["request"],
  setup(props, { emit }) {
    return () => props.canDelete
      ? h("button", {
          class: "focus-ring flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 text-slate-400 hover:border-rose-200 hover:bg-rose-50 hover:text-rose-500",
          title: "Request removal",
          onClick: () => emit("request", props.attachmentId),
        }, h(X, { class: "h-3.5 w-3.5" }))
      : null;
  },
});

/** Universal file row tile */
const FileTile = defineComponent({
  props: {
    att: { type: Object as () => FileAttachment, required: true },
    orderId: { type: [String, Number], required: true },
    role: { type: String as () => UserRole, required: true },
    downloading: { type: Number as PropType<number | null>, default: null },
    canDelete: { type: Boolean, default: false },
    canStaffDetach: { type: Boolean, default: false },
    showRevisionBadge: { type: Boolean, default: true },
  },
  emits: ["download", "request-delete", "staff-detach"],
  setup(props, { emit }) {
    const PURPOSE_LABELS: Record<string, string> = {
      order_instruction: "Instruction", order_reference: "Reference",
      order_sample: "Sample", order_outline: "Outline",
      order_questionnaire: "Questionnaire", order_notes: "Notes",
      order_class_material: "Class material",
      order_draft: "Draft", order_final: "Final",
      order_revision: "Revision", writer_guide: "Guide",
      style_reference: "Style ref", extra_service_file: "Extra service",
      admin_internal: "Internal",
    };
    const PURPOSE_COLOR: Record<string, string> = {
      order_instruction: "bg-violet-100 text-violet-700",
      order_reference: "bg-slate-100 text-slate-600",
      order_sample: "bg-indigo-100 text-indigo-700",
      order_outline: "bg-sky-100 text-sky-700",
      order_questionnaire: "bg-pink-100 text-pink-700",
      order_notes: "bg-yellow-100 text-yellow-700",
      order_class_material: "bg-teal-100 text-teal-700",
      order_draft: "bg-blue-100 text-blue-700",
      order_revision: "bg-amber-100 text-amber-700",
      writer_guide: "bg-signal/10 text-signal",
      admin_internal: "bg-amber-50 text-amber-700",
    };

    function name(att: FileAttachment) {
      return att.managed_file?.original_filename ?? att.external_link?.title ?? att.display_name ?? `File #${att.id}`;
    }
    function ext(att: FileAttachment) {
      const n = name(att); const p = n.split(".");
      return p.length > 1 ? p.pop()!.toLowerCase() : "";
    }
    function sz(bytes?: number | null) {
      if (!bytes) return "";
      if (bytes < 1024) return `${bytes} B`;
      if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
      return `${(bytes / 1048576).toFixed(1)} MB`;
    }
    function fmtD(iso: string) {
      return new Date(iso).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
    }

    return () => {
      const att = props.att;
      const isLink = !!att.external_link;
      const isDownloading = props.downloading === att.id;
      const extStr = ext(att) || (isLink ? "url" : "");
      const EXT_COLOR: Record<string, string> = {
        pdf: "bg-rose-100 text-rose-700", doc: "bg-blue-100 text-blue-700", docx: "bg-blue-100 text-blue-700",
        pptx: "bg-orange-100 text-orange-700", xlsx: "bg-emerald-100 text-emerald-700",
        zip: "bg-purple-100 text-purple-700",
      };
      const extCls = EXT_COLOR[extStr] ?? "bg-slate-100 text-slate-600";

      return h("div", { class: "flex items-start gap-3 px-5 py-3.5 hover:bg-slate-50/60 transition-colors" }, [
        // Extension badge
        h("div", { class: `mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-slate-200 text-[10px] font-bold uppercase ${extCls}` },
          extStr || "file"),

        // Info
        h("div", { class: "min-w-0 flex-1 space-y-1" }, [
          h("div", { class: "flex items-center gap-2" }, [
            h("p", { class: "truncate text-sm font-medium text-ink" }, name(att)),
            att.is_new_for_user
              ? h("span", { class: "shrink-0 rounded-full bg-saffron px-2 py-0.5 text-[9px] font-bold text-white" }, "New")
              : null,
          ]),
          h("div", { class: "flex flex-wrap items-center gap-2 text-xs" }, [
            // Purpose badge
            h("span", { class: `rounded px-1.5 py-0.5 text-[10px] font-medium ${PURPOSE_COLOR[att.purpose] ?? "bg-slate-100 text-slate-600"}` },
              PURPOSE_LABELS[att.purpose] ?? att.purpose.replace(/_/g, " ")),
            // Revision cycle
            props.showRevisionBadge && att.revision_cycle && att.revision_cycle > 0
              ? h("span", { class: "rounded-full bg-amber-100 px-1.5 py-0.5 text-[9px] font-bold text-amber-700" }, `Rev. ${att.revision_cycle}`)
              : null,
            // Size
            att.managed_file?.file_size_bytes
              ? h("span", { class: "text-graphite" }, sz(att.managed_file.file_size_bytes)) : null,
            // Date
            h("span", { class: "text-graphite" }, fmtD(att.attached_at)),
            // Uploader
            att.attached_by_name
              ? h(UploaderBadge, { name: att.attached_by_name, role: att.attached_by_role ?? null })
              : null,
            // Downloaded indicator
            att.first_downloaded_at
              ? h("span", { class: "text-emerald-600 font-medium" }, `✓ Downloaded`)
              : null,
          ]),
        ]),

        // Actions
        h("div", { class: "flex shrink-0 items-center gap-1.5" }, [
          // Download / open
          h("button", {
            class: "focus-ring flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 text-graphite hover:border-slate-300 hover:text-ink disabled:opacity-40",
            disabled: isDownloading, title: isLink ? "Open link" : "Download",
            onClick: () => emit("download", att.id),
          }, isDownloading ? h(Loader2, { class: "h-3.5 w-3.5 animate-spin" }) : h(isLink ? ExternalLink : Download, { class: "h-3.5 w-3.5" })),

          // Staff detach
          props.canStaffDetach
            ? h("button", {
                class: "focus-ring flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 text-slate-400 hover:border-rose-200 hover:bg-rose-50 hover:text-rose-500",
                title: "Remove", onClick: () => emit("staff-detach", att.id),
              }, h(X, { class: "h-3.5 w-3.5" }))
            : props.canDelete
              ? h("button", {
                  class: "focus-ring flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 text-slate-400 hover:border-rose-200 hover:bg-rose-50 hover:text-rose-500",
                  title: "Request removal", onClick: () => emit("request-delete", att.id),
                }, h(X, { class: "h-3.5 w-3.5" }))
              : null,
        ]),
      ]);
    };
  },
});

// ── Props & emits ──────────────────────────────────────────────────────────
const props = defineProps<{
  orderId: string;
  order: OrderSummary;
  lifecycle: OrderLifecycle | null;
  role: UserRole;
}>();
const emit = defineEmits<{ (e: "go-to-payments"): void }>();

// ── Store & role helpers ───────────────────────────────────────────────────
const files = useFilesStore();
const isStaffRole = computed(() => isStaff(props.role));
const canRequestDeletion = computed(() => props.role === "client" || isStaffRole.value);
const canSeeWriterGuides = computed(() => props.role === "writer" || isStaffRole.value);

// ── File groupings ─────────────────────────────────────────────────────────
const CLIENT_PURPOSES = [
  "order_instruction", "order_reference", "order_sample",
  "order_outline", "order_questionnaire", "order_notes", "order_class_material",
];
const clientMaterials  = computed(() => files.attachments.filter(a => CLIENT_PURPOSES.includes(a.purpose)));
const finalFiles       = computed(() => files.attachments.filter(a => a.purpose === "order_final" || a.purpose === "extra_service_file"));
const draftFiles       = computed(() => files.attachments.filter(a => a.purpose === "order_draft"));
const allRevisionFiles = computed(() => files.attachments.filter(a => a.purpose === "order_revision"));
const writerGuides     = computed(() => files.attachments.filter(a => a.purpose === "writer_guide" || a.purpose === "style_reference"));
const internalFiles    = computed(() => files.attachments.filter(a => a.purpose === "admin_internal"));

/** Group revision files by revision_cycle, sorted ascending */
const revisionFilesByRound = computed((): [number, FileAttachment[]][] => {
  const map = new Map<number, FileAttachment[]>();
  for (const f of allRevisionFiles.value) {
    const cycle = f.revision_cycle ?? 0;
    if (!map.has(cycle)) map.set(cycle, []);
    map.get(cycle)!.push(f);
  }
  return [...map.entries()].sort(([a], [b]) => a - b);
});

const currentRevisionCycle = computed(() => {
  const cycles = revisionFilesByRound.value.map(([c]) => c);
  return cycles.length ? Math.max(...cycles) + 1 : 1;
});

const hasRevision = computed(() =>
  props.order.status === "revision_requested" ||
  (props.lifecycle?.latest_revision_status != null &&
    !["resolved", "rejected", "withdrawn"].includes(props.lifecycle.latest_revision_status ?? ""))
);

// ── Helpers ────────────────────────────────────────────────────────────────
function fileName(att: FileAttachment) {
  return att.managed_file?.original_filename ?? att.external_link?.title ?? att.display_name ?? `File #${att.id}`;
}
function fileSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1048576).toFixed(1)} MB`;
}
function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

const DELIVERY_LABELS: Record<string, string> = {
  pending: "Awaiting submission", submitted: "Submitted for delivery",
  locked: "Payment required", approved: "Ready to download", rejected: "Rejected by staff",
};
const DELIVERY_BADGE: Record<string, string> = {
  approved: "bg-emerald-100 text-emerald-700",
  submitted: "bg-blue-100 text-blue-700",
  rejected: "bg-rose-100 text-rose-700",
  locked: "bg-amber-100 text-amber-700",
  pending: "bg-slate-100 text-slate-600",
};
function deliveryLabel(s: DeliveryStatus) { return DELIVERY_LABELS[s] ?? s?.replace(/_/g, " "); }
function deliveryBadge(s: DeliveryStatus) { return DELIVERY_BADGE[s] ?? "bg-slate-100 text-slate-600"; }

// ── Client upload ──────────────────────────────────────────────────────────
const clientFiles   = ref<File[]>([]);
const clientPurpose = ref<FilePurpose>("order_instruction");
const clientFileInput = ref<HTMLInputElement | null>(null);

function onClientFilePick(e: Event) {
  const el = e.target as HTMLInputElement;
  clientFiles.value = el.files ? [...el.files] : [];
  files.clearMessages();
}
async function clientUpload() {
  for (const file of clientFiles.value) {
    await files.uploadSingleFile(props.orderId, file, clientPurpose.value);
  }
  clientFiles.value = [];
  if (clientFileInput.value) clientFileInput.value.value = "";
}

// ── Internal upload ────────────────────────────────────────────────────────
const internalFile = ref<File | null>(null);
const internalNote = ref("");
function onInternalPick(e: Event) {
  internalFile.value = (e.target as HTMLInputElement).files?.[0] ?? null;
}
async function internalUpload() {
  if (!internalFile.value) return;
  await files.uploadSingleFile(props.orderId, internalFile.value, "admin_internal",
    internalNote.value ? { description: internalNote.value } : undefined);
  internalFile.value = null;
  internalNote.value = "";
}

// ── Writer guide helpers ───────────────────────────────────────────────────
const guideFile        = ref<File | null>(null);
const guideType        = ref("guide");
const guideDescription = ref("");
const guideLinkTitle   = ref("");
const guideLinkUrl     = ref("");
const guideArticles    = ref<HelpArticleSummary[]>([]);
const selectedGuideSlug = ref("");

function onGuidePick(e: Event) {
  guideFile.value = (e.target as HTMLInputElement).files?.[0] ?? null;
  files.clearMessages();
}
async function uploadGuideFile() {
  if (!guideFile.value) return;
  await files.uploadSingleFile(props.orderId, guideFile.value, "writer_guide", {
    category_code: guideType.value, description: guideDescription.value,
  });
  guideFile.value = null; guideDescription.value = ""; guideType.value = "guide";
}
async function addGuideLink() {
  if (!guideLinkUrl.value) return;
  await files.submitExternalLink(props.orderId, { url: guideLinkUrl.value, title: guideLinkTitle.value || guideLinkUrl.value, purpose: "writer_guide" });
  guideLinkTitle.value = ""; guideLinkUrl.value = "";
}
async function loadGuideArticles() {
  if (guideArticles.value.length) return;
  try {
    const { data } = await legalApi.articles();
    guideArticles.value = data.filter(a => ["writer", "staff", "all", "everyone"].includes(String(a.audience ?? "").toLowerCase()));
  } catch { guideArticles.value = []; }
}
async function attachExistingGuide() {
  const article = guideArticles.value.find(a => a.slug === selectedGuideSlug.value);
  if (!article) return;
  await files.submitExternalLink(props.orderId, { url: `/writer/guides/${article.slug}`, title: article.title, purpose: "writer_guide" });
  selectedGuideSlug.value = "";
}

// ── Staff detach ───────────────────────────────────────────────────────────
async function staffDetach(id: number) {
  await files.requestFileDeletion(props.orderId, id, "Staff detached file");
}

// ── Submit final (writer) ──────────────────────────────────────────────────
const submittingFinal = ref<number | null>(null);
async function submitFinal(id: number) {
  submittingFinal.value = id;
  await files.submitFinalFile(props.orderId, id);
  submittingFinal.value = null;
}

// ── Download ───────────────────────────────────────────────────────────────
const downloading = ref<number | null>(null);
async function download(id: number) {
  downloading.value = id;
  try { await files.downloadFile(props.orderId, id); }
  finally { downloading.value = null; }
}

// ── Delete request ─────────────────────────────────────────────────────────
const deletingId       = ref<number | null>(null);
const deleteReason     = ref("");
const deletingInFlight = ref(false);
function openDeletePrompt(id: number) { deletingId.value = id; deleteReason.value = ""; }
function cancelDelete()               { deletingId.value = null; deleteReason.value = ""; }
async function confirmDelete() {
  if (!deletingId.value || !deleteReason.value) return;
  deletingInFlight.value = true;
  try {
    await files.requestFileDeletion(props.orderId, deletingId.value, deleteReason.value);
    deletingId.value = null; deleteReason.value = "";
  } finally { deletingInFlight.value = false; }
}

// ── Submit work (writer) ───────────────────────────────────────────────────
const submissionNote = ref("");
const isSubmitting   = ref(false);
const submitError    = ref("");
const submitNotice   = ref("");
async function submitWork() {
  submitError.value = ""; submitNotice.value = ""; isSubmitting.value = true;
  try {
    const { data } = await writerApi.submitOrder(props.orderId, { note: submissionNote.value || undefined });
    submitNotice.value = (data as any).message ?? "Work submitted.";
    submissionNote.value = "";
  } catch { submitError.value = "Submission failed. Make sure a final file is uploaded and submitted first."; }
  finally { isSubmitting.value = false; }
}
</script>
