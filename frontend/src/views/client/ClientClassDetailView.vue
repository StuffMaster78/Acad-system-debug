<template>
  <div class="min-h-full bg-slate-50 p-6">
    <div class="mx-auto max-w-4xl space-y-4">

      <!-- Loading -->
      <div v-if="store.isLoadingDetail" class="py-24 text-center text-graphite animate-pulse">
        Loading class…
      </div>

      <template v-else-if="store.detail">
        <!-- Header -->
        <div>
          <button class="mb-3 inline-flex items-center gap-1.5 text-sm text-graphite hover:text-ink" @click="router.back()">
            <ArrowLeft class="size-3.5" /> My Classes
          </button>
          <div class="rounded-lg border border-slate-200 bg-white p-6">
            <div class="flex items-start justify-between gap-4">
              <div class="min-w-0">
                <div class="flex flex-wrap items-center gap-2">
                  <span
                    class="rounded-full px-2.5 py-0.5 text-xs font-semibold"
                    :class="statusClass[store.detail.status]"
                  >{{ statusLabel[store.detail.status] }}</span>
                  <span class="font-mono text-xs text-graphite">{{ store.detail.reference }}</span>
                </div>
                <h1 class="mt-2 text-xl font-bold text-ink">{{ store.detail.title }}</h1>
                <p class="mt-0.5 text-sm text-graphite">{{ store.detail.subject }} · {{ store.detail.academic_level }}</p>
                <div class="mt-3 flex flex-wrap items-center gap-4 text-xs text-graphite">
                  <span class="flex items-center gap-1.5">
                    <Calendar class="size-3.5" />
                    {{ fmtDate(store.detail.start_date) }} — {{ fmtDate(store.detail.end_date) }}
                  </span>
                  <span v-if="store.detail.writer_username" class="flex items-center gap-1.5 text-emerald-700">
                    <CheckCircle class="size-3.5" />
                    Expert assigned
                  </span>
                  <span v-else class="flex items-center gap-1.5 text-amber-600">
                    <Clock class="size-3.5" />
                    Awaiting expert assignment
                  </span>
                  <span v-if="store.detail.portal_access_enabled" class="flex items-center gap-1.5 text-blue-600">
                    <Globe class="size-3.5" />
                    Portal access provided
                  </span>
                </div>
              </div>
              <div class="shrink-0 text-right">
                <p class="text-2xl font-bold text-ink">${{ store.detail.total_price }}</p>
                <p class="mt-0.5 text-xs font-semibold capitalize" :class="paymentTone">{{ store.detail.payment_status }}</p>
              </div>
            </div>

            <!-- Progress bar -->
            <div class="mt-5">
              <div class="mb-1.5 flex items-center justify-between text-xs">
                <span class="text-graphite">{{ store.detail.completed_tasks }} of {{ store.detail.total_tasks }} tasks completed</span>
                <span class="font-semibold text-ink">{{ progressPct }}%</span>
              </div>
              <div class="h-2 overflow-hidden rounded-full bg-slate-100">
                <div
                  class="h-full rounded-full transition-all duration-500"
                  :class="progressPct === 100 ? 'bg-emerald-500' : 'bg-berry'"
                  :style="{ width: `${progressPct}%` }"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Summary cards -->
        <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div class="rounded-lg border border-slate-200 bg-white p-4">
            <p class="text-xs text-graphite">Total price</p>
            <p class="mt-1 text-lg font-bold text-ink">${{ store.detail.total_price }}</p>
          </div>
          <div class="rounded-lg border border-slate-200 bg-white p-4">
            <p class="text-xs text-graphite">Tasks done</p>
            <p class="mt-1 text-lg font-bold text-ink">{{ store.detail.completed_tasks }}<span class="text-sm font-normal text-graphite">/{{ store.detail.total_tasks }}</span></p>
          </div>
          <div class="rounded-lg border border-slate-200 bg-white p-4">
            <p class="text-xs text-graphite">Payment</p>
            <p class="mt-1 text-sm font-semibold capitalize" :class="paymentTone">{{ store.detail.payment_status }}</p>
          </div>
          <div class="rounded-lg border border-slate-200 bg-white p-4">
            <p class="text-xs text-graphite">Next due</p>
            <p class="mt-1 text-sm font-semibold text-ink">{{ nextDue }}</p>
          </div>
        </div>

        <!-- Tabs -->
        <div class="flex gap-1 rounded-lg border border-slate-200 bg-white p-1">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="flex-1 rounded-md py-1.5 text-sm font-medium transition-colors"
            :class="activeTab === tab.key ? 'bg-berry text-white shadow-sm' : 'text-graphite hover:text-ink'"
            @click="activeTab = tab.key"
          >{{ tab.label }}</button>
        </div>

        <!-- Tasks tab -->
        <div v-if="activeTab === 'tasks'" class="space-y-3">
          <div v-if="!store.detail.tasks.length" class="rounded-xl border border-dashed border-slate-200 bg-white py-14 text-center text-sm text-graphite">
            No tasks have been set up yet. Check back soon.
          </div>
          <div
            v-for="task in store.detail.tasks"
            :key="task.id"
            class="rounded-lg border border-slate-200 bg-white p-5"
          >
            <div class="flex items-start justify-between gap-4">
              <div class="min-w-0">
                <div class="flex items-center gap-2">
                  <span class="font-mono text-xs text-graphite">#{{ task.sequence }}</span>
                  <span class="rounded-full px-2 py-0.5 text-xs font-semibold" :class="taskStatusClass[task.status]">
                    {{ taskStatusLabel[task.status] }}
                  </span>
                </div>
                <h3 class="mt-1.5 font-semibold text-ink">{{ task.title }}</h3>
                <p class="mt-0.5 text-sm text-graphite">{{ task.description }}</p>
              </div>
              <div class="shrink-0 text-right text-xs text-graphite">
                <p>Due {{ fmtDate(task.due_date) }}</p>
                <p v-if="task.grade" class="mt-1.5 rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-bold text-emerald-700">
                  Grade: {{ task.grade }}
                </p>
              </div>
            </div>
            <!-- Submission view (already submitted) -->
            <div v-if="task.submission_notes && task.status !== 'pending' && task.status !== 'in_progress'" class="mt-3 rounded-lg bg-slate-50 px-4 py-2.5 text-sm text-graphite">
              <span class="font-medium text-ink">Your submission:</span> {{ task.submission_notes }}
            </div>
            <div v-if="task.submission_file_url && task.status !== 'pending' && task.status !== 'in_progress'" class="mt-2">
              <a
                :href="task.submission_file_url"
                target="_blank"
                rel="noreferrer"
                class="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-600 hover:underline"
              >
                <ExternalLink class="size-3" /> View submitted file
              </a>
            </div>

            <div v-if="task.grade_feedback" class="mt-3 rounded-lg bg-slate-50 px-4 py-2.5 text-sm text-graphite">
              <span class="font-medium text-ink">Feedback:</span> {{ task.grade_feedback }}
            </div>

            <!-- Submit task form (pending / in_progress tasks) -->
            <div
              v-if="task.status === 'pending' || task.status === 'in_progress'"
              class="mt-4 border-t border-slate-100 pt-4"
            >
              <template v-if="submittingTaskId !== task.id">
                <button
                  class="inline-flex items-center gap-1.5 rounded-md border border-slate-200 px-3 py-1.5 text-xs font-semibold text-ink hover:bg-slate-50"
                  @click="openSubmitForm(task.id)"
                >
                  <Send class="size-3.5" /> Submit task
                </button>
              </template>
              <template v-else>
                <p class="mb-2 text-xs font-semibold text-ink">Submit task</p>
                <textarea
                  v-model="submitNotes"
                  class="focus-ring w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                  rows="3"
                  placeholder="Describe what you've completed or add any notes for the reviewer…"
                />
                <input
                  v-model="submitFileUrl"
                  class="focus-ring mt-2 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                  type="url"
                  placeholder="Link to submitted file (Google Drive, Dropbox, etc.) — optional"
                />
                <p v-if="submitError" class="mt-2 text-xs text-berry">{{ submitError }}</p>
                <div class="mt-3 flex gap-2">
                  <button
                    class="focus-ring inline-flex items-center gap-1.5 rounded-md bg-signal px-4 py-2 text-xs font-semibold text-white disabled:opacity-60"
                    :disabled="isSubmittingTask"
                    @click="confirmSubmit(task.id)"
                  >
                    <Loader2 v-if="isSubmittingTask" class="size-3.5 animate-spin" />
                    <Send v-else class="size-3.5" />
                    Confirm submission
                  </button>
                  <button
                    class="focus-ring rounded-md border border-slate-200 px-3 py-2 text-xs text-graphite hover:bg-slate-50"
                    @click="cancelSubmit"
                  >
                    Cancel
                  </button>
                </div>
              </template>
            </div>
          </div>
        </div>

        <!-- Installments tab -->
        <div v-else-if="activeTab === 'installments'" class="rounded-lg border border-slate-200 bg-white overflow-hidden">
          <div v-if="!store.detail.installments.length" class="py-14 text-center text-sm text-graphite">
            No payment schedule set yet.
          </div>
          <div class="overflow-x-auto">
          <table class="min-w-full text-sm">
            <thead class="bg-slate-50 text-xs font-semibold uppercase tracking-wide text-graphite">
              <tr>
                <th class="px-3 py-2 text-left">Payment</th>
                <th class="px-3 py-2 text-left">Due date</th>
                <th class="px-3 py-2 text-right">Amount</th>
                <th class="px-3 py-2 text-center">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-50">
              <tr v-for="inst in store.detail.installments" :key="inst.id">
                <td class="px-3 py-2.5 font-medium text-ink">{{ inst.label }}</td>
                <td class="px-3 py-2.5 text-graphite">{{ fmtDate(inst.due_date) }}</td>
                <td class="px-3 py-2.5 text-right font-bold text-ink">${{ inst.amount }}</td>
                <td class="px-3 py-2.5 text-center">
                  <span class="rounded-full px-2.5 py-0.5 text-xs font-semibold" :class="installmentStatusClass[inst.status]">
                    {{ installmentStatusLabel[inst.status] }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
          </div>
          <div class="flex items-center gap-2 border-t border-slate-100 px-5 py-3 text-xs text-graphite">
            <CreditCard class="size-3.5 shrink-0" />
            Contact support to make a payment or dispute an installment charge.
          </div>
        </div>

        <!-- Portal access tab -->
        <div v-else-if="activeTab === 'portal'" class="rounded-lg border border-slate-200 bg-white p-6">
          <div v-if="store.detail.portal_access?.enabled" class="space-y-4">
            <div class="flex items-center gap-2">
              <Globe class="size-4 text-blue-600" />
              <h3 class="font-semibold text-ink">LMS / Portal Access</h3>
              <span class="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-semibold text-emerald-700">Active</span>
            </div>
            <div class="space-y-3 rounded-lg bg-slate-50 px-5 py-4 text-sm">
              <div v-if="store.detail.portal_access.portal_url" class="flex items-start gap-3">
                <span class="w-32 shrink-0 text-graphite">Portal URL</span>
                <a
                  :href="store.detail.portal_access.portal_url"
                  target="_blank"
                  rel="noreferrer"
                  class="flex items-center gap-1 break-all text-berry hover:underline"
                >
                  {{ store.detail.portal_access.portal_url }}
                  <ExternalLink class="size-3 shrink-0" />
                </a>
              </div>
              <div v-if="store.detail.portal_access.username" class="flex items-center gap-3">
                <span class="w-32 shrink-0 text-graphite">Username</span>
                <span class="font-mono text-ink">{{ store.detail.portal_access.username }}</span>
              </div>
              <div v-if="store.detail.portal_access.password_hint" class="flex items-center gap-3">
                <span class="w-32 shrink-0 text-graphite">Password hint</span>
                <span class="text-ink">{{ store.detail.portal_access.password_hint }}</span>
              </div>
              <div v-if="store.detail.portal_access.notes" class="flex items-start gap-3">
                <span class="w-32 shrink-0 text-graphite">Notes</span>
                <span class="text-ink">{{ store.detail.portal_access.notes }}</span>
              </div>
              <div v-if="store.detail.portal_access.last_accessed_at" class="flex items-center gap-3 border-t border-slate-200 pt-3">
                <span class="w-32 shrink-0 text-graphite">Last accessed</span>
                <span class="text-graphite">{{ fmtDateTime(store.detail.portal_access.last_accessed_at) }}</span>
              </div>
            </div>
          </div>
          <div v-else class="py-12 text-center">
            <Globe class="mx-auto mb-3 size-8 text-slate-300" />
            <p class="text-sm text-graphite">No portal access has been configured for this class.</p>
            <p class="mt-1 text-xs text-graphite">If your course uses an LMS, please contact support.</p>
          </div>
        </div>

      </template>

      <!-- Error state -->
      <div v-else class="py-20 text-center text-sm text-graphite">
        <p>Class not found or failed to load.</p>
        <button class="mt-3 text-berry hover:underline" @click="router.back()">Go back</button>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ArrowLeft, Calendar, CheckCircle, Clock, CreditCard, ExternalLink, Globe, Loader2, Send } from "@lucide/vue";
