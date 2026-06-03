<script setup lang="ts">
import { computed, onMounted, ref, reactive } from "vue";
import {
  CheckCircle, XCircle, Eye, Clock, RefreshCw,
  FileText, User, Globe, GraduationCap, Briefcase,
  ChevronRight, Download, AlertTriangle,
} from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useWriterApplicationsStore } from "@/stores/writerApplications";
import { writerVettingApi, type ApplicationQuizStatusResponse } from "@/api/writerVetting";

const apps = useWriterApplicationsStore();
type StatusPillTone = "neutral" | "success" | "warning" | "danger";
type StatusFilter = "all" | "pending" | "under_review" | "approved" | "rejected" | "withdrawn";

const STATUS_FILTERS: StatusFilter[] = ["all", "pending", "under_review", "approved", "rejected", "withdrawn"];

onMounted(() => apps.load());

// ── Status helpers ─────────────────────────────────────────────────────────
const STATUS_TONE: Record<string, StatusPillTone> = {
  pending: "warning",
  under_review: "neutral",
  approved: "success",
  rejected: "danger",
  withdrawn: "neutral",
};

function statusLabel(s: string) {
  return {
    pending: "Pending",
    under_review: "Under Review",
    approved: "Approved",
    rejected: "Rejected",
    withdrawn: "Withdrawn",
  }[s] ?? s;
}

function dateLabel(v?: string | null) {
  if (!v) return "—";
  return new Intl.DateTimeFormat("en", {
    month: "short", day: "numeric", year: "numeric",
  }).format(new Date(v));
}

function countForStatus(status: StatusFilter) {
  return apps.counts[status as keyof typeof apps.counts] ?? apps.counts.all;
}

// ── Detail panel ────────────────────────────────────────────────────────────
const panelOpen = ref(false);
const quizStatus = ref<ApplicationQuizStatusResponse | null>(null);

async function openDetail(id: number) {
  await apps.select(id);
  panelOpen.value = true;
  quizStatus.value = null;
  // Fetch quiz status for this applicant
  const email = apps.selectedApplication?.email;
  if (email) {
    try {
      const { data } = await writerVettingApi.applicationQuizStatus(email);
      quizStatus.value = data;
    } catch { /* non-fatal */ }
  }
}

function closePanel() {
  panelOpen.value = false;
  apps.clearSelection();
}

// ── Approve modal ───────────────────────────────────────────────────────────
const approveModal = ref(false);
const approveForm = reactive({ require_review: true });

async function submitApprove() {
  const id = apps.selectedApplication?.id;
  if (!id) return;
  await apps.approve(id, { require_review: approveForm.require_review });
  approveModal.value = false;
}

// ── Reject modal ────────────────────────────────────────────────────────────
const rejectModal = ref(false);
const rejectForm = reactive({ rejection_reason: "", admin_notes: "" });

async function submitReject() {
  const id = apps.selectedApplication?.id;
  if (!id) return;
  if (rejectForm.rejection_reason.trim().length < 10) return;
  await apps.reject(id, {
    rejection_reason: rejectForm.rejection_reason,
    admin_notes: rejectForm.admin_notes,
  });
  rejectModal.value = false;
  rejectForm.rejection_reason = "";
  rejectForm.admin_notes = "";
}

