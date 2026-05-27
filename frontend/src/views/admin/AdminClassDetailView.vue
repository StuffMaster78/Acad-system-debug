<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { Check, UserCheck, Clock, ExternalLink } from "@lucide/vue";
import { useClassesStore } from "@/stores/classes";
import type { ClassTaskStatus, InstallmentStatus } from "@/types/classes";

const route = useRoute();
const store = useClassesStore();

onMounted(() => store.loadDetail(route.params.id as string));

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

const installmentStatusClass: Record<InstallmentStatus, string> = {
  pending: "bg-amber-100 text-amber-700",
  paid: "bg-emerald-100 text-emerald-700",
  overdue: "bg-rose-100 text-rose-700",
  waived: "bg-slate-100 text-graphite",
};

// Grading
const gradingTaskId = ref<number | null>(null);
const gradeValue = ref("");
const gradeFeedback = ref("");

function startGrade(taskId: number) {
  gradingTaskId.value = taskId;
  gradeValue.value = "";
  gradeFeedback.value = "";
}

async function confirmGrade(taskId: number) {
  if (!store.detail) return;
  await store.gradeTask(store.detail.id, taskId, { grade: gradeValue.value, grade_feedback: gradeFeedback.value });
  gradingTaskId.value = null;
}
</script>