import { classesApi } from "@/api/classes";
import { useClassesStore } from "@/stores/classes";
import type { ClassStatus, ClassTaskStatus, InstallmentStatus } from "@/types/classes";

const route = useRoute();
const router = useRouter();
const store = useClassesStore();

onMounted(() => store.loadDetail(route.params.id as string));

const tabs = [
  { key: "tasks", label: "Tasks" },
  { key: "installments", label: "Installments" },
  { key: "portal", label: "Portal Access" },
];
const activeTab = ref("tasks");

const statusLabel: Record<ClassStatus, string> = {
  pending: "Pending Review",
  active: "Active",
  paused: "Paused",
  completed: "Completed",
  cancelled: "Cancelled",
};

const statusClass: Record<ClassStatus, string> = {
  pending: "bg-amber-100 text-amber-700",
  active: "bg-emerald-100 text-emerald-700",
  paused: "bg-slate-100 text-graphite",
  completed: "bg-blue-100 text-blue-700",
  cancelled: "bg-rose-100 text-rose-700",
};

const taskStatusLabel: Record<ClassTaskStatus, string> = {
  pending: "Pending",
  assigned: "Assigned",
  in_progress: "In Progress",
  submitted: "Submitted",
  revision_requested: "Revision",
  approved: "Approved",
  cancelled: "Cancelled",
};

