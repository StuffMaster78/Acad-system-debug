<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
  AlertCircle,
  BookOpen,
  CheckCircle2,
  Clock3,
  FileText,
  Loader2,
  RefreshCw,
  Zap,
} from "@lucide/vue";
import { RouterLink } from "vue-router";
import Pagination from "@/components/ui/Pagination.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useWriterWorkspaceStore } from "@/stores/writerWorkspace";
import type { OrderSummary } from "@/types/orders";

const workspace = useWriterWorkspaceStore();

type StatusTab = "active" | "submitted" | "completed";

const activeTab = ref<StatusTab>("active");

const tabDefs: Array<{ key: StatusTab; label: string; statuses: string[] }> = [
  { key: "active", label: "Active", statuses: ["in_progress", "revision_requested"] },
  { key: "submitted", label: "Submitted", statuses: ["submitted", "awaiting_approval"] },
  { key: "completed", label: "Completed", statuses: ["completed", "cancelled", "archived"] },
];

const statusParam = computed(() => tabDefs.find((t) => t.key === activeTab.value)?.statuses.join(","));

function statusTone(status: string): "success" | "warning" | "danger" | "neutral" {
  if (["completed"].includes(status)) return "success";
  if (["revision_requested"].includes(status)) return "warning";
  if (["cancelled"].includes(status)) return "danger";
  return "neutral";
}

function deadlineLabel(value: string | null | undefined): string {
  if (!value) return "No deadline";
  const h = (new Date(value).getTime() - Date.now()) / 3600000;
  if (h < 0) return `${Math.round(Math.abs(h))}h overdue`;
  if (h < 24) return `${Math.round(h)}h left`;
  return `${Math.round(h / 24)}d left`;
}

function deadlineTone(value: string | null | undefined): "danger" | "warning" | "neutral" {
  if (!value) return "neutral";
  const h = (new Date(value).getTime() - Date.now()) / 3600000;
  if (h < 0) return "danger";
  if (h < 12) return "warning";
  return "neutral";
}

function pagesLabel(order: OrderSummary): string {
  const pages = order.number_of_pages;
  if (!pages) return "—";
  const spacing = order.spacing ? ` (${order.spacing})` : "";
  return `${pages} page${Number(pages) !== 1 ? "s" : ""}${spacing}`;
}

function compensation(order: OrderSummary): string {
  if (!order.writer_compensation) return "—";
  const n = Number(order.writer_compensation);
  if (Number.isNaN(n)) return String(order.writer_compensation);
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: order.currency ?? "USD",
  }).format(n);
}

function accentBar(status: string): string {
  const s = status.toLowerCase();
  if (s === "revision_requested") return "border-l-amber-400";
  if (["submitted", "awaiting_approval"].includes(s)) return "border-l-sky-400";
  if (["completed", "approved"].includes(s)) return "border-l-emerald-500";
  if (["cancelled", "archived"].includes(s)) return "border-l-rose-400";
  return "border-l-blue-500"; // in_progress default
}

async function switchTab(tab: StatusTab) {
  activeTab.value = tab;
  await workspace.fetchAssignments(1, tabDefs.find((t) => t.key === tab)?.statuses.join(","));
}

function goToPage(page: number) {
  void workspace.fetchAssignments(page, statusParam.value);
}

onMounted(() => {
  void workspace.fetchAssignments(1, statusParam.value);
});
</script>

