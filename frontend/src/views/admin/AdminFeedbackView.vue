<template>
  <div class="space-y-5 px-4 py-6">
    <!-- Header -->
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-xl font-bold text-ink">Feedback & Requests</h1>
        <p class="mt-0.5 text-sm text-graphite">Triage, respond, and track product improvement requests.</p>
      </div>
      <button
        class="focus-ring inline-flex h-9 items-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold"
        @click="loadAll"
      >
        <RefreshCw class="h-4 w-4" /> Refresh
      </button>
    </div>

    <!-- Summary widgets -->
    <div v-if="fb.summary" class="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-7">
      <div
        v-for="(count, st) in fb.summary.by_status"
        :key="st"
        class="cursor-pointer rounded-lg border border-slate-200 bg-white p-3 transition-shadow hover:shadow-sm"
        :class="filters.status === st ? 'ring-2 ring-signal' : ''"
        @click="toggleFilter('status', st)"
      >
        <p class="text-xs font-semibold uppercase text-graphite">{{ st.replace("_", " ") }}</p>
        <p class="mt-1 text-2xl font-bold text-ink">{{ count }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap items-center gap-2 rounded-lg border border-slate-200 bg-white p-3">
      <input
        v-model="filters.search"
        type="search"
        placeholder="Search title or description…"
        class="focus-ring h-8 min-w-[200px] rounded-md border border-slate-200 px-3 text-sm"
        @keyup.enter="applyFilters"
      />
      <select v-model="filters.surface" class="focus-ring h-8 rounded-md border border-slate-200 px-2 text-sm" @change="applyFilters">
        <option value="">All surfaces</option>
        <option value="client">Client</option>
        <option value="writer">Writer</option>
        <option value="staff">Staff</option>
      </select>
      <select v-model="filters.category" class="focus-ring h-8 rounded-md border border-slate-200 px-2 text-sm" @change="applyFilters">
        <option value="">All categories</option>
        <option v-for="cat in allCategories" :key="cat.value" :value="cat.value">{{ cat.label }}</option>
      </select>
      <select v-model="filters.priority" class="focus-ring h-8 rounded-md border border-slate-200 px-2 text-sm" @change="applyFilters">
        <option value="">All priorities</option>
        <option value="critical">Critical</option>
        <option value="high">High</option>
        <option value="medium">Medium</option>
        <option value="low">Low</option>
      </select>
      <select v-model="filters.request_type" class="focus-ring h-8 rounded-md border border-slate-200 px-2 text-sm" @change="applyFilters">
        <option value="">All types</option>
        <option value="feature_request">Feature</option>
        <option value="improvement">Improvement</option>
        <option value="bug_report">Bug</option>
        <option value="question">Question</option>
      </select>
      <select v-model="filters.owner" class="focus-ring h-8 rounded-md border border-slate-200 px-2 text-sm" @change="applyFilters">
        <option value="">All owners</option>
        <option value="me">Assigned to me</option>
        <option value="unassigned">Unassigned</option>
      </select>
      <button
        v-if="fb.activeFilterCount"
        class="h-8 rounded-md px-2 text-xs font-semibold text-graphite hover:text-ink"
        @click="() => { fb.resetFilters(); applyFilters(); }"
      >
        Clear ({{ fb.activeFilterCount }})
      </button>
    </div>

    <!-- Notice -->
    <p v-if="fb.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm text-emerald-900">{{ fb.notice }}</p>
    <p v-if="fb.error" class="rounded-md border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-800">{{ fb.error }}</p>

    <!-- Table -->
    <div class="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
      <table class="min-w-full text-sm">
        <thead class="border-b border-slate-100 bg-slate-50">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-semibold uppercase text-graphite">Request</th>
            <th class="px-3 py-3 text-left text-xs font-semibold uppercase text-graphite">Type</th>
            <th class="px-3 py-3 text-left text-xs font-semibold uppercase text-graphite">Surface</th>
            <th class="px-3 py-3 text-left text-xs font-semibold uppercase text-graphite">Category</th>
            <th class="px-3 py-3 text-left text-xs font-semibold uppercase text-graphite">Priority</th>
            <th class="px-3 py-3 text-left text-xs font-semibold uppercase text-graphite">Status</th>
            <th class="px-3 py-3 text-left text-xs font-semibold uppercase text-graphite">▲ Votes</th>
            <th class="px-3 py-3 text-left text-xs font-semibold uppercase text-graphite">Owner</th>
            <th class="px-3 py-3 text-left text-xs font-semibold uppercase text-graphite">Submitted</th>
            <th class="px-3 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-if="fb.isLoading">
            <td colspan="10" class="px-4 py-8 text-center text-sm text-graphite">Loading…</td>
          </tr>
          <tr v-else-if="!fb.items.length">
            <td colspan="10" class="px-4 py-8 text-center text-sm text-graphite">No requests match the current filters.</td>
          </tr>
          <tr
            v-for="item in fb.items"
            :key="item.id"
            class="hover:bg-slate-50 cursor-pointer"
            @click="openDetail(item)"
          >
            <td class="max-w-xs px-4 py-3">
              <p class="truncate font-semibold text-ink">{{ item.title }}</p>
              <p class="truncate text-xs text-graphite">by {{ item.requester_display }}</p>
            </td>
            <td class="px-3 py-3 text-xs text-graphite capitalize">{{ item.request_type.replace("_", " ") }}</td>
            <td class="px-3 py-3">
              <span class="rounded-full px-2 py-0.5 text-xs font-semibold capitalize"
                :class="surfaceClass(item.portal_surface)">{{ item.portal_surface }}</span>
            </td>
            <td class="px-3 py-3 text-xs text-graphite">{{ item.category }}</td>
            <td class="px-3 py-3">
              <span class="rounded-full px-2 py-0.5 text-xs font-semibold capitalize"
                :class="priorityClass(item.priority)">{{ item.priority }}</span>
            </td>
            <td class="px-3 py-3">
              <span class="rounded-full px-2 py-0.5 text-xs font-semibold"
                :class="statusClass(item.status)">{{ item.status.replace("_", " ") }}</span>
            </td>
            <td class="px-3 py-3 text-center text-sm font-semibold text-graphite">{{ item.upvote_count }}</td>
            <td class="px-3 py-3 text-xs text-graphite">{{ item.staff_owner_name ?? "—" }}</td>
            <td class="px-3 py-3 text-xs text-graphite">{{ fmtDate(item.created_at) }}</td>
            <td class="px-3 py-3" @click.stop>
              <button
                class="focus-ring rounded-md border border-slate-200 px-2 py-1 text-xs font-semibold hover:bg-slate-50"
                @click="openDetail(item)"
              >Open</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="fb.totalCount > 25" class="flex items-center justify-between text-sm text-graphite">
      <span>{{ fb.items.length }} of {{ fb.totalCount }} requests</span>
      <button
        v-if="fb.hasMore"
        class="focus-ring rounded-md border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold"
        :disabled="fb.isLoading"
        @click="loadMore"
      >Load more</button>
    </div>

    <!-- Detail panel (slide-over) -->
    <Transition name="slide">
      <div v-if="detailItem" class="fixed inset-y-0 right-0 z-50 flex w-full max-w-xl flex-col border-l border-slate-200 bg-white shadow-2xl">
        <!-- Panel header -->
        <div class="flex items-center justify-between border-b border-slate-100 px-5 py-4">
          <h2 class="text-base font-semibold text-ink">Request #{{ detailItem.id }}</h2>
          <button class="rounded-md p-1 text-graphite hover:bg-slate-100" @click="detailItem = null">✕</button>
        </div>

        <div class="flex-1 overflow-y-auto px-5 py-4 space-y-5">
          <!-- Meta -->
          <div>
            <p class="text-lg font-bold text-ink">{{ detailItem.title }}</p>
            <div class="mt-2 flex flex-wrap gap-2 text-xs">
              <span class="rounded-full px-2 py-0.5 font-semibold" :class="statusClass(detailItem.status)">
                {{ detailItem.status.replace("_", " ") }}</span>
              <span class="rounded-full px-2 py-0.5 font-semibold" :class="priorityClass(detailItem.priority)">
                {{ detailItem.priority }}</span>
              <span class="rounded-full px-2 py-0.5 font-semibold" :class="surfaceClass(detailItem.portal_surface)">
                {{ detailItem.portal_surface }}</span>
              <span class="text-graphite">{{ detailItem.category }} · {{ detailItem.request_type.replace("_", " ") }}</span>
            </div>
            <p class="mt-1 text-xs text-graphite">
              By {{ detailItem.requester_display }} ({{ detailItem.requester_role }}) · {{ fmtDate(detailItem.created_at) }}
              · ▲ {{ detailItem.upvote_count }} votes
            </p>
          </div>

          <div class="prose prose-sm max-w-none rounded-md border border-slate-100 bg-slate-50 p-3 text-sm text-ink">
            {{ detailItem.description }}
          </div>

          <!-- Triage controls -->
          <div class="space-y-3 rounded-xl border border-slate-200 p-4">
            <h3 class="text-xs font-semibold uppercase text-graphite">Triage</h3>
            <div class="grid grid-cols-2 gap-3">
              <label class="block">
                <span class="text-xs text-graphite">Status</span>
                <select v-model="triage.status" class="focus-ring mt-1 h-9 w-full rounded-md border border-slate-200 px-2 text-sm">
                  <option value="new">New</option>
                  <option value="triaging">Triaging</option>
                  <option value="planned">Planned</option>
                  <option value="in_progress">In Progress</option>
                  <option value="released">Released</option>
                  <option value="declined">Declined</option>
                  <option value="duplicate">Duplicate</option>
                </select>
              </label>
            </div>
            <label class="block">
              <span class="text-xs text-graphite">Internal note (optional)</span>
              <textarea v-model="triage.note" rows="2"
                class="focus-ring mt-1 w-full rounded-md border border-slate-200 px-3 py-1.5 text-sm" />
            </label>
            <label class="block">
              <span class="text-xs text-graphite">Internal notes (persistent)</span>
              <textarea v-model="triage.internal_notes" rows="3"
                class="focus-ring mt-1 w-full rounded-md border border-slate-200 px-3 py-1.5 text-sm" />
            </label>
            <button
              class="focus-ring h-9 rounded-md bg-ink px-4 text-sm font-semibold text-white disabled:opacity-50"
              :disabled="fb.isMutating"
              @click="saveTriage"
            >Save triage</button>
          </div>

          <!-- Public response -->
          <div class="space-y-3 rounded-xl border border-slate-200 p-4">
            <h3 class="text-xs font-semibold uppercase text-graphite">Public response</h3>
            <p v-if="detailItem.public_response" class="rounded-md bg-emerald-50 p-3 text-sm text-emerald-900">
              {{ detailItem.public_response }}
            </p>
            <label class="block">
              <span class="text-xs text-graphite">{{ detailItem.public_response ? "Update response" : "Write a response" }}</span>
              <textarea v-model="responseText" rows="4"
                class="focus-ring mt-1 w-full rounded-md border border-slate-200 px-3 py-1.5 text-sm"
                placeholder="Visible to the requester…" />
            </label>
            <button
              class="focus-ring h-9 rounded-md bg-signal px-4 text-sm font-semibold text-white disabled:opacity-50"
              :disabled="fb.isMutating || !responseText.trim()"
              @click="postResponse"
            >Post response</button>
          </div>

          <!-- Mark duplicate -->
          <div class="space-y-2 rounded-xl border border-slate-200 p-4">
            <h3 class="text-xs font-semibold uppercase text-graphite">Mark as duplicate</h3>
            <div class="flex gap-2">
              <input v-model.number="duplicateId" type="number" placeholder="Parent request ID"
                class="focus-ring h-9 w-full rounded-md border border-slate-200 px-3 text-sm" />
              <button
                class="focus-ring shrink-0 h-9 rounded-md border border-slate-200 px-3 text-xs font-semibold"
                :disabled="!duplicateId || fb.isMutating"
                @click="markDup"
              >Mark</button>
            </div>
          </div>

          <!-- Status history -->
          <div v-if="detailItem.status_history?.length" class="space-y-2">
            <h3 class="text-xs font-semibold uppercase text-graphite">Status history</h3>
            <div v-for="ev in detailItem.status_history" :key="ev.id"
              class="rounded-md border border-slate-100 px-3 py-2 text-xs text-graphite">
              <span class="font-semibold text-ink">{{ ev.from_status || "—" }} → {{ ev.to_status }}</span>
              <span v-if="ev.changed_by_name"> by {{ ev.changed_by_name }}</span>
              · {{ fmtDate(ev.created_at) }}
              <p v-if="ev.note" class="mt-0.5 text-graphite">{{ ev.note }}</p>
            </div>
          </div>
        </div>
      </div>
    </Transition>
    <div v-if="detailItem" class="fixed inset-0 z-40 bg-black/20" @click="detailItem = null" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { RefreshCw } from "@lucide/vue";
import { useFeedbackStore } from "@/stores/feedback";
import type { FeedbackItem, FeedbackStatus } from "@/api/feedback";

const fb = useFeedbackStore();
const detailItem = ref<FeedbackItem | null>(null);
const responseText = ref("");
const duplicateId = ref<number | null>(null);
const triage = reactive({ status: "new" as FeedbackStatus, note: "", internal_notes: "" });

const filters = computed(() => fb.filters);

const allCategories = computed(() => [
  { value: "orders", label: "Orders" },
  { value: "payments", label: "Payments & Billing" },
  { value: "client_experience", label: "Client Experience" },
  { value: "writer_workflow", label: "Writer Workflow" },
  { value: "payout_earnings", label: "Payout & Earnings" },
  { value: "bidding", label: "Bidding & Queue" },
  { value: "cms", label: "CMS & Content" },
  { value: "analytics", label: "Analytics" },
  { value: "admin_tools", label: "Admin Tools" },
  { value: "bug_report", label: "Bug Report" },
  { value: "other", label: "Other" },
]);

onMounted(loadAll);

async function loadAll() {
  await Promise.all([fb.load(true), fb.loadSummary()]);
}

function applyFilters() {
  fb.load(true);
}

function toggleFilter(key: keyof typeof fb.filters, value: string) {
  fb.filters[key] = fb.filters[key] === value ? "" : value;
  applyFilters();
}

async function loadMore() {
  fb.page += 1;
  await fb.load(false);
}

function openDetail(item: FeedbackItem) {
  detailItem.value = item;
  triage.status = item.status;
  triage.internal_notes = item.internal_notes ?? "";
  triage.note = "";
  responseText.value = "";
  duplicateId.value = null;
  // Load full detail with status_history
  fb.loadDetail(item.id).then(() => {
    if (fb.detail) detailItem.value = fb.detail;
  });
}

async function saveTriage() {
  if (!detailItem.value) return;
  await fb.triageUpdate(detailItem.value.id, {
    status: triage.status,
    internal_notes: triage.internal_notes,
    note: triage.note,
  });
  if (fb.detail) detailItem.value = fb.detail;
  triage.note = "";
}

async function postResponse() {
  if (!detailItem.value || !responseText.value.trim()) return;
  await fb.respond(detailItem.value.id, responseText.value.trim());
  if (fb.detail) detailItem.value = fb.detail;
  responseText.value = "";
}

async function markDup() {
  if (!detailItem.value || !duplicateId.value) return;
  await fb.markDuplicate(detailItem.value.id, duplicateId.value);
  if (fb.detail) detailItem.value = fb.detail;
  duplicateId.value = null;
}

function fmtDate(d: string) {
  return new Date(d).toLocaleDateString();
}

function statusClass(s: string) {
  const m: Record<string, string> = {
    new: "bg-slate-100 text-slate-700",
    triaging: "bg-blue-50 text-blue-700",
    planned: "bg-indigo-50 text-indigo-700",
    in_progress: "bg-amber-50 text-amber-700",
    released: "bg-emerald-50 text-emerald-700",
    declined: "bg-red-50 text-red-700",
    duplicate: "bg-slate-100 text-slate-500",
  };
  return m[s] ?? "bg-slate-100 text-slate-700";
}

function priorityClass(p: string) {
  return { low: "bg-slate-100 text-slate-600", medium: "bg-blue-50 text-blue-700",
    high: "bg-amber-50 text-amber-700", critical: "bg-red-50 text-red-700" }[p] ?? "bg-slate-100";
}

function surfaceClass(s: string) {
  return { client: "bg-violet-50 text-violet-700", writer: "bg-teal-50 text-teal-700",
    staff: "bg-slate-100 text-slate-700" }[s] ?? "bg-slate-100";
}
</script>

<style scoped>
.slide-enter-active, .slide-leave-active { transition: transform 0.25s ease; }
.slide-enter-from, .slide-leave-to { transform: translateX(100%); }
</style>