const taskStatusClass: Record<ClassTaskStatus, string> = {
  pending: "bg-slate-100 text-graphite",
  assigned: "bg-blue-100 text-blue-700",
  in_progress: "bg-amber-100 text-amber-700",
  submitted: "bg-purple-100 text-purple-700",
  revision_requested: "bg-rose-100 text-rose-700",
  approved: "bg-emerald-100 text-emerald-700",
  cancelled: "bg-slate-100 text-slate-400",
};

const installmentStatusLabel: Record<InstallmentStatus, string> = {
  pending: "Pending",
  paid: "Paid",
  overdue: "Overdue",
  waived: "Waived",
};

const installmentStatusClass: Record<InstallmentStatus, string> = {
  pending: "bg-amber-100 text-amber-700",
  paid: "bg-emerald-100 text-emerald-700",
  overdue: "bg-rose-100 text-rose-700",
  waived: "bg-slate-100 text-graphite",
};

const progressPct = computed(() => {
  const d = store.detail;
  if (!d || !d.total_tasks) return 0;
  return Math.round((d.completed_tasks / d.total_tasks) * 100);
});

const paymentTone = computed(() => {
  const s = store.detail?.payment_status;
  if (s === "paid") return "text-emerald-700";
  if (s === "overdue") return "text-rose-600";
  if (s === "partial") return "text-amber-600";
  return "text-graphite";
});

