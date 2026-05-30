<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { Check, Upload } from "@lucide/vue";
import { useClassesStore } from "@/stores/classes";
import type { ClassTaskStatus } from "@/types/classes";

const route = useRoute();
const store = useClassesStore();

onMounted(() => store.loadDetail(route.params.id as string));

const taskStatusLabel: Record<ClassTaskStatus, string> = {
  pending: "Pending",
  assigned: "Assigned",
  in_progress: "In Progress",
  submitted: "Submitted",
  revision_requested: "Revision Needed",
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

const submittingTaskId = ref<number | null>(null);
const submissionNotes = ref("");
const submissionFileUrl = ref("");

function canSubmit(status: ClassTaskStatus) {
  return status === "in_progress" || status === "assigned" || status === "revision_requested";
}

function startSubmit(taskId: number) {
  submittingTaskId.value = taskId;
  submissionNotes.value = "";
  submissionFileUrl.value = "";
}

async function confirmSubmit(taskId: number) {
  if (!store.detail) return;
  await store.submitTask(store.detail.id, taskId, {
    submission_notes: submissionNotes.value,
    ...(submissionFileUrl.value ? { submission_file_url: submissionFileUrl.value } : {}),
  });
  submittingTaskId.value = null;
}
</script>

<template>
  <div class="min-h-full bg-slate-50 p-6">
    <div class="mx-auto max-w-3xl space-y-4">

      <div v-if="store.isLoadingDetail" class="py-20 text-center text-graphite animate-pulse">Loading class…</div>

      <template v-else-if="store.detail">
        <!-- Header -->
        <div class="rounded-lg border border-slate-200 bg-white p-6">
          <p class="text-xs font-mono text-graphite">{{ store.detail.reference }}</p>
          <h1 class="mt-1 text-xl font-bold text-ink">{{ store.detail.title }}</h1>
          <p class="text-sm text-graphite">{{ store.detail.subject }} · {{ store.detail.academic_level }}</p>
          <div class="mt-3 text-xs text-graphite">
            {{ store.detail.start_date }} – {{ store.detail.end_date }}
          </div>
        </div>

        <!-- Tasks -->
        <h2 class="text-xs font-semibold uppercase tracking-wide text-graphite">Your Tasks</h2>

        <div v-if="!store.detail.tasks.length" class="py-12 text-center text-graphite rounded-lg border border-slate-200 bg-white">
          No tasks assigned yet.
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="task in store.detail.tasks"
            :key="task.id"
            class="rounded-lg border border-slate-200 bg-white p-5"
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

            <!-- Revision notes -->
            <div v-if="task.status === 'revision_requested' && task.submission_notes" class="mt-3 rounded-lg border border-rose-200 bg-rose-50 px-4 py-2 text-sm text-rose-700">
              <p class="font-medium">Revision needed:</p>
              <p>{{ task.submission_notes }}</p>
            </div>

            <!-- Grade feedback -->
            <div v-if="task.grade" class="mt-3 rounded-lg bg-emerald-50 px-4 py-2 text-sm">
              <span class="font-semibold text-emerald-700">Grade: {{ task.grade }}</span>
              <span v-if="task.grade_feedback" class="ml-2 text-emerald-600">— {{ task.grade_feedback }}</span>
            </div>

            <!-- Submit inline form -->
            <div v-if="submittingTaskId === task.id" class="mt-4 space-y-2">
              <textarea
                v-model="submissionNotes"
                rows="3"
                placeholder="Notes for the client (optional)…"
                class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring resize-none"
              />
              <div>
                <label class="text-xs font-medium text-graphite">Submission file URL (optional)</label>
                <input
                  v-model="submissionFileUrl"
                  type="url"
                  placeholder="https://drive.google.com/…"
                  class="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring"
                />
                <p class="mt-0.5 text-xs text-graphite">Paste a Google Drive, Dropbox, or OneDrive share link.</p>
              </div>
              <div class="flex gap-2">
                <button
                  class="flex items-center gap-1.5 rounded-lg bg-berry px-4 py-1.5 text-sm font-medium text-white hover:bg-berry/90 disabled:opacity-60"
                  :disabled="store.isSaving"
                  @click="confirmSubmit(task.id)"
                >
                  <Check class="size-4" /> Submit Task
                </button>
                <button class="rounded-lg border border-slate-200 px-4 py-1.5 text-sm text-graphite hover:text-ink" @click="submittingTaskId = null">
                  Cancel
                </button>
              </div>
            </div>

            <!-- Submit button -->
            <div v-else-if="canSubmit(task.status)" class="mt-4">
              <button
                class="flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-sm text-graphite hover:text-ink transition-colors"
                @click="startSubmit(task.id)"
              >
                <Upload class="size-4" />
                {{ task.status === 'revision_requested' ? 'Resubmit' : 'Submit Task' }}
              </button>
            </div>
          </div>
        </div>
      </template>

    </div>
  </div>
</template>