const selected = computed(() => apps.selectedApplication);
const canReview = computed(() => selected.value?.status === "pending");
const quizGatePassed = computed(() =>
  !quizStatus.value?.has_required_quizzes || quizStatus.value?.all_required_passed,
);
const canApprove = computed(
  () => (selected.value?.status === "pending" || selected.value?.status === "under_review")
    && quizGatePassed.value,
);
const canReject = computed(
  () => selected.value?.status === "pending" || selected.value?.status === "under_review",
);
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white border-b border-gray-200 px-6 py-5">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-xl font-semibold text-gray-900">Writer Applications</h1>
          <p class="text-sm text-gray-500 mt-0.5">Review and process writer applications</p>
        </div>
        <button
          class="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
          @click="apps.load()"
        >
          <RefreshCw class="w-4 h-4" />
          Refresh
        </button>
      </div>

      <!-- Count chips -->
      <div class="flex gap-2 mt-4 flex-wrap">
        <button
          v-for="s in STATUS_FILTERS"
          :key="s"
          class="px-3 py-1 text-xs font-medium rounded-full border transition-colors"
          :class="apps.statusFilter === s
            ? 'bg-indigo-600 text-white border-indigo-600'
            : 'bg-white text-gray-600 border-gray-300 hover:border-gray-400'"
          @click="apps.statusFilter = s"
        >
          {{ statusLabel(s === 'all' ? 'all' : s) }}
          <span class="ml-1 opacity-75">({{ countForStatus(s) }})</span>
        </button>
      </div>
    </div>

    <!-- Notice -->
    <div
      v-if="apps.notice"
      class="mx-6 mt-4 px-4 py-3 rounded-lg text-sm font-medium"
      :class="apps.notice.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'"
    >
      {{ apps.notice.message }}
    </div>

    <div class="flex h-[calc(100vh-185px)]">
      <!-- List -->
      <div class="flex-1 overflow-y-auto">
        <!-- Search -->
        <div class="px-6 py-3 border-b border-gray-100">
          <input
            v-model="apps.search"
            type="text"
            placeholder="Search by name, email, or country…"
            class="w-full max-w-sm px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <!-- Loading -->
        <div v-if="apps.loading" class="flex justify-center items-center py-16">
          <RefreshCw class="w-6 h-6 text-gray-400 animate-spin" />
        </div>

        <!-- Empty -->
        <div v-else-if="apps.filtered.length === 0" class="flex flex-col items-center py-16 text-gray-400">
          <FileText class="w-10 h-10 mb-3" />
          <p class="text-sm">No applications found.</p>
        </div>

        <!-- Table -->
        <table v-else class="w-full text-sm">
          <thead class="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide sticky top-0">
            <tr>
              <th class="px-6 py-3 text-left font-medium">Applicant</th>
              <th class="px-6 py-3 text-left font-medium">Country</th>
              <th class="px-6 py-3 text-left font-medium">Experience</th>
              <th class="px-6 py-3 text-left font-medium">Submitted</th>
              <th class="px-6 py-3 text-left font-medium">Status</th>
              <th class="px-6 py-3"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr
              v-for="app in apps.filtered"
              :key="app.id"
              class="bg-white hover:bg-gray-50 cursor-pointer transition-colors"
              :class="{ 'bg-indigo-50': selected?.id === app.id }"
              @click="openDetail(app.id)"
            >
              <td class="px-6 py-4">
                <div class="font-medium text-gray-900">{{ app.full_name }}</div>
                <div class="text-xs text-gray-500">{{ app.email }}</div>
              </td>
              <td class="px-6 py-4 text-gray-600">{{ app.country || "—" }}</td>
              <td class="px-6 py-4 text-gray-600">{{ app.years_of_experience }} yr{{ app.years_of_experience === 1 ? "" : "s" }}</td>
              <td class="px-6 py-4 text-gray-500">{{ dateLabel(app.submitted_at) }}</td>
              <td class="px-6 py-4">
                <StatusPill :status="app.status" :tone="STATUS_TONE[app.status]" :label="statusLabel(app.status)" />
              </td>
              <td class="px-6 py-4 text-right">
                <ChevronRight class="w-4 h-4 text-gray-400 ml-auto" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Detail panel -->
      <transition name="panel">
        <div
          v-if="panelOpen && selected"
          class="w-96 border-l border-gray-200 bg-white overflow-y-auto flex-shrink-0"
        >
          <!-- Panel header -->
          <div class="px-5 py-4 border-b border-gray-100 flex items-start justify-between">
            <div>
              <div class="flex items-center gap-2">
                <h2 class="font-semibold text-gray-900">{{ selected.full_name }}</h2>
                <StatusPill :status="selected.status" :tone="STATUS_TONE[selected.status]" :label="statusLabel(selected.status)" />
              </div>
              <p class="text-xs text-gray-500 mt-0.5">{{ selected.email }}</p>
            </div>
            <button class="text-gray-400 hover:text-gray-600 p-1" @click="closePanel">
              <XCircle class="w-5 h-5" />
            </button>
          </div>

          <!-- Actions -->
          <div v-if="canReview || canApprove || canReject" class="px-5 py-3 border-b border-gray-100 flex gap-2 flex-wrap">
            <button
              v-if="canReview"
              :disabled="apps.actionLoading"
              class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-blue-700 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 disabled:opacity-50"
              @click="apps.markUnderReview(selected!.id)"
            >
              <Eye class="w-3.5 h-3.5" /> Mark reviewing
            </button>
            <button
              v-if="canApprove"
              :disabled="apps.actionLoading"
              class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-green-700 bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 disabled:opacity-50"
              @click="approveModal = true"
            >
              <CheckCircle class="w-3.5 h-3.5" /> Approve
            </button>
            <button
              v-if="canReject"
              :disabled="apps.actionLoading"
              class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-red-700 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 disabled:opacity-50"
              @click="rejectModal = true"
            >
              <XCircle class="w-3.5 h-3.5" /> Reject
            </button>
          </div>

          <!-- Details -->
          <div class="px-5 py-4 space-y-5">
            <!-- Contact -->
            <div>
              <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Contact</h3>
              <div class="space-y-1.5 text-sm">
                <div class="flex items-center gap-2 text-gray-600">
                  <Globe class="w-4 h-4 text-gray-400 flex-shrink-0" />
                  {{ selected.country || "—" }}
                </div>
                <div class="flex items-center gap-2 text-gray-600">
                  <User class="w-4 h-4 text-gray-400 flex-shrink-0" />
                  {{ selected.phone_number || "—" }}
                </div>
              </div>
            </div>

            <!-- Qualifications -->
            <div>
              <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Qualifications</h3>
              <div class="space-y-1.5 text-sm">
                <div class="flex items-center gap-2 text-gray-600">
                  <GraduationCap class="w-4 h-4 text-gray-400 flex-shrink-0" />
                  {{ selected.education_level || "—" }}
                </div>
                <div class="flex items-center gap-2 text-gray-600">
                  <Briefcase class="w-4 h-4 text-gray-400 flex-shrink-0" />
                  {{ selected.years_of_experience }} years experience
                </div>
                <div v-if="selected.subjects?.length" class="flex flex-wrap gap-1 mt-1">
                  <span
                    v-for="s in selected.subjects"
                    :key="s"
                    class="px-2 py-0.5 text-xs bg-indigo-50 text-indigo-700 rounded-full"
                  >{{ s }}</span>
                </div>
              </div>
            </div>

            <!-- Application text -->
            <div v-if="selected.application_text">
              <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Cover Letter</h3>
              <p class="text-sm text-gray-700 leading-relaxed whitespace-pre-line bg-gray-50 rounded-lg p-3">{{ selected.application_text }}</p>
            </div>

            <!-- Files -->
            <div v-if="selected.resume || selected.sample_work">
              <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Files</h3>
              <div class="space-y-1.5">
                <a
                  v-if="selected.resume"
                  :href="selected.resume"
                  target="_blank"
                  class="flex items-center gap-2 text-sm text-indigo-600 hover:text-indigo-800"
                >
                  <Download class="w-4 h-4" /> Resume / CV
                </a>
                <a
                  v-if="selected.sample_work"
                  :href="selected.sample_work"
                  target="_blank"
                  class="flex items-center gap-2 text-sm text-indigo-600 hover:text-indigo-800"
                >
                  <Download class="w-4 h-4" /> Sample Work
                </a>
              </div>
            </div>

            <!-- Review info -->
            <div v-if="selected.reviewed_at">
              <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Review</h3>
              <div class="text-sm text-gray-600 space-y-1">
                <p>Reviewed by: {{ selected.reviewed_by_name || "—" }}</p>
                <p>Date: {{ dateLabel(selected.reviewed_at) }}</p>
                <p v-if="selected.rejection_reason" class="text-red-600">
                  Reason: {{ selected.rejection_reason }}
                </p>
                <p v-if="selected.admin_notes" class="text-gray-500 italic text-xs">
                  Notes: {{ selected.admin_notes }}
                </p>
              </div>
            </div>

            <!-- Quiz gate status -->
            <div v-if="quizStatus?.has_required_quizzes" class="space-y-1.5">
              <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Required quizzes</h3>
              <div
                v-for="q in quizStatus.required_quizzes"
                :key="q.quiz_id"
                class="flex items-center justify-between rounded-lg px-3 py-2 text-sm"
                :class="q.passed === true ? 'bg-green-50 border border-green-200' : q.passed === false ? 'bg-red-50 border border-red-200' : 'bg-gray-50 border border-gray-200'"
              >
                <span class="font-medium text-gray-700 truncate">{{ q.quiz_title }}</span>
                <span class="flex items-center gap-1 text-xs font-semibold ml-2 shrink-0"
                  :class="q.passed === true ? 'text-green-700' : q.passed === false ? 'text-red-700' : 'text-gray-500'"
                >
                  <CheckCircle v-if="q.passed" class="w-3.5 h-3.5" />
                  <XCircle v-else-if="q.passed === false" class="w-3.5 h-3.5" />
                  <Clock v-else class="w-3.5 h-3.5" />
                  {{ q.passed === true ? `Passed (${q.attempt?.score}%)` : q.passed === false ? `Failed (${q.attempt?.score}%)` : 'Not taken' }}
                </span>
              </div>
              <div v-if="!quizGatePassed" class="flex items-center gap-1.5 rounded-lg bg-amber-50 border border-amber-200 px-3 py-2 text-xs text-amber-800">
                <AlertTriangle class="w-3.5 h-3.5 shrink-0" />
                Approve is locked until all required quizzes are passed.
              </div>
            </div>

            <!-- Timestamps -->
            <div class="pt-2 border-t border-gray-100 text-xs text-gray-400 space-y-0.5">
              <p>Submitted: {{ dateLabel(selected.submitted_at) }}</p>
              <p>Last updated: {{ dateLabel(selected.updated_at) }}</p>
            </div>
          </div>
        </div>
      </transition>
    </div>

    <!-- Approve modal -->
    <div v-if="approveModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-sm mx-4 p-6">
        <h3 class="text-base font-semibold text-gray-900 mb-4">Approve Application</h3>
        <div class="space-y-3">
          <label class="flex items-start gap-3 cursor-pointer">
            <input
              v-model="approveForm.require_review"
              type="checkbox"
              class="mt-0.5 rounded border-gray-300 text-indigo-600"
            />
            <div>
              <p class="text-sm font-medium text-gray-700">Require document review</p>
              <p class="text-xs text-gray-500">Writer's account stays "under review" until manually activated.</p>
            </div>
          </label>
        </div>
        <div class="mt-5 flex gap-2 justify-end">
          <button
            class="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
            @click="approveModal = false"
          >Cancel</button>
          <button
            :disabled="apps.actionLoading"
            class="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50"
            @click="submitApprove"
          >
            <RefreshCw v-if="apps.actionLoading" class="w-4 h-4 animate-spin inline mr-1" />
            Approve
          </button>
        </div>
      </div>
    </div>

    <!-- Reject modal -->
    <div v-if="rejectModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-sm mx-4 p-6">
        <h3 class="text-base font-semibold text-gray-900 mb-4">Reject Application</h3>
        <div class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Reason <span class="text-red-500">*</span></label>
            <textarea
              v-model="rejectForm.rejection_reason"
              rows="3"
              placeholder="Minimum 10 characters…"
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 resize-none"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Admin notes <span class="text-gray-400">(optional)</span></label>
            <textarea
              v-model="rejectForm.admin_notes"
              rows="2"
              placeholder="Internal notes…"
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 resize-none"
            />
          </div>
        </div>
        <div class="mt-5 flex gap-2 justify-end">
          <button
            class="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
            @click="rejectModal = false"
          >Cancel</button>
          <button
            :disabled="apps.actionLoading || rejectForm.rejection_reason.trim().length < 10"
            class="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50"
            @click="submitReject"
          >
            <RefreshCw v-if="apps.actionLoading" class="w-4 h-4 animate-spin inline mr-1" />
            Reject
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.panel-enter-active,
.panel-leave-active {
  transition: transform 0.2s ease, opacity 0.2s ease;
}
.panel-enter-from,
.panel-leave-to {
  transform: translateX(1rem);
  opacity: 0;
}
</style>