const nextDue = computed(() => {
  const pending = (store.detail?.installments ?? []).find((i) => i.status === "pending" || i.status === "overdue");
  if (!pending) return "All paid";
  return fmtDate(pending.due_date);
});

function fmtDate(v: string): string {
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", year: "numeric" }).format(new Date(v));
}

function fmtDateTime(v: string): string {
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }).format(new Date(v));
}

// ── Task submission ──────────────────────────────────────────────────────────
const submittingTaskId = ref<number | null>(null);
const submitNotes = ref("");
const submitFileUrl = ref("");
const isSubmittingTask = ref(false);
const submitError = ref("");

function openSubmitForm(taskId: number) {
  submittingTaskId.value = taskId;
  submitNotes.value = "";
  submitFileUrl.value = "";
  submitError.value = "";
}

function cancelSubmit() {
  submittingTaskId.value = null;
}

async function confirmSubmit(taskId: number) {
  if (!store.detail) return;
  isSubmittingTask.value = true;
  submitError.value = "";
  try {
    const { data: updated } = await classesApi.tasks.submit(store.detail.id, taskId, {
      submission_notes: submitNotes.value || undefined,
      submission_file_url: submitFileUrl.value || undefined,
    });
    // Patch the task in the store
    const idx = store.detail.tasks.findIndex((t) => t.id === taskId);
    if (idx !== -1) store.detail.tasks[idx] = updated;
    submittingTaskId.value = null;
  } catch {
    submitError.value = "Submission failed. Please try again.";
  } finally {
    isSubmittingTask.value = false;
  }
}
</script>