<template>
  <div class="min-h-full bg-slate-50 p-6">
    <div class="mx-auto max-w-4xl space-y-6">

      <div v-if="store.isLoadingDetail" class="py-20 text-center text-graphite animate-pulse">Loading…</div>

      <template v-else-if="store.detail">
        <!-- Header -->
        <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-panel">
          <div class="flex items-start justify-between gap-4">
            <div>
              <p class="text-xs font-mono text-graphite">{{ store.detail.reference }}</p>
              <h1 class="mt-1 text-xl font-bold text-ink">{{ store.detail.title }}</h1>
              <p class="text-sm text-graphite">{{ store.detail.subject }} · {{ store.detail.academic_level }}</p>
            </div>
            <div class="shrink-0 text-right">
              <p class="text-lg font-bold text-ink">${{ store.detail.total_price }}</p>
              <p class="text-xs text-graphite capitalize">{{ store.detail.payment_status }}</p>
            </div>
          </div>
          <div class="mt-4 flex flex-wrap gap-4 text-xs text-graphite">
            <span class="flex items-center gap-1">
              <Clock class="size-3.5" />
              {{ store.detail.start_date }} – {{ store.detail.end_date }}
            </span>
            <span class="flex items-center gap-1">
              <UserCheck class="size-3.5" />
              Client: {{ store.detail.client_username }}
            </span>
            <span v-if="store.detail.writer_username" class="text-emerald-700">
              Writer: {{ store.detail.writer_username }}
            </span>
            <span v-else class="text-amber-600">Unassigned</span>
          </div>
        </div>

        <!-- Tabs -->
        <div class="flex gap-1 rounded-lg border border-slate-200 bg-white p-1 shadow-panel">
          <button
            v-for="tab in [{ key: 'tasks', label: 'Tasks' }, { key: 'installments', label: 'Installments' }, { key: 'portal', label: 'Portal Access' }]"
            :key="tab.key"
            class="flex-1 rounded-md py-1.5 text-sm font-medium transition-colors"
            :class="store.activeTab === tab.key ? 'bg-berry text-white shadow-sm' : 'text-graphite hover:text-ink'"
            @click="store.activeTab = tab.key as typeof store.activeTab"
          >{{ tab.label }}</button>
        </div>

        <!-- Tasks -->
        <div v-if="store.activeTab === 'tasks'" class="space-y-3">
          <div
            v-for="task in store.detail.tasks"
            :key="task.id"
            class="rounded-xl border border-slate-200 bg-white p-5 shadow-panel"
          >
            <div class="flex items-start justify-between gap-4">
              <div class="min-w-0">
                <div class="flex items-center gap-2">
                  <span class="text-xs font-mono text-graphite">#{{ task.sequence }}</span>
                  <span class="rounded-full px-2 py-0.5 text-xs font-semibold" :class="taskStatusClass[task.status]">
                    {{ taskStatusLabel[task.status] }}
                  </span>
                </div>
                <h3 class="mt-1 font-semibold text-ink">{{ task.title }}</h3>
                <p class="text-sm text-graphite">{{ task.description }}</p>
              </div>
              <p class="shrink-0 text-xs text-graphite">Due {{ task.due_date }}</p>
            </div>

            <div v-if="task.submission_notes" class="mt-3 rounded-lg bg-slate-50 px-4 py-2 text-sm text-graphite">
              <span class="font-medium text-ink">Submission notes:</span> {{ task.submission_notes }}
            </div>

            <!-- Grade inline form -->
            <div v-if="gradingTaskId === task.id" class="mt-4 space-y-2">
              <div class="flex gap-2">
                <input v-model="gradeValue" placeholder="Grade (e.g. A, B+, 92)" class="w-36 rounded-lg border border-slate-200 px-3 py-1.5 text-sm focus-ring" />
                <input v-model="gradeFeedback" placeholder="Feedback (optional)" class="flex-1 rounded-lg border border-slate-200 px-3 py-1.5 text-sm focus-ring" />
              </div>
              <div class="flex gap-2">
                <button
                  class="flex items-center gap-1.5 rounded-lg bg-emerald-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-60"
                  :disabled="store.isSaving || !gradeValue.trim()"
                  @click="confirmGrade(task.id)"
                >
                  <Check class="size-4" /> Save Grade
                </button>
                <button class="rounded-lg border border-slate-200 px-4 py-1.5 text-sm text-graphite hover:text-ink" @click="gradingTaskId = null">
                  Cancel
                </button>
              </div>
            </div>

            <div v-else-if="task.status === 'submitted'" class="mt-4">
              <button
                class="flex items-center gap-1.5 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-sm text-emerald-700 hover:bg-emerald-100 transition-colors"
                @click="startGrade(task.id)"
              >
                <Check class="size-4" /> Grade Task
              </button>
            </div>

            <div v-if="task.grade" class="mt-3 flex items-center gap-2 text-sm">
              <span class="font-semibold text-emerald-700">Grade: {{ task.grade }}</span>
              <span v-if="task.grade_feedback" class="text-graphite">— {{ task.grade_feedback }}</span>
            </div>
          </div>
        </div>

        <!-- Installments -->
        <div v-else-if="store.activeTab === 'installments'" class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-panel">
          <table class="w-full text-sm">
            <thead class="bg-slate-50 text-xs font-semibold uppercase tracking-wide text-graphite">
              <tr>
                <th class="px-5 py-3 text-left">Payment</th>
                <th class="px-5 py-3 text-left">Due</th>
                <th class="px-5 py-3 text-right">Amount</th>
                <th class="px-5 py-3 text-center">Status</th>
                <th class="px-5 py-3 text-left">Reference</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-50">
              <tr v-for="inst in store.detail.installments" :key="inst.id">
                <td class="px-5 py-3 font-medium text-ink">{{ inst.label }}</td>
                <td class="px-5 py-3 text-graphite">{{ inst.due_date }}</td>
                <td class="px-5 py-3 text-right font-semibold text-ink">${{ inst.amount }}</td>
                <td class="px-5 py-3 text-center">
                  <span class="rounded-full px-2 py-0.5 text-xs font-semibold" :class="installmentStatusClass[inst.status]">
                    {{ inst.status }}
                  </span>
                </td>
                <td class="px-5 py-3 font-mono text-xs text-graphite">{{ inst.payment_reference ?? '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Portal Access -->
        <div v-else-if="store.activeTab === 'portal'" class="rounded-xl border border-slate-200 bg-white p-6 shadow-panel">
          <h3 class="font-semibold text-ink">Portal / LMS Access</h3>
          <div v-if="store.detail.portal_access" class="mt-4 space-y-3 text-sm">
            <div class="flex items-center gap-3">
              <span class="w-32 text-graphite">Status</span>
              <span :class="store.detail.portal_access.enabled ? 'text-emerald-700' : 'text-graphite'">
                {{ store.detail.portal_access.enabled ? 'Enabled' : 'Disabled' }}
              </span>
            </div>
            <div v-if="store.detail.portal_access.portal_url" class="flex items-center gap-3">
              <span class="w-32 text-graphite">URL</span>
              <a :href="store.detail.portal_access.portal_url" target="_blank" class="flex items-center gap-1 text-berry hover:underline">
                {{ store.detail.portal_access.portal_url }}
                <ExternalLink class="size-3" />
              </a>
            </div>
            <div v-if="store.detail.portal_access.username" class="flex items-center gap-3">
              <span class="w-32 text-graphite">Username</span>
              <span class="font-mono text-ink">{{ store.detail.portal_access.username }}</span>
            </div>
            <div v-if="store.detail.portal_access.notes" class="flex gap-3">
              <span class="w-32 shrink-0 text-graphite">Notes</span>
              <span class="text-ink">{{ store.detail.portal_access.notes }}</span>
            </div>
          </div>
          <p v-else class="mt-4 text-graphite">No portal access configured.</p>
        </div>

      </template>
    </div>
  </div>
</template>
