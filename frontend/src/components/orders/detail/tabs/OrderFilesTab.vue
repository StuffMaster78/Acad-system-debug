<template>
  <div class="divide-y divide-slate-100 rounded-xl border border-slate-200 bg-white overflow-hidden">

    <!-- Notices -->
    <div v-if="files.error" class="px-5 py-3 text-sm text-rose-700 bg-rose-50 flex items-center gap-2">
      <AlertCircle class="h-4 w-4 shrink-0" />{{ files.error }}
    </div>
    <div v-if="files.notice" class="px-5 py-3 text-sm text-emerald-700 bg-emerald-50 flex items-center gap-2">
      <CheckCircle2 class="h-4 w-4 shrink-0" />{{ files.notice }}
    </div>

    <!-- ═══ SECTION 1 — Client materials ════════════════════════════════ -->
    <section>
      <!-- Header -->
      <div class="flex flex-wrap items-center justify-between gap-2 bg-slate-50 px-5 py-3">
        <div class="flex items-center gap-2">
          <Paperclip class="h-4 w-4 text-graphite" />
          <h3 class="text-sm font-semibold text-ink">Client materials</h3>
          <span class="rounded-full border px-2 py-0.5 text-[10px] font-semibold bg-emerald-50 text-emerald-700 border-emerald-200">All participants</span>
        </div>
        <p class="text-xs text-graphite">Instructions, references, and context provided by the client.</p>
      </div>
      <!-- Upload (client or staff on behalf) -->
      <div v-if="role === 'client' || isStaffRole" class="border-b border-slate-100 p-4">
        <form class="flex flex-wrap items-end gap-3" @submit.prevent="() => { singlePurpose = singlePurpose === 'admin_internal' ? 'order_reference' : singlePurpose; singleUpload(); }">
          <label class="flex-1 min-w-40">
            <span class="block text-xs font-medium text-graphite mb-1">File</span>
            <input type="file" class="focus-ring block w-full rounded-md border border-slate-200 px-2 py-1.5 text-xs" @change="onSinglePick" />
          </label>
          <label class="w-44">
            <span class="block text-xs font-medium text-graphite mb-1">Type</span>
            <select v-model="singlePurpose" class="focus-ring h-9 w-full rounded-md border border-slate-200 bg-white px-2 text-xs">
              <option value="order_instruction">Instruction</option>
              <option value="order_reference">Reference</option>
            </select>
          </label>
          <button type="submit" class="focus-ring h-9 rounded-md bg-ink px-4 text-xs font-semibold text-white disabled:opacity-50" :disabled="!singleFile || files.isUploading">Upload</button>
        </form>
      </div>
      <!-- File list -->
      <div v-if="!clientMaterials.length" class="px-5 py-8 text-center text-xs text-graphite">No client materials yet.</div>
      <div v-else class="divide-y divide-slate-50">
        <FileTile
          v-for="att in clientMaterials" :key="att.id"
          :att="att" :order-id="orderId" :role="role"
          :downloading="downloading" :deleting-id="deletingId"
          :deleting-in-flight="deletingInFlight" :delete-reason="deleteReason"
          :can-delete="canRequestDeletion" :can-staff-detach="false"
          @download="download" @open-delete="openDeletePrompt"
          @confirm-delete="confirmDelete" @cancel-delete="cancelDelete"
          @update:delete-reason="deleteReason = $event"
        />
      </div>
    </section>

    <!-- ═══ SECTION 2 — Writer guides ══════════════════════════════════ -->
    <section v-if="canSeeWriterGuides">
      <div class="flex flex-wrap items-center justify-between gap-2 bg-slate-50 px-5 py-3">
        <div class="flex items-center gap-2">
          <BookOpen class="h-4 w-4 text-blue-500" />
          <h3 class="text-sm font-semibold text-ink">Writer guides</h3>
          <span class="rounded-full border px-2 py-0.5 text-[10px] font-semibold bg-blue-50 text-blue-700 border-blue-200">Writer + Staff</span>
        </div>
        <p class="text-xs text-graphite">Rubrics, style guides, and resources for the assigned writer only.</p>
      </div>
      <!-- Staff upload forms -->
      <div v-if="isStaffRole" class="border-b border-slate-100 p-4 space-y-3">
        <div class="grid gap-4 lg:grid-cols-2">
          <form class="rounded-lg border border-slate-200 bg-slate-50 p-3 space-y-2" @submit.prevent="uploadGuideFile">
            <div class="flex items-center gap-2"><FileUp class="h-4 w-4 text-signal" /><span class="text-xs font-semibold text-ink">Upload guide file</span></div>
            <input type="file" class="focus-ring block w-full rounded-md border border-slate-200 px-2 py-1.5 text-xs" @change="onGuidePick" />
            <div class="grid grid-cols-2 gap-2">
              <select v-model="guideType" class="focus-ring h-8 w-full rounded-md border border-slate-200 bg-white px-2 text-xs">
                <option value="guide">General guide</option><option value="rubric">Rubric</option>
                <option value="style_guide">Style guide</option><option value="article">Article</option>
                <option value="client_context">Client context</option>
              </select>
              <input v-model="guideDescription" type="text" placeholder="Description (optional)" class="focus-ring h-8 w-full rounded-md border border-slate-200 px-2 text-xs" />
            </div>
            <button type="submit" class="focus-ring h-8 w-full rounded-md bg-signal text-xs font-semibold text-white disabled:opacity-50" :disabled="!guideFile || files.isUploading">Upload guide</button>
          </form>
          <div class="space-y-3">
            <form class="rounded-lg border border-slate-200 bg-slate-50 p-3 space-y-2" @submit.prevent="addGuideLink">
              <div class="flex items-center gap-2"><ExternalLink class="h-4 w-4 text-signal" /><span class="text-xs font-semibold text-ink">Add external link</span></div>
              <input v-model="guideLinkUrl" type="url" placeholder="https://..." class="focus-ring h-8 w-full rounded-md border border-slate-200 px-2 text-xs" />
              <input v-model="guideLinkTitle" type="text" placeholder="Title (optional)" class="focus-ring h-8 w-full rounded-md border border-slate-200 px-2 text-xs" />
              <button type="submit" class="focus-ring h-8 w-full rounded-md border border-slate-200 bg-white text-xs font-semibold text-ink disabled:opacity-50" :disabled="!guideLinkUrl || files.isUploading">Add link</button>
            </form>
            <div class="rounded-lg border border-slate-200 bg-slate-50 p-3 space-y-2" @mouseenter="loadGuideArticles">
              <div class="flex items-center gap-2"><BookOpen class="h-4 w-4 text-signal" /><span class="text-xs font-semibold text-ink">Attach help article</span></div>
              <select v-model="selectedGuideSlug" class="focus-ring h-8 w-full rounded-md border border-slate-200 bg-white px-2 text-xs">
                <option value="">— pick an article —</option>
                <option v-for="a in guideArticles" :key="a.slug" :value="a.slug">{{ a.title }}</option>
              </select>
              <button class="focus-ring h-8 w-full rounded-md border border-slate-200 bg-white text-xs font-semibold text-ink disabled:opacity-50" :disabled="!selectedGuideSlug || files.isUploading" @click="attachExistingGuide">Attach article</button>
            </div>
          </div>
        </div>
      </div>
      <div v-if="!writerGuides.length" class="px-5 py-8 text-center text-xs text-graphite">No writer guides attached yet.</div>
      <div v-else class="divide-y divide-slate-50">
        <FileTile
          v-for="att in writerGuides" :key="att.id"
          :att="att" :order-id="orderId" :role="role"
          :downloading="downloading" :deleting-id="deletingId"
          :deleting-in-flight="deletingInFlight" :delete-reason="deleteReason"
          :can-delete="canRequestDeletion" :can-staff-detach="isStaffRole"
          :detaching-id="detachingId"
          @download="download" @open-delete="openDeletePrompt"
          @confirm-delete="confirmDelete" @cancel-delete="cancelDelete"
          @update:delete-reason="deleteReason = $event"
          @staff-detach="staffDetach"
        />
      </div>
    </section>

    <!-- ═══ SECTION 3 — Drafts & Deliverables ══════════════════════════ -->
    <section>
      <div class="flex flex-wrap items-center justify-between gap-2 bg-slate-50 px-5 py-3">
        <div class="flex items-center gap-2">
          <FileUp class="h-4 w-4 text-graphite" />
          <h3 class="text-sm font-semibold text-ink">Drafts &amp; deliverables</h3>
          <span class="rounded-full border px-2 py-0.5 text-[10px] font-semibold bg-emerald-50 text-emerald-700 border-emerald-200">All participants</span>
        </div>
        <p class="text-xs text-graphite">Work-in-progress and final files submitted by the writer.</p>
      </div>
      <!-- Writer upload queue -->
      <div v-if="role === 'writer'" class="border-b border-slate-100 p-4 space-y-3">
        <div class="flex flex-wrap items-end gap-3">
          <label class="flex-1 min-w-40">
            <span class="block text-xs font-medium text-graphite mb-1">Add file(s)</span>
            <input type="file" multiple class="focus-ring block w-full rounded-md border border-slate-200 px-2 py-1.5 text-xs" @change="onFilePick" />
          </label>
          <label class="w-44">
            <span class="block text-xs font-medium text-graphite mb-1">Type</span>
            <select v-model="defaultPurpose" class="focus-ring h-9 w-full rounded-md border border-slate-200 bg-white px-2 text-xs">
              <option value="order_final">Final deliverable</option>
              <option value="order_draft">Draft (for review)</option>
            </select>
          </label>
          <button v-if="files.uploadQueue.length" class="focus-ring h-9 rounded-md bg-signal px-4 text-xs font-semibold text-white disabled:opacity-50" :disabled="!pendingCount || files.isUploading" @click="files.uploadFiles(orderId)">
            Upload{{ pendingCount ? ` (${pendingCount})` : '' }}
          </button>
        </div>
        <!-- Queue items -->
        <div v-if="files.uploadQueue.length" class="space-y-1">
          <div v-for="item in files.uploadQueue" :key="item.id" class="flex items-center justify-between rounded-md border border-slate-100 bg-slate-50 px-3 py-2 text-xs">
            <div class="flex items-center gap-2 min-w-0">
              <Loader2 v-if="item.status === 'uploading'" class="h-3 w-3 animate-spin text-signal shrink-0" />
              <CheckCircle2 v-else-if="item.status === 'done'" class="h-3 w-3 text-signal shrink-0" />
              <AlertCircle v-else-if="item.status === 'error'" class="h-3 w-3 text-berry shrink-0" />
              <span class="truncate text-graphite">{{ item.file.name }}</span>
            </div>
            <div class="flex items-center gap-2 shrink-0">
              <span class="text-[10px] capitalize" :class="queueTone(item)">{{ item.status }}</span>
              <button v-if="item.status !== 'uploading'" class="text-slate-400 hover:text-slate-600" @click="files.removeFromQueue(item.id)"><X class="h-3 w-3" /></button>
            </div>
          </div>
        </div>
        <!-- Submit work -->
        <div v-if="hasDeliverable" class="rounded-lg border border-signal/20 bg-signal/5 p-3 space-y-2">
          <p class="text-xs font-semibold text-ink">Ready to submit this work for delivery?</p>
          <textarea v-model="submissionNote" rows="2" placeholder="Optional note to the client..." class="focus-ring w-full rounded-md border border-slate-200 px-2 py-1.5 text-xs" />
          <button class="focus-ring h-9 rounded-md bg-signal px-4 text-xs font-semibold text-white flex items-center gap-2 disabled:opacity-50" :disabled="isSubmitting" @click="submitWork">
            <Send class="h-3.5 w-3.5" />{{ isSubmitting ? 'Submitting...' : 'Submit work for delivery' }}
          </button>
          <p v-if="submitError" class="text-xs text-berry">{{ submitError }}</p>
          <p v-if="submitNotice" class="text-xs text-signal">{{ submitNotice }}</p>
        </div>
      </div>
      <div v-if="!draftDeliverables.length" class="px-5 py-8 text-center text-xs text-graphite">No deliverables uploaded yet.</div>
      <div v-else class="divide-y divide-slate-50">
        <FileTile
          v-for="att in draftDeliverables" :key="att.id"
          :att="att" :order-id="orderId" :role="role"
          :downloading="downloading" :deleting-id="deletingId"
          :deleting-in-flight="deletingInFlight" :delete-reason="deleteReason"
          :can-delete="canRequestDeletion" :can-staff-detach="false"
          :submitting-final="submittingFinal" :show-submit-final="role === 'writer'"
          @download="download" @open-delete="openDeletePrompt"
          @confirm-delete="confirmDelete" @cancel-delete="cancelDelete"
          @update:delete-reason="deleteReason = $event"
          @submit-final="submitFinal"
        />
      </div>
    </section>

    <!-- ═══ SECTION 4 — Revision files ═════════════════════════════════ -->
    <section v-if="hasRevision || revisionFiles.length">
      <div class="flex flex-wrap items-center justify-between gap-2 bg-amber-50/50 px-5 py-3">
        <div class="flex items-center gap-2">
          <RefreshCw class="h-4 w-4 text-amber-600" />
          <h3 class="text-sm font-semibold text-ink">Revision files</h3>
          <span class="rounded-full border px-2 py-0.5 text-[10px] font-semibold bg-emerald-50 text-emerald-700 border-emerald-200">All participants</span>
        </div>
        <p class="text-xs text-graphite">Files submitted or added in support of this revision round.</p>
      </div>
      <div v-if="role === 'writer' && hasRevision" class="border-b border-slate-100 p-4">
        <form class="flex flex-wrap items-end gap-3" @submit.prevent="() => { singlePurpose = 'order_revision'; singleUpload(); }">
          <label class="flex-1 min-w-40">
            <input type="file" class="focus-ring block w-full rounded-md border border-slate-200 px-2 py-1.5 text-xs" @change="(e) => { singlePurpose = 'order_revision'; onSinglePick(e); }" />
          </label>
          <button type="submit" class="focus-ring h-9 rounded-md bg-ink px-4 text-xs font-semibold text-white disabled:opacity-50" :disabled="!singleFile || files.isUploading">Upload revision file</button>
        </form>
      </div>
      <div v-if="!revisionFiles.length" class="px-5 py-8 text-center text-xs text-graphite">No revision files yet.</div>
      <div v-else class="divide-y divide-slate-50">
        <FileTile
          v-for="att in revisionFiles" :key="att.id"
          :att="att" :order-id="orderId" :role="role"
          :downloading="downloading" :deleting-id="deletingId"
          :deleting-in-flight="deletingInFlight" :delete-reason="deleteReason"
          :can-delete="canRequestDeletion" :can-staff-detach="false"
          @download="download" @open-delete="openDeletePrompt"
          @confirm-delete="confirmDelete" @cancel-delete="cancelDelete"
          @update:delete-reason="deleteReason = $event"
        />
      </div>
    </section>

    <!-- ═══ SECTION 5 — Internal / Staff only ══════════════════════════ -->
    <section v-if="isStaffRole">
      <div class="flex flex-wrap items-center justify-between gap-2 bg-amber-50/40 px-5 py-3">
        <div class="flex items-center gap-2">
          <Lock class="h-4 w-4 text-amber-600" />
          <h3 class="text-sm font-semibold text-ink">Internal files</h3>
          <span class="rounded-full border px-2 py-0.5 text-[10px] font-semibold bg-amber-50 text-amber-700 border-amber-200">Staff only</span>
        </div>
        <p class="text-xs text-graphite">Admin attachments and evidence not visible to clients or writers.</p>
      </div>
      <div class="border-b border-slate-100 p-4">
        <form class="flex flex-wrap items-end gap-3" @submit.prevent="() => { singlePurpose = 'admin_internal'; singleUpload(); }">
          <label class="flex-1 min-w-40">
            <input type="file" class="focus-ring block w-full rounded-md border border-slate-200 px-2 py-1.5 text-xs" @change="(e) => { singlePurpose = 'admin_internal'; onSinglePick(e); }" />
          </label>
          <button type="submit" class="focus-ring h-9 rounded-md bg-amber-600 px-4 text-xs font-semibold text-white disabled:opacity-50" :disabled="!singleFile || files.isUploading">Upload internal</button>
        </form>
      </div>
      <div v-if="!internalFiles.length" class="px-5 py-8 text-center text-xs text-graphite">No internal files.</div>
      <div v-else class="divide-y divide-slate-50">
        <FileTile
          v-for="att in internalFiles" :key="att.id"
          :att="att" :order-id="orderId" :role="role"
          :downloading="downloading" :deleting-id="deletingId"
          :deleting-in-flight="deletingInFlight" :delete-reason="deleteReason"
          :can-delete="true" :can-staff-detach="true" :detaching-id="detachingId"
          @download="download" @open-delete="openDeletePrompt"
          @confirm-delete="confirmDelete" @cancel-delete="cancelDelete"
          @update:delete-reason="deleteReason = $event"
          @staff-detach="staffDetach"
        />
      </div>
    </section>

    <!-- Delete confirm modal -->
    <div v-if="deletingId" class="fixed inset-0 z-50 flex items-center justify-center bg-black/30 p-4" @click.self="cancelDelete">
      <div class="w-full max-w-sm rounded-xl border border-slate-200 bg-white p-5 shadow-xl space-y-3">
        <h3 class="text-sm font-semibold text-ink">Request file removal</h3>
        <textarea :value="deleteReason" rows="3" placeholder="Reason for removal..." class="focus-ring w-full rounded-md border border-slate-200 px-3 py-2 text-sm" @input="deleteReason = ($event.target as HTMLTextAreaElement).value" />
        <div class="flex gap-2">
          <button class="focus-ring flex-1 h-9 rounded-md border border-slate-200 text-xs font-semibold text-graphite" @click="cancelDelete">Cancel</button>
          <button class="focus-ring flex-1 h-9 rounded-md bg-rose-600 text-xs font-semibold text-white disabled:opacity-50" :disabled="!deleteReason.trim() || deletingInFlight" @click="confirmDelete">
            {{ deletingInFlight ? 'Requesting...' : 'Request removal' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>
<script setup lang="ts">
import { computed, defineComponent, h, ref, type PropType } from "vue";
import {
  AlertCircle, BookOpen, CheckCircle2, Download, ExternalLink,
  FileUp, Loader2, Lock, Paperclip, Plus, RefreshCw, Send, Trash2, X,
} from "@lucide/vue";
import type { UserRole } from "@/types/roles";
import type { OrderSummary, OrderLifecycle } from "@/types/orders";
import { type DeliveryStatus, type FilePurpose } from "@/api/files";
import type { FileAttachment } from "@/api/files";
import { legalApi, type HelpArticleSummary } from "@/api/legal";
import { writerApi } from "@/api/writer";
import { useFilesStore, type QueuedFile } from "@/stores/files";
import { isStaff } from "../types";

// ── FileTile — inline file card component ────────────────────────────────────
const FileTile = defineComponent({
  props: {
    att: { type: Object as () => import("@/api/files").FileAttachment, required: true },
    orderId: { type: [String, Number], required: true },
    role: { type: String, required: true },
    downloading: { type: Number as PropType<number | null>, default: null },
    deletingId: { type: Number as PropType<number | null>, default: null },
    deletingInFlight: Boolean,
    deleteReason: { type: String, default: "" },
    canDelete: Boolean,
    canStaffDetach: Boolean,
    detachingId: { type: Number as PropType<number | null>, default: null },
    submittingFinal: { type: Number as PropType<number | null>, default: null },
    showSubmitFinal: Boolean,
  },
  emits: ["download","open-delete","confirm-delete","cancel-delete","update:delete-reason","submit-final","staff-detach"],
  setup(props, { emit }) {
    // Visibility badge colours (re-declared locally for the render fn)
    const VIS_LOCAL: Record<string, { label: string; cls: string }> = {
      client_writer_staff: { label: "All participants", cls: "bg-emerald-50 text-emerald-700 border-emerald-200" },
      order_participants:  { label: "All participants", cls: "bg-emerald-50 text-emerald-700 border-emerald-200" },
      writer_and_staff:    { label: "Writer + Staff",  cls: "bg-blue-50 text-blue-700 border-blue-200" },
      client_and_staff:    { label: "Client + Staff",  cls: "bg-violet-50 text-violet-700 border-violet-200" },
      staff_only:          { label: "Staff only",      cls: "bg-amber-50 text-amber-700 border-amber-200" },
      internal_only:       { label: "Internal",        cls: "bg-amber-50 text-amber-700 border-amber-200" },
      tenant_staff:        { label: "Staff only",      cls: "bg-amber-50 text-amber-700 border-amber-200" },
    };
    function vis(v: string) { return VIS_LOCAL[v] ?? { label: v.replace(/_/g," "), cls: "bg-slate-100 text-slate-500 border-slate-200" }; }

    function fileName(att: typeof props.att): string {
      return att.managed_file?.original_filename ?? att.external_link?.title ?? att.display_name ?? `File #${att.id}`;
    }
    function fileExt(att: typeof props.att): string {
      const n = fileName(att);
      const parts = n.split(".");
      return parts.length > 1 ? parts.pop()!.toLowerCase() : "";
    }
    function fileSz(bytes?: number | null): string {
      if (!bytes) return "";
      if (bytes < 1024) return `${bytes} B`;
      if (bytes < 1024*1024) return `${(bytes/1024).toFixed(1)} KB`;
      return `${(bytes/(1024*1024)).toFixed(1)} MB`;
    }
    function purposeLabel(p: string): string {
      return { order_instruction:"Instruction", order_reference:"Reference", order_draft:"Draft", order_final:"Final", order_revision:"Revision", writer_guide:"Guide", style_reference:"Style ref", admin_internal:"Internal", extra_service_file:"Extra service" }[p] ?? p.replace(/_/g," ");
    }

    return () => {
      const att = props.att as typeof props.att;
      const v = vis(att.visibility ?? "");
      const name = fileName(att);
      const ext = fileExt(att);
      const isLink = !!att.external_link;
      const isDownloading = props.downloading === att.id;
      const isDetaching = props.detachingId === att.id;

      return h("div", { class: "flex items-start gap-3 px-5 py-3 hover:bg-slate-50/60 transition-colors" }, [
        // File type icon / ext badge
        h("div", { class: "mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-slate-200 bg-slate-50 text-[10px] font-bold uppercase text-graphite" }, ext || (isLink ? "url" : "file")),
        // File info
        h("div", { class: "min-w-0 flex-1 space-y-0.5" }, [
          h("p", { class: "truncate text-sm font-medium text-ink" }, name),
          h("div", { class: "flex flex-wrap items-center gap-2 text-xs text-graphite" }, [
            att.is_new_for_user
              ? h("span", { class: "rounded-full bg-saffron px-2 py-0.5 text-[10px] font-bold text-white" }, "New")
              : null,
            // Purpose badge
            h("span", { class: "rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-medium capitalize" }, purposeLabel(att.purpose)),
            // Visibility badge
            h("span", { class: `rounded-full border px-2 py-0.5 text-[10px] font-semibold ${v.cls}` }, v.label),
            // Size
            att.managed_file?.file_size_bytes ? h("span", {}, fileSz(att.managed_file.file_size_bytes)) : null,
            // Date
            att.attached_at ? h("span", {}, new Date(att.attached_at).toLocaleDateString()) : null,
            // Delivery status badge
            att.delivery_status && att.delivery_status !== "pending" ?
              h("span", { class: att.delivery_status === "approved" ? "text-emerald-600 font-semibold" : att.delivery_status === "submitted" ? "text-blue-600 font-semibold" : "text-amber-600 font-semibold" },
                att.delivery_status) : null,
          ]),
        ]),
        // Actions
        h("div", { class: "flex shrink-0 items-center gap-1.5" }, [
          // Download / open link
          h("button", {
            class: "focus-ring flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 text-graphite hover:border-slate-300 hover:text-ink disabled:opacity-40",
            disabled: isDownloading,
            title: isLink ? "Open link" : "Download file",
            onClick: () => emit("download", att.id),
          }, isDownloading
            ? h(Loader2, { class: "h-3.5 w-3.5 animate-spin" })
            : h(isLink ? ExternalLink : Download, { class: "h-3.5 w-3.5" })),

          // Submit final (writer only)
          props.showSubmitFinal && att.delivery_status === "pending" ?
            h("button", {
              class: "focus-ring flex h-8 items-center gap-1 rounded-lg border border-signal px-2 text-[11px] font-semibold text-signal hover:bg-signal hover:text-white disabled:opacity-40",
              disabled: props.submittingFinal === att.id,
              title: "Mark as final deliverable",
              onClick: () => emit("submit-final", att.id),
            }, props.submittingFinal === att.id ? [h(Loader2, { class: "h-3 w-3 animate-spin" })] : [h(Send, { class: "h-3 w-3" }), " Submit"]) : null,

          // Staff quick-detach (for guides and internal)
          props.canStaffDetach ?
            h("button", {
              class: "focus-ring flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 text-slate-400 hover:border-rose-200 hover:bg-rose-50 hover:text-rose-500 disabled:opacity-40",
              disabled: isDetaching,
              title: "Detach file",
              onClick: () => emit("staff-detach", att.id),
            }, isDetaching ? h(Loader2, { class: "h-3.5 w-3.5 animate-spin" }) : h(X, { class: "h-3.5 w-3.5" })) : null,

          // Standard delete request
          props.canDelete && !props.canStaffDetach ?
            h("button", {
              class: "focus-ring flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 text-slate-400 hover:border-rose-200 hover:bg-rose-50 hover:text-rose-500",
              title: "Request removal",
              onClick: () => emit("open-delete", att.id),
            }, h(Trash2, { class: "h-3.5 w-3.5" })) : null,
        ]),
      ]);
    };
  },
});

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
const canSeeWriterGuides = computed(() => props.role === "writer" || isStaffRole.value);
const writerGuides    = computed(() => files.attachments.filter((a) => a.purpose === "writer_guide" || a.purpose === "style_reference"));
const clientMaterials = computed(() => files.attachments.filter((a) => a.purpose === "order_instruction" || a.purpose === "order_reference"));
const draftDeliverables = computed(() => files.attachments.filter((a) => ["order_draft","order_final","extra_service_file"].includes(a.purpose)));
const revisionFiles   = computed(() => files.attachments.filter((a) => a.purpose === "order_revision"));
const internalFiles   = computed(() => files.attachments.filter((a) => a.purpose === "admin_internal"));

// ── Visibility badge ─────────────────────────────────────────────────────────
interface VisBadge { label: string; cls: string }
const VIS: Record<string, VisBadge> = {
  client_writer_staff:  { label: "All participants", cls: "bg-emerald-50 text-emerald-700 border-emerald-200" },
  order_participants:   { label: "All participants", cls: "bg-emerald-50 text-emerald-700 border-emerald-200" },
  writer_and_staff:     { label: "Writer + Staff",   cls: "bg-blue-50 text-blue-700 border-blue-200" },
  client_and_staff:     { label: "Client + Staff",   cls: "bg-violet-50 text-violet-700 border-violet-200" },
  staff_only:           { label: "Staff only",       cls: "bg-amber-50 text-amber-700 border-amber-200" },
  internal_only:        { label: "Internal",         cls: "bg-amber-50 text-amber-700 border-amber-200" },
  tenant_staff:         { label: "Staff only",       cls: "bg-amber-50 text-amber-700 border-amber-200" },
  owner_only:           { label: "Private",          cls: "bg-slate-100 text-slate-500 border-slate-200" },
  private:              { label: "Private",          cls: "bg-slate-100 text-slate-500 border-slate-200" },
};
function visBadge(v: string): VisBadge {
  return VIS[v] ?? { label: v.replace(/_/g," "), cls: "bg-slate-100 text-slate-500 border-slate-200" };
}
// ── Staff quick-detach ────────────────────────────────────────────────────────
const detachingId = ref<number | null>(null);
async function staffDetach(attachmentId: number) {
  detachingId.value = attachmentId;
  try {
    await files.requestFileDeletion(props.orderId, attachmentId, "Staff detached file");
  } finally {
    detachingId.value = null;
  }
}

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
  writer_guide: "Writer guide",
  style_reference: "Style reference",
  extra_service_file: "Extra service",
  message_attachment: "Message attachment",
};

function purposeLabel(p: string): string {
  return PURPOSE_LABELS[p] ?? p.replace(/_/g, " ");
}

function guideDescriptionText(guide: FileAttachment): string {
  const value = guide.metadata?.description;
  return typeof value === "string" ? value : "";
}

function guideTypeLabel(guide: FileAttachment): string {
  const value = guide.metadata?.guide_type;
  const raw = typeof value === "string" && value ? value : "guide";
  return raw.replace(/_/g, " ");
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
const guideFile = ref<File | null>(null);
const guideType = ref("guide");
const guideDescription = ref("");
const guideLinkTitle = ref("");
const guideLinkUrl = ref("");
const guideArticles = ref<HelpArticleSummary[]>([]);
const selectedGuideSlug = ref("");

function onSinglePick(event: Event) {
  const input = event.target as HTMLInputElement;
  singleFile.value = input.files?.[0] ?? null;
  files.clearMessages();
}

function onGuidePick(event: Event) {
  const input = event.target as HTMLInputElement;
  guideFile.value = input.files?.[0] ?? null;
  files.clearMessages();
}

async function singleUpload() {
  if (!singleFile.value) return;
  await files.uploadSingleFile(
    props.orderId,
    singleFile.value,
    singlePurpose.value,
    singlePurpose.value === "writer_guide"
      ? { category_code: "guide", description: "Staff-provided writer guide." }
      : undefined,
  );
  singleFile.value = null;
}

async function uploadGuideFile() {
  if (!guideFile.value) return;
  await files.uploadSingleFile(props.orderId, guideFile.value, "writer_guide", {
    category_code: guideType.value,
    description: guideDescription.value,
  });
  guideFile.value = null;
  guideDescription.value = "";
  guideType.value = "guide";
}

async function addGuideLink() {
  if (!guideLinkUrl.value) return;
  await files.submitExternalLink(props.orderId, {
    url: guideLinkUrl.value,
    title: guideLinkTitle.value || guideLinkUrl.value,
    purpose: "writer_guide",
  });
  guideLinkTitle.value = "";
  guideLinkUrl.value = "";
}

async function loadGuideArticles() {
  if (guideArticles.value.length) return;
  try {
    const { data } = await legalApi.articles();
    guideArticles.value = data.filter((article) =>
      ["writer", "staff", "all", "everyone"].includes(String(article.audience || "").toLowerCase()),
    );
  } catch {
    guideArticles.value = [];
  }
}

async function attachExistingGuide() {
  const article = guideArticles.value.find((item) => item.slug === selectedGuideSlug.value);
  if (!article) return;
  // Use a relative URL so the link resolves against the writer portal origin,
  // not the staff origin this page is served from. Full portal-aware URL
  // generation requires the portal context API (not yet built).
  const url = `/writer/guides/${article.slug}`;
  await files.submitExternalLink(props.orderId, {
    url,
    title: article.title,
    purpose: "writer_guide",
  });
  selectedGuideSlug.value = "";
}

// ── Payment re-check ─────────────────────────────────────────────────────────

async function recheckAccess() {
  files.clearMessages();
  await files.fetchOrderAttachments(props.orderId);
}

// ── Delivery helpers ─────────────────────────────────────────────────────────

const DELIVERY_LABELS: Record<DeliveryStatus, string> = {
  pending: "Awaiting submission",
  submitted: "Submitted",
  locked: "Payment required",
  approved: "Ready to download",
  rejected: "Rejected",
};

function deliveryLabel(s: DeliveryStatus): string {
  return DELIVERY_LABELS[s] ?? s.replace(/_/g, " ");
}

function deliveryBadge(s: DeliveryStatus): string {
  if (s === "approved") return "bg-emerald-100 text-emerald-700";
  if (s === "submitted") return "bg-blue-100 text-blue-700";
  if (s === "rejected") return "bg-rose-100 text-rose-700";
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
