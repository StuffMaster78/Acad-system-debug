<script setup lang="ts">
import { onMounted, ref } from "vue";
import { FileWarning, History, Link2, RefreshCw, ShieldCheck, Trash2 } from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useAdminFilesStore } from "@/stores/adminFiles";
import { filesApi, type FileVersion } from "@/api/files";

const files = useAdminFilesStore();

const expandedFileId = ref<number | null>(null);
const versions = ref<FileVersion[]>([]);
const versionsLoading = ref(false);
const versionsError = ref("");

async function toggleVersions(fileId: number) {
  if (expandedFileId.value === fileId) {
    expandedFileId.value = null;
    return;
  }
  expandedFileId.value = fileId;
  versionsLoading.value = true;
  versionsError.value = "";
  versions.value = [];
  try {
    const { data } = await filesApi.fileVersions(fileId);
    versions.value = data;
  } catch {
    versionsError.value = "Could not load version history.";
  } finally {
    versionsLoading.value = false;
  }
}

function bytesLabel(value?: number) {
  if (!value) return "0 B";
  if (value < 1024 * 1024) return `${Math.round(value / 1024)} KB`;
  return `${(value / 1024 / 1024).toFixed(1)} MB`;
}

function dateLabel(value?: string) {
  if (!value) return "Not recorded";
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function fileName(file: { name?: string; original_filename?: string }) {
  return file.name || file.original_filename || "Untitled file";
}

onMounted(() => {
  files.hydrate().catch(() => undefined);
});
</script>

<template>
  <div class="space-y-4">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Admin</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Files</h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
          Centralized file governance for uploads, external links, quarantine, policies, and deletion requests.
        </p>
      </div>
      <button
        class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-300 px-4 text-sm font-semibold text-ink disabled:cursor-not-allowed disabled:opacity-60"
        type="button"
        :disabled="files.isLoading"
        @click="files.hydrate()"
      >
        <RefreshCw class="h-4 w-4" />
        Refresh
      </button>
    </section>

    <div v-if="files.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ files.error }}
    </div>
    <div v-if="files.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
      {{ files.notice }}
    </div>

    <section class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <div class="rounded-md border border-slate-200 bg-white p-4">
        <p class="text-sm font-medium text-graphite">Managed files</p>
        <p class="mt-3 text-3xl font-semibold text-ink">{{ files.files.length }}</p>
        <p class="mt-2 text-sm text-graphite">{{ files.activeFiles.length }} active</p>
      </div>
      <div class="rounded-md border border-amber-200 bg-amber-50 p-4">
        <p class="text-sm font-medium text-amber-900">Quarantine</p>
        <p class="mt-3 text-3xl font-semibold text-amber-950">{{ files.quarantinedFiles.length }}</p>
        <p class="mt-2 text-sm text-amber-900">Needs staff review</p>
      </div>
      <div class="rounded-md border border-rose-200 bg-rose-50 p-4">
        <p class="text-sm font-medium text-rose-900">Deletion requests</p>
        <p class="mt-3 text-3xl font-semibold text-rose-950">{{ files.pendingDeletionRequests.length }}</p>
        <p class="mt-2 text-sm text-rose-900">Pending review</p>
      </div>
      <div class="rounded-md border border-slate-200 bg-white p-4">
        <p class="text-sm font-medium text-graphite">Policies</p>
        <p class="mt-3 text-3xl font-semibold text-ink">{{ files.policies.length }}</p>
        <p class="mt-2 text-sm text-graphite">Tenant file rules</p>
      </div>
    </section>

    <section class="rounded-lg border border-slate-200 bg-white p-5">
      <div class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <h2 class="text-lg font-semibold text-ink">Managed files</h2>
          <p class="mt-1 text-sm text-graphite">Search and review tenant uploads.</p>
        </div>
        <form class="flex gap-2" @submit.prevent="files.hydrate()">
          <input
            v-model.trim="files.query"
            class="focus-ring h-10 rounded-md border border-slate-300 px-3 text-sm"
            placeholder="Search files"
          />
          <button class="focus-ring rounded-md bg-ink px-4 text-sm font-semibold text-white" type="submit">
            Search
          </button>
        </form>
      </div>

      <div class="mt-5 overflow-hidden rounded-md border border-slate-200">
        <div class="grid grid-cols-[1fr_120px_120px_120px_auto_auto] gap-3 bg-slate-50 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
          <span>File</span>
          <span>Size</span>
          <span>Scan</span>
          <span>Status</span>
          <span class="text-right">Action</span>
          <span class="text-right">History</span>
        </div>
        <div v-if="files.isLoading" class="px-4 py-6 text-sm text-graphite">Loading files...</div>
        <div v-else-if="!files.files.length" class="px-4 py-6 text-sm text-graphite">No files found.</div>
        <template v-else>
          <div
            v-for="file in files.files"
            :key="String(file.id ?? file.uuid ?? fileName(file))"
          >
            <div class="grid grid-cols-[1fr_120px_120px_120px_auto_auto] items-center gap-3 border-t border-slate-100 px-4 py-3 text-sm">
              <div>
                <p class="font-semibold text-ink">{{ fileName(file) }}</p>
                <p class="mt-1 text-xs text-graphite">{{ file.mime_type || file.file_kind || "unknown" }}</p>
              </div>
              <span class="text-graphite">{{ bytesLabel(file.file_size_bytes) }}</span>
              <StatusPill :label="file.scan_status ?? 'unknown'" />
              <StatusPill :label="file.lifecycle_status ?? 'unknown'" />
              <button
                v-if="file.lifecycle_status === 'quarantined' && file.id"
                class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-amber-300 px-3 py-2 text-xs font-semibold text-amber-900 disabled:cursor-not-allowed disabled:opacity-60"
                type="button"
                :disabled="files.isMutating"
                @click="files.releaseQuarantine(file.id)"
              >
                <ShieldCheck class="h-3.5 w-3.5" />
                Release
              </button>
              <span v-else />
              <button
                v-if="file.id"
                class="focus-ring inline-flex items-center justify-center gap-1.5 rounded-md border border-slate-200 px-3 py-2 text-xs font-semibold text-graphite hover:border-ink hover:text-ink"
                :class="expandedFileId === file.id ? 'border-ink text-ink' : ''"
                type="button"
                @click="toggleVersions(file.id!)"
              >
                <History class="h-3.5 w-3.5" />
                Versions
              </button>
              <span v-else />
            </div>

            <div
              v-if="expandedFileId === file.id"
              class="border-t border-dashed border-slate-100 bg-slate-50/60 px-5 py-4"
            >
              <p class="mb-3 text-xs font-semibold uppercase tracking-wide text-graphite">Version history</p>
              <div v-if="versionsLoading" class="text-sm text-graphite">Loading versions…</div>
              <div v-else-if="versionsError" class="text-sm text-berry">{{ versionsError }}</div>
              <div v-else-if="!versions.length" class="text-sm text-graphite">No version history recorded.</div>
              <table v-else class="min-w-full text-xs">
                <thead class="text-left text-graphite">
                  <tr>
                    <th class="pb-2 pr-4 font-semibold uppercase">#</th>
                    <th class="pb-2 pr-4 font-semibold uppercase">Replaced file</th>
                    <th class="pb-2 pr-4 font-semibold uppercase">Uploaded by</th>
                    <th class="pb-2 pr-4 font-semibold uppercase">Date</th>
                    <th class="pb-2 font-semibold uppercase">Notes</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
                  <tr v-for="v in versions" :key="v.id">
                    <td class="py-2 pr-4 font-mono font-semibold text-ink">v{{ v.version_number }}</td>
                    <td class="py-2 pr-4 text-graphite">{{ v.replaced_file_name ?? "—" }}</td>
                    <td class="py-2 pr-4 text-graphite">{{ v.created_by_email ?? "—" }}</td>
                    <td class="py-2 pr-4 text-graphite">{{ dateLabel(v.created_at ?? undefined) }}</td>
                    <td class="py-2 text-graphite">{{ v.notes ?? "—" }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </template>
      </div>
    </section>

    <section class="grid gap-6 xl:grid-cols-2">
      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <div class="flex items-center justify-between gap-3">
          <div>
            <h2 class="text-lg font-semibold text-ink">Deletion requests</h2>
            <p class="mt-1 text-sm text-graphite">Review detach/delete workflows.</p>
          </div>
          <Trash2 class="h-5 w-5 text-rose-700" />
        </div>
        <div class="mt-5 space-y-3">
          <p v-if="!files.deletionRequests.length" class="text-sm text-graphite">No deletion requests.</p>
          <article
            v-for="request in files.deletionRequests"
            :key="request.id"
            class="rounded-md border border-slate-200 p-4"
          >
            <div class="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p class="text-sm font-semibold text-ink">Request #{{ request.id }}</p>
                <p class="mt-1 text-sm text-graphite">{{ request.reason }}</p>
                <p class="mt-1 text-xs text-slate-500">{{ request.scope }} · {{ dateLabel(request.created_at) }}</p>
              </div>
              <StatusPill :label="request.status" />
            </div>
            <div class="mt-4 flex flex-wrap gap-2">
              <button
                class="focus-ring rounded-md border border-emerald-300 px-3 py-2 text-xs font-semibold text-emerald-800 disabled:cursor-not-allowed disabled:opacity-60"
                type="button"
                :disabled="files.isMutating || request.status !== 'pending'"
                @click="files.reviewDeletionRequest(request.id, 'approve')"
              >
                Approve
              </button>
              <button
                class="focus-ring rounded-md border border-rose-300 px-3 py-2 text-xs font-semibold text-rose-800 disabled:cursor-not-allowed disabled:opacity-60"
                type="button"
                :disabled="files.isMutating || request.status !== 'pending'"
                @click="files.reviewDeletionRequest(request.id, 'reject')"
              >
                Reject
              </button>
              <button
                class="focus-ring rounded-md border border-slate-300 px-3 py-2 text-xs font-semibold text-ink disabled:cursor-not-allowed disabled:opacity-60"
                type="button"
                :disabled="files.isMutating || request.status !== 'approved'"
                @click="files.reviewDeletionRequest(request.id, 'complete')"
              >
                Complete
              </button>
            </div>
          </article>
        </div>
      </div>

      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <div class="flex items-center justify-between gap-3">
          <div>
            <h2 class="text-lg font-semibold text-ink">External links</h2>
            <p class="mt-1 text-sm text-graphite">Review submitted cloud links before download access.</p>
          </div>
          <Link2 class="h-5 w-5 text-signal" />
        </div>
        <div class="mt-5 space-y-3">
          <p v-if="!files.externalLinks.length" class="text-sm text-graphite">No external links.</p>
          <article
            v-for="link in files.externalLinks"
            :key="link.id"
            class="rounded-md border border-slate-200 p-4"
          >
            <div class="flex flex-wrap items-start justify-between gap-3">
              <div class="min-w-0">
                <p class="truncate text-sm font-semibold text-ink">{{ link.url }}</p>
                <p class="mt-1 text-xs text-graphite">{{ link.provider || "external" }} · {{ dateLabel(link.created_at) }}</p>
              </div>
              <StatusPill :label="link.review_status ?? 'unknown'" />
            </div>
            <div class="mt-4 flex flex-wrap gap-2">
              <button
                class="focus-ring rounded-md border border-emerald-300 px-3 py-2 text-xs font-semibold text-emerald-800 disabled:cursor-not-allowed disabled:opacity-60"
                type="button"
                :disabled="files.isMutating || link.review_status === 'approved'"
                @click="files.reviewExternalLink(link.id, 'approve')"
              >
                Approve
              </button>
              <button
                class="focus-ring rounded-md border border-rose-300 px-3 py-2 text-xs font-semibold text-rose-800 disabled:cursor-not-allowed disabled:opacity-60"
                type="button"
                :disabled="files.isMutating || link.review_status === 'rejected'"
                @click="files.reviewExternalLink(link.id, 'reject')"
              >
                Reject
              </button>
            </div>
          </article>
        </div>
      </div>
    </section>

    <section class="rounded-lg border border-slate-200 bg-white p-5">
      <div class="flex items-center gap-2">
        <FileWarning class="h-5 w-5 text-saffron" />
        <h2 class="text-lg font-semibold text-ink">Policy summary</h2>
      </div>
      <div class="mt-5 grid gap-3 lg:grid-cols-2">
        <article
          v-for="policy in files.policies"
          :key="policy.id"
          class="rounded-md border border-slate-200 p-4"
        >
          <div class="flex items-start justify-between gap-3">
            <div>
              <p class="text-sm font-semibold text-ink">{{ policy.name }}</p>
              <p class="mt-1 text-xs text-graphite">{{ policy.purpose }} · {{ bytesLabel(policy.max_file_size_bytes) }} max</p>
            </div>
            <StatusPill :label="policy.is_active ? 'active' : 'inactive'" :tone="policy.is_active ? 'success' : 'warning'" />
          </div>
          <p class="mt-3 text-sm text-graphite">
            {{ policy.require_scan_before_download ? "Scan required" : "Scan optional" }} ·
            {{ policy.external_links_require_review ? "External links reviewed" : "External links direct" }}
          </p>
        </article>
      </div>
    </section>
  </div>
</template>