<template>
  <div class="space-y-5">

    <!-- Header -->
    <div class="flex items-center justify-between gap-4">
      <div>
        <p class="text-xs font-semibold uppercase tracking-widest text-signal">Writer</p>
        <h1 class="mt-1 text-2xl font-bold text-ink">My assignments</h1>
      </div>
      <button
        class="focus-ring inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-graphite hover:text-ink disabled:opacity-50"
        type="button"
        :disabled="workspace.isAssignmentsLoading"
        @click="void workspace.fetchAssignments(workspace.assignmentsPagination.page, statusParam)"
      >
        <Loader2 v-if="workspace.isAssignmentsLoading" class="h-3.5 w-3.5 animate-spin" />
        <RefreshCw v-else class="h-3.5 w-3.5" />
        Refresh
      </button>
    </div>

    <div v-if="workspace.assignmentsError" class="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ workspace.assignmentsError }}
    </div>
    <div v-if="workspace.notice" class="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
      {{ workspace.notice }}
    </div>

    <!-- Tab bar — fit-content, not full-width -->
    <div class="inline-flex gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1">
      <button
        v-for="tab in tabDefs" :key="tab.key"
        class="rounded-md px-4 py-1.5 text-sm font-semibold transition-colors"
        :class="activeTab === tab.key ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
        type="button"
        @click="switchTab(tab.key)"
      >{{ tab.label }}</button>
    </div>

    <!-- Skeletons -->
    <div v-if="workspace.isAssignmentsLoading" class="space-y-2">
      <div v-for="n in 4" :key="n" class="animate-pulse rounded-xl border border-slate-200 bg-white p-5">
        <div class="flex items-center justify-between gap-4">
          <div class="flex-1 space-y-2">
            <div class="h-4 w-3/5 rounded bg-slate-200" />
            <div class="h-3 w-2/5 rounded bg-slate-100" />
          </div>
          <div class="h-5 w-20 rounded-full bg-slate-100" />
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else-if="!workspace.assignments.length" class="rounded-xl border border-slate-200 bg-white px-6 py-12 text-center">
      <BookOpen class="mx-auto h-9 w-9 text-slate-200" />
      <p class="mt-3 text-sm font-semibold text-ink">No {{ activeTab }} assignments</p>
      <p class="mt-1 text-xs text-graphite">
        {{ activeTab === 'active' ? 'Browse the available orders pool to pick up work.' : 'Nothing here yet.' }}
      </p>
      <RouterLink
        v-if="activeTab === 'active'"
        to="/writer/available"
        class="focus-ring mt-4 inline-flex h-8 items-center gap-1.5 rounded-lg bg-signal px-4 text-xs font-semibold text-white hover:bg-signal/90"
      >
        Browse job pool
      </RouterLink>
    </div>

    <!-- Assignment cards -->
    <div v-else class="space-y-2">
      <RouterLink
        v-for="order in workspace.assignments"
        :key="order.id"
        :to="`/writer/orders/${order.id}`"
        class="group flex items-center gap-0 overflow-hidden rounded-xl border border-slate-200 bg-white transition-all hover:border-slate-300 hover:shadow-sm"
      >
        <!-- Accent bar -->
        <div class="w-1 self-stretch shrink-0 rounded-l-xl" :class="accentBar(order.status)" />

        <div class="flex flex-1 min-w-0 items-center gap-4 px-5 py-4">

          <!-- Topic + meta -->
          <div class="min-w-0 flex-1">
            <div class="flex flex-wrap items-center gap-2">
              <span class="text-xs font-semibold text-slate-400">#{{ order.id }}</span>
              <p class="truncate text-sm font-semibold text-ink group-hover:text-signal transition-colors">
                {{ order.topic || 'Untitled order' }}
              </p>
              <span
                v-if="order.is_urgent"
                class="inline-flex items-center gap-0.5 rounded-full bg-rose-100 px-1.5 py-0.5 text-xs font-bold text-rose-700"
              >
                <Zap class="h-2.5 w-2.5" /> Urgent
              </span>
            </div>
            <div class="mt-1 flex flex-wrap items-center gap-3 text-xs text-graphite">
              <span v-if="order.academic_level">{{ order.academic_level }}</span>
              <span v-if="order.number_of_pages" class="flex items-center gap-1">
                <FileText class="h-3 w-3" /> {{ pagesLabel(order) }}
              </span>
            </div>
          </div>

          <!-- Status -->
          <div class="hidden shrink-0 sm:block">
            <StatusPill :label="order.status" :tone="statusTone(order.status)" />
          </div>

          <!-- Deadline + compensation -->
          <div class="shrink-0 text-right">
            <div class="flex items-center justify-end gap-1">
              <component
                :is="deadlineTone(order.writer_deadline) === 'danger' ? AlertCircle : deadlineTone(order.writer_deadline) === 'warning' ? Clock3 : CheckCircle2"
                class="h-3.5 w-3.5"
                :class="{
                  'text-rose-500':  deadlineTone(order.writer_deadline) === 'danger',
                  'text-amber-500': deadlineTone(order.writer_deadline) === 'warning',
                  'text-slate-300': deadlineTone(order.writer_deadline) === 'neutral',
                }"
              />
              <span
                class="text-sm font-bold tabular-nums"
                :class="{
                  'text-rose-600':  deadlineTone(order.writer_deadline) === 'danger',
                  'text-amber-600': deadlineTone(order.writer_deadline) === 'warning',
                  'text-graphite':  deadlineTone(order.writer_deadline) === 'neutral',
                }"
              >{{ deadlineLabel(order.writer_deadline) }}</span>
            </div>
            <p class="mt-1 text-base font-extrabold text-ink tabular-nums">
              {{ compensation(order) }}
            </p>
          </div>
        </div>
      </RouterLink>
    </div>

    <Pagination
      :page="workspace.assignmentsPagination.page"
      :page-size="workspace.assignmentsPagination.pageSize"
      :count="workspace.assignmentsPagination.count"
      @update:page="goToPage"
    />

  </div>
</template>
