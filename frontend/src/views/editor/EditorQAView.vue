<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import {
  CheckCircle2,
  ClipboardCheck,
  ExternalLink,
  FileSearch,
  Loader2,
  RefreshCw,
  RotateCcw,
  Send,
  ShieldAlert,
  UserPlus,
  XCircle,
} from "@lucide/vue";
const router = useRouter();
import StatusPill from "@/components/ui/StatusPill.vue";
import { useEditorWorkspaceStore } from "@/stores/editorWorkspace";
import type { EditorTask, SubmitEditorReviewPayload } from "@/types/editor";

const workspace = useEditorWorkspaceStore();

const selectedTaskId = ref<string>("");
const reviewForm = reactive({
  quality_score: "9.0",
  issues_found: "",
  corrections_made: "",
  recommendations: "",
  is_approved: true,
  requires_revision: false,
  revision_notes: "",
  final_notes: "",
  rejection_reason: "",
});

const selectedTask = computed(() =>
  workspace.tasks.find((task) => String(task.id) === selectedTaskId.value) ?? workspace.activeTasks[0],
);

function statusTone(status: string | undefined) {
  if (status === "completed") return "success";
  if (status === "rejected") return "danger";
  if (status === "in_review") return "warning";
  return "neutral";
}

function dateLabel(value: string | null | undefined): string {
  if (!value) return "No deadline";
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function relativeDeadline(task: EditorTask): string {
  if (!task.order_deadline) return "No deadline set";
  const diff = new Date(task.order_deadline).getTime() - Date.now();
  const hours = Math.round(diff / (1000 * 60 * 60));
  if (hours < 0) return `${Math.abs(hours)}h overdue`;
  if (hours < 24) return `${hours}h left`;
  return `${Math.round(hours / 24)}d left`;
}

function taskTitle(task: EditorTask): string {
  return task.order_topic || `Order #${task.order_id ?? task.order ?? task.id}`;
}

async function submitReview() {
  const task = selectedTask.value;
  if (!task) return;

  const payload: SubmitEditorReviewPayload = {
    task_id: task.id,
    quality_score: reviewForm.quality_score,
    issues_found: reviewForm.issues_found,
    corrections_made: reviewForm.corrections_made,
    recommendations: reviewForm.recommendations,
    is_approved: reviewForm.is_approved,
    requires_revision: reviewForm.requires_revision,
    revision_notes: reviewForm.revision_notes,
    edited_files: [],
  };

  await workspace.submitReview(payload);
}

async function completeSelectedTask() {
  const task = selectedTask.value;
  if (!task) return;
  await workspace.mutateTask("complete", task.id, reviewForm.final_notes);
}

async function rejectSelectedTask() {
  const task = selectedTask.value;
  if (!task || !reviewForm.rejection_reason) return;
  await workspace.mutateTask("reject", task.id, reviewForm.rejection_reason);
}

onMounted(async () => {
  if (!workspace.tasks.length) await workspace.hydrate();
  selectedTaskId.value = String(workspace.activeTasks[0]?.id ?? workspace.tasks[0]?.id ?? "");
});
</script>

<template>
  <div class="space-y-4">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Editor workspace</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">QA queue</h1>
        <p class="mt-2 max-w-2xl text-sm text-graphite">
          Assigned reviews, claimable tasks, and review decision controls.
        </p>
      </div>
      <button
        class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold disabled:opacity-60"
        type="button"
        :disabled="workspace.isLoading"
        @click="workspace.refreshTasks()"
      >
        <RefreshCw class="h-4 w-4" :class="workspace.isLoading ? 'animate-spin' : ''" />
        Refresh
      </button>
    </section>

    <div v-if="workspace.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ workspace.error }}
    </div>
    <div v-if="workspace.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
      {{ workspace.notice }}
    </div>

    <section class="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 class="text-lg font-semibold text-ink">Assigned reviews</h2>
            <p class="mt-1 text-sm text-graphite">Select a task to open the review decision panel.</p>
          </div>
          <button
            class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-slate-300 px-3 py-2 text-sm font-semibold text-ink disabled:opacity-60"
            type="button"
            :disabled="workspace.isLoading"
            @click="workspace.hydrate()"
          >
            <RotateCcw class="h-4 w-4" />
            Reload all
          </button>
        </div>

        <div class="mt-5 overflow-hidden rounded-md border border-slate-200">
          <div class="grid grid-cols-[1.2fr_auto_auto] gap-3 bg-slate-50 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
            <span>Order</span>
            <span>Status</span>
            <span class="text-right">Deadline</span>
          </div>
          <div v-if="workspace.isLoading" class="flex items-center gap-2 px-4 py-6 text-sm text-graphite">
            <Loader2 class="h-4 w-4 animate-spin" />
            Loading QA queue...
          </div>
          <div v-else-if="!workspace.tasks.length" class="px-4 py-6 text-sm text-graphite">
            No assigned reviews. Claim work from the pool below.
          </div>
          <button
            v-for="task in workspace.tasks"
            v-else
            :key="String(task.id)"
            class="grid w-full grid-cols-[1.2fr_auto_auto] gap-3 border-t border-slate-100 px-4 py-3 text-left text-sm transition hover:bg-slate-50"
            :class="selectedTask?.id === task.id ? 'bg-slate-50 ring-1 ring-inset ring-signal/20' : 'bg-white'"
            type="button"
            @click="selectedTaskId = String(task.id)"
          >
            <span class="min-w-0">
              <span class="block truncate font-semibold text-ink">{{ taskTitle(task) }}</span>
              <span class="mt-1 block truncate text-xs text-graphite">
                Order #{{ task.order_id ?? task.order ?? "unknown" }} · {{ task.assignment_type ?? "assigned" }}
              </span>
            </span>
            <span>
              <StatusPill :label="String(task.review_status ?? 'pending')" :tone="statusTone(task.review_status)" />
            </span>
            <span class="text-right text-xs font-semibold text-graphite">
              {{ relativeDeadline(task) }}
            </span>
          </button>
        </div>
      </div>

      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <div class="flex items-center justify-between gap-3">
          <div>
            <h2 class="text-lg font-semibold text-ink">Review decision</h2>
            <p class="mt-1 text-sm text-graphite">
              {{ selectedTask ? taskTitle(selectedTask) : "Select a task to review." }}
            </p>
            <button
              v-if="selectedTask"
              class="mt-1 inline-flex items-center gap-1 text-xs font-semibold text-signal hover:underline"
              @click="router.push(`/editor/orders/${selectedTask.order_id ?? selectedTask.order ?? selectedTask.id}`)"
            >
              <ExternalLink class="h-3 w-3" /> Open full order
            </button>
          </div>
          <ClipboardCheck class="h-5 w-5 text-signal" />
        </div>

        <div v-if="selectedTask" class="mt-5 space-y-4">
          <div class="grid gap-3 sm:grid-cols-2">
            <button
              class="focus-ring inline-flex items-center justify-center gap-2 rounded-md bg-ink px-3 py-2.5 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
              type="button"
              :disabled="workspace.isMutating || selectedTask.review_status === 'in_review'"
              @click="workspace.mutateTask('start', selectedTask.id)"
            >
              <FileSearch class="h-4 w-4" />
              Start review
            </button>
            <button
              class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-slate-300 px-3 py-2.5 text-sm font-semibold text-ink disabled:cursor-not-allowed disabled:opacity-60"
              type="button"
              :disabled="workspace.isMutating"
              @click="workspace.mutateTask('unclaim', selectedTask.id)"
            >
              <XCircle class="h-4 w-4" />
              Unclaim
            </button>
          </div>

          <label class="block text-sm font-medium text-ink">
            Quality score
            <input
              v-model.trim="reviewForm.quality_score"
              class="focus-ring mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              inputmode="decimal"
              placeholder="0.00 to 10.00"
            />
          </label>

          <div class="grid gap-3 sm:grid-cols-2">
            <label class="flex items-center gap-2 text-sm font-medium text-ink">
              <input v-model="reviewForm.is_approved" class="h-4 w-4 rounded border-slate-300 text-signal" type="checkbox" />
              Approved for delivery
            </label>
            <label class="flex items-center gap-2 text-sm font-medium text-ink">
              <input v-model="reviewForm.requires_revision" class="h-4 w-4 rounded border-slate-300 text-signal" type="checkbox" />
              Requires writer revision
            </label>
          </div>

          <label class="block text-sm font-medium text-ink">
            Issues found
            <textarea
              v-model.trim="reviewForm.issues_found"
              class="focus-ring mt-2 min-h-20 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              placeholder="Clarity, formatting, citation, or content issues"
            />
          </label>

          <label class="block text-sm font-medium text-ink">
            Corrections made
            <textarea
              v-model.trim="reviewForm.corrections_made"
              class="focus-ring mt-2 min-h-20 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              placeholder="Summarize edits made before delivery"
            />
          </label>

          <label class="block text-sm font-medium text-ink">
            Recommendations
            <textarea
              v-model.trim="reviewForm.recommendations"
              class="focus-ring mt-2 min-h-20 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              placeholder="Notes for client delivery or writer coaching"
            />
          </label>

          <div class="grid gap-3 sm:grid-cols-2">
            <button
              class="focus-ring inline-flex items-center justify-center gap-2 rounded-md bg-signal px-3 py-2.5 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
              type="button"
              :disabled="workspace.isMutating"
              @click="submitReview"
            >
              <Send class="h-4 w-4" />
              Submit review
            </button>
            <button
              class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-emerald-300 px-3 py-2.5 text-sm font-semibold text-emerald-800 disabled:cursor-not-allowed disabled:opacity-60"
              type="button"
              :disabled="workspace.isMutating"
              @click="completeSelectedTask"
            >
              <CheckCircle2 class="h-4 w-4" />
              Complete task
            </button>
          </div>

          <div class="border-t border-slate-200 pt-4">
            <label class="block text-sm font-medium text-ink">
              Rejection reason
              <textarea
                v-model.trim="reviewForm.rejection_reason"
                class="focus-ring mt-2 min-h-20 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                placeholder="Reason this task cannot be reviewed"
              />
            </label>
            <button
              class="focus-ring mt-3 inline-flex w-full items-center justify-center gap-2 rounded-md border border-rose-300 px-3 py-2.5 text-sm font-semibold text-rose-800 disabled:cursor-not-allowed disabled:opacity-60"
              type="button"
              :disabled="workspace.isMutating || !reviewForm.rejection_reason"
              @click="rejectSelectedTask"
            >
              <ShieldAlert class="h-4 w-4" />
              Reject task
            </button>
          </div>
        </div>

        <div v-else class="mt-5 rounded-md border border-slate-200 bg-slate-50 px-4 py-6 text-sm text-graphite">
          No active task selected. Click a task in the queue to open the review panel.
        </div>
      </div>
    </section>

    <section class="rounded-lg border border-slate-200 bg-white p-5">
      <div class="flex items-center justify-between gap-3">
        <div>
          <h2 class="text-lg font-semibold text-ink">Available QA work</h2>
          <p class="mt-1 text-sm text-graphite">Claimable under-editing orders from the editor management queue.</p>
        </div>
        <UserPlus class="h-5 w-5 text-signal" />
      </div>

      <div class="mt-5 grid gap-3 lg:grid-cols-2">
        <div
          v-for="task in workspace.availableTasks"
          :key="String(task.id)"
          class="rounded-md border border-slate-200 p-4"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <h3 class="truncate text-sm font-semibold text-ink">{{ taskTitle(task) }}</h3>
              <p class="mt-1 text-xs text-graphite">
                Order #{{ task.order_id ?? task.order }} · {{ dateLabel(task.order_deadline) }}
              </p>
            </div>
            <StatusPill
              :label="relativeDeadline(task)"
              :tone="task.order_deadline && new Date(task.order_deadline) < new Date() ? 'danger' : 'neutral'"
            />
          </div>
          <button
            class="focus-ring mt-4 inline-flex w-full items-center justify-center gap-2 rounded-md bg-ink px-3 py-2.5 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
            type="button"
            :disabled="workspace.isMutating"
            @click="workspace.claim(task.order_id ?? task.order ?? task.id)"
          >
            <UserPlus class="h-4 w-4" />
            Claim order
          </button>
        </div>
        <div v-if="!workspace.availableTasks.length" class="rounded-md border border-slate-200 bg-slate-50 px-4 py-6 text-sm text-graphite">
          No claimable QA work is available right now.
        </div>
      </div>
    </section>
  </div>
</template>
